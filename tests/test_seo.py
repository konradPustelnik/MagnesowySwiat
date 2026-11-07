"""SEO contracts and optional real-browser mobile checks; never sends email."""
import argparse
from functools import partial
from html.parser import HTMLParser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import threading
import unittest
from urllib.parse import urlparse
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
CANONICAL = 'https://magnesowyswiat.pl/'
parser = argparse.ArgumentParser(description='Lokalne testy SEO; nie wysylaja e-maili.')
parser.add_argument('--browser', action='store_true', help='Sprawdz tez Chrome na telefonie, tablecie i komputerze.')
parser.add_argument('--baseline', action='store_true', help='Tylko pomiary przegladarkowe przed zmianami.')
args = parser.parse_args()


class Page(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.tags = []
        self.heading = None
        self.headings = []
        self.json_ld = None
        self.schemas = []
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.tags.append((tag, attrs))
        if tag in ('h1', 'h2', 'h3'):
            self.heading = [tag, '']
        if tag == 'script' and attrs.get('type') == 'application/ld+json':
            self.json_ld = ''

    def handle_data(self, data):
        if self.heading is not None:
            self.heading[1] += data
        if self.json_ld is not None:
            self.json_ld += data

    def handle_endtag(self, tag):
        if self.heading is not None and tag == self.heading[0]:
            self.headings.append(tuple(self.heading))
            self.heading = None
        if tag == 'script' and self.json_ld is not None:
            self.schemas.append(json.loads(self.json_ld))
            self.json_ld = None


class SEOTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (ROOT / 'index.html').read_text(encoding='utf-8')
        cls.page = Page(cls.source)

    def test_canonical_and_indexability(self):
        canonical = [a['href'] for t, a in self.page.tags if t == 'link' and a.get('rel') == 'canonical']
        self.assertEqual(canonical, [CANONICAL])
        self.assertNotIn('noindex', self.source.lower())
        robots = (ROOT / 'robots.txt').read_text(encoding='utf-8')
        self.assertIn('Sitemap: ' + CANONICAL + 'sitemap.xml', robots)
        self.assertNotIn('Disallow: /\n', robots)
        urls = ET.parse(ROOT / 'sitemap.xml').findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
        self.assertEqual([u.text for u in urls], [CANONICAL])
        descriptions = [a['content'] for t, a in self.page.tags if t == 'meta' and a.get('name') == 'description']
        self.assertEqual(len(descriptions), 1)
        self.assertIn('Limanowa', descriptions[0])
        self.assertIn('Magnesy na wesele', descriptions[0])

    def test_headings_and_local_content(self):
        h1 = [text for tag, text in self.page.headings if tag == 'h1']
        self.assertEqual(len(h1), 1)
        self.assertIn('Fotomagnesy', h1[0])
        self.assertIn('Limanow', h1[0])
        self.assertIn('powiat limanowski', self.source)
        self.assertIn('powiat nowosądecki', self.source)
        self.assertIn('Nowy Sącz', self.source)
        self.assertIn('Dalszy dojazd jest dodatkowo płatny.', self.source)
        self.assertIn('przed potwierdzeniem rezerwacji', self.source)
        previous = 1
        for tag, text in self.page.headings:
            level = int(tag[1])
            self.assertLessEqual(level, previous + 1, text)
            previous = level

    def test_schema_uses_confirmed_facts(self):
        self.assertEqual(len(self.page.schemas), 1)
        nodes = self.page.schemas[0]['@graph']
        org = next(n for n in nodes if n['@type'] == 'Organization')
        service = next(n for n in nodes if n['@type'] == 'Service')
        self.assertEqual(org['email'], 'magnesowyswiat@gmail.com')
        self.assertEqual(org['url'], CANONICAL)
        self.assertEqual({a['name'] for a in service['areaServed']}, {'powiat limanowski', 'powiat nowosądecki'})
        serialized = json.dumps(nodes)
        for forbidden in ('aggregateRating', 'review', 'streetAddress', 'telephone', 'openingHours', 'geo'):
            self.assertNotIn('"' + forbidden + '"', serialized)

    def test_links_images_and_form(self):
        ids = [a['id'] for t, a in self.page.tags if 'id' in a]
        self.assertEqual(len(ids), len(set(ids)))
        for tag, attrs in self.page.tags:
            if tag == 'a' and attrs.get('href', '').startswith('#'):
                self.assertIn(attrs['href'][1:], ids)
            if tag == 'img':
                self.assertIn('alt', attrs)
                self.assertGreater(int(attrs['width']), 0)
                self.assertGreater(int(attrs['height']), 0)
                if attrs['src'].startswith('https://images.unsplash.com/'):
                    self.assertIn('srcset', attrs)
                    self.assertIn('sizes', attrs)
                else:
                    self.assertTrue((ROOT / attrs['src']).is_file())
        form = next(a for t, a in self.page.tags if t == 'form')
        self.assertEqual(form['action'], 'https://formsubmit.co/magnesowyswiat@gmail.com')
        self.assertEqual(form['method'].lower(), 'post')
        hidden = {a['name']: a.get('value') for t, a in self.page.tags if t == 'input' and a.get('type') == 'hidden'}
        self.assertEqual(hidden['_url'], CANONICAL)
        self.assertEqual(hidden['_next'], CANONICAL + '?wyslano=1#kontakt')


class BrowserTests(unittest.TestCase):
    def test_responsive_layout_and_diagnostics(self):
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import Select
        class Handler(SimpleHTTPRequestHandler):
            def log_message(self, *args):
                pass
            def handle(self):
                try:
                    super().handle()
                except (ConnectionResetError, BrokenPipeError):
                    pass

        server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Handler, directory=str(ROOT)))
        threading.Thread(target=server.serve_forever, daemon=True).start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        options = webdriver.ChromeOptions()
        options.add_argument('--headless=new')
        browser = webdriver.Chrome(options=options)
        self.addCleanup(browser.quit)
        browser.set_page_load_timeout(45)
        browser.execute_cdp_cmd('Network.enable', {})
        browser.execute_cdp_cmd('Network.setBlockedURLs', {'urls': ['*formsubmit.co*']})
        browser.execute_cdp_cmd('Emulation.setEmulatedMedia', {
            'features': [{'name': 'prefers-reduced-motion', 'value': 'reduce'}]})
        browser.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {'source': """
          window.seoMetrics = {cls: 0, lcp: null};
          new PerformanceObserver(list => {
            for (const e of list.getEntries()) if (!e.hadRecentInput) window.seoMetrics.cls += e.value;
          }).observe({type: 'layout-shift', buffered: true});
          new PerformanceObserver(list => {
            window.seoMetrics.lcp = list.getEntries().at(-1).startTime;
          }).observe({type: 'largest-contentful-paint', buffered: true});
        """})
        results = []
        output = ROOT / 'test-results'
        output.mkdir(exist_ok=True)
        for width in (360, 390, 768, 1440):
            browser.execute_cdp_cmd('Emulation.setDeviceMetricsOverride', {
                'width': width, 'height': 900, 'deviceScaleFactor': 1,
                'mobile': width < 600})
            browser.get(f'http://127.0.0.1:{server.server_port}/')
            browser.execute_async_script('document.fonts.ready.then(() => setTimeout(arguments[0], 1000));')
            metrics = browser.execute_script("""return {
              width: innerWidth, contentWidth: document.documentElement.scrollWidth,
              ...window.seoMetrics,
              navigation: performance.getEntriesByType('navigation')[0].toJSON(),
              images: Array.from(document.images).map(i => ({src:i.currentSrc, naturalWidth:i.naturalWidth,
                naturalHeight:i.naturalHeight, renderedWidth:i.getBoundingClientRect().width})),
              resourceBytes: performance.getEntriesByType('resource').reduce((n,r)=>n+r.transferSize,0)
            }""")
            results.append(metrics)
            if width == 1440:
                browser.execute_async_script("""const done=arguments[0];
                  const images=Array.from(document.images); images.forEach(i=>i.loading='eager');
                  Promise.race([Promise.all(images.map(i=>i.decode().catch(()=>null))),
                    new Promise(r=>setTimeout(r,10000))]).then(()=>done());""")
                metrics['decoded_images'] = browser.execute_script("return Array.from(document.images).map(i=>({src:i.src,naturalWidth:i.naturalWidth,naturalHeight:i.naturalHeight}))")
            browser.save_screenshot(str(output / f'seo-{width}.png'))
            if not args.baseline:
                self.assertLessEqual(metrics['contentWidth'], metrics['width'] + 1, f'Overflow at {width}px')
                self.assertEqual(len(browser.find_elements(By.TAG_NAME, 'h1')), 1)
                menu = browser.find_element(By.ID, 'menuToggle')
                if width < 1100:
                    menu.click()
                    self.assertEqual(menu.get_attribute('aria-expanded'), 'true')
                    browser.find_element(By.CSS_SELECTOR, '#navLinks a').click()
                    self.assertEqual(menu.get_attribute('aria-expanded'), 'false')
                for link in browser.find_elements(By.CSS_SELECTOR, '.choose-package'):
                    browser.execute_script('arguments[0].click()', link)
                    selected = Select(browser.find_element(By.ID, 'package')).first_selected_option.text
                    self.assertTrue(selected.startswith(link.get_attribute('data-package')))
                self.assertFalse(browser.execute_script("return document.getElementById('contactForm').checkValidity()"))
        filename = 'seo-baseline.json' if args.baseline else 'seo-browser.json'
        (output / filename).write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
        print('Pomiary lokalne (bez symulacji sieci mobilnej): ' + str(output / filename))


if __name__ == '__main__':
    suite = unittest.TestSuite()
    if not args.baseline:
        suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(SEOTests))
    if args.browser or args.baseline:
        suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(BrowserTests))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    raise SystemExit(0 if result.wasSuccessful() else 1)
