"""Native multipart order inquiry using the same provider as reservations."""
import re

def enable_order_form(markup):
    markup=re.sub(r'<div class="preview-notice">.*?</div>', '', markup, count=1, flags=re.S)
    markup=markup.replace('<form data-inquiry="order">', '''<form data-inquiry="order" action="https://formsubmit.co/magnesowyswiat@gmail.com" method="POST" enctype="multipart/form-data" accept-charset="UTF-8">
<input type="hidden" name="_subject" value="[NA ZAMÓWIENIE] Zapytanie o magnesy ze zdjęć | Magnesowy Świat">
<input type="hidden" name="Rodzaj zapytania" value="Magnesy na zamówienie ze zdjęć">
<input type="hidden" name="_template" value="table">
<input type="hidden" name="_captcha" value="false">
<input type="hidden" name="_url" value="https://magnesowyswiat.pl/magnesy-na-zamowienie/">
<input type="hidden" name="_next" value="https://magnesowyswiat.pl/magnesy-na-zamowienie/?wyslano=1#zamowienie">
<input type="text" name="_honey" tabindex="-1" autocomplete="off" aria-hidden="true" style="display:none">
<div data-attachments hidden></div>
<input type="hidden" name="Zdjęcia i liczba kopii" id="photo-summary">''')
    markup=markup.replace('Pola oznaczone * są obowiązkowe. Nie wpisuj danych wrażliwych w wersji demonstracyjnej.', 'Pola oznaczone * są obowiązkowe. Wyślij zapytanie — cenę i szczegóły zamówienia potwierdzimy mailowo.')
    markup=markup.replace('JPEG, PNG lub WebP. Maksymalnie 20 zdjęć, każde do 10 MB. Podgląd działa wyłącznie w pamięci tej karty przeglądarki. Zdjęcia nie są wysyłane ani zapisywane na serwerze.', 'JPEG, PNG lub WebP. Maksymalnie 20 zdjęć, łącznie do 10 MB. Przy każdym zdjęciu podaj liczbę kopii. Pliki i dane zostaną przesłane przez FormSubmit na naszą pocztę dopiero po kliknięciu przycisku wysyłki.')
    markup=markup.replace('Rozumiem, że to lokalny podgląd i zapytanie nie zostanie wysłane.', 'Wyrażam zgodę na kontakt w sprawie zapytania oraz przesłanie podanych danych i wybranych zdjęć przez FormSubmit w celu jego obsługi.')
    markup=markup.replace('required name="consent"','required name="consent" value="Tak"')
    markup=markup.replace('Ten formularz demonstracyjny nie składa zamówienia.', 'Wysłanie zapytania nie jest jeszcze potwierdzeniem zamówienia.')
    for name,label in [('name','Imię i nazwisko'),('phone','Numer telefonu'),('quantity','Liczba magnesów'),('caption','Napis lub data'),('delivery','Sposób dostawy'),('address','Dane do dostawy'),('message','Uwagi do zamówienia')]:
        markup=markup.replace(f'name="{name}"',f'name="{label}"')
    markup=markup.replace('Włącz JavaScript, aby korzystać z podglądu zdjęć i zapytań.', 'Włącz JavaScript, aby wybrać zdjęcia i wysłać zapytanie z załącznikami. Bez niego skontaktuj się z nami e-mailem.')
    return markup
