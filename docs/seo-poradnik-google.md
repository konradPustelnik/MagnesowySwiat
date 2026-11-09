# Kontrola zgodności z poradnikiem Google — 9 listopada 2026

Źródło: [SEO — przewodnik Google dla początkujących](https://developers.google.com/search/docs/fundamentals/seo-starter-guide?hl=pl).

## Zakres bez zmiany wyglądu

- Zachowano unikalne tytuły i opisy trzech stron, własne canonical, czytelne adresy, linki HTML i pojedyncze H1. robots.txt dopuszcza roboty i zasoby. Sitemap zawiera tylko trzy produkcyjne adresy.
- Dodano `BreadcrumbList` do obu ofert: strona główna → konkretna oferta, zgodnie z istniejącymi linkami. Nie dodawano widocznego menu okruszkowego. Zachowano `WebSite` na głównej.
- Poprawiono trzy opisy `alt` w galerii zamówień, tak aby opisywały rzeczywistą zawartość zdjęć, zamiast przypisywać im nieobecne sceny wakacyjne lub spotkania z przyjaciółmi.
- Główne zdjęcie każdej strony ma `fetchpriority="high"`; zdjęcia poniżej pozostają ładowane leniwie. Wygląd, pliki obrazów, kadrowanie, CSS, marketingowe teksty i funkcje nie zostały zmienione.

Test SEO sprawdza teraz także poprawność JSON i adresów w BreadcrumbList. Porównanie HTML z poprzednim commitem potwierdza identyczność części od `<body>` po pominięciu atrybutów `alt` i `fetchpriority`.

## Dalsze działania właściciela

W Search Console zgłoś `https://magnesowyswiat.pl/sitemap.xml`, sprawdź trzy adresy produkcyjne i renderowanie strony, następnie obserwuj indeksowanie i zapytania. Nie wykonano operacji w Search Console, bo nie ma podłączonego dostępu do konta.

Treści i widoczne podpisy zdjęć wymagają osobnej oceny redakcyjnej: w galerii zamówień część podpisów nie odpowiada zdjęciom i są miejsca do uzupełnienia. Nie zmieniano ich w tym zadaniu ze względu na wymóg zachowania wyglądu. Zdjęcia poglądowe nie stanowią dowodu realizacji firmy.

Optymalizacja nie gwarantuje pozycji ani dodatkowych linków Google. Ocena efektów wymaga czasu i danych Search Console. Nie dodawano sztucznych opinii, ukrytych słów kluczowych ani niepotwierdzonych danych firmy.
