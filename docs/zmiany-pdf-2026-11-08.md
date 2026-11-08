# Wdrożenie MAGNESY-NA-ŻYWO.pdf

Źródło: dziesięciostronicowy PDF przekazany przez właściciela. Dokument wykorzystano jako materiał do zmian strony; notatek redakcyjnych, separatorów ani pól zastępczych nie opublikowano jako treści dla klientów.

## Wprowadzone zmiany

- Strona główna: treść otwarcia i miasta Limanowa, Nowy Sącz, Kraków; zachowano jedno H1 „Wyjątkowe magnesy na każdą okazję”, miasta są osobną mniejszą linią. Z dwóch alternatywnych zakończeń wybrano „Bo najpiękniejsze wspomnienia warto mieć zawsze blisko siebie”.
- Trzy ilustracje wyodrębniono bezpośrednio ze stron 1–3 PDF jako JPEG, po około 150–171 KB. Pokazują ofertę, a nie potwierdzone realizacje, dlatego mają podpisy „Wizualizacja oferty”. Oryginalny PDF nie jest publikowany w repozytorium.
- Karty dwóch usług zawierają opisy i przyciski prowadzące na właściwe podstrony.
- Na żywo: trzy kroki, cztery duże karty okazji (dwie kolumny na komputerze, jedna na telefonie), inne okazje, rozbudowane korzyści oraz zachowany format 6,35 × 6,35 cm.
- Pakiety: opisy i przyciski zgodne z PDF; ceny 1190/1490/2390/3290 zł, limity 100/150/250/350 sztuk i czas 3/4/5/6 godzin pozostają bez zmian. Zachowano ustaloną wcześniej promocję 20% na pierwsze trzy zlecenia.
- Dodano dojazd do 30 km od Limanowej w cenie każdego pakietu na żywo; dla dalszych lokalizacji transport wyceniany indywidualnie. Informacja jest spójna na stronie głównej, w pakietach i FAQ.
- Dodatkowy magnes poza limitem pakietu kosztuje 10 zł/szt.; dostępność techniczną i liczbę dodatkowych sztuk potwierdzamy indywidualnie. Nie zmienia to wyceny produktów na zamówienie.
- Dodano kontakt w sprawie pakietu indywidualnego, pełniejsze teksty dla firm i „O nas”, dziesięć pytań FAQ oraz opis zapytania o rezerwację.
- Galeria inspiracji na żywo i link „Inspiracje” w menu na wszystkich stronach zostały usunięte. Produktowe zdjęcia na podstronie zamówień pozostają dostępne.
- Formularz, polski kalendarz, wysyłka przez FormSubmit, rozróżnienie tematów wiadomości, zgoda oraz okno po powrocie z wysyłki zachowują dotychczasowy mechanizm. Zapytanie nie oznacza automatycznej rezerwacji.
- Nie uzupełniano telefonu zmyślonym numerem: PDF zawiera tylko pole zastępcze. Kontakt prowadzi do rzeczywistego e-maila i profili podanych wcześniej przez właściciela.

## Utrzymanie

`wersja-2/home_pdf.py` oraz `wersja-2/live_pdf.py` zawierają nowe treści. `build_preview.py` nakłada je na istniejący szablon; dla podstrony na żywo kolejność to `apply_live_pdf(arrange_live_sections(live))`. Funkcję nakładającą zmiany należy wywołać raz, ponieważ usuwa poprzednią galerię i zastępuje sekcje.

Generator nadal zapisuje wyłącznie podgląd `wersja-2/`. Zmieniając produkcję, przenosić odpowiedni `<main>` z dostosowaniem ścieżek; zachować produkcyjne canonical, indeksowanie i adresy katalogowe. Aktualizacje menu dotyczą również `nav_dropdown.py`. Archiwum `backup/` pozostaje nietknięte.

## Weryfikacja

Sprawdzono lokalne linki, kotwice i zasoby wersji produkcyjnej i podglądu. Selenium obejmuje wybór pakietu, specjalne znaki i lokalny odbiór danych formularzy, zdjęcia z liczbą kopii, kalendarz, menu, powrót po wysyłce oraz nowe sekcje w szerokościach 1440/390/320 px. Zdjęcia okazji mają proporcje 16:9 i kadrowanie bez rozciągania. Lokalny test formularzy nie jest dowodem dostarczenia wiadomości do skrzynki Gmail.
