# Testy strony Magnesowy Świat

Testy w `tests/test_site.py` sprawdzają stronę główną oraz obie oferty na tych samych plikach, które trafiają do GitHub Pages.

## Uruchamianie

W Windows uruchom `test-strony.cmd` dwuklikiem lub wybierz tryb w terminalu:

```powershell
.\test-strony.cmd --static
.\test-strony.cmd --browser
```

Tryb statyczny wymaga tylko Pythona. Tryb przeglądarkowy wymaga Google Chrome i Selenium. Skrypt tworzy lokalne środowisko `.venv-tests` oraz instaluje Selenium, jeśli go brakuje.

```powershell
python tests/test_site.py StaticTests -v
.\.venv-tests\Scripts\python.exe tests/test_site.py --browser BrowserTests.test_reservation_special_characters_and_package -v
```

GitHub Actions uruchamia testy statyczne przed publikacją i na pull requestach do `main`. Testy Chrome uruchamiają lokalny serwer i zapisują zrzuty w ignorowanym katalogu `tests/artifacts/`.

## Zakres

| Obszar | Sprawdzane zachowanie |
| --- | --- |
| Linki i SEO | Lokalny cel odnośników i kotwic, unikalne identyfikatory, teksty alternatywne obrazów, canonical, mapa witryny, dane strukturalne i przekierowania zachowujące parametry oraz fragment adresu. |
| Grafiki i stopka | Katalog `images/` zawiera dokładnie grafiki wskazane w HTML i CSS. Obie publiczne pozycje w stopce prowadzą do plików PDF. Chrome sprawdza dekodowanie wszystkich obrazów, również ładowanych z opóźnieniem, kadrowanie zdjęć i rozmiar ikon. |
| Formularze produkcyjne | Adres odbiorcy FormSubmit, metoda POST, UTF-8, kodowanie załączników, temat, pole przeciw spamowi i adres powrotu do właściwej sekcji. |
| Rezerwacja na żywo | Wybór pakietu, polski format daty, obsługa kalendarza klawiaturą, walidacja oraz pakiet, data i znaki specjalne w odebranym lokalnie formularzu. |
| Zamówienie ze zdjęć | Podgląd i usuwanie zdjęć, suma kopii, adres dostawy, limit 10 MB oraz nazwy i bajty dwóch syntetycznych PNG odebranych przez lokalny serwer. |
| Kalkulator i rabaty | Granice cenowe, wybór liczby sztuk, zakres 201–10000 dla opcji „200+”, przeniesienie ilości do formularza, rabat procentowy i kod darmowej dostawy. |
| Menu i układ | Nawigacja myszą i klawiaturą, położenie przycisków, widoczność sekcji na małych ekranach oraz poziome przepełnienie widoku. |
| Powrót po wysyłce | Obsługa parametru `wyslano=1`, odliczanie i powrót na stronę główną. |

Standardowy zestaw Chrome blokuje połączenia z FormSubmit i przechwytuje formularze pod `127.0.0.1`. W ten sposób można zweryfikować przygotowanie danych i załączników. Doręczenie e-maila, produkcyjne HTTPS oraz indeksowanie wymagają osobnego sprawdzenia.

## Pomiar czasu wysyłki

- `test-strony.cmd --czas` mierzy oba formularze z lokalnym odbiornikiem HTTP.
- `test-strony.cmd --czas-formsubmit` wysyła po jednym syntetycznym formularzu każdej oferty do produkcyjnego FormSubmit. Wiadomości mają temat z prefiksem `[TEST CZASU]`. Zamówienie zawiera sztuczne obrazy PNG.
- Wyniki trafiają do `test-results/czasy-formularzy.jsonl`. `page_seconds` mierzy przygotowanie danych, `upload_seconds` ich przesłanie, a `http_after_upload_seconds` czas od końca przesyłania do pierwszych nagłówków odpowiedzi HTTP. Dostarczenie wiadomości sprawdza się w skrzynce odbiorczej.
