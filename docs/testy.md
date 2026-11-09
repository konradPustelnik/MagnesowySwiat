# Testy strony Magnesowy Świat

Aktualny zestaw to `tests/test_site.py`: **19 testów — 3 statyczne i 16 przeglądarkowych**. Sprawdza pliki produkcyjne: stronę główną, `/magnesy-na-zywo/` i `/magnesy-na-zamowienie/`. Zastępuje testy dawnej wersji strony.

## Jak uruchomić

W Windows kliknij dwukrotnie `test-strony.cmd`. Uruchomi pełny zestaw w niewidocznym oknie Chrome i zatrzyma okno z wynikiem, aby dało się go przeczytać.

Z terminala w katalogu projektu:

```powershell
# Wszystkie 19 testów, w tym obsługa strony w Chrome:
.\test-strony.cmd

# Ten sam pełny zestaw, bez zatrzymywania terminala po wyniku:
.\test-strony.cmd --browser

# Tylko 3 szybkie kontrole plików — bez Chrome i instalowania Selenium:
.\test-strony.cmd --static
```

Wymagany jest Python 3. Dla pełnego zestawu zainstaluj także Google Chrome. Skrypt tworzy lokalne środowisko `.venv-tests`, jeśli go nie ma. W trybie przeglądarkowym instaluje brakujące Selenium według `tests/requirements.txt`; Selenium może przy pierwszym uruchomieniu pobrać odpowiedni sterownik Chrome. Instalacja zależności i sterownika może wymagać internetu. Testowana strona działa na lokalnym serwerze uruchamianym i zatrzymywanym przez testy.

Bez skryptu Windows:

```powershell
python tests/test_site.py -v
.\.venv-tests\Scripts\python.exe tests/test_site.py --browser -v

# Jeden wybrany scenariusz:
.\.venv-tests\Scripts\python.exe tests/test_site.py --browser BrowserTests.test_reservation_special_characters_and_package -v
```

Przy `--static` / bez `--browser` 15 scenariuszy przeglądarkowych ma status `skipped` — to oczekiwane, nie jest to pełna weryfikacja strony. Kod wyjścia `0` oznacza zaliczenie uruchomionych testów, a kod różny od `0` błąd. Nieznany argument skryptu `.cmd` zwraca `2`. Zrzuty pomocnicze trafiają do ignorowanego folderu `tests/artifacts/` i mogą być nadpisywane kolejnym uruchomieniem.

## Dokładny zakres testów

| Nr | Test | Co sprawdza |
|---:|---|---|
| 1 | `StaticTests.test_links_assets_and_structure` | Po jednym H1 na każdej z trzech stron, brak powtórzonych identyfikatorów, obecność `alt` przy obrazach, istnienie lokalnych plików i celów odnośników między stronami oraz do sekcji. |
| 2 | `StaticTests.test_canonical_indexability_and_sitemap` | Canonical dla trzech adresów produkcyjnych, brak `noindex` w meta robots, język polski, obecność opisu i tytułu, domenę w `CNAME`, adres mapy w robots.txt, brak blokady stron w aktualnych regułach robots oraz komplet adresów i odpowiadających im plików w sitemap.xml. |
| 3 | `StaticTests.test_legacy_redirects_preserve_destination_and_fragment` | Oba stare adresy `.html`: prawidłowy canonical, zapasowy meta refresh i link, istnienie strony docelowej oraz mechanizm przekazywania parametrów i fragmentu adresu. Faktyczną nawigację sprawdza również test nr 11. |
| 4 | `BrowserTests.test_responsive_menu_and_pages` | Trzy strony przy kilku szerokościach: brak poziomego przepełnienia, brak błędu obrazów już załadowanych oraz otwieranie mobilnego menu i kliknięcie odnośnika. |
| 5 | `BrowserTests.test_pdf_offer_and_responsive_sections` | Kluczowe sekcje po zmianach z PDF, trzy kroki obsługi, brak dawnej galerii na żywo, informacje o dojeździe 30 km i dodatkowym magnesie 10 zł/szt., ładowanie zdjęć w sprawdzanych sekcjach i układ przy 1440, 390 i 320 px. |
| 6 | `BrowserTests.test_service_name_navigates_instead_of_toggling` | Rozwijanie menu po najechaniu na nazwę usługi, przejście na stronę na żywo po kliknięciu oraz przejście na stronę zamówień klawiszem Enter. |
| 7 | `BrowserTests.test_quantity_choices_and_mobile_layout` | Wybory 5, 20, 50, 100 i 100+ w cenniku, uzupełnienie ilości w formularzu, przejście do `#zamowienie`, wysokość przycisków co najmniej 44 px i brak przepełnienia przy 1440, 390 i 320 px. Dla „100+” formularz otrzymuje 101 sztuk. |
| 8 | `BrowserTests.test_reservation_special_characters_and_package` | Wybór pakietu Gold i wysłanie formularza na żywo do lokalnego odbiornika. Porównuje dokładnie ciąg `:()@&%$#*($#^*!@(#&#@%&@(#$@!`, pakiet, datę, e-mail, ustawienia oraz temat i rodzaj zapytania. Sprawdza także produkcyjny adres usługi przed jego lokalnym zastąpieniem. |
| 9 | `BrowserTests.test_footer_icons_stay_small_without_stylesheet` | Cztery ikony w stopce każdej strony (Gmail, Instagram, Facebook, TikTok): rozmiar 18 × 18 px także po wyłączeniu arkusza CSS. Sprawdza także adres, podpis i etykietę dostępności profilu TikTok. |
| 10 | `BrowserTests.test_occasion_photos_have_consistent_crops_on_mobile_and_desktop` | Cztery zdjęcia okazji: równa wysokość, proporcje 16:9, kadrowanie `cover`, dwie kolumny na komputerze i jedna na telefonie, brak przepełnienia. |
| 11 | `BrowserTests.test_home_url_hides_index_and_preserves_contact_anchor` | Ukrycie `index.html` w adresie strony głównej z zachowaniem parametrów i `#kontakt`; brak `index.html` w głównej nawigacji. Dodatkowo przejście z obu starych adresów `.html` do nowych katalogów z zachowaniem query i fragmentu formularza. |
| 12 | `BrowserTests.test_order_preview_counts_delete_and_validation` | Dodawanie i usuwanie lokalnego podglądu zdjęć, liczby kopii, sumę magnesów, kod pocztowy i dane dostawy, wybór paragonu lub faktury imiennej. Wysyła do lokalnego odbiornika dwa syntetyczne PNG przez multipart i sprawdza nazwy, wszystkie bajty plików, liczby kopii, temat, rodzaj zapytania i znaki specjalne w uwagach. „Preview” w nazwie oznacza podgląd wybranych zdjęć, nie dawny demonstracyjny formularz. |
| 13 | `BrowserTests.test_order_total_attachment_limit` | Próbę wyboru 11 MB plików: odrzucenie pliku przekraczającego łączny limit 10 MB i komunikat. |
| 14 | `BrowserTests.test_return_dialog_countdown_and_manual_home` | Okno po symulowanym powrocie `?wyslano=1` na obu formularzach, usunięcie parametru z adresu, automatyczny powrót po kilku sekundach i ręczny przycisk powrotu. Nie weryfikuje doręczenia wiadomości. |
| 15 | `BrowserTests.test_live_dropdown_desktop_keyboard_and_mobile` | Menu na żywo: hover, Escape z przywróceniem fokusu, Enter, link do cennika, mobilną strzałkę, zamknięcie mobilnego menu po wyborze i szerokości 1024, 981, 390 oraz 320 px. |
| 16 | `BrowserTests.test_event_date_polish_format_validation_and_calendar` | Maskę `dd/mm/rrrr`, poprawną datę, nieistniejące daty lutowe i datę przeszłą, lata przestępne oraz synchronizację z wartością kalendarza. |
| 17 | `BrowserTests.test_order_dropdown_and_exclusive_open_state` | Menu zamówień: otwarcie po najechaniu, zamknięcie poprzedniego menu, przejście do cennika i FAQ, mobilną strzałkę, zamknięcie menu po wyborze i brak przepełnienia. |
| 18 | `BrowserTests.test_calendar_polish_labels_selection_and_mobile` | Polskie miesiące i dni tygodnia od poniedziałku, polskie etykiety dostępności dat, wybór strzałką i Enter, zmianę miesiąca i roku, 29 lutego w roku przestępnym i brak tej daty w 2100 oraz dopasowanie okna do 1440, 390 i 320 px. |
| 19 | `BrowserTests.test_home_service_choices_fit_first_viewport` | Na stronie głównej: pogrubiony H1, dwa przyciski pod całym opisem, jednakowe szerokości i widoczność bez przewijania na komputerach (od 981 px szerokości). Mniejsze ekrany mogą przewijać cały opis. W ofercie na żywo oba przyciski, a w zamówieniach jeden przycisk pozostają na pierwszym ekranie we wszystkich sprawdzanych rozmiarach: 1440 × 900, 1366 × 768, 1024 × 768, 768 × 1024, 390 × 844, 360 × 740 i 320 × 640. Sprawdza wysokość co najmniej 44 px, cele linków, linki kart ofert i brak poziomego przepełnienia. Czeka na fonty; zapisuje zrzuty nagłówków i kart. |

## Co oznacza zaliczony test formularza

Oba formularze są testowane przez rzeczywisty lokalny POST z przeglądarki do odbiornika `127.0.0.1`. Odbiornik przyjmuje POST wyłącznie pod `/__capture`; porównuje odebrane pola i bajty załączników. W całym zestawie Chrome ma zablokowane połączenia z FormSubmit. Używane pliki to sztuczne obrazy PNG utworzone tymczasowo przez test, bez prywatnych zdjęć klienta.

To potwierdza, że kod strony poprawnie przygotowuje i przekazuje dane w sprawdzonych scenariuszach. **Nie potwierdza przyjęcia przez FormSubmit ani dostarczenia e-maila do Gmaila.** Samo wyświetlenie okna powrotu również nie jest dowodem doręczenia — test uruchamia je kontrolowanym parametrem adresu.

Pełną próbę doręczenia wykonuje właściciel: wysyła formularz na opublikowanej stronie z własnymi danymi i unikalnym oznaczeniem, np. `MS-SPRAWDZENIE-20261108-01`, a następnie sprawdza nową wiadomość z tym samym oznaczeniem w skrzynce `magnesowyswiat@gmail.com` i spamie. Warto wykonać osobną próbę dla na żywo i dla zamówienia z własnym testowym zdjęciem. Ten zestaw nie wysyła takich wiadomości samodzielnie.

Kontrola SEO obejmuje też unikalność tytułów i opisów, wymagany tytuł strony głównej, poprawny JSON-LD `WebSite` z nazwą marki i adresem domeny oraz wzajemne linkowanie trzech stron. Raport: [SEO z 9 listopada 2026](seo-2026-11-09.md).

## Ograniczenia

- Testy opisują zachowanie sprawdzanej wersji w chwili uruchomienia. Nie gwarantują przyszłej dostępności FormSubmit, Gmaila, DNS ani GitHub Pages.
- Testy uruchamiają stronę lokalnie. Nie sprawdzają produkcyjnego HTTPS, nagłówków HTTP, aktualnego wdrożenia ani działania wszystkich zewnętrznych profili i usług.
- Sprawdzane są wybrane szerokości i Chrome. To nie pełne testy Safari, Firefox, wszystkich telefonów, powiększeń tekstu i czytników ekranu.
- Testy linków sprawdzają istnienie plików i sekcji. Nie oceniają użyteczności treści ani nie gwarantują, że publiczny zewnętrzny link odpowie.
- Kontrole SEO dotyczą podstawowej konfiguracji plików. Nie są audytem pozycji Google, potwierdzeniem indeksacji ani danymi Core Web Vitals; nie oceniają jakości każdego opisu `alt` czy prawdziwości danych strukturalnych.
- Zrzuty ułatwiają przegląd wyglądu. Nie ma automatycznego porównywania pikseli z wzorcem ani oceny estetyki.
- Walidacja obejmuje wskazane przypadki, a nie wszystkie możliwe pliki, teksty i błędne dane. Limit zdjęć sprawdzany jest reprezentatywną próbą 11 MB, nie każdym wariantem granicznym.
