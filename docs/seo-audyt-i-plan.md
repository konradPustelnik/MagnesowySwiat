# Audyt i plan lokalnego SEO — Magnesowy Świat

Data: 7 listopada 2026. Stan wyjściowy kodu: commit `0915756`.
Zakres początkowy: lokalne przygotowanie zmian. **Aktualizacja 7 listopada 2026: właściciel zatwierdził publikację wszystkich przygotowanych zmian i ponownie zezwolił na publikowanie kolejnych sprawdzonych poprawek bez pytania. Wcześniejsze wstrzymanie publikacji tej partii zostało odwołane.**

## Potwierdzone fakty

- Marka: Magnesowy Świat; adres kontaktowy: magnesowyswiat@gmail.com.
- Fotografowanie gości i wykonywanie personalizowanych fotomagnesów na miejscu podczas wesel, uroczystości rodzinnych i wydarzeń firmowych.
- Cztery istniejące pakiety, zakres i ceny pozostają bez zmian.
- Właściciel potwierdził główny obszar: powiat limanowski i powiat nowosądecki.
- Doprecyzowanie właściciela: przede wszystkim powiat limanowski i okolice; dalsze wyjazdy są możliwe z dodatkową opłatą za dojazd. Brak ustalonej stawki za kilometr lub bezpłatnego promienia. Lokalna treść wyróżnia ten warunek, a koszt jest uzgadniany przed potwierdzeniem rezerwacji.
- Brak potwierdzonego publicznego adresu siedziby, telefonu, godzin, zasad bezpłatnego dojazdu, opinii i własnego portfolio. Nowy Sącz jest odrębnym miastem na prawach powiatu — nie należy automatycznie utożsamiać go z powiatem nowosądeckim. Zapytania o wydarzenia w mieście kierujemy do indywidualnego potwierdzenia miejsca i dojazdu.
- Zdjęcia Unsplash są ilustracyjne; nie są realizacjami firmy. Alternatywne opisy nie mogą przypisywać im lokalizacji zleceń.

## Audyt stanu wyjściowego

| Priorytet | Element | Wynik przed zmianami |
| --- | --- | --- |
| P0 | Domena i HTTPS | HTTP domeny oraz adres GitHub Pages prowadziły do `http://www.magnesowyswiat.pl/`, strona OVH „Site en construction”, HTTP 200. Połączenia HTTPS z domeną główną i www nie powiodły się w tym środowisku. DNS A domeny głównej: 213.186.33.5. |
| P0 | Indeksowalność produkcji | Nie można potwierdzić indeksowalności strony firmy pod docelowym adresem. Sam HTTP 200 strony parkingowej nie jest poprawną publikacją. Nie ma dostępu do Search Console — status indeksowania w Google pozostaje niezweryfikowany. |
| P1 | Title, description | Obecne, poprawne językowo, ogólne, bez lokalnych usług i obszaru. |
| P1 | Canonical | Brak. Docelowy adres wskazany przez właściciela: https://magnesowyswiat.pl/. Sam canonical nie naprawi DNS lub HTTPS. |
| P1 | Sitemap i robots | Brak plików w repozytorium. Ich publicznych wersji HTTPS nie udało się pobrać. Brak robots.txt sam w sobie nie blokuje indeksowania. |
| P1 | H1 i treść lokalna | Jeden H1, lecz hasło reklamowe bez nazwy usługi. Pozostała hierarchia H2–H3 logiczna. Limanowa występuje jedynie w podpowiedziach formularza; brak widocznej sekcji obszaru. |
| P2 | Obrazy | Alt obecne; logo nagłówka ma pusty alt wewnątrz linku z nazwą dostępną — to poprawne. Brak atrybutów wymiarów i srcset. Większość zdjęć lazy, hero fetchpriority=high. |
| P2 | Wydajność | Statyczny HTML, bez frameworka aplikacji. Logo nagłówka 148 310 B, pełne logo 488 368 B; razem 636 678 B. Dwa zewnętrzne fonty i zdjęcia wymagają dostępu do Google Fonts i Unsplash. |
| P2 | Mobilność | Viewport i breakpointy już istnieją. Lokalne Chrome: brak overflow przy 360/390/768/1440 px. Potrzebny test po zmianach i sprawdzenie menu/formularza. |
| P2 | Dane strukturalne | Brak. Dostępne fakty wystarczają do Organization i Service, nie do kompletnego profilu LocalBusiness z adresem. |

## Plan i przygotowane zmiany

1. Spójne metadane, canonical i podgląd udostępnienia pod domeną główną.
2. H1 z usługą i Limanową; widoczna sekcja głównych obszarów i pytań o dojazd. Naturalna polszczyzna zamiast listy fraz SEO.
3. JSON-LD Organization i Service: marka, e-mail, logo, URL, nazwa usługi, dwa potwierdzone powiaty. Bez fikcyjnych lokalizacji, ocen, godzin i klientów. Nie obiecujemy rozszerzonego wyniku w Google.
4. Jedna pozycja w sitemap — wyłącznie istniejąca strona główna; robots ze wskazaniem mapy. Bez wymyślonych dat lastmod i linków do nieistniejących podstron.
5. Wymiary i responsywne warianty zdjęć, lazy loading pełnego logo poniżej pierwszego ekranu. Zachowanie oryginalnej palety, fotografii, formularza, pakietów i obsługi JavaScript.
6. Testy kontraktów SEO, mobilnej nawigacji, wyboru pakietów oraz lokalnej walidacji formularza. W tej partii testy nie wysyłają e-maili.
7. Ujednolicenie pól `_url` i `_next` formularza oraz domyślnego adresu testu live do docelowej domeny HTTPS. Odbiorca, endpoint POST, ukryta pułapka antyspamowa, wyłączenie CAPTCHA i pozostała obsługa formularza pozostają takie jak wcześniej. Przed publikacją domena musi działać.

## Wyniki lokalnej weryfikacji przygotowanych zmian

- `python tests/test_seo.py`: 4 testy przeszły — canonical/robots/sitemap, nagłówki i treść lokalna, JSON-LD, obrazy/odnośniki/formularz.
- `.venv-tests\Scripts\python.exe tests/test_seo.py --browser`: łącznie 5 testów przeszło. Cztery szerokości: 360, 390, 768 i 1440 px; brak poziomego overflow. Działają menu mobilne, wybór pakietów i wstępna walidacja formularza. Zrzut 390 px obejrzano także wizualnie.
- `test-mail.cmd` bez opcji live: lokalna walidacja formularza przeszła; test wysyłki pominięty zgodnie z trybem. Żadna wiadomość nie została wysłana w audycie SEO.
- Po zmianach lokalny odczyt LCP wyniósł odpowiednio 1,820 / 0,452 / 0,540 / 0,432 s; zaobserwowany CLS wyniósł 0 przy tych szerokościach. Wyniki dotyczą jednego przejścia w desktopowym Chrome przy emulowanych szerokościach, bez ograniczenia CPU i sieci. Kolejne przejścia korzystają z cache, więc nie stanowią porównawczego benchmarku ani gwarancji spełnienia CWV. INP nie był mierzony.
- Przeglądarka wybierała dla mobilnego hero wariant 480 px zamiast stałego 1000 px. Wielkości `resourceBytes` w raportach obejmują tylko transfery dostępne przez Resource Timing i cache — nie są pełnym rozmiarem wszystkich zewnętrznych zasobów. Oryginalne logotypy PNG pozostają zachowane; ich dalsza kompresja to potencjalny kolejny etap.
- Raporty JSON i zrzuty są lokalne w ignorowanym `test-results/`. Nie wykonano Rich Results Test, PageSpeed Insights ani URL Inspection dla działającej produkcji, ponieważ docelowa domena nie udostępnia obecnie poprawnej strony HTTPS.
- Zmiany nie zostały opublikowane; DNS, ustawienia hostingu i CNAME nie zostały zmienione.
- Aktualizacja po zgłoszeniu właściciela: wcześniejsze testowe zgłoszenie przyjęte przez FormSubmit nie dotarło do skrzynki. Nie uznajemy wysyłki za zweryfikowaną od formularza do odbioru. Powód niedoręczenia pozostaje nieustalony; pełna lista ryzyk i prac jest w README.

## Proponowana architektura podstron — nie są jeszcze tworzone

| Proponowany URL | Odrębna intencja i wartościowa zawartość | Co potwierdzić przed stworzeniem |
| --- | --- | --- |
| `/magnesy-na-wesele/` | Fotomagnesy jako atrakcja i pamiątka weselna: przebieg obsługi, projekt z imionami i datą, wybór liczby magnesów wobec liczby gości, przygotowanie stanowiska, porównanie pakietów, pytania dotyczące wesel. | Realne terminy uzgadniania projektu, ewentualne szczególne wymagania stanowiska; nie podawać wymyślonego czasu wykonania jednej sztuki. |
| `/fotomagnesy-na-eventy/` | Obsługa firm: personalizacja logo, rodzaje wydarzeń, ustalanie projektu, potrzeby organizatora, limit magnesów i czas obsługi, wycena indywidualna. | Potwierdzić proces akceptacji materiałów marki i warunki organizacyjne. Bez fikcyjnych logotypów klientów. |
| `/obszar-dzialania/` | Jedna użyteczna strona logistyczna dla powiatu limanowskiego i nowosądeckiego: ustalanie dojazdu, informacje potrzebne do wyceny, montaż stanowiska, dostęp do zasilania i zasady kontaktu. | Konkretne zasady dojazdu, dopłaty, ograniczenia i harmonogram. Nie deklarować bezpłatnego dojazdu. |
| `/fotomagnesy-limanowa/` — warunkowo | Oddzielna strona lokalna wyłącznie gdy pojawi się istotna treść o obsłudze Limanowej: rzeczywista logistyka, lokalne pytania klientów, autentyczne realizacje za zgodą uczestników. | Materiały różniące się od strony głównej; uniknąć konkurencji z główną stroną o tę samą intencję. Obecnie wystarcza sekcja na stronie głównej. |
| `/fotomagnesy-nowy-sacz/` — warunkowo | Obsługa wydarzeń w Nowym Sączu opisana osobno dopiero po potwierdzeniu miasta i zdobyciu odrębnych informacji organizacyjnych. | Potwierdzenie obsługi miasta, rzeczywiste warunki dojazdu, własne materiały. Nie kopiować strony Limanowej. |

Na tym etapie nie proponujemy dziesiątek stron dla sąsiednich miejscowości. Każda przyszła podstrona powinna mieć własny title/H1, canonical do siebie, unikalne odpowiedzi i widoczne linkowanie. Sitemap uzupełniamy dopiero po jej faktycznym przygotowaniu. Wspólny formularz może pozostać na stronie głównej; oferta i ceny powinny mieć jedno źródło utrzymania.

## Warunki publikacji i dalszej weryfikacji

1. Właściciel zatwierdził treści i publikację tej partii 7 listopada 2026; stała zgoda została zapisana w instrukcjach projektu.
2. Poprawne skierowanie domeny na GitHub Pages, ukończenie konfiguracji certyfikatu i wymuszenie HTTPS. Sprawdzić apex/www/http/https oraz stary adres GitHub Pages: jedna wersja docelowa `https://magnesowyswiat.pl/`.
3. Po wdrożeniu: HTTP 200 dla strony, robots i sitemap; właściwa zawartość i Content-Type; brak X-Robots-Tag:noindex oraz brak blokady crawl; canonical w źródle.
4. Sprawdzić Rich Results Test / Schema Markup Validator. Lokalny test JSON potwierdza składnię i zakres faktów, nie wynik zewnętrznego walidatora Google.
5. W Search Console zweryfikować domenę, zgłosić sitemap i sprawdzić URL Inspection. Nie dodajemy fikcyjnego tokenu weryfikacyjnego.
6. PageSpeed Insights dla poprawnie działającej domeny; dane CrUX, jeśli będą dostępne. Pomiary lokalne nie są oceną Lighthouse ani gwarancją Core Web Vitals. Sprawdzić LCP, CLS i INP w danych terenowych.
7. Powtórzyć istniejący test prawdziwej wysyłki dopiero na polecenie właściciela; lokalna wysyłka była potwierdzona przez usługę wcześniej, ale test SEO nie potwierdza doręczenia.

## Źródła

- Canonical: https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls
- Mapa strony: https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap
- Organizacja: https://developers.google.com/search/docs/appearance/structured-data/organization
- LocalBusiness i wymagane informacje: https://developers.google.com/search/docs/appearance/structured-data/local-business
- Doorway abuse: https://developers.google.com/search/docs/essentials/spam-policies#doorway-abuse
- Domena GitHub Pages: https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site
