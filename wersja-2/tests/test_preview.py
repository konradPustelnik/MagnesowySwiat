"""Lokalne testy. Nie wysyłają e-maili ani zdjęć."""
import argparse
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
from urllib.parse import unquote, urlsplit, parse_qs

ROOT = Path(__file__).resolve().parents[1]
PRODUCTION = '--production' in __import__('sys').argv
if PRODUCTION: ROOT = ROOT.parent
PAGES = ['index.html', 'magnesy-na-zywo.html', 'magnesy-na-zamowienie.html']
if PRODUCTION: PAGES = ['index.html', 'magnesy-na-zywo/index.html', 'magnesy-na-zamowienie/index.html']
BROWSER = '--browser' in __import__('sys').argv

class CaptureHandler(SimpleHTTPRequestHandler):
    """Local-only receiver: tests must never send a real email."""
    def do_POST(self):
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
        super().__init__(); self.ids=[]; self.links=[]; self.assets=[]; self.h1=0; self.images=[]
    def handle_starttag(self, tag, attrs):
        attrs=dict(attrs)
        if 'id' in attrs: self.ids.append(attrs['id'])
        if tag=='a': self.links.append(attrs.get('href',''))
        if tag in ['img','script']: self.assets.append(attrs.get('src',''))
        if tag=='link': self.assets.append(attrs.get('href',''))
        if tag=='h1': self.h1+=1
        if tag=='img': self.images.append(attrs)

class StaticTests(unittest.TestCase):
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
        handler=partial(CaptureHandler,directory=str(ROOT if PRODUCTION else ROOT.parent))
        cls.server=ThreadingHTTPServer(('127.0.0.1',0),handler)
        Thread(target=cls.server.serve_forever,daemon=True).start()
        cls.base=f'http://127.0.0.1:{cls.server.server_port}/'+('' if PRODUCTION else 'wersja-2/')
        options=webdriver.ChromeOptions()
        options.add_argument('--headless=new'); options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1440,1000')
        cls.driver=webdriver.Chrome(options=options)
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
        d.execute_script("document.getElementById('f-date').value='2099-01-01'")
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
                    self.assertLessEqual(photo.rect['height'],240)
                    self.assertEqual(photo.value_of_css_property('object-fit'),'cover')
                if width<600:
                    self.assertEqual(len({card.rect['x'] for card in cards}),1)
                else:
                    self.assertEqual(len({card.rect['y'] for card in cards}),1)
                self.assertLessEqual(d.execute_script('return document.documentElement.scrollWidth'),width+1)
                artifacts=Path(__file__).parent/'artifacts'; artifacts.mkdir(exist_ok=True)
                d.execute_script("document.querySelector('.occasion-grid').scrollIntoView({behavior:'instant',block:'center'})")
                from selenium.webdriver.support.ui import WebDriverWait
                WebDriverWait(d,10).until(lambda browser: browser.execute_script("return [...document.querySelectorAll('.occasion-grid img')].every(img => img.complete && img.naturalWidth > 0)"))
                d.save_screenshot(str(artifacts/f'occasions-{width}.png'))
        finally:
            d.execute_cdp_cmd('Emulation.clearDeviceMetricsOverride',{})
    @unittest.skipUnless(PRODUCTION, 'Dotyczy produkcyjnych adresów')
    def test_home_url_hides_index_and_preserves_contact_anchor(self):
        from selenium.webdriver.common.by import By
        d=self.driver
        d.get(self.base+'index.html?preview=1#kontakt')
        self.assertEqual(d.current_url,self.base+'?preview=1#kontakt')
        for link in d.find_elements(By.CSS_SELECTOR,'.main-nav a'):
            self.assertNotIn('index.html',link.get_attribute('href'))
        self.assertTrue(d.find_element(By.ID,'kontakt').is_displayed())
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
            d.find_element(By.ID,'f-message').send_keys(':()@&%$#*($#^*!@(#&#@%&@(#$@!')
            d.find_element(By.NAME,'consent').click()
            d.find_element(By.CSS_SELECTOR,'form button[type=submit]').click()
            self.assertIn('__capture',d.current_url)
            self.assertEqual(len(self.server.uploads),2)
            self.assertEqual([item['filename'] for item in self.server.uploads],['test.png','second.png'])
            self.assertTrue(all(item['content']==image.read_bytes() for item in self.server.uploads))
            self.assertEqual(self.server.submission['Liczba magnesów'],['4'])
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

if __name__=='__main__':
    import sys
    unittest.main(argv=[sys.argv[0]]+[arg for arg in sys.argv[1:] if arg not in ['--browser','--production']])
