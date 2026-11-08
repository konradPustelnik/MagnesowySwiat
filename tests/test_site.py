"""Lokalne testy. Nie wysyłają e-maili ani zdjęć."""
import base64
from email.parser import BytesParser
from email.policy import default
from functools import partial
from html.parser import HTMLParser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import tempfile
from threading import Thread
import unittest
import xml.etree.ElementTree as ET
from urllib.parse import unquote, urlsplit, parse_qs

ROOT = Path(__file__).resolve().parents[1]
PAGES = ['index.html', 'magnesy-na-zywo/index.html', 'magnesy-na-zamowienie/index.html']
CANONICAL = 'https://magnesowyswiat.pl/'
BROWSER = '--browser' in __import__('sys').argv

class CaptureHandler(SimpleHTTPRequestHandler):
    """Local-only receiver: tests must never send a real email."""
    def log_message(self, *args):
        pass

    def handle(self):
        try:
            super().handle()
        except (BrokenPipeError, ConnectionResetError):
            pass  # Chrome may close speculative local connections.

    def do_POST(self):
        if urlsplit(self.path).path != '/__capture':
            self.send_error(404)
            return
        body=self.rfile.read(int(self.headers['Content-Length']))
        self.server.uploads=[]
        if self.headers['Content-Type'].startswith('multipart/form-data'):
            message=BytesParser(policy=default).parsebytes(b'Content-Type: '+self.headers['Content-Type'].encode()+b'\r\nMIME-Version: 1.0\r\n\r\n'+body)
            data={}
            for part in message.iter_parts():
                name=part.get_param('name',header='content-disposition')
                content=part.get_payload(decode=True)
                if part.get_filename():
                    self.server.uploads.append({'field':name,'filename':part.get_filename(),'content':content})
                else:
                    data.setdefault(name,[]).append(content.decode('utf-8'))
            self.server.submission=data
        else:
            self.server.submission=parse_qs(body.decode('utf-8'))
        self.send_response(200)
        self.send_header('Content-Type','text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(b'<!doctype html><title>Local test</title><p>Captured locally. No email sent.</p>')

class Parser(HTMLParser):
    def __init__(self):
        super().__init__(); self.ids=[]; self.links=[]; self.assets=[]; self.h1=0; self.images=[]; self.tags=[]
    def handle_starttag(self, tag, attrs):
        attrs=dict(attrs)
        self.tags.append((tag, attrs))
        if 'id' in attrs: self.ids.append(attrs['id'])
        if tag=='a': self.links.append(attrs.get('href',''))
        if tag in ['img','script']: self.assets.append(attrs.get('src',''))
        if tag=='link': self.assets.append(attrs.get('href',''))
        if tag=='h1': self.h1+=1
        if tag=='img': self.images.append(attrs)

class StaticTests(unittest.TestCase):
    def test_canonical_indexability_and_sitemap(self):
        expected = [CANONICAL + ('' if page == 'index.html' else page.removesuffix('index.html')) for page in PAGES]
        for page, canonical in zip(PAGES, expected):
            with self.subTest(page=page):
                source = (ROOT / page).read_text(encoding='utf-8')
                parser = Parser(); parser.feed(source)
                self.assertEqual([attrs.get('href') for tag, attrs in parser.tags if tag == 'link' and attrs.get('rel') == 'canonical'], [canonical])
                robots = [attrs.get('content', '').lower() for tag, attrs in parser.tags if tag == 'meta' and attrs.get('name', '').lower() == 'robots']
                self.assertFalse(any('noindex' in value or 'none' in value.split(',') for value in robots), page)
                self.assertEqual([attrs.get('lang') for tag, attrs in parser.tags if tag == 'html'], ['pl'])
                descriptions = [attrs.get('content', '').strip() for tag, attrs in parser.tags if tag == 'meta' and attrs.get('name') == 'description']
                self.assertEqual(len(descriptions), 1)
                self.assertTrue(descriptions[0], page)
                self.assertIn('<title>', source.lower())
        self.assertEqual((ROOT / 'CNAME').read_text(encoding='utf-8').strip(), urlsplit(CANONICAL).hostname)
        robots_source = (ROOT / 'robots.txt').read_text(encoding='utf-8')
        directives = [line.split('#', 1)[0].strip() for line in robots_source.splitlines()]
        self.assertIn('Sitemap: ' + CANONICAL + 'sitemap.xml', directives)
        blocked = [line.split(':', 1)[1].strip() for line in directives if line.lower().startswith('disallow:')]
        for canonical in expected:
            path = urlsplit(canonical).path
            self.assertFalse(any(prefix and (prefix == '/' or path.startswith(prefix)) for prefix in blocked), canonical)
        urls = ET.parse(ROOT / 'sitemap.xml').findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
        self.assertEqual([node.text for node in urls], expected)
        for url in expected:
            target = ROOT / urlsplit(url).path.lstrip('/') / 'index.html'
            self.assertTrue(target.is_file(), url)

    def test_legacy_redirects_preserve_destination_and_fragment(self):
        for slug in ['magnesy-na-zywo', 'magnesy-na-zamowienie']:
            with self.subTest(slug=slug):
                source = (ROOT / (slug + '.html')).read_text(encoding='utf-8')
                parser = Parser(); parser.feed(source)
                canonical = CANONICAL + slug + '/'
                self.assertEqual([attrs.get('href') for tag, attrs in parser.tags if tag == 'link' and attrs.get('rel') == 'canonical'], [canonical])
                fallback = [attrs.get('content', '') for tag, attrs in parser.tags if tag == 'meta' and attrs.get('http-equiv', '').lower() == 'refresh']
                self.assertEqual(len(fallback), 1)
                self.assertEqual(fallback[0].split('url=', 1)[-1].strip(), slug + '/')
                self.assertIn(slug + '/', parser.links)
                # Runtime behavior is also checked in the browser URL test.
                self.assertIn('location.replace', source)
                self.assertIn('location.search', source)
                self.assertIn('location.hash', source)
                self.assertTrue((ROOT / slug / 'index.html').is_file())

    def test_links_assets_and_structure(self):
        parsed={}
        for name in PAGES:
            parser=Parser(); parser.feed((ROOT/name).read_text(encoding='utf-8')); parsed[name]=parser
            self.assertEqual(parser.h1,1,name)
            self.assertEqual(len(parser.ids),len(set(parser.ids)),name)
            for img in parser.images: self.assertIn('alt',img)
        for name,parser in parsed.items():
            for href in parser.links+parser.assets:
                url=urlsplit(href)
                if url.scheme or not href: continue
                target=(Path(name).parent/unquote(url.path)).as_posix() if url.path else name
                resolved=(ROOT/target).resolve()
                if resolved.is_dir(): resolved=resolved/'index.html'
                target=resolved.relative_to(ROOT).as_posix()
                self.assertTrue((ROOT/target).is_file(),f'{name}: {href}')
                if url.fragment: self.assertIn(url.fragment,parsed[target].ids,f'{name}: {href}')

@unittest.skipUnless(BROWSER,'Dodaj --browser, aby uruchomić Chrome / Selenium')
class BrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from selenium import webdriver
        handler=partial(CaptureHandler,directory=str(ROOT))
        cls.server=ThreadingHTTPServer(('127.0.0.1',0),handler)
        Thread(target=cls.server.serve_forever,daemon=True).start()
        cls.base=f'http://127.0.0.1:{cls.server.server_port}/'
        options=webdriver.ChromeOptions()
        options.add_argument('--headless=new'); options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1440,1000')
        cls.driver=webdriver.Chrome(options=options)
        cls.driver.execute_cdp_cmd('Network.enable', {})
        cls.driver.execute_cdp_cmd('Network.setBlockedURLs', {'urls': ['*formsubmit.co*']})
        cls.driver.execute_cdp_cmd('Emulation.setEmulatedMedia', {'features':[{'name':'prefers-reduced-motion','value':'reduce'}]})
    @classmethod
    def tearDownClass(cls):
        cls.driver.quit(); cls.server.shutdown(); cls.server.server_close()
    def test_responsive_menu_and_pages(self):
        from selenium.webdriver.common.by import By
        d=self.driver
        for width,height in [(1440,1000),(390,844),(320,740)]:
            d.set_window_size(width,height)
            for page in PAGES:
                d.get(self.base+page)
                if width in [1440,390]:
                    artifacts=Path(__file__).parent/'artifacts'; artifacts.mkdir(exist_ok=True)
                    d.save_screenshot(str(artifacts/f'{Path(page).stem}-{width}.png'))
                self.assertLessEqual(d.execute_script('return document.documentElement.scrollWidth'),d.execute_script('return innerWidth')+1,page)
                self.assertFalse(d.execute_script('return [...document.images].some(i=>i.hasAttribute("src") && i.complete && i.naturalWidth===0)'),page)
                if width<981:
                    menu=d.find_element(By.CSS_SELECTOR,'.menu-toggle'); menu.click()
                    self.assertEqual(menu.get_attribute('aria-expanded'),'true')
                    d.find_element(By.CSS_SELECTOR,'.main-nav a').click()
        d.set_window_size(1440,1000)
    def test_pdf_offer_and_responsive_sections(self):
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        d = self.driver
        try:
            for width in [1440, 390, 320]:
                d.execute_cdp_cmd('Emulation.setDeviceMetricsOverride', {'width': width, 'height': 1000, 'deviceScaleFactor': 1, 'mobile': width < 600})
                for page, selectors in [(PAGES[0], ['.hero--home', '.offers-grid']), (PAGES[1], ['#jak-dzialamy', '#okazje', '#pakiety', '#rezerwacja'])]:
                    d.get(self.base + page)
                    d.execute_script('document.documentElement.style.scrollBehavior="auto"')
                    if page == PAGES[1]:
                        self.assertFalse(d.find_elements(By.ID, 'galeria'))
                        self.assertEqual(len(d.find_elements(By.CSS_SELECTOR, '#jak-dzialamy .process-step')), 3)
                        self.assertIn('30 km', d.find_element(By.CSS_SELECTOR, '.live-package-extras').text)
                        self.assertIn('10 zł/szt.', d.find_element(By.CSS_SELECTOR, '.live-package-extras').text)
                    for selector in selectors:
                        element = d.find_element(By.CSS_SELECTOR, selector)
                        d.execute_script('arguments[0].scrollIntoView({behavior:"instant"})', element)
                        WebDriverWait(d, 5).until(lambda browser: browser.execute_script('return [...arguments[0].querySelectorAll("img")].every(i => i.complete && i.naturalWidth > 0)', element))
                        self.assertLessEqual(d.execute_script('return document.documentElement.scrollWidth'), width + 1)
                        artifacts = Path(__file__).parent / 'artifacts'
                        artifacts.mkdir(exist_ok=True)
                        d.save_screenshot(str(artifacts / f'pdf-{selector.strip(".#")}-{width}.png'))
        finally:
            d.execute_cdp_cmd('Emulation.clearDeviceMetricsOverride', {})

    def test_service_name_navigates_instead_of_toggling(self):
        from selenium.webdriver.common.by import By
        from selenium.webdriver.common.action_chains import ActionChains
        from selenium.webdriver.support.ui import WebDriverWait
        d = self.driver
        d.set_window_size(1440, 1000)
        d.get(self.base + PAGES[2])
        link = d.find_element(By.CSS_SELECTOR, '[data-service="live"] .nav-service-link')
        target = link.get_attribute('href')
        ActionChains(d).move_to_element(link).perform()
        self.assertTrue(d.find_element(By.CSS_SELECTOR, '[data-service="live"]').get_attribute('open'))
        link.click()
        WebDriverWait(d, 5).until(lambda browser: browser.current_url.rstrip('/') == target.replace('index.html', '').rstrip('/'))
        link = d.find_element(By.CSS_SELECTOR, '[data-service="order"] .nav-service-link')
        target = link.get_attribute('href')
        link.send_keys('\ue007')
        WebDriverWait(d, 5).until(lambda browser: browser.current_url.rstrip('/') == target.replace('index.html', '').rstrip('/'))

    def test_quantity_choices_and_mobile_layout(self):
        from selenium.webdriver.common.by import By
        d = self.driver
        d.get(self.base + PAGES[2])
        d.execute_script('document.documentElement.style.scrollBehavior="auto"')
        for value in ['5', '20', '50', '100', '101']:
            link = d.find_element(By.CSS_SELECTOR, f'[data-quantity="{value}"]')
            d.execute_script('arguments[0].scrollIntoView({block:"center",behavior:"instant"})', link)
            link.click()
            self.assertEqual(d.find_element(By.ID, 'f-quantity').get_attribute('value'), value)
            self.assertTrue(d.current_url.endswith('#zamowienie'))
        try:
            for width in [1440, 390, 320]:
                d.execute_cdp_cmd('Emulation.setDeviceMetricsOverride', {'width': width, 'height': 900, 'deviceScaleFactor': 1, 'mobile': width < 600})
                self.assertLessEqual(d.execute_script('return document.documentElement.scrollWidth'), width + 1)
                for link in d.find_elements(By.CSS_SELECTOR, '[data-quantity]'):
                    self.assertGreaterEqual(link.rect['height'], 44)
                d.execute_script('document.getElementById("cennik").scrollIntoView({behavior:"instant"})')
                artifacts = Path(__file__).parent / 'artifacts'
                artifacts.mkdir(exist_ok=True)
                d.save_screenshot(str(artifacts / f'quantity-{width}.png'))
        finally:
            d.execute_cdp_cmd('Emulation.clearDeviceMetricsOverride', {})

    def test_reservation_special_characters_and_package(self):
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import Select
        d=self.driver; d.get(self.base+PAGES[1])
        form=d.find_element(By.CSS_SELECTOR,'form[data-inquiry="live"]')
        self.assertEqual(form.get_attribute('action'),'https://formsubmit.co/magnesowyswiat@gmail.com')
        self.assertEqual(form.get_attribute('method'),'post')
        self.assertFalse(d.find_elements(By.CSS_SELECTOR,'.preview-notice'))
        # Redirect only this local test to our receiver, never to FormSubmit.
        d.execute_script('arguments[0].action=arguments[1]',form,self.base+'__capture')
        d.find_element(By.CSS_SELECTOR,'[data-package="Gold"]').click()
        self.assertEqual(d.find_element(By.ID,'f-package').get_attribute('value'),'Gold')
        for name,value in [('name','Test lokalny'),('email','test@example.com'),('city','Limanowa'),('guests','100'),('message',':()@&%$#*($#^*!@(#&#@%&@(#$@!')]:
            d.find_element(By.ID,'f-'+name).send_keys(value)
        d.find_element(By.ID,'f-date').send_keys('01012099')
        Select(d.find_element(By.ID,'f-event')).select_by_visible_text('Wesele')
        d.find_element(By.NAME,'consent').click()
        d.find_element(By.CSS_SELECTOR,'form button[type=submit]').click()
        self.assertIn('__capture',d.current_url)
        data=self.server.submission
        self.assertEqual(data['Wiadomość'],[':()@&%$#*($#^*!@(#&#@%&@(#$@!'])
        self.assertEqual(data['Wybrany pakiet'],['Gold'])
        self.assertEqual(data['email'],['test@example.com'])
        self.assertEqual(data['_captcha'],['false'])
        self.assertEqual(data['_template'],['table'])
        self.assertEqual(data['Data wydarzenia'],['01/01/2099'])
        self.assertEqual(data['_subject'],['[NA ŻYWO] Zapytanie o termin | Magnesowy Świat'])
        self.assertEqual(data['Rodzaj zapytania'],['Magnesy na żywo'])
    def test_footer_icons_stay_small_without_stylesheet(self):
        from selenium.webdriver.common.by import By
        d=self.driver
        for page in PAGES:
            d.get(self.base+page)
            icons=d.find_elements(By.CSS_SELECTOR,'.site-footer .social-icon')
            self.assertEqual(len(icons),3)
            for icon in icons:
                self.assertEqual(icon.rect['width'],18)
                self.assertEqual(icon.rect['height'],18)
            d.execute_script("document.querySelector('link[rel=stylesheet]').disabled=true")
            for icon in icons:
                self.assertEqual(icon.rect['width'],18)
                self.assertEqual(icon.rect['height'],18)
                self.assertEqual(icon.get_attribute('fill'),'none')
    def test_occasion_photos_have_consistent_crops_on_mobile_and_desktop(self):
        from selenium.webdriver.common.by import By
        d=self.driver
        try:
            for width in [1440,390,320]:
                d.execute_cdp_cmd('Emulation.setDeviceMetricsOverride',{'width':width,'height':1000,'deviceScaleFactor':1,'mobile':width<600})
                d.get(self.base+PAGES[1])
                cards=d.find_elements(By.CSS_SELECTOR,'.occasion-grid article')
                photos=d.find_elements(By.CSS_SELECTOR,'.occasion-grid img')
                self.assertEqual(len(photos),4)
                self.assertEqual(len({photo.rect['height'] for photo in photos}),1)
                for photo in photos:
                    # The PDF requests two large cards per row, with 16:9 photos.
                    self.assertAlmostEqual(photo.rect['width'] / photo.rect['height'], 16 / 9, delta=.03)
                    self.assertEqual(photo.value_of_css_property('object-fit'),'cover')
                if width<600:
                    self.assertEqual(len({card.rect['x'] for card in cards}),1)
                else:
                    self.assertEqual(len({card.rect['x'] for card in cards}),2)
                    self.assertEqual(len({card.rect['y'] for card in cards}),2)
                self.assertLessEqual(d.execute_script('return document.documentElement.scrollWidth'),width+1)
                artifacts=Path(__file__).parent/'artifacts'; artifacts.mkdir(exist_ok=True)
                d.execute_script("document.querySelector('.occasion-grid').scrollIntoView({behavior:'instant',block:'center'})")
                from selenium.webdriver.support.ui import WebDriverWait
                WebDriverWait(d,10).until(lambda browser: browser.execute_script("return [...document.querySelectorAll('.occasion-grid img')].every(img => img.complete && img.naturalWidth > 0)"))
                d.save_screenshot(str(artifacts/f'occasions-{width}.png'))
        finally:
            d.execute_cdp_cmd('Emulation.clearDeviceMetricsOverride',{})
    def test_home_url_hides_index_and_preserves_contact_anchor(self):
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        d=self.driver
        d.get(self.base+'index.html?preview=1#kontakt')
        self.assertEqual(d.current_url,self.base+'?preview=1#kontakt')
        for link in d.find_elements(By.CSS_SELECTOR,'.main-nav a'):
            self.assertNotIn('index.html',link.get_attribute('href'))
        self.assertTrue(d.find_element(By.ID,'kontakt').is_displayed())
        for slug, anchor in [('magnesy-na-zywo', 'rezerwacja'), ('magnesy-na-zamowienie', 'zamowienie')]:
            d.get(self.base + slug + '.html?source=test#' + anchor)
            expected = self.base + slug + '/?source=test#' + anchor
            WebDriverWait(d, 5).until(lambda browser: browser.current_url == expected)
            self.assertTrue(d.find_element(By.ID, anchor).is_displayed())
    def test_order_preview_counts_delete_and_validation(self):
        from selenium.webdriver.common.by import By
        d=self.driver; d.get(self.base+PAGES[2])
        form=d.find_element(By.CSS_SELECTOR,'form[data-inquiry="order"]')
        self.assertFalse(d.find_elements(By.ID,'draft-dialog'))
        self.assertEqual(form.get_attribute('action'),'https://formsubmit.co/magnesowyswiat@gmail.com')
        self.assertEqual(form.get_attribute('enctype'),'multipart/form-data')
        self.assertFalse(d.find_elements(By.CSS_SELECTOR,'.preview-notice'))
        d.execute_script('arguments[0].action=arguments[1]',form,self.base+'__capture')
        with tempfile.TemporaryDirectory() as folder:
            image=Path(folder)/'test.png'
            image.write_bytes(base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII='))
            d.find_element(By.ID,'photos').send_keys(str(image))
            self.assertEqual(len(d.find_elements(By.CSS_SELECTOR,'.photo-preview')),1)
            count=d.find_element(By.CSS_SELECTOR,'.photo-preview input')
            d.execute_script("arguments[0].value=3;arguments[0].dispatchEvent(new Event('input'))",count)
            self.assertEqual(d.find_element(By.ID,'f-quantity').get_attribute('value'),'3')
            d.find_element(By.CSS_SELECTOR,'.remove-photo').click()
            self.assertEqual(len(d.find_elements(By.CSS_SELECTOR,'.photo-preview')),0)
            second=Path(folder)/'second.png'; second.write_bytes(image.read_bytes())
            d.find_element(By.ID,'photos').send_keys(str(image)+'\n'+str(second))
            count=d.find_element(By.CSS_SELECTOR,'.photo-preview input')
            d.execute_script("arguments[0].value=3;arguments[0].dispatchEvent(new Event('input'))",count)
            d.find_element(By.ID,'f-name').send_keys('Test lokalny')
            d.find_element(By.ID,'f-email').send_keys('test@example.com')
            for id,value in [('f-delivery-town','Testowa miejscowość'),('f-delivery-street','Testowa'),('f-delivery-house','12A/3'),('f-post-office','Poczta testowa')]:
                d.find_element(By.ID,id).send_keys(value)
            code=d.find_element(By.ID,'f-postal-code')
            code.send_keys('1234')
            self.assertFalse(d.execute_script('return arguments[0].checkValidity()',code))
            code.clear(); code.send_keys('34500')
            self.assertEqual(code.get_attribute('value'),'34-500')
            self.assertTrue(d.find_element(By.ID,'document-receipt').is_selected())
            d.find_element(By.ID,'document-invoice').click()
            self.assertFalse(d.find_element(By.ID,'document-receipt').is_selected())
            d.find_element(By.ID,'f-message').send_keys(':()@&%$#*($#^*!@(#&#@%&@(#$@!')
            d.find_element(By.NAME,'consent').click()
            d.find_element(By.CSS_SELECTOR,'form button[type=submit]').click()
            self.assertIn('__capture',d.current_url)
            self.assertEqual(len(self.server.uploads),2)
            self.assertEqual([item['filename'] for item in self.server.uploads],['test.png','second.png'])
            self.assertTrue(all(item['content']==image.read_bytes() for item in self.server.uploads))
            self.assertEqual(self.server.submission['Liczba magnesów'],['4'])
            self.assertEqual(self.server.submission['Miejscowość dostawy'],['Testowa miejscowość'])
            self.assertEqual(self.server.submission['Ulica'],['Testowa'])
            self.assertEqual(self.server.submission['Numer domu/lokalu'],['12A/3'])
            self.assertEqual(self.server.submission['Kod pocztowy'],['34-500'])
            self.assertEqual(self.server.submission['Poczta'],['Poczta testowa'])
            self.assertEqual(self.server.submission['Dokument zakupu'],['Faktura imienna'])
            self.assertEqual(self.server.submission['_subject'],['[NA ZAMÓWIENIE] Zapytanie o magnesy ze zdjęć | Magnesowy Świat'])
            self.assertEqual(self.server.submission['Rodzaj zapytania'],['Magnesy na zamówienie ze zdjęć'])
            self.assertIn('test.png: 3 szt.',self.server.submission['Zdjęcia i liczba kopii'][0])
            self.assertIn('second.png: 1 szt.',self.server.submission['Zdjęcia i liczba kopii'][0])
            self.assertEqual(self.server.submission['Uwagi do zamówienia'],[':()@&%$#*($#^*!@(#&#@%&@(#$@!'])
    def test_order_total_attachment_limit(self):
        from selenium.webdriver.common.by import By
        d=self.driver; d.get(self.base+PAGES[2])
        d.execute_script("""
          const input=document.getElementById('photos'); const files=new DataTransfer();
          files.items.add(new File([new Uint8Array(6000000)],'first.png',{type:'image/png'}));
          files.items.add(new File([new Uint8Array(5000000)],'too-large.png',{type:'image/png'}));
          input.files=files.files; input.dispatchEvent(new Event('change'));
        """)
        self.assertEqual(len(d.find_elements(By.CSS_SELECTOR,'.photo-preview')),1)
        self.assertIn('10 MB',d.find_element(By.ID,'photo-status').text)
        self.assertFalse(d.find_elements(By.CSS_SELECTOR,'[data-attachments] input'))
    def test_return_dialog_countdown_and_manual_home(self):
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        d=self.driver
        for index,page in enumerate(PAGES[1:]):
            d.get(self.base+page+'?wyslano=1')
            dialog=d.find_element(By.CSS_SELECTOR,'.send-confirmation[open]')
            self.assertTrue(dialog.is_displayed())
            self.assertIn('Dziękujemy',dialog.text)
            self.assertNotIn('wyslano=',d.current_url)
            if index:
                dialog.find_element(By.TAG_NAME,'button').click()
            WebDriverWait(d,8).until(lambda browser: browser.current_url in [self.base,self.base+'index.html'])
            self.assertFalse(d.find_elements(By.CSS_SELECTOR,'.send-confirmation[open]'))
    def test_live_dropdown_desktop_keyboard_and_mobile(self):
        from selenium.webdriver.common.by import By
        from selenium.webdriver.common.keys import Keys
        from selenium.webdriver.common.action_chains import ActionChains
        from selenium.webdriver.support.ui import WebDriverWait
        d=self.driver
        try:
            d.set_window_size(1440,1000); d.get(self.base)
            summary=d.find_element(By.CSS_SELECTOR,'.nav-dropdown summary')
            ActionChains(d).move_to_element(summary).perform()
            self.assertTrue(d.find_element(By.CSS_SELECTOR,'.nav-dropdown').get_attribute('open'))
            summary.send_keys(Keys.ESCAPE)
            self.assertFalse(d.find_element(By.CSS_SELECTOR,'.nav-dropdown').get_attribute('open'))
            self.assertEqual(d.switch_to.active_element,summary)
            summary.send_keys(Keys.ENTER)
            self.assertTrue(d.find_element(By.CSS_SELECTOR,'.nav-dropdown').get_attribute('open'))
            artifacts=Path(__file__).parent/'artifacts'; artifacts.mkdir(exist_ok=True)
            d.save_screenshot(str(artifacts/'service-dropdown-desktop.png'))
            d.find_element(By.CSS_SELECTOR,'.nav-dropdown a[href$="#pakiety"]').click()
            WebDriverWait(d,5).until(lambda browser: browser.current_url.endswith('#pakiety'))
            self.assertFalse(d.find_elements(By.CSS_SELECTOR,'.live-section-nav'))
            for width in [1024,981,390,320]:
                d.execute_cdp_cmd('Emulation.setDeviceMetricsOverride',{'width':width,'height':1000,'deviceScaleFactor':1,'mobile':width<600})
                d.get(self.base)
                self.assertLessEqual(d.execute_script('return document.documentElement.scrollWidth'),width+1)
                if width<981:
                    d.find_element(By.CSS_SELECTOR,'.menu-toggle').click()
                    d.find_element(By.CSS_SELECTOR,'.nav-dropdown .nav-chevron').click()
                    self.assertTrue(d.find_element(By.CSS_SELECTOR,'.nav-dropdown').get_attribute('open'))
                    if width==390: d.save_screenshot(str(artifacts/'service-dropdown-mobile.png'))
                    d.find_element(By.CSS_SELECTOR,'.nav-dropdown a[href$="#pakiety"]').click()
                    WebDriverWait(d,5).until(lambda browser: browser.current_url.endswith('#pakiety'))
                    self.assertEqual(d.find_element(By.CSS_SELECTOR,'.menu-toggle').get_attribute('aria-expanded'),'false')
        finally:
            d.execute_cdp_cmd('Emulation.clearDeviceMetricsOverride',{})
    def test_event_date_polish_format_validation_and_calendar(self):
        from selenium.webdriver.common.by import By
        d=self.driver; d.get(self.base+PAGES[1])
        date=d.find_element(By.ID,'f-date')
        self.assertEqual(date.get_attribute('placeholder'),'dd/mm/rrrr')
        date.send_keys('28112099')
        self.assertEqual(date.get_attribute('value'),'28/11/2099')
        self.assertTrue(d.execute_script('return arguments[0].checkValidity()',date))
        for value in ['31/02/2099','29/02/2100','01/01/2000']:
            d.execute_script("arguments[0].value=arguments[1];arguments[0].dispatchEvent(new Event('change'))",date,value)
            self.assertFalse(d.execute_script('return arguments[0].checkValidity()',date),value)
        d.execute_script("arguments[0].value='29/02/2096';arguments[0].dispatchEvent(new Event('change'))",date)
        self.assertTrue(d.execute_script('return arguments[0].checkValidity()',date))
        d.execute_script("const picker=document.getElementById('date-picker');picker.value='2099-11-28';picker.dispatchEvent(new Event('change'))")
        self.assertEqual(date.get_attribute('value'),'28/11/2099')
        self.assertTrue(d.find_element(By.ID,'date-picker-button').is_enabled())
    def test_order_dropdown_and_exclusive_open_state(self):
        from selenium.webdriver.common.by import By
        from selenium.webdriver.common.action_chains import ActionChains
        from selenium.webdriver.support.ui import WebDriverWait
        d=self.driver
        try:
            d.set_window_size(1440,1000); d.get(self.base)
            live=d.find_element(By.CSS_SELECTOR,'[data-service="live"]')
            order=d.find_element(By.CSS_SELECTOR,'[data-service="order"]')
            ActionChains(d).move_to_element(live.find_element(By.TAG_NAME,'summary')).perform()
            self.assertTrue(live.get_attribute('open'))
            ActionChains(d).move_to_element(order.find_element(By.TAG_NAME,'summary')).perform()
            WebDriverWait(d,3).until(lambda browser: not live.get_attribute('open'))
            self.assertTrue(order.get_attribute('open'))
            artifacts=Path(__file__).parent/'artifacts'; artifacts.mkdir(exist_ok=True)
            d.save_screenshot(str(artifacts/'order-dropdown-desktop.png'))
            order.find_element(By.CSS_SELECTOR,'a[href$="#cennik"]').click()
            WebDriverWait(d,5).until(lambda browser: browser.current_url.endswith('#cennik'))
            self.assertTrue(d.find_element(By.ID,'cennik').is_displayed())
            for width in [1024,981,390,320]:
                d.execute_cdp_cmd('Emulation.setDeviceMetricsOverride',{'width':width,'height':1000,'deviceScaleFactor':1,'mobile':width<600})
                d.get(self.base)
                self.assertLessEqual(d.execute_script('return document.documentElement.scrollWidth'),width+1)
                if width<981:
                    d.find_element(By.CSS_SELECTOR,'.menu-toggle').click()
                    d.find_element(By.CSS_SELECTOR,'[data-service="order"] .nav-chevron').click()
                    d.find_element(By.CSS_SELECTOR,'[data-service="order"] a[href$="#faq"]').click()
                    WebDriverWait(d,5).until(lambda browser: browser.current_url.endswith('#faq'))
                    self.assertEqual(d.find_element(By.CSS_SELECTOR,'.menu-toggle').get_attribute('aria-expanded'),'false')
        finally:
            d.execute_cdp_cmd('Emulation.clearDeviceMetricsOverride',{})
    def test_calendar_polish_labels_selection_and_mobile(self):
        from selenium.webdriver.common.by import By
        from selenium.webdriver.common.keys import Keys
        from selenium.webdriver.support.ui import Select
        d=self.driver; d.get(self.base+PAGES[1])
        date=d.find_element(By.ID,'f-date')
        date.send_keys('28112099')
        trigger=d.find_element(By.ID,'date-picker-button'); trigger.click()
        dialog=d.find_element(By.CSS_SELECTOR,'#event-calendar[open]')
        self.assertEqual(Select(dialog.find_element(By.CSS_SELECTOR,'.calendar-month')).first_selected_option.text,'Listopad')
        self.assertEqual([day.text for day in dialog.find_elements(By.TAG_NAME,'th')],['Pon','Wt','Śr','Czw','Pt','Sob','Nd'])
        selected=d.switch_to.active_element
        self.assertEqual(selected.get_attribute('data-date'),'2099-11-28')
        self.assertIn('listopada',selected.get_attribute('aria-label'))
        selected.send_keys(Keys.ARROW_RIGHT)
        d.switch_to.active_element.send_keys(Keys.ENTER)
        self.assertEqual(date.get_attribute('value'),'29/11/2099')
        self.assertFalse(dialog.get_attribute('open'))
        trigger.click()
        dialog.find_element(By.CSS_SELECTOR,'.calendar-next').click()
        self.assertEqual(Select(dialog.find_element(By.CSS_SELECTOR,'.calendar-month')).first_selected_option.text,'Grudzień')
        year=dialog.find_element(By.CSS_SELECTOR,'.calendar-year'); year.send_keys(Keys.CONTROL,'a'); year.send_keys('2096',Keys.TAB)
        self.assertEqual(year.get_attribute('value'),'2096')
        Select(dialog.find_element(By.CSS_SELECTOR,'.calendar-month')).select_by_visible_text('Luty')
        dialog.find_element(By.CSS_SELECTOR,'[data-date="2096-02-29"]').click()
        self.assertEqual(date.get_attribute('value'),'29/02/2096')
        trigger.click(); year.send_keys(Keys.CONTROL,'a'); year.send_keys('2100',Keys.TAB)
        self.assertFalse(dialog.find_elements(By.CSS_SELECTOR,'[data-date="2100-02-29"]'))
        dialog.find_element(By.CSS_SELECTOR,'.calendar-close').click()
        artifacts=Path(__file__).parent/'artifacts'; artifacts.mkdir(exist_ok=True)
        try:
            for width in [1440,390,320]:
                d.execute_cdp_cmd('Emulation.setDeviceMetricsOverride',{'width':width,'height':900,'deviceScaleFactor':1,'mobile':width<600})
                trigger.click()
                self.assertLessEqual(d.execute_script('return document.documentElement.scrollWidth'),width+1)
                self.assertLessEqual(dialog.rect['width'],width)
                d.save_screenshot(str(artifacts/f'calendar-polish-{width}.png'))
                dialog.find_element(By.CSS_SELECTOR,'.calendar-close').click()
        finally:
            d.execute_cdp_cmd('Emulation.clearDeviceMetricsOverride',{})

if __name__=='__main__':
    import sys
    unittest.main(argv=[sys.argv[0]]+[arg for arg in sys.argv[1:] if arg not in ['--browser']])
