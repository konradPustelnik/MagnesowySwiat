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
- `magnesy-na-zywo.html` — przebieg obsługi, okazje, cztery pakiety, FAQ, podgląd zapytania.
- `magnesy-na-zamowienie.html` — produkt, zamawianie, ilościowy cennik bez wymyślonych cen, podgląd zdjęć i zapytania.
- `css/style.css` — wspólny wygląd, responsywność i ograniczenie animacji.
- `js/script.js` — menu, dialogi, wybór pakietu, zdjęcia i szkic wiadomości.
- `images/` — kopie logo oraz zdjęcia inspiracyjne; oryginały pozostają nietknięte.
- `build_preview.py` — opcjonalny generator statycznych HTML ze wspólnym nagłówkiem i stopką. Po edycji treści generatora uruchom `python wersja-2/build_preview.py`. Uwaga: nadpisuje wyłącznie trzy nowe HTML; nie uruchamiaj po ręcznych zmianach w tych HTML, jeśli chcesz je zachować.
- `tests/test_preview.py` — kontrola linków i opcjonalne testy przeglądarkowe.

## Co działa, a co wymaga integracji

Działają: nawigacja, menu telefonu, FAQ, powiększanie fotografii, wybór pakietu/ilości, walidacja, lokalne miniatury, liczba kopii każdego zdjęcia, usuwanie miniatur, podgląd i kopiowanie zapytania. Znaki specjalne pozostają w treści; szkic `mailto:` koduje je przez `encodeURIComponent`.

**Formularze NIE wysyłają e-maili, zdjęć ani zamówień.** Wyraźnie informują o tym przed przyciskiem i w oknie podglądu. Przycisk poczty otwiera szkic w programie użytkownika, bez załączników. Użytkownik musi sam dodać pliki i wysłać wiadomość. Duże szkice mogą podlegać limitom programu pocztowego; alternatywą jest skopiowanie tekstu. Żaden z testów nie potwierdza doręczenia e-maila do skrzynki.

Zdjęcia użytkownika są przechowywane tylko w pamięci karty, przez lokalne adresy `blob:`. Brak uploadu, localStorage i zewnętrznego serwisu do zdjęć. Limit interfejsu: 20 plików JPEG/PNG/WebP, po 10 MB. Suma egzemplarzy musi odpowiadać liczbie magnesów. Zamknięcie/opuszczenie strony usuwa podglądy. Frontendowa kontrola plików nie zastępuje przyszłej walidacji na serwerze.

Bez JavaScript formularze są ukryte i dostępny jest kontakt e-mail. Wszystkie strony zawierają `noindex, nofollow` na czas porównywania wersji. Nie dodano produkcyjnego canonical ani danych strukturalnych z niepotwierdzonymi informacjami.

## Przed uruchomieniem publicznym

- [ ] Bezpieczny backend wysyłki zapytań i zdjęć: limity, walidacja serwerowa, kontrola dostępu, przechowywanie i usuwanie plików, ochrona przed spamem, obsługa błędów i prawdziwe potwierdzenie przyjęcia. Nie zapisuj zdjęć klientów w GitHub.
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

Pełniejszy test w Chrome (istniejące środowisko projektu ma Selenium):

```powershell
.\.venv-tests\Scripts\python.exe wersja-2/tests/test_preview.py --browser
```

Na innym komputerze potrzebujesz Chrome, Pythona i Selenium (`python -m pip install selenium`). Test automatycznie uruchamia i zatrzymuje lokalny serwer. Sprawdza linki/zasoby/kotwice, H1 i alt, szerokości 1440/390/320 px, menu, pakiet, znaki specjalne w szkicu oraz miniatury i liczbę kopii. Nie wysyła wiadomości. Zrzuty trafiają do ignorowanego `tests/artifacts/`.

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
