# Magnesowy Świat

Prosta strona wizytówka w jednym pliku HTML.

Plik `logo-magnesowy-swiat.jpg` zawiera logo używane w nagłówku i stopce. Zostaw go w folderze projektu obok `index.html`.

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

Nie otwieraj pliku `index.html` bezpośrednio przez `file://` — strona formularza korzysta z FormSubmit i wymaga uruchomienia przez serwer HTTP.
