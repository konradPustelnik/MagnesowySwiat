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
