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

Formularz otwiera przygotowaną wiadomość w domyślnej aplikacji pocztowej użytkownika. Wiadomość nie jest wysyłana automatycznie — użytkownik musi sprawdzić jej treść i kliknąć „Wyślij”. Automatyczna wysyłka ze statycznej strony wymaga skonfigurowanej zewnętrznej usługi formularzy albo własnego backendu; nie należy umieszczać poświadczeń SMTP w kodzie strony.
