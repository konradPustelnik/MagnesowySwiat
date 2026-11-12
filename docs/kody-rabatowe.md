# Kody rabatowe — osobno dla każdej oferty

Każda oferta ładuje wyłącznie własny plik konfiguracji. Kod z jednej listy nie działa w drugiej ofercie.

## Magnesy na żywo

Edytuj `js/discounts-live.js`, listę `window.MAGNET_DISCOUNTS_LIVE`.
Aktywny wpis: `{ code: 'NA-START', percent: 20 }`.
Kod daje 20% wyłącznie na magnesy na żywo, bez dojazdu. Karty pakietów pokazują ceny bazowe; kod i procent są przekazywane w zapytaniu.

## Magnesy na zamówienie

Edytuj `js/discounts-order.js`, listę `window.MAGNET_DISCOUNTS_ORDER`.
Aktywny kod to `{ code: 'DOSTAWA', type: 'shipping' }`. Zapewnia darmową dostawę na terenie Polski; nie zmienia ceny magnesów.
`NA-START` nie działa dla zamówień. Nowe kody dodawaj wyłącznie do tej listy.

## Edycja i działanie

Każdy wpis zawiera `code` (nazwę) oraz albo `percent` (procent większy od 0, maksymalnie 100), albo `type: 'shipping'` (darmowa dostawa, wyłącznie dla zamówień). Wielkość liter i skrajne spacje nie mają znaczenia. Pusta lista wyłącza kody dla danej oferty. Rabaty nie sumują się.

Po edycji zmień parametr `?v=` przy odpowiednim pliku konfiguracji w HTML danej oferty. Opublikuj zmianę przez commit i push do `origin/main`.

Wpisanie poprawnego kodu automatycznie otwiera okienko i pokazuje potwierdzenie pod polem. Błędny lub pusty kod usuwa poprzedni rabat. Kod oraz `Rabat (%)` trafiają do formularza; kod `DOSTAWA` przekazuje dodatkowo `Darmowa dostawa: Tak`. Kalkulator zaokrągla procentowo obniżoną cenę jednostkową do groszy i mnoży ją przez liczbę sztuk.

Konfiguracje są publiczne, bo strona jest statyczna. Przed potwierdzeniem realizacji sprawdź kod i procent z zapytania według listy odpowiedniej oferty. Mechanizm nie weryfikuje liczby użyć kodów ani limitu pierwszych trzech zleceń — dostępność promocji potwierdza właściciel.
