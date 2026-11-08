# Magnesowy Świat

Strona firmy tworzącej personalizowane magnesy fotograficzne na wydarzeniach i na zamówienie. HTML, CSS i JavaScript, bez frameworka aplikacji i bez etapu budowania.

**Produkcja:** [magnesowyswiat.pl](https://magnesowyswiat.pl/). Hosting: GitHub Pages z gałęzi `main`, katalog główny repozytorium. Domena jest zapisana w `CNAME`; publikacja kodu odbywa się przez commit i push zgodnie z `AGENTS.md`.

## Jedna aktualna wersja

Na polecenie właściciela 8 listopada 2026 usunięto starą stronę `backup/`, podwójną wersję `wersja-2/`, nieużywane zasoby i testy poprzedniej architektury. Kod produkcyjny jest teraz jedynym źródłem strony. Nie trzeba niczego generować ani kopiować między wersjami.

| Plik / katalog | Przeznaczenie |
| --- | --- |
| `index.html` | Strona główna, wybór usług, o nas, zasięg i kontakt. |
| `magnesy-na-zywo/index.html` | Oferta wydarzeń, okazje, pakiety, FAQ i formularz rezerwacyjny. |
| `magnesy-na-zamowienie/index.html` | Magnesy ze zdjęć, wycena, zdjęcia i formularz zamówienia. |
| `css/style.css` | Wspólny wygląd i responsywność. |
| `js/script.js` | Menu, formularze, podgląd zdjęć, walidacja i okno po powrocie z wysyłki. |
| `js/calendar-pl.js` | Kalendarz po polsku, z obsługą klawiatury. |
| `images/` | Używane logo, fotografie i wizualizacje. |
| `magnesy-na-zywo.html`, `magnesy-na-zamowienie.html` | Przekierowania dawnych adresów na katalogowe; zachowują parametry i fragmenty URL. |
| `tests/test_site.py` | Jeden aktualny zestaw testów dla produkcyjnych plików. |
| `test-strony.cmd` | Proste uruchamianie testów na Windows. |
| `robots.txt`, `sitemap.xml` | Dostęp robotów i mapa trzech stron. |

Publiczne adresy: `/`, `/magnesy-na-zywo/`, `/magnesy-na-zamowienie/`. Nagłówki i stopki są zapisane w każdym HTML — przy zmianie wspólnej nawigacji trzeba uaktualnić wszystkie trzy pliki.

Stopki zawierają e-mail oraz profile Instagram, Facebook i [TikTok](https://www.tiktok.com/@magnesowyswiat), z małymi kolorowymi ikonami. Podpisy profili Instagram i TikTok to `magnesowyswiat`.

Na stronie głównej H1 jest pogrubiony, a dwa przyciski wyboru usługi znajdują się na końcu pełnego opisu i mają jednakową szerokość. Na małych ekranach opis może wymagać przewinięcia. Karty ofert mają wspólną oprawę, krótkie opisy i przyciski wyrównane na dole.

Na podstronie na żywo przyciski „Zobacz pakiety” i „Zapytaj o termin” również są bezpośrednio pod H1, przed opisem. Kompaktowy nagłówek i odstępy pozwalają wyświetlić oba przyciski bez przewijania w testowanych rozmiarach ekranu.

Podstrona zamówień korzysta z tego samego kompaktowego układu: przycisk „Zamów magnesy” jest pod H1 i pozostaje widoczny na pierwszym ekranie.

## Uruchomienie lokalnie

W terminalu w katalogu projektu:

```powershell
python -m http.server 8000 --bind 127.0.0.1
```

Otwórz [localhost:8000](http://localhost:8000/). Zatrzymanie: `Ctrl+C`. Jeśli `python` nie działa, użyj `py`.

## Testy — najprościej

Potrzebne są Python i Google Chrome. Dwuklik w **`test-strony.cmd`** uruchamia pełny zestaw i pozostawia widoczny wynik. Przy pierwszym uruchomieniu skrypt tworzy `.venv-tests` oraz instaluje Selenium z `tests/requirements.txt`, jeśli go brakuje.

Z terminala:

```powershell
.\test-strony.cmd --browser
```

Szybkie kontrole HTML, linków i SEO, bez uruchamiania Chrome:

```powershell
.\test-strony.cmd --static
```

Bezpośrednio, gdy środowisko jest już gotowe:

```powershell
python tests/test_site.py
.\.venv-tests\Scripts\python.exe tests/test_site.py --browser
```

Zestaw zawiera **19 testów: 3 statyczne i 16 w Chrome**. Testy statyczne nie wymagają Selenium. W trybie bez `--browser` testy przeglądarkowe mają wynik `skipped` — to oczekiwane. Powodzenie kończy się `OK` i kodem wyjścia 0; `FAIL`/`ERROR` oznacza problem do sprawdzenia.

| Obszar | Co faktycznie sprawdzamy |
| --- | --- |
| Struktura i linki | Trzy strony, pojedyncze H1, unikalne ID, opisy alt, lokalne zasoby i kotwice. |
| Podstawy SEO i stare adresy | Canonical, title, meta description, indeksowalność, CNAME, robots, sitemap i przekierowania. |
| Menu | Najechanie, kliknięcie nazwy, strzałki na telefonie, Escape/Enter, fokus i przejścia do sekcji. |
| Formularz na żywo | Wybór pakietu, poprawne dane, data, temat wiadomości oraz zachowanie znaków specjalnych w rzeczywistym lokalnym POST. |
| Formularz ze zdjęciami | Dodawanie/usuwanie podglądów, liczba kopii, adres i kod pocztowy, paragon/faktura, limit 10 MB, zawartość multipart i bajty dwóch syntetycznych zdjęć. |
| Kalendarz | Polskie nazwy, format dd/mm/rrrr, daty niepoprawne i przeszłe, lata przestępne oraz klawiatura. |
| Wygląd i responsywność | Brak poziomego przewijania w sprawdzanych widokach, małe ikony, kadrowanie zdjęć i sekcje 320/390/1440 px. |
| Nagłówki i przyciski | Na głównej: pogrubiony H1, dwa równe przyciski pod opisem, na komputerach bez przewijania. W obu ofertach: przyciski na pierwszym ekranie także na telefonach. Siedem rozmiarów od 320 × 640 do 1440 × 900 oraz poprawne linki kart ofert. |
| Powrót po wysyłce | Symulowany powrót `?wyslano=1`, okno podziękowania, odliczanie i przycisk powrotu. |

Pełna lista nazw i zakresów: [docs/testy.md](docs/testy.md). Zrzuty z testów trafiają do ignorowanego `tests/artifacts/`; można je usunąć i odtworzyć kolejnym uruchomieniem.

**Testy nie wysyłają prawdziwych e-maili.** Uruchamiają lokalny serwer, przechwytują dane formularzy lokalnie i blokują połączenia przeglądarki z FormSubmit. Testują mechanizm strony, ale nie potwierdzają doręczenia do Gmaila, działania DNS/HTTPS produkcji, indeksowania w Google ani zachowania we wszystkich przeglądarkach. Pierwsze uruchomienie Selenium może potrzebować internetu do pobrania sterownika; strona używa także Google Fonts.

## Formularze i prawdziwy test poczty

- Oba formularze wysyłają do `https://formsubmit.co/magnesowyswiat@gmail.com` zwykłym HTML POST; brak AJAX.
- Zapytanie na żywo ma temat `[NA ŻYWO]`, a zamówienie ze zdjęć `[NA ZAMÓWIENIE]`. `_captcha=false` wyłącza obrazkowe zadania; pozostaje pole `_honey`.
- Formularz zdjęciowy używa `multipart/form-data`: maksymalnie 20 plików JPEG/PNG/WebP, łącznie **10 000 000 bajtów (10 MB)**. Zdjęcia pozostają w pamięci karty do świadomego wysłania i nie trafiają do GitHuba ani localStorage.
- Suma kopii zdjęć musi zgadzać się z liczbą magnesów. Do maila trafiają również wybrany dokument zakupu i dane dostawy.
- Bez JavaScript działa formularz na żywo; przy zamówieniach zdjęciowych pozostaje bezpośredni kontakt e-mail.
- Po powrocie z FormSubmit okno podziękowania odlicza 5 sekund i prowadzi na stronę główną. Nie jest dowodem odbioru wiadomości ani przyjęcia rezerwacji.

Żeby sprawdzić rzeczywiste doręczenie, otwórz publiczną podstronę i wyślij kontrolowane zapytanie z własnymi danymi kontaktowymi oraz unikalnym oznaczeniem, np. `MS-TEST-data-godzina`. Sprawdź odbiór, spam, zgodność treści i możliwość odpowiedzi. Formularz zdjęciowy sprawdź osobno, używając niesensytywnego zdjęcia testowego. Sam ekran sukcesu dostawcy lub HTTP 200 nie dowodzi doręczenia. Aktualizacje kodu nie są automatycznym testem skrzynki.

## Ustalenia oferty i pozostałe prace

Treści pochodzą z PDF właściciela. Dojazd do 30 km od Limanowej jest w cenie pakietu na żywo; dalszy transport ustalamy indywidualnie. Dodatkowy magnes poza limitem pakietu: 10 zł/szt. Zachowano promocję 20% na pierwsze trzy zlecenia — dostępność potwierdzana przy rezerwacji. Po wykorzystaniu promocji usuń panel `.launch-offer` z podstrony na żywo.

Progi zamówień ze zdjęć: 5, 20, 50, 100 i 100+ sztuk. [Analiza cen](docs/cennik-na-zamowienie.md) zawiera propozycję, która nie jest jeszcze publicznym cennikiem.

Do uzupełnienia pozostają:

- Finalna polityka prywatności, regulamin i prawdziwe dane usługodawcy. Obecne okna informacyjne nie są gotowymi dokumentami prawnymi.
- Zatwierdzone ceny zamówień na podstawie realnych kosztów oraz warunki płatności i realizacji.
- Własne fotografie produktów i stanowiska; obecne materiały ilustracyjne są podpisane.
- Potwierdzenie rzeczywistego doręczania obu formularzy po stronie skrzynki, okresowa kontrola aktywacji i filtrów FormSubmit.
- Pomiary wydajności produkcji i kontrola indeksowania w Search Console; rozważenie lokalnego hostowania fontów.

Dokumentacja: [zmiany z PDF](docs/zmiany-pdf-2026-11-08.md), [źródła grafik](docs/grafiki.md), [historyczny audyt SEO](docs/seo-audyt-i-plan.md). Audyt opisuje wcześniejszy stan i nie jest aktualnym raportem dostępności domeny.
