> Po zatwierdzeniu przez użytkownika skopiowano tę wersję do katalogu głównego. Stara wersja jest w `../backup/`. Adresy produkcyjne: `/`, `/magnesy-na-zywo/`, `/magnesy-na-zamowienie/`. Stare adresy `.html` przekierowują. Kopia w tym folderze pozostaje podglądem z noindex i własnymi plikami `.html`. Poniżej dokumentacja utworzenia wersji 2 i ograniczeń. Test produkcyjnych adresów: dodaj `--production` do polecenia testów.

# Magnesowy Świat — wersja 2 (lokalny podgląd)

Nowa, niezależna wersja. Żaden plik dotychczasowej strony ani konfiguracji GitHub Pages nie został zmieniony. Nie wykonano publikacji. Wszystkie nowe pliki są w `wersja-2/`.

## Jak otworzyć

Najprościej otwórz `wersja-2/index.html` w przeglądarce. Nawigacja działa także bez serwera. Dla pełnego podglądu i wygodnego kopiowania uruchom w terminalu **głównego katalogu projektu**:

```powershell
python -m http.server 8000 --bind 127.0.0.1
```

- Obecna strona: http://localhost:8000/
- Nowa główna: http://localhost:8000/wersja-2/index.html
- Na żywo: http://localhost:8000/wersja-2/magnesy-na-zywo.html
- Na zamówienie: http://localhost:8000/wersja-2/magnesy-na-zamowienie.html

Zatrzymanie serwera: Ctrl+C. Ścieżki zasobów i nawigacji są względne, więc działają również w podkatalogu repozytorium na GitHub Pages po świadomej publikacji.

## Pliki

- `index.html` — nowa strona główna, wybór usług, o nas, obszar działania i kontakt.
- `magnesy-na-zywo.html` — przebieg obsługi, okazje, cztery pakiety, FAQ, formularz zapytania.
- `magnesy-na-zamowienie.html` — produkt, zamawianie, ilościowy cennik bez wymyślonych cen, podgląd zdjęć i zapytania.
- `css/style.css` — wspólny wygląd, responsywność i ograniczenie animacji.
- `js/script.js` — menu, dialogi, wybór pakietu, zdjęcia, przygotowanie załączników i okno podziękowania.
- `images/` — kopie logo oraz zdjęcia inspiracyjne; oryginały pozostają nietknięte.
- `build_preview.py` — opcjonalny generator statycznych HTML ze wspólnym nagłówkiem i stopką. Po edycji treści generatora uruchom `python wersja-2/build_preview.py`. Uwaga: nadpisuje wyłącznie trzy nowe HTML; nie uruchamiaj po ręcznych zmianach w tych HTML, jeśli chcesz je zachować.
- `live_layout.py` — układ podstrony „Magnesy na żywo” wzorowany na backupie: oferta → jak działamy → okazje → inspiracje → wyróżniki → cennik → dla firm → o nas → FAQ → formularz. Inspiracje używają lokalnych zdjęć ilustracyjnych, podpisanych jako fotografie spoza realizacji marki.
- Obok nagłówka cennika jest promocja właściciela: 20% zniżki dla pierwszych 3 zleceń na żywo. Nie ma automatycznego licznika zleceń; dostępność potwierdzana jest przy rezerwacji. Po wykorzystaniu promocji ustaw `LAUNCH_PROMO_ACTIVE = False` w `live_layout.py`, przebuduj i opublikuj stronę produkcyjną bez panelu. Podane ceny pakietów pozostają cenami bazowymi.
- `nav_dropdown.py` — wspólne rozwijane menu pod zakładkami „Magnesy na żywo” i „Magnesy na zamówienie”. Natywne `details/summary` obsługuje klawiaturę i dotyk także bez JS; JavaScript dodaje najechanie, zamykanie po wyborze, poza menu i klawiszem Escape. Jednocześnie otwarta jest tylko jedna zakładka. Skróty zamówień prowadzą do: jak zamówić, produkt, cennik, formularz, pomysły, pakowanie i dostawa, FAQ, kontakt.
- `order_form.py` — konfiguracja formularza zamówienia: multipart POST do FormSubmit, temat wiadomości, zgoda na kontakt i przekazanie zdjęć, adres powrotu.
- `order_faq.py` — FAQ zamówień, w tym pakowanie, dostawa głównie do Paczkomatów InPost i reklamacje. Wyłączenie 14-dniowego odstąpienia dla produktów indywidualnych nie wyłącza reklamacji. Źródła sprawdzone 2026-11-08: [wyjątki od odstąpienia — UOKiK](https://prawakonsumenta.uokik.gov.pl/prawo-odstapienia-od-umowy/wylaczenia-prawa-do-odstapienia/), [reklamacje — UOKiK](https://prawakonsumenta.uokik.gov.pl/reklamacja/).
- Dane do dostawy są osobnymi polami: miejscowość, ulica, numer domu/lokalu, kod pocztowy `00-000` i poczta. Trafiają do oddzielnych wierszy wiadomości. Pozostają opcjonalne na etapie zapytania (dostawę można dopiero ustalić).
- W formularzu zamówienia „Dokument zakupu” pozwala wybrać paragon (domyślnie) lub fakturę imienną. Wybór jest pojedynczy i trafia do maila.
- `date_field.py` — pole daty wydarzenia zawsze w formacie `dd/mm/rrrr`, z wyborem z kalendarza i kontrolą rzeczywistej daty, lat przestępnych oraz dat przeszłych. Do maila trafia data w tym samym formacie.
- `tests/test_preview.py` — kontrola linków i opcjonalne testy przeglądarkowe.

## Co działa, a co wymaga integracji

Tematy wiadomości odróżniają usługi już na liście poczty: `[NA ŻYWO] Zapytanie o termin | Magnesowy Świat` i `[NA ZAMÓWIENIE] Zapytanie o magnesy ze zdjęć | Magnesowy Świat`. Dodatkowe pole „Rodzaj zapytania” wskazuje usługę także w treści maila.

Działają: nawigacja, menu telefonu, FAQ, powiększanie fotografii, wybór pakietu/ilości, walidacja, miniatury, liczba kopii każdego zdjęcia, usuwanie miniatur i bezpośrednia wysyłka formularzy. Usunięto dawny dialog „Podgląd zapytania” i kopiowanie szkicu. Znaki specjalne i załączniki są przekazywane przez natywny POST.

**Zapytanie o termin:** przywrócono normalną wysyłkę HTML POST do `https://formsubmit.co/magnesowyswiat@gmail.com`, tak jak w backupie. Formularz działa również bez JavaScript. Nie używa AJAX, nie otwiera lokalnego szkicu i nie wysyła zdjęć. Ma normalną zgodę na kontakt, `_captcha=false`, `_honey`, temat i tabelaryczny szablon wiadomości oraz adres powrotu `/magnesy-na-zywo/?wyslano=1#rezerwacja`. Aktywacja i doręczenie zależą od FormSubmit oraz skrzynki odbiorczej. Powrót z serwisu nie jest dowodem doręczenia. Szczegóły integracji: https://formsubmit.co/

**Zapytanie o zamówienie ze zdjęć:** formularz wysyła dane, zdjęcia i rozpiskę kopii przez zwykły HTML POST z `enctype="multipart/form-data"` do tego samego FormSubmit. JavaScript obsługuje kolejkę plików, podgląd, walidację i przygotowanie osobnych pól załączników. Nie ma AJAX ani dodatkowego uploadu przed wysłaniem. Obowiązuje maksymalnie 20 plików JPEG/PNG/WebP o łącznym rozmiarze do 10 000 000 bajtów (10 MB). Limit wynika z dokumentacji: https://formsubmit.co/documentation#file-uploads . Dane i zdjęcia są przekazywane zewnętrznemu dostawcy dopiero po świadomym wysłaniu formularza. Cena i przyjęcie zamówienia wymagają osobnego potwierdzenia. Testy nie potwierdzają doręczenia do rzeczywistej skrzynki.

Właściciel wyraźnie zatwierdził przesyłanie zdjęć i danych przez FormSubmit 2026-11-08. Po powrocie z obu formularzy (`?wyslano=1`) pojawia się okno „Dziękujemy za kontakt!” z odliczaniem 5 sekund i przyciskiem „Wróć teraz”. Następnie użytkownik wraca na stronę główną. Ekran jest potwierdzeniem powrotu z usługi, nie dowodem doręczenia e-maila. Parametr jest usuwany, aby odświeżenie nie otwierało okna ponownie.

Przed wysyłką zdjęcia są w pamięci karty i lokalnych adresach `blob:`; nie są zapisywane w repozytorium ani localStorage. Suma egzemplarzy musi odpowiadać liczbie magnesów. Zamknięcie/opuszczenie strony usuwa podglądy. Kontrole przeglądarkowe nie zastępują ograniczeń i polityki przetwarzania po stronie dostawcy FormSubmit.

Bez JavaScript formularz zamówienia ze zdjęć jest ukryty; dostępny jest kontakt e-mail. Formularz zapytania o termin działa jako zwykły HTML POST. Kopie w folderze `wersja-2/` zawierają `noindex, nofollow`, ale ich formularze również mogą wysłać prawdziwe zapytanie. Produkcja ma własne canonical i pozwala na indeksowanie.

## Przed uruchomieniem publicznym

- [ ] Ocena docelowego dostawcy formularzy, zasad przechowywania i usuwania plików, polityki prywatności i ochrony przed spamem. W razie potrzeby zastąp FormSubmit własnym backendem. Nie zapisuj zdjęć klientów w GitHub.
- [ ] Rzeczywisty test doręczenia: zwykła treść, polskie litery, znaki specjalne, wiadomość z plikami; sprawdzenie w docelowej skrzynce. Odpowiedź HTTP dostawcy nie daje gwarancji doręczenia.
- [ ] Prawdziwe zdjęcia produktów 6,35 × 6,35 cm, stanowiska, personalizacji i realizacji. Obecne ilustracje są podpisane i mogą pokazywać inne formaty. Puste miejsca są celowe.
- [ ] Ostateczne ceny zamówień 1/3/5/10/20+, płatności, dostawa i terminy. Ceny czterech pakietów na żywo pochodzą z wymagań, przed publikacją potwierdź ich aktualność i zasady rozliczenia.
- [ ] Pełne prawdziwe dane usługodawcy, adresy Facebook/Instagram, ostateczna polityka prywatności i regulamin. Obecne okna informacyjne nie są gotowymi dokumentami prawnymi.
- [ ] Potwierdzenie treści i zakresu dojazdów, opłat, parametrów produktów oraz warunków współpracy.
- [ ] Docelowe adresy, canonical, sitemap, robots i usunięcie `noindex` po zatwierdzeniu. Nie publikować automatycznie wersji demonstracyjnej jako produkcyjnej.
- [ ] Lokalnie hostowane fonty zamiast obecnego Google Fonts (zewnętrzne połączenie); licencja i pliki fontów, ostateczna optymalizacja obrazów i pomiary po wdrożeniu.
- [ ] HTTPS i kontrola formularzy na docelowej domenie. Obecna konfiguracja hostingu nie została zmieniona.

## Testy

Szybki test bez zależności, z głównego katalogu:

```powershell
python wersja-2/tests/test_preview.py
```

Pełniejszy test produkcyjnych stron w Chrome (istniejące środowisko projektu ma Selenium):

```powershell
.\.venv-tests\Scripts\python.exe wersja-2/tests/test_preview.py --browser --production
```

Na innym komputerze potrzebujesz Chrome, Pythona i Selenium (`python -m pip install selenium`). Test automatycznie uruchamia i zatrzymuje lokalny serwer. Sprawdza linki, menu, karty, małe ikony i oba formularze. Wysyłkę kieruje wyłącznie do lokalnego odbiornika: porównuje znaki specjalne, liczbę kopii, nazwy i bajty dwóch syntetycznych załączników, a także blokadę przekroczenia 10 MB. Nie wysyła prawdziwych wiadomości ani prywatnych zdjęć. Zrzuty trafiają do ignorowanego `tests/artifacts/`.

## Pochodzenie zdjęć

Logo skopiowano z istniejącego projektu. Fotografie inspiracyjne z Unsplash, użyte wcześniej jako źródła zdjęć w projekcie, pobrano lokalnie; nie są realizacjami marki:

| Plik | Identyfikator źródła images.unsplash.com |
| --- | --- |
| magnesy-na-lodowce.jpg | photo-1686644472167-4dabcd14bc53 |
| magnesy-rodzinne.jpg | photo-1684741940768-c40eca4ac4ab |
| wspomnienia.jpg | photo-1686644823534-eba27f016efb |
| kolekcja-zdjec.jpg | photo-1686644823172-e9b24140af3a |
| wesele.jpg | photo-1519741497674-611481863552 |
| urodziny.jpg | photo-1530103862676-de8c9debad1d |
| jubileusz.jpg | photo-1511795409834-ef04bbd61622 |
| event.jpg | photo-1511578314322-379afb476865 |

Adres każdego źródła: `https://images.unsplash.com/` + powyższy identyfikator. Przed publicznym użyciem zastąp ilustracje własnymi zdjęciami produktów i potwierdź prawa do materiałów oraz wizerunków.
