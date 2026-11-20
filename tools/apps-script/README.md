# Potwierdzenia zgłoszeń z formularzy

Skrypt odpowiada na nowe zgłoszenia FormSubmit, które wpłynęły do firmowego Gmaila po aktywacji. Sprawdza skrzynkę co pięć minut. Używa adresu `Reply-To` i wysyła stały tekst bez danych zgłoszenia oraz załączników.

## Konfiguracja i próba

1. Na koncie `magnesowyswiat@gmail.com` utwórz projekt w [Google Apps Script](https://script.google.com/). Wklej `Autoresponder.gs` do edytora kodu. W ustawieniach projektu pokaż plik manifestu i wklej `appsscript.json`.
2. Wyślij po jednym zgłoszeniu z każdej oferty z tym samym własnym adresem kontrolnym. W zamówieniu użyj sztucznego obrazu. W Gmailu otwórz obie wiadomości i użyj opcji **Pokaż oryginał**. Potwierdź, że oba mają ten sam adres w `From`, wynik DMARC `pass` z tą samą domeną `header.from` w nagłówku `Authentication-Results: mx.google.com` i kontrolny adres w `Reply-To`.
3. Wpisz do skryptu dokładny adres nadawcy, domenę i adres kontrolny w polach `FORMSUBMIT_SENDER`, `FORMSUBMIT_DMARC_DOMAIN` i `TEST_RECIPIENT`. Uruchom `preview` i zatwierdź dostęp. W logu powinny pojawić się obie oferty, `live` i `order`. Podgląd nie wysyła poczty.
4. Uruchom `testReply`, aby wysłać potwierdzenie wyłącznie na kontrolny adres, i sprawdź odbiór. Następnie uruchom `install`. Dodaje harmonogram co pięć minut. Wyślij po jednym nowym zgłoszeniu kontrolnym i sprawdź odbiór oraz to, czy następny cykl nie wysyła kopii. Zgłoszenia zebrane przed aktywacją pozostają poza harmonogramem.

Jeśli podgląd nie rozpoznaje jednej z ofert, sprawdź nagłówki na firmowym koncie przed uruchomieniem harmonogramu. Skrypt kończy konfigurację bez aktywacji, jeśli nie znajdzie obu zgłoszeń kontrolnych.

## Obsługa

Po wysłaniu potwierdzenia zgłoszenie dostaje etykietę `MS-Autoodpowiedz-Obsluzone`. Jeśli próba została przerwana lub wynik jest niejasny, etykieta `MS-Autoodpowiedz-DoSprawdzenia` zatrzymuje kolejne automatyczne próby. W takim przypadku przed ręczną odpowiedzią sprawdź folder Wysłane. Aby zatrzymać automatyzację, usuń wyzwalacz `sendConfirmations` w sekcji Wyzwalacze projektu Apps Script.

[Usługa Gmail w Apps Script](https://developers.google.com/apps-script/advanced/gmail) · [Limity Google](https://developers.google.com/apps-script/guides/services/quotas)
