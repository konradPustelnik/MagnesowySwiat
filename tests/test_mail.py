"""Browser tests. Live submission is explicit and never retried automatically."""
import argparse
from datetime import date, timedelta, datetime, timezone
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import threading
import unittest
from urllib.parse import urlparse, parse_qs
import uuid

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_URL = 'https://magnesowyswiat.pl/'
RECIPIENT = 'magnesowyswiat@gmail.com'
parser = argparse.ArgumentParser(description='Test formularza w Chrome (domyslnie bez wysylania e-maila).')
parser.add_argument('--live', action='store_true', help='Wyslij JEDNO prawdziwe zgloszenie testowe.')
parser.add_argument('--local-live', action='store_true', help='Wyslij prawdziwe zgloszenie z lokalnego serwera, bez domeny.')
parser.add_argument('--confirm-delivery', action='store_true', help='Potwierdz kod z odebranej wiadomosci.')
parser.add_argument('--url', default=PUBLIC_URL, help='Adres opublikowanej strony (domyslnie https://magnesowyswiat.pl/).')
args = parser.parse_args()
if args.local_live:
    args.live = True
if args.confirm_delivery and not args.live:
    parser.error('--confirm-delivery wymaga --live')

RESULTS = ROOT / 'test-results'
RESULTS.mkdir(exist_ok=True)
report = {'started_utc': datetime.now(timezone.utc).isoformat(), 'mode': 'local-live' if args.local_live else ('live' if args.live else 'local'),
          'provider_accepted': False, 'delivery': 'not_checked'}


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def handle(self):
        try:
            super().handle()
        except (BrokenPipeError, ConnectionResetError):
            pass  # Chrome may close speculative connections during teardown.


class MailTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(ROOT)))
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()
        cls.addClassCleanup(cls.server.server_close)
        cls.addClassCleanup(cls.server.shutdown)
        options = webdriver.ChromeOptions()
        options.add_argument('--headless=new')
        options.add_argument('--window-size=1440,1100')
        options.add_argument('--no-first-run')
        cls.browser = webdriver.Chrome(options=options)
        cls.addClassCleanup(cls.browser.quit)
        cls.browser.set_page_load_timeout(45)
        cls.browser.execute_cdp_cmd('Emulation.setEmulatedMedia', {
            'features': [{'name': 'prefers-reduced-motion', 'value': 'reduce'}]})

    def tearDown(self):
        self.browser.save_screenshot(str(RESULTS / (self._testMethodName + '.png')))

    def fill_form(self, marker):
        b = self.browser
        for field, value in {
            'name': 'TEST TECHNICZNY - prosze zignorowac',
            'email': RECIPIENT,
            'location': 'Test formularza - bez rezerwacji',
            'guests': '10',
            'message': f'TEST TECHNICZNY. Kod: {marker}. Weryfikacja wysylki formularza; to nie jest zapytanie ani rezerwacja.'
        }.items():
            b.find_element(By.ID, field).send_keys(value)
        Select(b.find_element(By.ID, 'event-type')).select_by_visible_text('Inne')
        b.execute_script("document.getElementById('date').value = arguments[0]", (date.today() + timedelta(days=30)).isoformat())
        consent = b.find_element(By.CSS_SELECTOR, '[name="Zgoda na kontakt"]')
        b.execute_script("arguments[0].scrollIntoView({block:'center', behavior:'instant'})", consent)
        consent.click()

    def test_01_local_form_contract_and_validation(self):
        b = self.browser
        # Block the provider in this mode, even if code accidentally submits.
        b.execute_cdp_cmd('Network.enable', {})
        b.execute_cdp_cmd('Network.setBlockedURLs', {'urls': ['*formsubmit.co*']})
        b.get(f'http://127.0.0.1:{self.server.server_port}/')
        form = b.find_element(By.ID, 'contactForm')
        self.assertEqual(form.get_attribute('action'), f'https://formsubmit.co/{RECIPIENT}')
        self.assertEqual(form.get_attribute('method').lower(), 'post')
        self.assertEqual(b.find_element(By.NAME, '_captcha').get_attribute('value'), 'false')
        self.assertEqual(b.find_element(By.NAME, '_honey').get_attribute('value'), '')
        self.assertFalse(b.execute_script('return arguments[0].checkValidity()', form))
        self.fill_form('LOCAL-NO-EMAIL')
        self.assertTrue(b.execute_script('return arguments[0].checkValidity()', form))
        b.find_element(By.ID, 'email').clear()
        b.find_element(By.ID, 'email').send_keys('niepoprawny-email')
        self.assertFalse(b.execute_script('return arguments[0].checkValidity()', form))
        b.find_element(By.ID, 'email').clear()
        b.find_element(By.ID, 'email').send_keys(RECIPIENT)
        b.execute_script("document.getElementById('date').value = '2000-01-01'")
        self.assertFalse(b.execute_script('return arguments[0].checkValidity()', form))
        broken = b.execute_script("return Array.from(document.querySelectorAll('a[href^=\"#\"]')).filter(a => !document.getElementById(a.hash.slice(1))).map(a => a.hash)")
        self.assertEqual(broken, [])
        report['local_validation'] = 'passed'

    @unittest.skipUnless(args.live, 'Tryb lokalny: nie wysylamy wiadomosci.')
    def test_02_live_provider_and_optional_delivery(self):
        b = self.browser
        b.execute_cdp_cmd('Network.setBlockedURLs', {'urls': []})
        source_url = f'http://127.0.0.1:{self.server.server_port}/' if args.local_live else args.url
        b.get(source_url)
        report['requested_url'] = source_url
        report['landing_url'] = b.current_url
        self.assertTrue(b.find_elements(By.ID, 'contactForm'),
            'Pod adresem ' + b.current_url + ' nie ma formularza contactForm. Tytul strony: ' + b.title)
        if args.local_live:
            # Only the return destination changes, in this test browser, not in source.
            # Production return still depends on the public domain and is not tested here.
            b.execute_script("document.querySelector('[name=\"_next\"]').value = arguments[0]", source_url + '?wyslano=1#kontakt')
            report['return_url_overridden_for_local_test'] = True
        marker = 'MS-TEST-' + uuid.uuid4().hex[:12].upper()
        report['marker'] = marker
        self.fill_form(marker)
        form = b.find_element(By.ID, 'contactForm')
        self.assertTrue(b.execute_script('return arguments[0].checkValidity()', form))
        self.assertEqual(form.get_attribute('action'), f'https://formsubmit.co/{RECIPIENT}')
        self.assertEqual(b.find_element(By.NAME, '_honey').get_attribute('value'), '')
        self.assertEqual(b.find_element(By.NAME, '_captcha').get_attribute('value'), 'false')
        expected_return = urlparse(b.find_element(By.NAME, '_next').get_attribute('value'))
        print(f'\nWysylam jedno zgloszenie: {marker}', flush=True)
        b.find_element(By.CSS_SELECTOR, '#contactForm [type="submit"]').click()

        def accepted_or_rejected(driver):
            url = urlparse(driver.current_url)
            if url.hostname == expected_return.hostname and url.path == expected_return.path and parse_qs(url.query).get('wyslano') == ['1']:
                return True
            # The site's script removes wyslano after loading; its return message is another signal.
            if url.hostname == expected_return.hostname and url.path == expected_return.path:
                status = driver.find_elements(By.ID, 'formStatus')
                if status and status[0].text.startswith('Powrót z formularza.'):
                    return True
            if url.hostname == 'formsubmit.co':
                text = driver.find_element(By.TAG_NAME, 'body').text.lower()
                if 'the form was submitted successfully.' in text:
                    report['acceptance_evidence'] = 'provider_success_page'
                    return True
                for failure in ('needs activation', 'unable to submit', 'not a robot', 'something went wrong', 'error'):
                    if failure in text:
                        raise AssertionError('FormSubmit nie potwierdzil wysylki: ' + text[:700])
            return False

        WebDriverWait(b, 45).until(accepted_or_rejected,
            'Brak potwierdzonego powrotu z FormSubmit. Zobacz zrzut w test-results. Nie ponawiam automatycznie.')
        report['provider_accepted'] = True
        print('PASS: FormSubmit potwierdzil przyjecie rzeczywistego formularza.', flush=True)
        if args.confirm_delivery:
            print(f'Otworz {RECIPIENT} (takze spam). Znajdz NOWA wiadomosc z kodem {marker}.', flush=True)
            answer = input('Przepisz kod z TRESCI odebranego e-maila (Enter = brak potwierdzenia): ').strip()
            self.assertEqual(answer, marker, 'Nie potwierdzono doreczenia do skrzynki.')
            report['delivery'] = 'confirmed_by_owner'
            print('PASS: wlasciciel potwierdzil odebranie wiadomosci z unikalnym kodem.', flush=True)
        else:
            mode_flag = '--local-live' if args.local_live else '--live'
            print(f'DORECZENIE NIEZWERYFIKOWANE. Pelny test: test-mail.cmd {mode_flag} --confirm-delivery', flush=True)


if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(MailTests)
    try:
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        report['tests_passed'] = result.wasSuccessful()
    finally:
        (RESULTS / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print('Raport i zrzuty: ' + str(RESULTS))
    raise SystemExit(0 if result.wasSuccessful() else 1)
