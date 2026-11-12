"""Lokalne testy. Nie wysyłają e-maili ani zdjęć."""
import base64
import json
import re
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
from urllib.parse import unquote, urlsplit, parse_qs, urljoin

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
        titles = []
        descriptions_seen = []
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
                descriptions_seen.append(descriptions[0])
                page_titles = re.findall(r'<title>(.*?)</title>', source, re.S)
                self.assertEqual(len(page_titles), 1, page)
                self.assertIn('Magnesowy Świat', page_titles[0])
                titles.append(page_titles[0])
                # All three canonical pages must be reachable through real HTML links.
                linked_paths = {urlsplit(urljoin(canonical, href)).path for href in parser.links}
                self.assertTrue({'/', '/magnesy-na-zywo/', '/magnesy-na-zamowienie/'} <= linked_paths, page)
                if page != 'index.html':
                    nodes = [json.loads(block) for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', source, re.S)]
                    trails = [node for node in nodes if node.get('@type') == 'BreadcrumbList']
                    self.assertEqual(len(trails), 1)
                    self.assertEqual(trails[0]['@context'], 'https://schema.org')
                    items = trails[0]['itemListElement']
                    self.assertEqual([item['position'] for item in items], [1, 2])
                    self.assertEqual([item['item'] for item in items], [CANONICAL, canonical])
                    self.assertTrue(all(item['@type'] == 'ListItem' and item['name'] for item in items))
        self.assertEqual(len(set(titles)), len(PAGES))
        self.assertEqual(len(set(descriptions_seen)), len(PAGES))
        self.assertEqual(titles[0], 'Magnesowy Świat – Magnesy na każdą okazję')
        home = (ROOT / PAGES[0]).read_text(encoding='utf-8')
        structured = [json.loads(block) for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', home, re.S)]
        websites = [node for node in structured if node.get('@type') == 'WebSite']
        self.assertEqual(len(websites), 1)
        self.assertEqual(websites[0]['@context'], 'https://schema.org')
        self.assertEqual(websites[0]['name'], 'Magnesowy Świat')
        self.assertEqual(websites[0]['url'], CANONICAL)
        self.assertIn('magnesy na żywo', descriptions_seen[0])
        self.assertIn('magnesy na zamówienie', descriptions_seen[0])
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
    def test_home_service_choices_fit_first_viewport(self):
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        d = self.driver
        artifacts = Path(__file__).parent / 'artifacts'
        artifacts.mkdir(exist_ok=True)
        home_destinations = ['/magnesy-na-zywo/', '/magnesy-na-zamowienie/']
        pages = [
            ('home', '', '.hero--home', [(path, '') for path in home_destinations]),
            ('live', 'magnesy-na-zywo/', '.hero--live', [('/magnesy-na-zywo/', 'pakiety'), ('/magnesy-na-zywo/', 'rezerwacja')]),
            ('order', 'magnesy-na-zamowienie/', '.hero--order', [('/magnesy-na-zamowienie/', 'cennik'), ('/magnesy-na-zamowienie/', 'zamowienie')]),
        ]
        viewports = [(1440, 900), (1366, 768), (1024, 768), (768, 1024), (390, 844), (360, 740), (320, 640)]
        try:
            for width, height in viewports:
                d.execute_cdp_cmd('Emulation.setDeviceMetricsOverride', {'width': width, 'height': height, 'deviceScaleFactor': 1, 'mobile': width < 600})
                for name, path, selector, destinations in pages:
                    with self.subTest(page=name, viewport=f'{width}x{height}'):
                        d.get(self.base + path)
                        d.execute_async_script('''
                            const done = arguments[arguments.length - 1];
                            document.fonts.ready.then(() => {
                                document.documentElement.style.scrollBehavior = 'auto';
                                window.scrollTo({top: 0, left: 0, behavior: 'instant'});
                                requestAnimationFrame(() => requestAnimationFrame(done));
                            });
                        ''')
                        self.assertEqual(d.execute_script('return [innerWidth, innerHeight, scrollY]'), [width, height, 0])
                        choices = d.find_elements(By.CSS_SELECTOR, selector + ' .actions a')
                        self.assertEqual(len(choices), len(destinations))
                        header_bottom = d.execute_script('return document.querySelector(".site-header").getBoundingClientRect().bottom')
                        if name in ['home', 'live']:
                            story = d.find_element(By.CSS_SELECTOR, selector + ' .hero-story')
                            story_bottom = d.execute_script('return arguments[0].getBoundingClientRect().bottom', story)
                            self.assertEqual(d.execute_script('return getComputedStyle(arguments[0]).textAlign', story), 'center')
                            h1_weight = d.execute_script('return getComputedStyle(document.querySelector(arguments[0] + " h1")).fontWeight', selector)
                            if name == 'live':
                                self.assertEqual(int(h1_weight), 500)
                            else:
                                self.assertGreaterEqual(int(h1_weight), 600)
                        if name == 'live':
                            image = d.find_element(By.CSS_SELECTOR, selector + ' .hero-image img')
                            image_size = d.execute_script('const r=arguments[0].getBoundingClientRect(); return [r.width,r.height]', image)
                            self.assertAlmostEqual(image_size[0] / image_size[1], 1627 / 916, delta=0.01)
                            column_width = d.execute_script('return arguments[0].parentElement.getBoundingClientRect().width', image)
                            self.assertAlmostEqual(image_size[0], column_width, delta=1)
                        if name == 'home':
                            widths = [d.execute_script('return arguments[0].getBoundingClientRect().width', choice) for choice in choices]
                            self.assertAlmostEqual(widths[0], widths[1], delta=1)
                            h1_weight = d.execute_script('return getComputedStyle(document.querySelector(".hero--home h1")).fontWeight')
                            self.assertGreaterEqual(int(h1_weight), 600)
                        for choice, destination in zip(choices, destinations):
                            self.assertTrue(choice.is_displayed())
                            url = urlsplit(choice.get_attribute('href'))
                            self.assertEqual((url.path, url.fragment), destination)
                            rect = d.execute_script('const r = arguments[0].getBoundingClientRect(); return {top:r.top,bottom:r.bottom,left:r.left,right:r.right,height:r.height}', choice)
                            self.assertGreaterEqual(rect['height'], 44, destination)
                            self.assertGreaterEqual(rect['top'], header_bottom - 1, destination)
                            if name in ['home', 'live']:
                                self.assertGreaterEqual(rect['top'], story_bottom - 1, 'Actions must follow the complete hero description')
                            if name == 'order' or width >= 981:
                                self.assertLessEqual(rect['bottom'], height, f'{destination} requires scrolling at {width}x{height}')
                            self.assertGreaterEqual(rect['left'], 0, destination)
                            self.assertLessEqual(rect['right'], width, destination)
                        self.assertLessEqual(d.execute_script('return document.documentElement.scrollWidth'), width + 1)
                        d.save_screenshot(str(artifacts / f'{name}-compact-{width}x{height}.png'))

                        if name == 'home':
                            offers = d.find_element(By.CSS_SELECTOR, '.offers-grid')
                            cards = offers.find_elements(By.CSS_SELECTOR, '.offer')
                            self.assertEqual(len(cards), 2)
                            for card, destination in zip(cards, home_destinations):
                                links = card.find_elements(By.TAG_NAME, 'a')
                                self.assertGreaterEqual(len(links), 1)
                                self.assertTrue(all(urlsplit(link.get_attribute('href')).path == destination for link in links))
                            if width in [1440, 390]:
                                d.execute_script('arguments[0].scrollIntoView({behavior:"instant",block:"start"})', offers)
                                WebDriverWait(d, 5).until(lambda browser: browser.execute_script('return [...arguments[0].querySelectorAll("img")].every(i => i.complete && i.naturalWidth > 0)', offers))
                                d.execute_async_script('const done=arguments[arguments.length-1]; requestAnimationFrame(()=>requestAnimationFrame(done))')
                                d.save_screenshot(str(artifacts / f'home-offers-{width}.png'))
        finally:
            d.execute_cdp_cmd('Emulation.clearDeviceMetricsOverride', {})

    def test_process_anchor_keeps_next_heading_below_viewport(self):
        from selenium.webdriver.support.ui import WebDriverWait
        d = self.driver
        try:
            for width, height in [(1440, 900), (1366, 650), (1192, 580), (390, 844)]:
                d.execute_cdp_cmd('Emulation.setDeviceMetricsOverride', {'width': width, 'height': height, 'deviceScaleFactor': 1, 'mobile': width < 600})
                d.get(self.base + 'magnesy-na-zywo/')
                d.execute_async_script('document.fonts.ready.then(arguments[0])')
                d.execute_script('document.documentElement.style.scrollBehavior="auto";location.hash="jak-dzialamy"')
                WebDriverWait(d, 5).until(lambda browser: browser.execute_script('return document.querySelector("#okazje").getBoundingClientRect().top >= innerHeight - 1'))
                self.assertLessEqual(d.execute_script('return document.documentElement.scrollWidth'), width + 1)
                d.execute_script('location.hash="okazje"')
                WebDriverWait(d, 5).until(lambda browser: browser.execute_script('return document.querySelector("#okazje h2").getBoundingClientRect().top < 180'))
                if width >= 981:
                    self.assertLessEqual(d.execute_script('return document.querySelectorAll(".live-occasions .occasion-card")[2].getBoundingClientRect().bottom'), height)
        finally:
            d.execute_cdp_cmd('Emulation.clearDeviceMetricsOverride', {})

    def test_live_sections_do_not_reveal_next_section(self):
        from selenium.webdriver.support.ui import WebDriverWait
        d = self.driver
        try:
            for width, height in [(1440, 900), (1366, 650), (1192, 580), (390, 844), (320, 740)]:
                d.execute_cdp_cmd('Emulation.setDeviceMetricsOverride', {'width': width, 'height': height, 'deviceScaleFactor': 1, 'mobile': width < 600})
                d.get(self.base + 'magnesy-na-zywo/')
                d.execute_async_script('document.fonts.ready.then(arguments[0])')
                sections = d.execute_script('return [...document.querySelectorAll("main > section")].map(s=>s.id)')
                self.assertEqual(len(sections), 7)
                for section_id in sections:
                    with self.subTest(viewport=(width, height), section=section_id):
                        d.execute_script('document.documentElement.style.scrollBehavior="auto";location.hash=arguments[0];document.getElementById(arguments[0]).scrollIntoView({behavior:"instant"})', section_id)
                        WebDriverWait(d, 5).until(lambda browser: browser.execute_script('const s=document.getElementById(arguments[0]);return s.nextElementSibling ? s.nextElementSibling.getBoundingClientRect().top>=innerHeight-1 : document.querySelector(".site-footer").getBoundingClientRect().top>=innerHeight-1', section_id))
                        self.assertLessEqual(d.execute_script('return document.documentElement.scrollWidth'), width + 1)
        finally:
            d.execute_cdp_cmd('Emulation.clearDeviceMetricsOverride', {})

    def test_order_sections_do_not_reveal_next_section(self):
        from selenium.webdriver.support.ui import WebDriverWait
        d = self.driver
        try:
            for width, height in [(1440, 900), (1366, 650), (1192, 580), (390, 844), (320, 740)]:
                d.execute_cdp_cmd('Emulation.setDeviceMetricsOverride', {'width': width, 'height': height, 'deviceScaleFactor': 1, 'mobile': width < 600})
                d.get(self.base + 'magnesy-na-zamowienie/')
                d.execute_async_script('document.fonts.ready.then(arguments[0])')
                sections = d.execute_script('return [...document.querySelectorAll("main > section")].map(s=>s.id)')
                self.assertEqual(len(sections), 7)
                for section_id in sections[:-1]:
                    with self.subTest(viewport=(width, height), section=section_id):
                        d.execute_script('document.documentElement.style.scrollBehavior="auto";location.hash=arguments[0];document.getElementById(arguments[0]).scrollIntoView({behavior:"instant"})', section_id)
                        WebDriverWait(d, 5).until(lambda browser: browser.execute_script('const s=document.getElementById(arguments[0]);return s.nextElementSibling ? s.nextElementSibling.getBoundingClientRect().top>=innerHeight-1 : document.querySelector(".site-footer").getBoundingClientRect().top>=innerHeight-1', section_id))
                        self.assertLessEqual(d.execute_script('return document.documentElement.scrollWidth'), width + 1)
                if width > 980:
                    order_step_heading_size = d.execute_script('return parseFloat(getComputedStyle(document.querySelector("#jak-zamowic .process-step h3")).fontSize)')
                    order_step_text_size = d.execute_script('return parseFloat(getComputedStyle(document.querySelector("#jak-zamowic .process-step p")).fontSize)')
                    order_padding_top = d.execute_script('return parseFloat(getComputedStyle(document.getElementById("zamowienie")).paddingTop)')
                    faq_height = d.execute_script('return document.getElementById("faq").getBoundingClientRect().height')
                    contact_and_footer = d.execute_script('const c=document.getElementById("kontakt").getBoundingClientRect(),f=document.querySelector(".site-footer").getBoundingClientRect();return f.bottom-c.top')
                    header_height = d.execute_script('return document.querySelector(".site-header").getBoundingClientRect().height')
                    self.assertGreaterEqual(order_step_heading_size, 34)
                    self.assertGreaterEqual(order_step_text_size, 15)
                    self.assertLessEqual(order_padding_top, 24)
                    self.assertLessEqual(faq_height, height - header_height + 1)
                    self.assertLessEqual(contact_and_footer, height - header_height + 1)
        finally:
            d.execute_cdp_cmd('Emulation.clearDeviceMetricsOverride', {})

    def test_business_event_tiles_fill_reservation(self):
        from selenium.webdriver.common.by import By
        from selenium.webdriver.common.keys import Keys
        from selenium.webdriver.support.ui import WebDriverWait
        d = self.driver
        for width in [1440, 390]:
            d.set_window_size(width, 900)
            d.get(self.base + 'magnesy-na-zywo/')
            tiles = d.find_elements(By.CSS_SELECTOR, '#oferta-firmowa [data-event]')
            self.assertEqual(len(tiles), 6)
            for tile in tiles:
                expected = tile.get_attribute('data-event')
                d.execute_script('arguments[0].scrollIntoView({block:"center",behavior:"instant"})', tile)
                tile.click()
                WebDriverWait(d, 5).until(lambda browser: browser.current_url.endswith('#rezerwacja'))
                self.assertEqual(d.find_element(By.ID, 'f-event').get_attribute('value'), expected)
                self.assertEqual(d.find_element(By.ID, 'f-event').get_attribute('name'), 'Rodzaj wydarzenia')
            d.execute_script('arguments[0].scrollIntoView({block:"center",behavior:"instant"})', tiles[0])
            tiles[0].send_keys(Keys.ENTER)
            self.assertEqual(d.find_element(By.ID, 'f-event').get_attribute('value'), tiles[0].get_attribute('data-event'))
        d.set_window_size(1440, 1000)

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
                        extras = d.find_element(By.CSS_SELECTOR, '.live-package-extras')
                        self.assertIn('30 km', extras.text)
                        self.assertIn('10 zł/szt.', extras.text.replace('\u00a0', ' '))
                        self.assertEqual(len(extras.find_elements(By.TAG_NAME, 'article')), 2)
                        includes = d.find_element(By.CSS_SELECTOR, '.package-includes')
                        prices = d.find_element(By.CSS_SELECTOR, '#pakiety .pricing-grid')
                        self.assertLess(includes.rect['y'], prices.rect['y'])
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
        cases = [(10, 12), (11, 11.9), (19, 11.9), (20, 11.9), (21, 11.8), (29, 11.8), (30, 11.8), (189, 10.2), (190, 10.2), (191, 10.1), (199, 10.1), (200, 10.1)]
        for count, price in cases:
            value = str(count)
            d.execute_script('const s=document.getElementById("magnet-quantity"); s.value=arguments[0]; s.dispatchEvent(new Event("input",{bubbles:true}))', value)
            self.assertEqual(d.find_element(By.ID, 'magnet-count').text, value)
            self.assertEqual(d.find_element(By.ID, 'magnet-unit-price').text, f'{price:.2f} zł'.replace('.', ','))
            total = d.find_element(By.ID, 'magnet-total-price').text.replace('\u00a0', '').replace(' ', '')
            self.assertEqual(total, f'{count * price:.2f}zł'.replace('.', ','))
            link = d.find_element(By.ID, 'magnet-order')
            d.execute_script('arguments[0].scrollIntoView({block:"center",behavior:"instant"})', link)
            link.click()
            self.assertEqual(d.find_element(By.ID, 'f-quantity').get_attribute('value'), value)
            self.assertTrue(d.current_url.endswith('#zamowienie'))
        slider = d.find_element(By.ID, 'magnet-quantity')
        from selenium.webdriver.common.keys import Keys
        d.execute_script('arguments[0].scrollIntoView({block:"center",behavior:"instant"})', slider)
        slider.send_keys(Keys.HOME)
        slider.send_keys(Keys.ARROW_RIGHT)
        self.assertEqual(slider.get_attribute('value'), '11')
        self.assertEqual(d.find_element(By.ID, 'magnet-count').text, '11')
        slider.send_keys(Keys.END)
        slider.send_keys(Keys.ARROW_RIGHT)
        self.assertEqual(slider.get_attribute('value'), '201')
        self.assertEqual(slider.get_attribute('step'), '1')
        bulk = d.find_element(By.ID, 'magnet-bulk-quantity')
        self.assertTrue(bulk.is_displayed())
        self.assertFalse(d.execute_script('return arguments[0].checkValidity()', bulk))
        order = d.find_element(By.ID, 'magnet-order')
        d.execute_script('arguments[0].click()', order)
        self.assertEqual(d.switch_to.active_element.get_attribute('id'), 'magnet-bulk-quantity')
        for value in ['200', '10001', '201', '357']:
            bulk.clear(); bulk.send_keys(value)
            valid = value in ['201', '357']
            self.assertEqual(d.execute_script('return arguments[0].checkValidity()', bulk), valid)
            if valid:
                self.assertEqual(d.find_element(By.ID, 'magnet-unit-price').text, '10,00 zł')
                self.assertEqual(d.find_element(By.ID, 'magnet-total-price').text.replace('\u00a0','').replace(' ',''), f'{int(value)*10},00zł')
                d.execute_script('arguments[0].click()', order)
                self.assertEqual(d.find_element(By.ID, 'f-quantity').get_attribute('value'), value)
            else:
                self.assertEqual(d.find_element(By.ID, 'magnet-total-price').text, '—')
        self.assertFalse(d.find_elements(By.ID, 'magnet-price-rule'))
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

    def test_discount_code_dialog_and_calculator(self):
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        d = self.driver
        for page in PAGES[1:]:
            d.get(self.base + page)
            test_code = 'NA-START'
            config_name = 'MAGNET_DISCOUNTS_LIVE'
            if page == PAGES[2]:
                field = d.find_element(By.ID, 'f-discount-code')
                promo = d.find_element(By.CSS_SELECTOR, '[data-launch-code="DOSTAWA"]')
                heading = d.find_element(By.CSS_SELECTOR, '#cennik .order-pricing-intro .section-heading')
                self.assertGreater(promo.rect['x'], heading.rect['x'] + heading.rect['width'] - 1)
                self.assertIn('Im więcej magnesów', d.find_element(By.CSS_SELECTOR, '#cennik h2').text)
                promo.click()
                self.assertTrue(d.find_element(By.ID, 'info-dialog').get_attribute('open'))
                self.assertEqual(d.find_element(By.ID, 'info-title').text, 'Darmowa dostawa')
                self.assertEqual(d.find_element(By.ID, 'discount-status').text, '')
                self.assertIn('discount-valid', field.get_attribute('class').split())
                self.assertEqual(d.find_element(By.NAME, 'Darmowa dostawa').get_attribute('value'), 'Tak')
                self.assertEqual(d.find_element(By.NAME, 'Rabat (%)').get_attribute('value'), '0')
                self.assertEqual(d.find_element(By.ID, 'magnet-total-price').text, '120,00 zł')
                d.find_element(By.CSS_SELECTOR, '#info-dialog [data-close]').click()
                field.clear()
                field.send_keys('D')
                d.execute_async_script('setTimeout(arguments[0], 450)')
                self.assertFalse(d.find_element(By.ID, 'info-dialog').get_attribute('open'))
                field.clear()
                d.execute_script('window.MAGNET_DISCOUNTS_LIVE=[{code:"NA-START",percent:20}]')
                field.send_keys('NA-START')
                d.execute_script('arguments[0].blur()', field)
                self.assertEqual(d.find_element(By.NAME, 'Darmowa dostawa').get_attribute('value'), 'Nie')
                d.execute_async_script('setTimeout(arguments[0], 450)')
                self.assertFalse(d.find_element(By.ID, 'info-dialog').get_attribute('open'))
                self.assertEqual(d.find_element(By.NAME, 'Rabat (%)').get_attribute('value'), '0')
                self.assertEqual(d.find_element(By.ID, 'magnet-unit-price').text, '12,00 zł')
                self.assertEqual(d.find_element(By.ID, 'discount-status').text, '')
                field.clear()
                # Synthetic order code exists only in this test, never in production.
                d.execute_script('window.MAGNET_DISCOUNTS_ORDER=[{code:"ORDER-TEST",percent:20}]')
                test_code = 'ORDER-TEST'
                config_name = 'MAGNET_DISCOUNTS_ORDER'
            if page == PAGES[1]:
                promo = d.find_element(By.CSS_SELECTOR, '[data-launch-code]')
                d.execute_script('arguments[0].scrollIntoView({block:"center",behavior:"instant"})', promo)
                promo.click()
                self.assertTrue(d.find_element(By.ID, 'info-dialog').get_attribute('open'))
                self.assertIn('20%', d.find_element(By.ID, 'info-title').text)
                self.assertEqual(d.find_element(By.ID, 'f-discount-code').get_attribute('value'), 'NA-START')
                d.find_element(By.CSS_SELECTOR, '#info-dialog [data-close]').click()
            field = d.find_element(By.ID, 'f-discount-code')
            field.clear()
            field.send_keys(' ' + test_code.swapcase() + ' ')
            self.assertFalse(d.find_elements(By.ID, 'apply-discount'))
            self.assertFalse(d.find_elements(By.ID, 'discount-code-help'))
            d.execute_async_script('setTimeout(arguments[0], 450)')
            self.assertFalse(d.find_element(By.ID, 'info-dialog').get_attribute('open'))
            self.assertEqual(d.find_element(By.NAME, 'Rabat (%)').get_attribute('value'), '20')
            self.assertEqual(d.find_element(By.ID, 'discount-status').text, '')
            self.assertIn('discount-valid', field.get_attribute('class').split())
            if page == PAGES[1]:
                field.send_keys(' ')
                d.execute_async_script('setTimeout(arguments[0], 450)')
                self.assertFalse(d.find_element(By.ID, 'info-dialog').get_attribute('open'))
            if page == PAGES[2]:
                self.assertEqual(d.find_element(By.ID, 'magnet-unit-price').text, '9,60 zł')
                self.assertEqual(d.find_element(By.ID, 'magnet-total-price').text, '96,00 zł')
                d.execute_script('const s=document.getElementById("magnet-quantity");s.value=200;s.dispatchEvent(new Event("input"))')
                self.assertEqual(d.find_element(By.ID, 'magnet-unit-price').text, '8,08 zł')
                self.assertEqual(d.find_element(By.ID, 'magnet-total-price').text.replace('\u00a0', ''), '1616,00 zł')
            field.clear()
            field.send_keys('invalid')
            d.execute_script('arguments[0].blur()', field)
            d.execute_async_script('setTimeout(arguments[0], 450)')
            self.assertFalse(d.find_element(By.ID, 'info-dialog').get_attribute('open'))
            self.assertEqual(d.find_element(By.NAME, 'Rabat (%)').get_attribute('value'), '0')
            self.assertEqual(d.find_element(By.ID, 'discount-status').text, '')
            if page == PAGES[2]:
                self.assertEqual(d.find_element(By.ID, 'magnet-unit-price').text, '10,10 zł')
            # Configuration remains editable without changing the mechanism.
            d.execute_script('window[arguments[0]]=[{code:"nowy",percent:15}]', config_name)
            field.clear(); field.send_keys('nowy')
            self.assertEqual(d.find_element(By.NAME, 'Rabat (%)').get_attribute('value'), '15')

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
        discount = d.find_element(By.ID, 'f-discount-code')
        self.assertFalse(discount.get_attribute('required'))
        discount.send_keys('NA-START')
        from selenium.webdriver.support.ui import WebDriverWait
        WebDriverWait(d, 5).until(lambda browser: browser.find_element(By.ID, 'info-dialog').get_attribute('open'))
        d.find_element(By.CSS_SELECTOR, '#info-dialog [data-close]').click()
        Select(d.find_element(By.ID,'f-event')).select_by_visible_text('Wesele')
        d.find_element(By.CSS_SELECTOR,'form button[type=submit]').click()
        self.assertIn('__capture',d.current_url)
        data=self.server.submission
        self.assertEqual(data['Wiadomość'],[':()@&%$#*($#^*!@(#&#@%&@(#$@!'])
        self.assertEqual(data['Wybrany pakiet'],['Gold'])
        self.assertEqual(data['Kod rabatowy'], ['NA-START'])
        self.assertEqual(data['Rabat (%)'], ['20'])
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
            tiktok=d.find_element(By.CSS_SELECTOR,'.site-footer a[href="https://www.tiktok.com/@magnesowyswiat"]')
            self.assertEqual(tiktok.find_element(By.TAG_NAME,'span').text,'magnesowyswiat')
            self.assertEqual(tiktok.get_attribute('aria-label'),'TikTok: magnesowyswiat')
            find_us=d.find_element(By.CSS_SELECTOR,'.site-footer .footer-grid > div:nth-child(3)')
            self.assertEqual(find_us.find_elements(By.CSS_SELECTOR,'a[href^="mailto:"]'),[])
            offer=d.find_element(By.CSS_SELECTOR,'.site-footer .footer-grid > div:nth-child(2)')
            offer_links=offer.find_elements(By.CSS_SELECTOR,'.footer-links > a')
            social_links=find_us.find_elements(By.CSS_SELECTOR,'.footer-links > a')
            for column in (offer,find_us):
                heading=column.find_element(By.CSS_SELECTOR,'.footer-heading')
                self.assertEqual(d.execute_script('return getComputedStyle(arguments[0]).fontSize',heading),'12px')
                self.assertAlmostEqual(heading.rect['x']+heading.rect['width']/2,column.rect['x']+column.rect['width']/2,delta=1)
            self.assertEqual(len(offer_links),len(social_links))
            for offer_link,social_link in zip(offer_links,social_links):
                self.assertAlmostEqual(offer_link.rect['y'],social_link.rect['y'],delta=1)
                offer_font=d.execute_script('return [getComputedStyle(arguments[0]).fontFamily,getComputedStyle(arguments[0]).fontSize,getComputedStyle(arguments[0]).fontWeight]',offer_link)
                social_font=d.execute_script('return [getComputedStyle(arguments[0]).fontFamily,getComputedStyle(arguments[0]).fontSize,getComputedStyle(arguments[0]).fontWeight]',social_link.find_element(By.TAG_NAME,'span'))
                self.assertEqual(offer_font,social_font)
            contact=d.find_element(By.CSS_SELECTOR,'.site-footer .footer-grid > div:nth-child(4)')
            contact_heading=contact.find_element(By.CSS_SELECTOR,'.footer-heading')
            self.assertAlmostEqual(contact_heading.rect['x']+contact_heading.rect['width']/2,contact.rect['x']+contact.rect['width']/2,delta=1)
            phone=contact.find_element(By.CSS_SELECTOR,'a[href^="tel:"]')
            self.assertEqual(phone.text,'505 606 707')
            self.assertEqual(phone.find_element(By.CSS_SELECTOR,'svg.contact-icon').get_attribute('aria-hidden'),'true')
            self.assertEqual(contact.find_element(By.CSS_SELECTOR,'a[href^="mailto:"]').text,'magnesowyswiat@gmail.com')
            self.assertEqual(len(contact.find_elements(By.CSS_SELECTOR,'svg.contact-icon')),2)
            privacy=d.find_element(By.CSS_SELECTOR,'.site-footer .footer-bottom [data-info="privacy"]')
            copyright=d.find_element(By.CSS_SELECTOR,'.site-footer .footer-copyright')
            terms=d.find_element(By.CSS_SELECTOR,'.site-footer .footer-bottom [data-info="terms"]')
            self.assertFalse(d.find_elements(By.XPATH,"//*[contains(text(),'Strona stworzona i zarządzana przez KP')]"))
            fonts=[d.execute_script('return [getComputedStyle(arguments[0]).fontFamily,getComputedStyle(arguments[0]).fontSize]',element) for element in (privacy,copyright,terms)]
            self.assertEqual(fonts[0],fonts[1])
            self.assertEqual(fonts[1],fonts[2])
            if d.get_window_size()['width'] > 980:
                widths=[column.rect['width'] for column in d.find_elements(By.CSS_SELECTOR,'.site-footer .footer-grid > div')]
                self.assertLessEqual(max(widths)-min(widths),1)
                footer_bottom=d.find_element(By.CSS_SELECTOR,'.site-footer .footer-bottom').rect
                self.assertAlmostEqual(copyright.rect['x']+copyright.rect['width']/2,footer_bottom['x']+footer_bottom['width']/2,delta=1)
                self.assertLess(privacy.rect['x']+privacy.rect['width'],copyright.rect['x'])
                self.assertGreater(terms.rect['x'],copyright.rect['x']+copyright.rect['width'])
                self.assertAlmostEqual(copyright.rect['x']-(privacy.rect['x']+privacy.rect['width']),24,delta=1)
                self.assertAlmostEqual(terms.rect['x']-(copyright.rect['x']+copyright.rect['width']),24,delta=1)
            for icon in icons:
                self.assertEqual(icon.rect['width'],18)
                self.assertEqual(icon.rect['height'],18)
            d.execute_script("document.querySelector('link[rel=stylesheet]').disabled=true")
            for icon in icons:
                self.assertEqual(icon.rect['width'],18)
                self.assertEqual(icon.rect['height'],18)
                self.assertEqual(icon.get_attribute('fill'),'none')
        d.set_window_size(390,844)
        d.get(self.base+PAGES[0])
        footer_bottom=d.find_element(By.CSS_SELECTOR,'.site-footer .footer-bottom')
        self.assertEqual(len(d.execute_script('return getComputedStyle(arguments[0]).gridTemplateColumns.split(" ")',footer_bottom)),1)
        mobile_items=d.find_elements(By.CSS_SELECTOR,'.site-footer .footer-bottom > *')
        self.assertEqual(len(mobile_items),3)
        self.assertLess(mobile_items[0].rect['y'],mobile_items[1].rect['y'])
        self.assertLess(mobile_items[1].rect['y'],mobile_items[2].rect['y'])
        d.set_window_size(1440,1000)
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
                    # Four smaller cards per desktop row, with consistent 16:9 photos.
                    self.assertAlmostEqual(photo.rect['width'] / photo.rect['height'], 16 / 9, delta=.03)
                    self.assertEqual(photo.value_of_css_property('object-fit'),'cover')
                if width<600:
                    self.assertEqual(len({card.rect['x'] for card in cards}),1)
                else:
                    self.assertEqual(len({card.rect['x'] for card in cards}),4)
                    self.assertEqual(len({card.rect['y'] for card in cards}),1)
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
        from selenium.webdriver.support.ui import WebDriverWait
        d=self.driver; d.get(self.base+PAGES[2])
        form=d.find_element(By.CSS_SELECTOR,'form[data-inquiry="order"]')
        self.assertEqual(d.find_element(By.CSS_SELECTOR,'.form-fields-title').text,'Wypełnij formularz!')
        self.assertFalse(d.find_elements(By.NAME,'consent'))
        self.assertFalse(d.find_elements(By.ID,'draft-dialog'))
        self.assertEqual(form.get_attribute('action'),'https://formsubmit.co/magnesowyswiat@gmail.com')
        self.assertEqual(form.get_attribute('enctype'),'multipart/form-data')
        self.assertFalse(d.find_elements(By.CSS_SELECTOR,'.preview-notice'))
        self.assertEqual(d.find_element(By.ID,'photo-picker').text,'Wybierz zdjęcia')
        self.assertFalse(d.find_elements(By.ID,'photo-picker-label'))
        self.assertEqual(d.find_element(By.CSS_SELECTOR,'form button[type=submit]').text,'ZOBACZ PODSUMOWANIE')
        submit=d.find_element(By.CSS_SELECTOR,'form button[type=submit]')
        self.assertAlmostEqual(submit.rect['x']+submit.rect['width']/2,form.rect['x']+form.rect['width']/2,delta=1)
        upload=d.find_element(By.CSS_SELECTOR,'.upload-zone')
        delivery_fields=d.find_element(By.CSS_SELECTOR,'fieldset .form-grid')
        message=d.find_element(By.ID,'f-message')
        regular_input=d.find_element(By.ID,'f-delivery-town')
        photo_help=d.find_element(By.ID,'photo-help')
        self.assertLessEqual(upload.rect['width'],680)
        self.assertLessEqual(upload.rect['height'],80)
        self.assertLess(delivery_fields.rect['y'],upload.rect['y'])
        self.assertLess(message.rect['y'],upload.rect['y'])
        self.assertAlmostEqual(message.rect['height'],regular_input.rect['height'],delta=1)
        self.assertLessEqual(d.execute_script('return arguments[0].scrollWidth',photo_help),photo_help.rect['width']+1)
        self.assertEqual(d.find_element(By.ID,'photos').get_attribute('aria-label'),'Dodaj zdjęcia')
        for field_id in ['f-name','f-email','f-phone','f-quantity','f-caption','f-discount-code','f-delivery-town','f-delivery-street','f-post-office','f-message']:
            label=d.find_element(By.CSS_SELECTOR,f'label[for="{field_id}"]')
            self.assertEqual(label.value_of_css_property('text-align'),'center')
        self.assertEqual(d.find_element(By.ID,'photos').value_of_css_property('opacity'),'0')
        d.execute_script('arguments[0].action=arguments[1]',form,self.base+'__capture')
        with tempfile.TemporaryDirectory() as folder:
            image=Path(folder)/'test.png'
            image.write_bytes(base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII='))
            d.find_element(By.ID,'photos').send_keys(str(image))
            self.assertEqual(len(d.find_elements(By.CSS_SELECTOR,'.photo-preview')),1)
            self.assertIn('Wybrano zdjęć: 1',d.find_element(By.ID,'photo-status').text)
            count=d.find_element(By.CSS_SELECTOR,'.photo-preview input')
            d.execute_script("arguments[0].value=3;arguments[0].dispatchEvent(new Event('input'))",count)
            self.assertEqual(d.find_element(By.ID,'f-quantity').get_attribute('value'),'')
            d.find_element(By.CSS_SELECTOR,'.remove-photo').click()
            self.assertEqual(len(d.find_elements(By.CSS_SELECTOR,'.photo-preview')),0)
            second=Path(folder)/'second.png'; second.write_bytes(image.read_bytes())
            d.find_element(By.ID,'photos').send_keys(str(image)+'\n'+str(second))
            count=d.find_element(By.CSS_SELECTOR,'.photo-preview input')
            d.execute_script("arguments[0].value=3;arguments[0].dispatchEvent(new Event('input'))",count)
            two_counts=d.find_elements(By.CSS_SELECTOR,'.photo-preview input')
            for photo_count in two_counts:
                d.execute_script("arguments[0].value=5;arguments[0].dispatchEvent(new Event('input'))",photo_count)
            d.find_element(By.ID,'f-name').send_keys('Test lokalny')
            d.find_element(By.ID,'f-email').send_keys('test@example.com')
            quantity=d.find_element(By.ID,'f-quantity')
            quantity.send_keys('20')
            d.find_element(By.CSS_SELECTOR,'form button[type=submit]').click()
            self.assertTrue(d.find_element(By.ID,'info-dialog').get_attribute('open'))
            mismatch=d.find_element(By.ID,'info-body').text
            self.assertIn('2 zdjęcia po 5 szt.',mismatch)
            self.assertIn('łącznie 10 magnesów',mismatch)
            self.assertIn('podano 20',mismatch)
            self.assertIn('suma wynosiła 20',mismatch)
            d.find_element(By.CSS_SELECTOR,'#info-dialog [data-close]').click()
            d.execute_script("arguments[0].value=3;arguments[0].dispatchEvent(new Event('input'))",two_counts[0])
            d.execute_script("arguments[0].value=1;arguments[0].dispatchEvent(new Event('input'))",two_counts[1])
            quantity.clear(); quantity.send_keys('5')
            self.assertTrue(d.find_element(By.ID, 'photos').get_attribute('multiple'))
            d.execute_script('window.photoPickerClicks=0;document.getElementById("photos").addEventListener("click",e=>{e.preventDefault();window.photoPickerClicks++})')
            d.find_element(By.CSS_SELECTOR, '.add-photo').click()
            self.assertEqual(d.execute_script('return window.photoPickerClicks'), 1)
            third=Path(folder)/'third.png'; third.write_bytes(image.read_bytes())
            d.find_element(By.ID, 'photos').send_keys(str(third))
            self.assertEqual(len(d.find_elements(By.CSS_SELECTOR, '.photo-preview')), 3)
            self.assertEqual(d.find_element(By.CSS_SELECTOR, '.photo-preview input').get_attribute('value'), '3')
            for id,value in [('f-delivery-town','Testowa miejscowość'),('f-delivery-street','Testowa 12A/3')]:
                d.find_element(By.ID,id).send_keys(value)
            code=d.find_element(By.ID,'f-post-office')
            code.send_keys('1234')
            self.assertFalse(d.execute_script('return arguments[0].checkValidity()',code))
            code.clear(); code.send_keys('34500 Poczta testowa')
            self.assertEqual(code.get_attribute('value'),'34-500 Poczta testowa')
            self.assertFalse(d.find_elements(By.CSS_SELECTOR,'.purchase-document'))
            self.assertFalse(d.find_elements(By.ID,'f-delivery'))
            d.find_element(By.ID,'f-message').send_keys(':()@&%$#*($#^*!@(#&#@%&@(#$@!')
            discount = d.find_element(By.ID, 'f-discount-code')
            self.assertFalse(discount.get_attribute('required'))
            discount.send_keys('BLEDNY')
            d.execute_script('arguments[0].blur()', discount)
            d.execute_async_script('setTimeout(arguments[0],450)')
            self.assertFalse(d.find_element(By.ID,'info-dialog').get_attribute('open'))
            d.find_element(By.CSS_SELECTOR,'form button[type=submit]').click()
            summary=d.find_element(By.ID,'order-summary-dialog')
            self.assertTrue(summary.get_attribute('open'))
            self.assertIn('Nie podano',summary.text)
            self.assertEqual(discount.get_attribute('value'),'')
            d.find_element(By.CSS_SELECTOR,'#order-summary-dialog [data-close]').click()
            discount.send_keys('DOSTAWA')
            d.execute_async_script('setTimeout(arguments[0],450)')
            self.assertFalse(d.find_element(By.ID,'info-dialog').get_attribute('open'))
            quantity.clear(); quantity.send_keys('6')
            d.find_element(By.CSS_SELECTOR,'form button[type=submit]').click()
            dialog=d.find_element(By.ID,'info-dialog')
            self.assertTrue(dialog.get_attribute('open'))
            self.assertIn('łącznie 5 magnesów',d.find_element(By.ID,'info-body').text)
            self.assertIn('podano 6',d.find_element(By.ID,'info-body').text)
            self.assertNotIn('__capture',d.current_url)
            d.find_element(By.CSS_SELECTOR,'#info-dialog [data-close]').click()
            quantity.clear(); quantity.send_keys('5')
            d.find_element(By.CSS_SELECTOR,'form button[type=submit]').click()
            summary=d.find_element(By.ID,'order-summary-dialog')
            self.assertTrue(summary.get_attribute('open'))
            self.assertIn('Test lokalny',summary.text)
            self.assertIn('Liczba magnesów',summary.text)
            self.assertIn('5 szt.',summary.text)
            self.assertIn('test.png — 3 szt.',summary.text)
            self.assertNotIn('__capture',d.current_url)
            d.find_element(By.ID,'confirm-order-submit').click()
            WebDriverWait(d,5).until(lambda browser: '__capture' in browser.current_url)
            self.assertEqual(len(self.server.uploads),3)
            self.assertEqual([item['filename'] for item in self.server.uploads],['test.png','second.png','third.png'])
            self.assertTrue(all(item['content']==image.read_bytes() for item in self.server.uploads))
            self.assertEqual(self.server.submission['Liczba magnesów'],['5'])
            self.assertEqual(self.server.submission['Miejscowość dostawy'],['Testowa miejscowość'])
            self.assertEqual(self.server.submission['Ulica i numer domu/lokalu'],['Testowa 12A/3'])
            self.assertEqual(self.server.submission['Poczta'],['34-500 Poczta testowa'])
            self.assertNotIn('Dokument zakupu', self.server.submission)
            self.assertNotIn('Sposób dostawy', self.server.submission)
            self.assertEqual(self.server.submission['Kod rabatowy'], ['DOSTAWA'])
            self.assertEqual(self.server.submission['Rabat (%)'], ['0'])
            self.assertEqual(self.server.submission['_subject'],['[NA ZAMÓWIENIE] Zapytanie o magnesy ze zdjęć | Magnesowy Świat'])
            self.assertEqual(self.server.submission['Rodzaj zapytania'],['Magnesy na zamówienie ze zdjęć'])
            self.assertIn('test.png: 3 szt.',self.server.submission['Zdjęcia i liczba kopii'][0])
            self.assertIn('second.png: 1 szt.',self.server.submission['Zdjęcia i liczba kopii'][0])
            self.assertIn('third.png: 1 szt.',self.server.submission['Zdjęcia i liczba kopii'][0])
            self.assertEqual(self.server.submission['Uwagi do zamówienia'],[':()@&%$#*($#^*!@(#&#@%&@(#$@!'])
    def test_order_total_attachment_limit(self):
        from selenium.webdriver.common.by import By
        d=self.driver; d.get(self.base+PAGES[2])
        d.execute_script("""
          const input=document.getElementById('photos'); const files=new DataTransfer();
          for (let index=1; index<=21; index++) files.items.add(new File([new Uint8Array([1])],`photo-${index}.png`,{type:'image/png'}));
          input.files=files.files; input.dispatchEvent(new Event('change'));
        """)
        self.assertEqual(len(d.find_elements(By.CSS_SELECTOR,'.photo-preview')),21)
        self.assertTrue(d.find_element(By.CSS_SELECTOR,'.add-photo').is_displayed())
        d.get(self.base+PAGES[2])
        d.execute_script("""
          const input=document.getElementById('photos'); const files=new DataTransfer();
          files.items.add(new File([new Uint8Array(6000000)],'first.png',{type:'image/png'}));
          files.items.add(new File([new Uint8Array(5000000)],'too-large.png',{type:'image/png'}));
          input.files=files.files; input.dispatchEvent(new Event('change'));
        """)
        self.assertEqual(len(d.find_elements(By.CSS_SELECTOR,'.photo-preview')),0)
        self.assertTrue(d.find_element(By.ID,'info-dialog').get_attribute('open'))
        self.assertEqual(d.find_element(By.ID,'info-title').text,'Za dużo zdjęć')
        message=d.find_element(By.ID,'info-body').text
        self.assertIn('magnesowyswiat@gmail.com',message)
        self.assertIn('505 606 707',message)
        self.assertEqual(message.count('505 606 707'),1)
        self.assertEqual(d.find_element(By.ID,'photo-status').text,message)
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
