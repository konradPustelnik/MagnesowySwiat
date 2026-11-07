# Magnesowy Świat

Prosta strona wizytówka w jednym pliku HTML.

Najnowszy tekst głównej sekcji został podany bezpośrednio przez właściciela: nagłówek „Magnesowy Świat – Magnesy na żywo na weselach i eventach | Limanowa, Nowy Sącz, Kraków” oraz wstęp „✨ Mały magnes. Wielkie wspomnienia.” z informacją o magnesach na żywo i indywidualnych zamówieniach ze zdjęć. Wcześniejsze cofnięcie lokalnej sekcji i opisów poniżej jest zapisem historii; osobna sekcja zasięgu nadal pozostaje usunięta.

**Aktualizacja wyglądu i treści:** na prośbę właściciela cofnięto promowanie Limanowej w nagłówku i metadanych oraz usunięto sekcję lokalnego zasięgu wraz z jej odnośnikami. Przywrócono poprzedni ogólny tekst wstępu i informacje o dojeździe. Zachowano poprawki techniczne domeny, favicon, format magnesów 6,35 × 6,35 cm, brązowe tło i okno potwierdzenia formularza. Audyt i propozycje lokalnego SEO poniżej oraz w osobnym dokumencie są zapisem wcześniejszych prac, nie opisem obecnej treści strony.

## Strona internetowa

**Docelowy adres strony:** [https://magnesowyswiat.pl/](https://magnesowyswiat.pl/)

Hosting: GitHub Pages, repozytorium `konradpustelnik/MagnesowySwiat`. Stary adres `konradpustelnik.github.io/MagnesowySwiat/` przekierowuje na domenę ustawioną w GitHub Pages. Domena wymaga prawidłowego DNS i aktywnego HTTPS. Audyt i poprawki SEO: [docs/seo-audyt-i-plan.md](docs/seo-audyt-i-plan.md). Właściciel zatwierdził publikację tej partii 7 listopada 2026 i ponownie udzielił zgody na publikowanie kolejnych sprawdzonych zmian bez pytania.

Strona jest opublikowana bezpłatnie w GitHub Pages. Repozytorium z jej kodem jest publiczne, więc każdy może je przeglądać, ale zmiany wprowadzać mogą tylko właściciel i osoby z uprawnieniami do zapisu.

## Status audytu, ryzyka i pozostałe prace

Stan ustaleń: **7 listopada 2026**. Przygotowane poprawki SEO, zasięgu i favicon zostały zatwierdzone do publikacji. Poniższe problemy domeny pochodzą z pomiaru podczas audytu — nie są deklaracją jej aktualnego stanu. Stan konkretnego wdrożenia należy sprawdzić w GitHub Pages i na publicznej stronie.

**Poczta nie ma potwierdzonego działania od formularza do skrzynki.** FormSubmit wyświetlił ekran przyjęcia testowego zgłoszenia, ale właściciel zgłosił, że wiadomość nie dotarła. Nie traktujemy tego jako udanego testu doręczenia. Dotychczasowy test przeglądarkowy bez `--confirm-delivery` sprawdza tylko odpowiedź usługi; nie odczytuje skrzynki. Przyczyna niedoręczenia nie została ustalona.

Właściciel zauważył możliwy związek niedoręczeń z wypełnieniem „Dodatkowych informacji” i podał przykład `rabacik ?`. To hipoteza do sprawdzenia, a nie ustalona przyczyna. Test lokalny sprawdza zachowanie pustej wiadomości, dokładnego przykładu `rabacik ?` oraz tekstu z polskimi znakami i nowym wierszem w `FormData`, poprawność walidacji i puste pole `_honey`. Nie sprawdza filtrów FormSubmit ani Gmaila. Następny krok: porównać dwa zgłoszenia różniące się tylko wiadomością i potwierdzić oba odbiory w skrzynce; nie uznawać samych ekranów sukcesu za dowód.

| Priorytet | Ryzyko / ustalenie | Co jeszcze trzeba zrobić | Warunek zamknięcia |
| --- | --- | --- | --- |
| P0 | Niedoręczone zgłoszenia mogą oznaczać utratę zapytań klientów, mimo ekranu sukcesu FormSubmit. | Sprawdzić aktywację odbiorcy, spam, wszystkie wiadomości i filtry skrzynki. Przeprowadzić jeden kontrolowany test z unikalnym kodem i rzeczywistym adresem kontaktowym. Jeśli nadal nie dociera, zgłosić problem dostawcy; rozważyć inny mechanizm wysyłki z możliwością sprawdzenia statusu doręczenia. | Nowa wiadomość z kodem faktycznie odebrana w skrzynce; możliwość odpowiedzi na adres klienta sprawdzona. Sam HTTP 200 lub `provider_accepted: true` nie wystarcza. |
| P0 | W audycie domena prowadziła do strony startowej OVH, a HTTPS nie odpowiadał. Użytkownicy i roboty mogli otrzymywać niewłaściwą stronę. | Poprawić DNS i ustawienia GitHub Pages, uruchomić certyfikat HTTPS; sprawdzić domenę główną, www, HTTP oraz stary adres GitHub Pages. Nie zmieniać przy tym rekordów pocztowych bez potrzeby. | Wszystkie warianty prowadzą do `https://magnesowyswiat.pl/`, gdzie serwowana jest strona firmy, bez błędu certyfikatu. |
| P1 | Sam zapis kodu w repozytorium nie potwierdza zakończenia wdrożenia; canonical sam nie naprawi domeny. | Publikacja jest zatwierdzona. Sprawdzić zakończenie GitHub Pages, publiczną zawartość, docelowy adres oraz powrót z formularza. | Kod z poprawkami jest dostępny pod działającą domeną HTTPS. |
| P1 | Stan indeksowania w Google jest nieznany. | Po wdrożeniu sprawdzić canonical, robots, sitemap, nagłówki HTTP i brak `noindex`; zweryfikować domenę w Search Console, zgłosić sitemap i sprawdzić URL Inspection. | Google ma dostęp do właściwej treści; raport indeksowania został sprawdzony. Nie gwarantuje to pozycji ani natychmiastowej indeksacji. |
| P1 | Dane lokalne muszą odpowiadać rzeczywistej ofercie. Głównie powiat limanowski i okolice; potwierdzono także powiat nowosądecki oraz dodatkową opłatę za dalsze wyjazdy. Miasto Nowy Sącz jest osobną jednostką. | Potwierdzić obsługę samego miasta Nowy Sącz i doprecyzować sposób wyceny dojazdu. Każdą lokalizację i koszt potwierdzać przed rezerwacją; nie deklarować nieustalonego bezpłatnego promienia ani stawki kilometrowej. | Właściciel zatwierdził obszary i warunki; treść oraz JSON-LD są z nimi zgodne. |
| P2 | JSON-LD przeszedł testy lokalne, ale nie zewnętrzną walidację Google. | Sprawdzić Organization w Rich Results Test i cały graf w Schema Markup Validator. Nie uzupełniać brakujących danych fikcyjnym adresem, telefonem, ocenami lub godzinami. | Brak błędów składni i zgodność danych z widoczną treścią. Nie każdy typ schema daje rozszerzony wynik w Google. |
| P2 | Lokalne wyniki mobilne nie potwierdzają szybkości na telefonach klientów. Logotypy PNG ważą łącznie około 637 KB; fonty i zdjęcia zależą od usług zewnętrznych. | Uruchomić PageSpeed Insights po naprawie domeny, sprawdzić LCP/CLS/INP i realne urządzenie; rozważyć kompresję logotypów, a własne zdjęcia optymalizować przed dodaniem. | Wyniki produkcyjne i konkretne problemy są zapisane; brak regresji menu, pakietów i formularza. |
| P2 | Powielone strony miast i zdjęcia stockowe przedstawiane jako portfolio obniżałyby wiarygodność treści. | Przygotować odrębne podstrony usług z użytecznymi informacjami; strony miast dopiero z rzeczywistą treścią lokalną. Pozyskać własne fotografie z prawem publikacji. | Każda podstrona wnosi inną wartość, ma własny canonical i jest uwzględniona w sitemap dopiero po utworzeniu. |

**Przygotowane lokalnie:** title i meta description, H1 opisujący usługę, sekcja obszaru obsługi, canonical, Open Graph, `robots.txt`, `sitemap.xml`, Organization/Service JSON-LD, wymiary i warianty rozmiarów obrazów oraz spójne adresy formularza. Zachowano złotą identyfikację, pakiety i mechanizm formularza.

**Sprawdzone lokalnie:** 4 testy kontraktów SEO oraz test przeglądarkowy przy 360, 390, 768 i 1440 px; brak przewijania poziomego, działanie menu i wyboru pakietów. Lokalna walidacja formularza również przeszła. To nie jest potwierdzenie dostarczenia poczty ani indeksowania strony. Szczegóły: [pełny audyt i plan](docs/seo-audyt-i-plan.md).

Kolejność dalszej pracy:

1. Wyjaśnić niedoręczanie poczty i potwierdzić odbiór kontrolnego zgłoszenia.
2. Naprawić domenę/HTTPS i doprecyzować sposób indywidualnej wyceny dojazdu.
3. Opublikować zatwierdzone poprawki i sprawdzić wynik wdrożenia GitHub Pages.
4. Sprawdzić SEO, mobilność i pełną ścieżkę formularza na produkcji; zgłosić sitemap w Search Console.
5. Rozwinąć podstrony `/magnesy-na-wesele/`, `/fotomagnesy-na-eventy/`, `/obszar-dzialania/`. Osobne strony Limanowej i Nowego Sącza pozostają propozycją warunkową, bez powielania tekstu.

**Zasięg i dojazd — aktualizacja od właściciela:** działamy przede wszystkim w powiecie limanowskim i okolicach; wcześniej potwierdzono także obsługę powiatu nowosądeckiego. Dalsze wyjazdy są możliwe po uzgodnieniu, za dodatkową opłatą za dojazd. W lokalnej wersji strony informacja jest wyróżniona w sekcji obszaru działania oraz powtórzona przy pakietach i w FAQ. Koszt ma być podany przed potwierdzeniem rezerwacji. Nie ustalono stałej stawki za kilometr, limitu kilometrów ani granicy bezpłatnego dojazdu — nie należy ich dopisywać bez potwierdzenia.

Plik `logo-magnesowy-swiat.png` zawiera pełne logo używane w sekcji „Jak działamy”. Zostaw go w folderze projektu obok `index.html`.

To samo kwadratowe logo jest ustawione jako favicon (ikona karty przeglądarki) i ikona skrótu na urządzeniach Apple. Po publikacji przeglądarka może przez pewien czas wyświetlać poprzednią ikonę z pamięci podręcznej; sprawdź nową kartę prywatną. Zmiana favicon nie usuwa komunikatu „Not secure” — wymaga on działającego HTTPS domeny.

Po powrocie z FormSubmit pod adres z `?wyslano=1#kontakt` strona pokazuje okno podziękowania i po 5 sekundach wraca do początku, odświeżając stronę i formularz. Przycisk „Wróć teraz” pozwala wrócić wcześniej. Okno informuje o przekazaniu zapytania do wysłania, nie o potwierdzonym doręczeniu. Jest wyświetlane po powrocie z usługi, a nie przy samym kliknięciu „Wyślij”; jeśli FormSubmit zatrzyma użytkownika na własnym ekranie, okno naszej strony nie zostanie jeszcze pokazane.

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

**Prawdziwa wysyłka z lokalnego serwera, niezależna od DNS i domeny:**

```powershell
.\test-mail.cmd --local-live --confirm-delivery
```

Ten tryb sam uruchamia lokalny serwer HTTP, otwiera lokalny `index.html` i wysyła jedno prawdziwe zgłoszenie do FormSubmit. Wyłącznie w pamięci przeglądarki testowej zmienia adres powrotu `_next` na lokalny, żeby nie trafić na niedziałającą domenę. Nie zmienia plików strony ani odbiorcy. Sprawdza rzeczywistą wysyłkę lokalnego kodu; nie potwierdza poprawności domeny i powrotu na stronę produkcyjną. Bez `--confirm-delivery` sprawdza przyjęcie zgłoszenia, bez potwierdzenia odbioru.

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

Raport JSON i zrzuty przeglądarki są zapisywane w `test-results/`. `provider_accepted: true` oznacza ekran FormSubmit „The form was submitted successfully” lub powrót po obsłudze zgłoszenia; dopiero `delivery: confirmed_by_owner` oznacza ręcznie potwierdzony odbiór wiadomości z kodem. Raporty, środowisko `.venv-tests/` i zrzuty nie trafiają do Git. Test zakończony powodzeniem potwierdza działanie w chwili uruchomienia, nie gwarantuje przyszłej dostępności usług pocztowych.

**Jak czytać wynik:** `tests_passed: true` oznacza przejście testów wybranego trybu, a nie automatycznie sprawną pocztę. W trybie lokalnym test wysyłki jest pomijany. `delivery: not_checked` oznacza brak potwierdzenia doręczenia, również gdy test usługi zakończył się `OK`. Raport `report.json` jest zastępowany przy kolejnym uruchomieniu; przed następną próbą zachowaj kopię raportu i kodu zgłoszenia, jeśli chcesz porównywać wyniki. Nie przepisuj kodu z terminala jako dowodu odbioru — ma pochodzić z nowej wiadomości w skrzynce.

Aktualizacja testów: każde uruchomienie zapisuje również osobny raport z datą w nazwie, więc wcześniejsze raporty JSON nie są już tracone. Pole `end_to_end_passed` jest prawdziwe tylko po ręcznym potwierdzeniu kodu z odebranej wiadomości. Tryb live bez potwierdzenia odbioru kończy się kodem **2 (wynik niepełny)**, nawet jeśli techniczne scenariusze unittest pokazały `OK`. Kod 1 oznacza błąd, a 0 — zaliczenie wybranego trybu (w lokalnym nadal bez wysyłki).

Regresja znaków specjalnych: lokalny test wysyła prawdziwy POST do kontrolowanego serwera testowego i porównuje odebraną treść znak po znaku, w tym `:()@&%$#*($#^*!@(#&#@%&@(#$@!`. Nie usuwa ani nie podmienia znaków. Na serwerze produkcyjnym zgłoszenie z tym ciągiem zostało przyjęte przez FormSubmit (kod testu `MS-TEST-1D9FE5A5C1A0`), ale właściciel potwierdził, że wiadomość **nie dotarła**. Test doręczenia jest więc niezaliczony. Przesłanie znaków przez formularz jest poprawne; bez logów dostawcy i poczty nie ustalono, na którym etapie po przyjęciu zgłoszenia wiadomość została zatrzymana. Nie należy zmieniać kodowania ani usuwać znaków jako pozornej naprawy.

Pełne powtórzenie testu dokładnego ciągu (wysyła jedną wiadomość; kod jest w temacie, aby nie zmieniać treści badanego pola):

```powershell
.\test-mail.cmd --live --special-characters --confirm-delivery
```

Przy błędzie aktywacji zatwierdź wiadomość „Activate Form” w skrzynce. Przy innym błędzie sprawdź zrzut w `test-results/` — nie zakładaj, że HTTP 200 lub sam parametr `wyslano=1` potwierdza dostarczenie e-maila.

## Testy SEO — bez publikacji i wysyłania e-maili

Podstawowe testy wymagają wyłącznie Pythona:

```powershell
python tests/test_seo.py
```

Test przeglądarkowy sprawdza również układ przy 360, 390, 768 i 1440 px, mobilne menu oraz wybór pakietów. Jeżeli nie masz jeszcze środowiska testowego, uruchom najpierw `.\test-mail.cmd` — zainstaluje zależności i wykona test lokalny bez wysyłki.

```powershell
.\.venv-tests\Scripts\python.exe tests/test_seo.py --browser
```

Raport: `test-results/seo-browser.json`, zrzuty: `test-results/seo-*.png`. Są to lokalne pomiary Chrome, bez symulacji sieci komórkowej; nie zastępują danych terenowych Core Web Vitals ani potwierdzenia indeksowania w Search Console. Testy sprawdzają canonical, sitemap, robots, hierarchię nagłówków, obrazy, zakres faktów JSON-LD i konfigurację formularza. Nie wysyłają zgłoszenia do FormSubmit.

Jeśli test zgłasza brak `contactForm` i stronę „Site en construction”, domena kieruje na stronę startową hostingu zamiast na stronę projektu. Najpierw trzeba poprawić publikację lub DNS. Test kończy się wtedy błędem przed wysłaniem wiadomości.
