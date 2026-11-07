# Magnesowy Świat

Prosta strona wizytówka w jednym pliku HTML.

## Strona internetowa

**Zobacz stronę:** [https://konradpustelnik.github.io/MagnesowySwiat/](https://konradpustelnik.github.io/MagnesowySwiat/)

Strona jest opublikowana bezpłatnie w GitHub Pages. Repozytorium z jej kodem jest publiczne, więc każdy może je przeglądać, ale zmiany wprowadzać mogą tylko właściciel i osoby z uprawnieniami do zapisu.

Plik `logo-magnesowy-swiat.png` zawiera pełne logo używane w sekcji „Jak działamy”. Zostaw go w folderze projektu obok `index.html`.

## Uruchomienie lokalnie

1. Zainstaluj Pythona, jeśli nie masz go na komputerze.
2. Otwórz folder projektu w VS Code i wybierz **Terminal → New Terminal**.
3. W terminalu, będąc w folderze projektu, uruchom:

   ```powershell
   py -m http.server 8000
   ```

   Jeśli polecenie `py` nie działa, spróbuj:

   ```powershell
   python -m http.server 8000
   ```

4. Otwórz w przeglądarce adres **http://localhost:8000/**.
5. Zostaw terminal otwarty, gdy korzystasz ze strony. Zatrzymaj serwer skrótem **Ctrl+C**.

Jeśli port 8000 jest zajęty, uruchom serwer na innym porcie, np. `py -m http.server 8001`, a następnie odwiedź **http://localhost:8001/**.

Formularz wysyła zapytania na `magnesowyswiat@gmail.com` standardową metodą HTML POST do FormSubmit. Nie korzysta z AJAX ani Fetch, więc wysyłka nie zależy od dostępu CORS do API. Pole `_url` wskazuje publiczny adres strony; `_next` zawiera pełny adres powrotu. Obrazkowa CAPTCHA jest wyłączona przez `_captcha=false`; pozostaje ukryte pole antyspamowe `_honey`. Formularz działa również bez JavaScript.

Przed korzystaniem z formularza trzeba potwierdzić adres odbiorczy w wiadomości aktywacyjnej od FormSubmit. Akceptacja zgłoszenia przez API nie potwierdza doręczenia do skrzynki. Po publikacji wyślij próbne zapytanie z własnym adresem kontaktowym, sprawdź skrzynkę odbiorczą i spam oraz przetestuj odpowiedź na wiadomość. W razie wiadomości aktywacyjnej zatwierdź ją i ponów test. Wysłanie zapytania nie rezerwuje terminu.

Nie otwieraj pliku `index.html` bezpośrednio przez `file://` do testowania wysyłki — korzystaj z lokalnego serwera HTTP opisanego powyżej.

## Test formularza i wysyłki (Selenium + unittest)

Wymagania: Windows, Python 3.10+ i Google Chrome. Otwórz terminal w folderze projektu. Pierwsze uruchomienie pobierze Selenium i odpowiedni sterownik Chrome; potrzebuje internetu. Nie wymaga Node.js ani hasła do poczty.

**Pełny test z potwierdzeniem odbioru:**

```powershell
.\test-mail.cmd --live --confirm-delivery
```

Test otwiera Chrome w tle, wypełnia formularz na publicznej stronie i wysyła **jedno prawdziwe zgłoszenie** do `magnesowyswiat@gmail.com`. Wiadomość jest oznaczona jako test, zawiera unikalny kod `MS-TEST-…` i nie dotyczy rezerwacji. Test nie ponawia wysyłki automatycznie. Po potwierdzeniu odpowiedzi usługi otwórz swoją skrzynkę, znajdź nową wiadomość (również w spamie) i przepisz kod z jej treści do terminala. Brak kodu oznacza niepotwierdzone doręczenie i nieudany pełny test. Nigdy nie wpisuj hasła do poczty w terminalu.

Pozostałe tryby:

```powershell
# Lokalna walidacja i konfiguracja formularza — bez wysyłania poczty:
.\test-mail.cmd

# Jedna prawdziwa wysyłka — tylko potwierdzenie obsługi przez FormSubmit:
.\test-mail.cmd --live

# Po podłączeniu własnej domeny można wskazać adres strony:
.\test-mail.cmd --live --confirm-delivery --url https://www.magnesowyswiat.pl/
```

Tryb lokalny blokuje połączenia z FormSubmit w przeglądarce. Sprawdza wymagane pola, błędny e-mail, datę z przeszłości, konfigurację odbiorcy i odnośniki wewnętrzne. W trybie `--live` test korzysta z opublikowanego kodu, więc najpierw trzeba wdrożyć zmiany, które chcesz sprawdzić.

Raport JSON i zrzuty przeglądarki są zapisywane w `test-results/`. `provider_accepted: true` oznacza powrót po obsłudze zgłoszenia przez FormSubmit; dopiero `delivery: confirmed_by_owner` oznacza ręcznie potwierdzony odbiór wiadomości z kodem. Raporty, środowisko `.venv-tests/` i zrzuty nie trafiają do Git. Test zakończony powodzeniem potwierdza działanie w chwili uruchomienia, nie gwarantuje przyszłej dostępności usług pocztowych.

Przy błędzie aktywacji zatwierdź wiadomość „Activate Form” w skrzynce. Przy innym błędzie sprawdź zrzut w `test-results/` — nie zakładaj, że HTTP 200 lub sam parametr `wyslano=1` potwierdza dostarczenie e-maila.

Jeśli test zgłasza brak `contactForm` i stronę „Site en construction”, domena kieruje na stronę startową hostingu zamiast na stronę projektu. Najpierw trzeba poprawić publikację lub DNS. Test kończy się wtedy błędem przed wysłaniem wiadomości.
