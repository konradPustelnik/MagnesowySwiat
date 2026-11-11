# Kody rabatowe — osobno dla każdej oferty

Każda oferta ładuje wyłącznie własny plik konfiguracji. Kod z jednej listy nie działa w drugiej ofercie.

## Magnesy na żywo

Edytuj `js/discounts-live.js`, listę `window.MAGNET_DISCOUNTS_LIVE`.
Aktywny wpis: `{ code: 'NA-START', percent: 20 }`.
Kod daje 20% wyłącznie na magnesy na żywo, bez dojazdu. Karty pakietów pokazują ceny bazowe; kod i procent są przekazywane w zapytaniu.

## Magnesy na zamówienie

Edytuj `js/discounts-order.js`, listę `window.MAGNET_DISCOUNTS_ORDER`.
Obecnie lista jest pusta: `[]`. Nie ma aktywnych kodów dla zamówień. `NA-START` jest odrzucany i nie zmienia ceny.
Nowe kody dodawaj wyłącznie do tej listy. Aktywny kod zamówień przelicza kalkulator magnesów, bez rabatu na dostawę.

## Edycja i działanie

Każdy wpis zawiera `code` (nazwę) i `percent` (procent większy od 0, maksymalnie 100). Wielkość liter i skrajne spacje nie mają znaczenia. Pusta lista wyłącza kody dla danej oferty. Rabaty nie sumują się.

Po edycji zmień parametr `?v=` przy odpowiednim pliku konfiguracji w HTML danej oferty. Opublikuj zmianę przez commit i push do `origin/main`.

Wpisanie poprawnego kodu automatycznie otwiera okienko i pokazuje potwierdzenie pod polem. Błędny lub pusty kod usuwa poprzedni rabat. Kod oraz `Rabat (%)` trafiają do formularza. Kalkulator zaokrągla cenę jednostkową po rabacie do groszy i mnoży ją przez liczbę sztuk.

Konfiguracje są publiczne, bo strona jest statyczna. Przed potwierdzeniem realizacji sprawdź kod i procent z zapytania według listy odpowiedniej oferty. Mechanizm nie weryfikuje liczby użyć kodów ani limitu pierwszych trzech zleceń — dostępność promocji potwierdza właściciel.
