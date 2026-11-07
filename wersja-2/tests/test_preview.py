"""Lokalne testy. Nie wysyłają e-maili ani zdjęć."""
import argparse
import base64
from functools import partial
from html.parser import HTMLParser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import tempfile
from threading import Thread
import unittest
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
PRODUCTION = '--production' in __import__('sys').argv
if PRODUCTION: ROOT = ROOT.parent
PAGES = ['index.html', 'magnesy-na-zywo.html', 'magnesy-na-zamowienie.html']
BROWSER = '--browser' in __import__('sys').argv

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
                target=unquote(url.path) or name
                self.assertTrue((ROOT/target).is_file(),f'{name}: {href}')
                if url.fragment: self.assertIn(url.fragment,parsed[target].ids,f'{name}: {href}')

@unittest.skipUnless(BROWSER,'Dodaj --browser, aby uruchomić Chrome / Selenium')
class BrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from selenium import webdriver
        handler=partial(SimpleHTTPRequestHandler,directory=str(ROOT if PRODUCTION else ROOT.parent))
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
        d.find_element(By.CSS_SELECTOR,'[data-package="Gold"]').click()
        self.assertEqual(d.find_element(By.ID,'f-package').get_attribute('value'),'Gold')
        for name,value in [('name','Test lokalny'),('email','test@example.com'),('city','Limanowa'),('guests','100'),('message',':()@&%$#*($#^*!@(#&#@%&@(#$@!')]:
            d.find_element(By.ID,'f-'+name).send_keys(value)
        d.execute_script("document.getElementById('f-date').value='2099-01-01'")
        Select(d.find_element(By.ID,'f-event')).select_by_visible_text('Wesele')
        d.find_element(By.NAME,'consent').click()
        d.find_element(By.CSS_SELECTOR,'form button[type=submit]').click()
        self.assertTrue(d.find_element(By.ID,'draft-dialog').get_attribute('open'))
        self.assertIn(':()@&%$#*($#^*!@(#&#@%&@(#$@!',d.find_element(By.ID,'draft-text').get_attribute('value'))
        self.assertIn('%26',d.find_element(By.ID,'email-draft').get_attribute('href'))
    def test_order_preview_counts_delete_and_validation(self):
        from selenium.webdriver.common.by import By
        d=self.driver; d.get(self.base+PAGES[2])
        with tempfile.TemporaryDirectory() as folder:
            image=Path(folder)/'test.png'
            image.write_bytes(base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII='))
            d.find_element(By.ID,'photos').send_keys(str(image))
            self.assertEqual(len(d.find_elements(By.CSS_SELECTOR,'.photo-preview')),1)
            count=d.find_element(By.CSS_SELECTOR,'.photo-preview input')
            d.execute_script("arguments[0].value=3;arguments[0].dispatchEvent(new Event('input'))",count)
            self.assertEqual(d.find_element(By.ID,'f-quantity').get_attribute('value'),'3')
            d.find_element(By.ID,'f-name').send_keys('Test lokalny')
            d.find_element(By.ID,'f-email').send_keys('test@example.com')
            d.find_element(By.NAME,'consent').click()
            d.find_element(By.CSS_SELECTOR,'form button[type=submit]').click()
            self.assertTrue(d.find_element(By.ID,'draft-dialog').get_attribute('open'))
            self.assertIn('test.png: 3 szt.',d.find_element(By.ID,'draft-text').get_attribute('value'))
            d.find_element(By.CSS_SELECTOR,'#draft-dialog [data-close]').click()
            d.find_element(By.CSS_SELECTOR,'.remove-photo').click()
            self.assertEqual(len(d.find_elements(By.CSS_SELECTOR,'.photo-preview')),0)

if __name__=='__main__':
    import sys
    unittest.main(argv=[sys.argv[0]]+[arg for arg in sys.argv[1:] if arg not in ['--browser','--production']])
