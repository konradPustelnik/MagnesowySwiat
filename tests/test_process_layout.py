"""Check that the complete process section fits after navigation, without sending mail."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By

ROOT = Path(__file__).resolve().parents[1]

class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def handle(self):
        try:
            super().handle()
        except (BrokenPipeError, ConnectionResetError):
            pass

class ProcessLayoutTests(unittest.TestCase):
    def test_complete_section_fits_viewport(self):
        server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(ROOT)))
        threading.Thread(target=server.serve_forever, daemon=True).start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        options = webdriver.ChromeOptions()
        options.add_argument('--headless=new')
        browser = webdriver.Chrome(options=options)
        self.addCleanup(browser.quit)
        browser.execute_cdp_cmd('Emulation.setEmulatedMedia', {'features': [{'name': 'prefers-reduced-motion', 'value': 'reduce'}]})
        output = ROOT / 'test-results'
        output.mkdir(exist_ok=True)
        for width, height in ((1366, 768), (1280, 600), (1210, 580), (768, 900), (390, 844), (360, 740)):
            with self.subTest(width=width, height=height):
                browser.execute_cdp_cmd('Emulation.setDeviceMetricsOverride', {'width': width, 'height': height, 'deviceScaleFactor': 1, 'mobile': width < 600})
                browser.get(f'http://127.0.0.1:{server.server_port}/')
                browser.execute_async_script('document.fonts.ready.then(arguments[0]);')
                menu = browser.find_element(By.ID, 'menuToggle')
                if menu.is_displayed():
                    menu.click()
                browser.find_element(By.CSS_SELECTOR, '#navLinks a[href="#jak-dzialamy"]').click()
                metrics = browser.execute_script("""const section=document.getElementById('jak-dzialamy');
                  return {top:section.querySelector('.process-heading').getBoundingClientRect().top,
                    bottom:section.getBoundingClientRect().bottom, height:innerHeight,
                    header:document.querySelector('header').getBoundingClientRect().bottom,
                    width:innerWidth, scrollWidth:document.documentElement.scrollWidth,
                    steps:section.querySelectorAll('.step').length};""")
                browser.save_screenshot(str(output / f'process-{width}x{height}.png'))
                self.assertGreaterEqual(metrics['top'], metrics['header'], metrics)
                self.assertLessEqual(metrics['bottom'], metrics['height'], metrics)
                self.assertLessEqual(metrics['scrollWidth'], metrics['width'] + 1, metrics)
                self.assertEqual(metrics['steps'], 3)
                print(f'{width}x{height}: section bottom {metrics["bottom"]:.0f}px / {height}px')

if __name__ == '__main__':
    unittest.main(verbosity=2)
