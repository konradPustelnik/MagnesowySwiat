# Zmiana kodów rabatowych

Edytuj wyłącznie listę w `js/discounts.js`, np.:

```js
window.MAGNET_DISCOUNTS = [
  { code: 'NA-START', percent: 10 },
  { code: 'WIOSNA', percent: 15 }
];
```

`code` to nazwa kodu, `percent` to liczba procentów większa od 0 i nie większa niż 100. Wielkość liter oraz spacje na początku i końcu nie mają znaczenia. Każdy kod powinien występować raz. Aby wyłączyć promocje, ustaw pustą listę `[]`. Aby wyłączyć pojedynczy kod, usuń jego wpis. Rabaty nie sumują się.

Po edycji zmień parametr `?v=` przy `js/discounts.js` w obu podstronach ofert na nową, unikalną wartość, np. datę i godzinę. Opublikuj pliki przez commit i push do `origin/main`. Zmiana obowiązuje po wdrożeniu i ponownym otwarciu strony.

W obu formularzach klient może sprawdzić kod przyciskiem i zobaczyć okienko z rabatem. Zmiana wpisanego kodu aktualizuje rabat od razu, także usuwa poprzedni rabat, gdy nowy kod jest błędny lub pusty. Kod oraz `Rabat (%)` trafiają do zapytania. Kalkulator zamówień przelicza cenę jednostkową z zaokrągleniem do groszy i mnoży ją przez liczbę magnesów. Cennik bazowy pozostaje bez zmian; rabat promocyjny może obniżyć końcową cenę poniżej bazowego minimum. Dostawa i dojazd nie są objęte rabatem. Na żywo procent dotyczy wyceny magnesów, bez automatycznej zmiany kart pakietów.

To statyczna strona: konfiguracja kodów jest publiczna, a formularz nie stanowi serwerowej autoryzacji rabatu. Przed potwierdzeniem zamówienia sprawdź kod i procent z zapytania względem aktualnej konfiguracji. Mechanizm nie obsługuje tajnych ani jednorazowych kodów i limitów użyć.
