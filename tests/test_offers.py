"""Offer navigation and custom-order composer; no messages are sent."""
from functools import partial
from html.parser import HTMLParser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading
import unittest
from urllib.parse import urlparse, parse_qs, unquote
from selenium import webdriver
from selenium.webdriver.common.by import By

ROOT = Path(__file__).resolve().parents[1]
PAGES = ('index.html', 'magnesy-na-zywo/index.html', 'magnesy-na-zamowienie/index.html')

class Page(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.tags = []
        self.feed(path.read_text(encoding='utf-8'))

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))

class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def handle(self):
        try:
            super().handle()
        except (BrokenPipeError, ConnectionResetError):
            pass

class OfferTests(unittest.TestCase):
    def test_internal_links_assets_and_canonicals(self):
        for relative in PAGES:
            path = ROOT / relative
            page = Page(path)
            self.assertEqual(sum(t == 'h1' for t, a in page.tags), 1)
            expected = 'https://magnesowyswiat.pl/' + ('' if relative == 'index.html' else relative.removesuffix('index.html'))
            self.assertEqual([a['href'] for t, a in page.tags if t == 'link' and a.get('rel') == 'canonical'], [expected])
            for tag, attrs in page.tags:
                for attr in ('href', 'src'):
                    if attr not in attrs:
                        continue
                    url = urlparse(attrs[attr])
                    if url.scheme or url.netloc:
                        continue
                    target = (ROOT / url.path.lstrip('/') if url.path.startswith('/') else path.parent / url.path).resolve() if url.path else path
                    if target.is_dir():
                        target = target / 'index.html'
                    self.assertTrue(target.is_relative_to(ROOT), str(target))
                    self.assertTrue(target.is_file(), f'{relative}: {attrs[attr]}')
                    if url.fragment:
                        ids = {a['id'] for t, a in Page(target).tags if 'id' in a}
                        self.assertIn(unquote(url.fragment), ids, attrs[attr])

    def test_browser_navigation_and_order_composition(self):
        server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(ROOT)))
        threading.Thread(target=server.serve_forever, daemon=True).start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        options = webdriver.ChromeOptions()
        options.add_argument('--headless=new')
        browser = webdriver.Chrome(options=options)
        self.addCleanup(browser.quit)
        browser.set_page_load_timeout(45)
        browser.execute_cdp_cmd('Network.enable', {})
        browser.execute_cdp_cmd('Network.setBlockedURLs', {'urls': ['*formsubmit.co*', '*mail.google.com*']})
        browser.execute_cdp_cmd('Emulation.setEmulatedMedia', {'features': [{'name': 'prefers-reduced-motion', 'value': 'reduce'}]})
        base = f'http://127.0.0.1:{server.server_port}/'
        results = ROOT / 'test-results'
        results.mkdir(exist_ok=True)
        for width in (360, 768, 1440):
            browser.execute_cdp_cmd('Emulation.setDeviceMetricsOverride', {'width': width, 'height': 900, 'deviceScaleFactor': 1, 'mobile': width < 600})
            browser.get(base)
            links = browser.find_elements(By.CSS_SELECTOR, '#navLinks a')
            self.assertEqual(links[0].text or links[0].get_attribute('textContent'), 'Oferta')
            self.assertEqual(links[1].get_attribute('href'), base + '#jak-dzialamy')
            for slug in ('magnesy-na-zywo', 'magnesy-na-zamowienie'):
                browser.get(base + '#oferta')
                browser.execute_async_script('document.fonts.ready.then(arguments[0]);')
                browser.save_screenshot(str(results / f'offers-{width}.png'))
                browser.find_element(By.CSS_SELECTOR, f'.offer-card[href="{slug}/"]').click()
                self.assertEqual(browser.current_url, base + slug + '/')
                browser.execute_async_script('document.fonts.ready.then(arguments[0]);')
                self.assertEqual(len(browser.find_elements(By.TAG_NAME, 'h1')), 1)
                self.assertLessEqual(browser.execute_script('return document.documentElement.scrollWidth'), width + 1)
                browser.save_screenshot(str(results / f'{slug}-{width}.png'))
                menu = browser.find_element(By.ID, 'menuToggle')
                if menu.is_displayed():
                    menu.click()
                    self.assertEqual(menu.get_attribute('aria-expanded'), 'true')
                    browser.execute_script("document.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape'}))")
                    self.assertEqual(menu.get_attribute('aria-expanded'), 'false')
            form = browser.find_element(By.ID, 'orderInquiry')
            self.assertFalse(browser.execute_script('return arguments[0].checkValidity()', form))
            special = ':()@&%$#*($#^*!@(#&#@%&@(#$@!'
            for field, value in {'orderName': 'Test', 'orderEmail': 'test@example.com', 'orderQuantity': '20', 'orderMessage': special}.items():
                browser.find_element(By.ID, field).send_keys(value)
            browser.find_element(By.CSS_SELECTOR, '#orderInquiry [type="submit"]').click()
            self.assertTrue(browser.find_element(By.ID, 'orderSummary').is_displayed())
            body = browser.find_element(By.ID, 'orderText').get_attribute('value')
            self.assertIn(special, body)
            mail = urlparse(browser.find_element(By.ID, 'orderMailLink').get_attribute('href'))
            self.assertEqual(mail.scheme, 'mailto')
            self.assertEqual(mail.path, 'magnesowyswiat@gmail.com')
            self.assertEqual(parse_qs(mail.query)['body'], [body])
            gmail = urlparse(browser.find_element(By.ID, 'orderGmailLink').get_attribute('href'))
            self.assertEqual(parse_qs(gmail.query)['body'], [body])

if __name__ == '__main__':
    unittest.main(verbosity=2)
