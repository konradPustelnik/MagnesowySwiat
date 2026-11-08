"""Live-service copy approved in MAGNESY-NA-ŻYWO.pdf, November 2026."""
import re
from html import escape


ABOUT = '''<p>Magnesowy Świat powstał z pomysłu, by zatrzymywać piękne chwile w formie, do której można wracać każdego dnia.</p><p>Wierzymy, że najcenniejsze pamiątki nie muszą być duże ani kosztowne. Czasem wystarczy jedno zdjęcie, żeby przypomnieć sobie atmosferę wyjątkowego dnia, wspólny śmiech czy spotkanie z bliskimi.</p><p>Dlatego tworzymy personalizowane magnesy fotograficzne, które łączą w sobie fotografię, emocje i odrobinę dobrej zabawy.</p><p>Chcemy, aby każdy magnes był czymś więcej niż upominkiem — małą pamiątką z wielką historią.</p><p><strong>Magnesowy Świat — magnesy na każdą okazję.</strong></p>'''

FAQ = [
    ('Czy magnesy powstają podczas uroczystości?', 'Tak! Zdjęcia wykonujemy podczas wydarzenia, a magnesy produkujemy na miejscu. Goście mogą odebrać je jeszcze w trakcie uroczystości.'),
    ('Ile magnesów otrzymamy?', 'Liczba magnesów zależy od wybranego pakietu. Oferujemy pakiety do 100, 150, 250 i 350 sztuk. Podane ilości są maksymalnymi limitami.'),
    ('Czy każdy gość może otrzymać magnes?', 'Zależy to od liczby gości, wybranego pakietu i liczby wykonanych fotografii. Pomożemy dopasować liczbę magnesów do charakteru wydarzenia.'),
    ('Czy możemy spersonalizować magnesy?', 'Tak, projekt może uwzględniać np. imiona, datę uroczystości, nazwę wydarzenia lub odpowiedni motyw graficzny. Szczegóły ustalimy przed realizacją.'),
    ('Czy potrzebujecie specjalnego miejsca?', 'Potrzebujemy stabilnego miejsca na stanowisko do produkcji magnesów oraz dostępu do zasilania elektrycznego. Szczegółowe wymagania ustalamy przed uroczystością.'),
    ('Czy dojeżdżacie do innych miejscowości?', 'Tak! Dojazd do 30 km od Limanowej jest wliczony w cenę każdego pakietu na żywo. Dla dalszych lokalizacji koszt transportu ustalamy indywidualnie na podstawie odległości, przed rezerwacją.'),
    ('Czy mogę zamówić dodatkowe magnesy?', 'Tak, w miarę możliwości technicznych i dostępności materiałów możemy zwiększyć liczbę magnesów poza limit pakietu. Cena dodatkowego magnesu wynosi 10 zł/szt. Liczbę dodatkowych sztuk potwierdzamy indywidualnie.'),
    ('Czy można wybrać własny pakiet?', 'Oczywiście! Jeśli żaden z gotowych pakietów nie odpowiada Twoim potrzebom, skontaktuj się z nami. Przygotujemy indywidualną propozycję, również przy innej liczbie magnesów lub dłuższym czasie obsługi.'),
    ('Jakiej wielkości są magnesy?', 'Nasze magnesy mają kwadratowy format 6,35 × 6,35 cm i zaokrąglone rogi.'),
    ('Jak zarezerwować termin?', 'Wystarczy wypełnić formularz kontaktowy i podać datę, miejsce oraz rodzaj wydarzenia. Sprawdzimy dostępność i przedstawimy ofertę. Szczegóły rezerwacji i płatności potwierdzimy w umowie. Przesłanie zapytania nie oznacza automatycznej rezerwacji terminu.'),
]


def section(id, label, title, body, soft=False):
    return f'<section id="{id}" class="section{" section--soft" if soft else ""}"><div class="wrap"><div class="section-heading"><p class="eyebrow">{label}</p><h2>{title}</h2></div>{body}</div></section>'


def apply_live_pdf(markup):
    hero = re.search(r'<section class="hero hero--service">.*?</section>', markup, re.S).group()
    hero = hero.replace('images/wesele.jpg', 'images/pdf-na-zywo.jpg').replace('Para ślubna z bukietem — inspiracja', 'Stanowisko z fotomagnesami podczas wesela — wizualizacja oferty').replace('width="1000" height="750"', 'width="1164" height="1164"').replace('Fotografia inspiracyjna. Nie przedstawia realizacji Magnesowego Świata.', 'Wizualizacja oferty.')
    markup = re.sub(r'<section class="hero hero--service">.*?</section>', lambda _: hero, markup, count=1, flags=re.S)

    def replace(id, content):
        nonlocal markup
        markup, count = re.subn(r'<section\b[^>]*\bid=(?:"' + re.escape(id) + r'"|' + re.escape(id) + r'(?=[\s>]))[^>]*>.*?</section>', lambda _: content, markup, count=1, flags=re.S)
        if count != 1:
            raise ValueError(f'Expected one live section: {id}')

    steps = [
        ('Przyjeżdżamy do Ciebie', 'Pojawiamy się na uroczystości, rozstawiamy stanowisko i przygotowujemy sprzęt.'),
        ('Fotografujemy i tworzymy', 'Robimy zdjęcia gościom, drukujemy fotografie i wykonujemy magnesy. Wszystko odbywa się na żywo, podczas trwania uroczystości!'),
        ('Goście odbierają gotowe pamiątki', 'Gotowe magnesy trafiają do gości jeszcze podczas wydarzenia.'),
    ]
    process = '<div class="live-process-grid">' + ''.join(f'<article class="process-step"><span class="number">{i:02}.</span><h3>{title}</h3><p>{text}</p></article>' for i, (title, text) in enumerate(steps, 1)) + '</div><p class="live-closing">Jedno zdjęcie. Jeden magnes. Tysiące uśmiechów.</p>'
    replace('jak-dzialamy', section('jak-dzialamy', 'Jak działamy?', 'Od spotkania do pamiątki', process))

    occasions = [
        ('Wesela i przyjęcia ślubne', 'wesele', 'Podaruj gościom coś więcej niż tradycyjny upominek.', 'Magnesy fotograficzne wykonywane na żywo to nie tylko oryginalna atrakcja weselna, ale przede wszystkim osobista pamiątka.', 'Wspólne zdjęcie z rodziną, zabawna fotografia z przyjaciółmi czy romantyczny kadr we dwoje — każdy znajdzie coś dla siebie.'),
        ('Urodziny i osiemnastki', 'urodziny', 'Uśmiechy, wspólne zdjęcia i niezapomniane chwile!', 'Magnesy świetnie sprawdzają się podczas osiemnastek, trzydziestek, czterdziestek i każdych kolejnych urodzin.', 'Bo najlepsze prezenty to często te, które przypominają nam o ludziach i wspólnie spędzonym czasie.'),
        ('Jubileusze i rocznice', 'jubileusz', 'Wyjątkowe historie zasługują na wyjątkowe pamiątki.', 'Rocznica ślubu, jubileusz rodzinny czy ważna uroczystość — personalizowane magnesy pomagają zachować atmosferę tych spotkań na dłużej.', ''),
        ('Eventy firmowe', 'event', 'Zadbaj o atrakcję, którą uczestnicy zapamiętają.', 'Magnesy ze zdjęciami sprawdzą się podczas imprez integracyjnych, jubileuszy firmowych, konferencji, pikników i wydarzeń promocyjnych.', 'Istnieje możliwość dopasowania projektu magnesu do charakteru wydarzenia oraz identyfikacji wizualnej marki.'),
    ]
    cards = '<p class="live-intro">Magnesowy Świat to atrakcja, która sprawdzi się wszędzie tam, gdzie spotykają się ludzie, emocje i wyjątkowe chwile.</p><div class="occasion-grid live-occasions">'
    for title, image, lead, text, ending in occasions:
        cards += f'<article class="occasion-card"><img src="images/{image}.jpg" alt="{escape(title)} — fotografia inspiracyjna" loading="lazy" width="1000" height="750" decoding="async"><div class="occasion-card-content"><h3>{title}</h3><p><strong>{lead}</strong></p><p>{text}</p>{f"<p>{ending}</p>" if ending else ""}</div></article>'
    cards += '</div><div class="other-occasions"><h3>Inne wyjątkowe okazje</h3><p>Chrzty, komunie, studniówki, bale, spotkania rodzinne i imprezy tematyczne.</p><p>Ty tworzysz okazję. My pomagamy zatrzymać wspomnienia.</p></div><p class="section-note">Fotografie powyżej są inspiracyjne.</p>'
    replace('okazje', section('okazje', 'Na jakie okazje?', 'Każda okazja jest dobra, żeby zatrzymać wspomnienia.', cards, True))
    replace('galeria', '')

    features = [
        ('Wyjątkowa pamiątka', 'Każdy magnes to osobista historia zamknięta w jednym zdjęciu.'),
        ('Pamiątka od razu', 'Magnesy powstają podczas uroczystości, dzięki czemu goście mogą zabrać je ze sobą jeszcze tego samego dnia.'),
        ('Atrakcja dla gości', 'Fotografowanie i obserwowanie, jak zdjęcie zmienia się w magnes, to dodatkowy element zabawy podczas wydarzenia.'),
        ('Na każdą okazję', 'Wesele, urodziny, wakacje, jubileusz czy po prostu ulubiona fotografia — nie potrzeba wielkiego wydarzenia, żeby zatrzymać piękne wspomnienia.'),
        ('Idealny pomysł na prezent', 'Magnesy ze zdjęciami to drobny, ale niezwykle osobisty upominek dla bliskich. Bo najpiękniejsze chwile zasługują na to, by zostać z nami na dłużej.'),
        ('Personalizacja', 'Magnesy możemy dopasować do charakteru uroczystości — m.in. poprzez dodanie imion, daty czy odpowiedniego motywu graficznego.'),
        ('Pamiątka na lata', 'Magnes trafia na lodówkę lub tablicę magnetyczną i przypomina o wydarzeniu dużo częściej niż zdjęcie zapomniane w telefonie.'),
        ('Format 6,35 × 6,35 cm', 'Więcej miejsca na Wasze wspomnienia — około 61% większa powierzchnia niż w formacie 5 × 5 cm.'),
    ]
    benefits = '<p class="live-intro">To nie tylko świetna atrakcja, ale także osobista pamiątka, która znajdzie swoje miejsce na lodówce i będzie przywoływać wspomnienia przez długi czas. Ty tworzysz wyjątkowe chwile. My pomagamy zatrzymać je na dłużej.</p><div class="live-benefits">' + ''.join(f'<article class="benefit"><span class="eyebrow" aria-hidden="true">{i:02}</span><h3>{title}</h3><p>{text}</p></article>' for i, (title, text) in enumerate(features, 1)) + '</div>'
    replace('wyrozniki', section('wyrozniki', 'Co nas wyróżnia?', 'Dlaczego warto wybrać magnesy fotograficzne?', benefits))

    # Keep confirmed package limits, selection controls and the existing launch promotion.
    pricing = re.search(r'<section\b[^>]*\bid="pakiety"[^>]*>.*?</section>', markup, re.S).group()
    pricing = pricing.replace('<h2>Nasze pakiety</h2>', '<h2>Nasze pakiety</h2><p>Wybierz pakiet dopasowany do Twojej uroczystości. Każde wydarzenie jest inne, dlatego przygotowaliśmy cztery pakiety różniące się liczbą magnesów oraz czasem obsługi.</p>')
    descriptions = {
        'Kameralne spotkania i małe wydarzenia.': 'Idealny na kameralne uroczystości, rodzinne przyjęcia i urodziny w gronie najbliższych.',
        'Mniejsze wesela i rodzinne uroczystości.': 'Doskonały wybór na mniejsze wesela, jubileusze i przyjęcia rodzinne.',
        'Większe wesela i więcej wspólnych kadrów.': 'Więcej zdjęć, więcej emocji i jeszcze więcej wspomnień. Pakiet idealny na wesela i większe uroczystości.',
        'Duże wydarzenia i rozbudowana obsługa.': 'Rozbudowana oferta dla dużych przyjęć, wesel i wydarzeń, podczas których chcecie podarować gościom jeszcze więcej wyjątkowych pamiątek.',
        'Magnesy o wymiarach około 6,35 × 6,35 cm.': 'Magnesy o wymiarach 6,35 × 6,35 cm.',
        'Podane liczby magnesów są maksymalnymi limitami. Czas i zakres usługi potwierdzamy przed zawarciem umowy. Dojazd i ewentualne rozszerzenia wyceniamy indywidualnie.': 'Podane ilości oznaczają maksymalną liczbę magnesów w danym pakiecie. Czas, zakres usługi i szczegóły realizacji potwierdzamy przed zawarciem umowy. Dojazd do 30 km od Limanowej jest w cenie; dalszy transport ustalamy indywidualnie przed rezerwacją.',
    }
    for old, new in descriptions.items():
        pricing = pricing.replace(old, new)
    pricing = re.sub(r'(data-package="([^"]+)" href="#rezerwacja">)Zapytaj o pakiet', lambda m: m[1] + 'Zapytaj o pakiet ' + m[2].upper(), pricing)
    extras = '''<div class="live-package-extras"><article><h3>Zasady dojazdu</h3><p>Działamy z Limanowej, ale chętnie dojeżdżamy również do innych miejscowości!</p><p><strong>Dojazd do 30 km od Limanowej jest wliczony w cenę każdego pakietu.</strong> W przypadku dalszych lokalizacji koszt transportu ustalamy indywidualnie, w zależności od odległości.</p></article><article><h3>Dodatkowe magnesy</h3><p>Chcesz podarować swoim gościom jeszcze więcej wyjątkowych wspomnień? Istnieje możliwość zamówienia dodatkowych magnesów poza limitem wybranego pakietu.</p><p><strong>Cena dodatkowego magnesu: 10 zł/szt.</strong> Dostępność dodatkowych sztuk potwierdzimy indywidualnie.</p></article></div><aside class="live-custom-offer"><div><h3>Potrzebujesz czegoś innego?</h3><p>Organizujesz większe wydarzenie? Chcesz zamówić inną liczbę magnesów lub wydłużyć czas obsługi? Przygotujemy ofertę dopasowaną do Twoich potrzeb.</p></div><a class="button" data-package="Pomóżcie mi wybrać" href="#rezerwacja">Zapytaj o indywidualną wycenę</a></aside>'''
    pricing = pricing.rsplit('</div></section>', 1)[0] + extras + '</div></section>'
    replace('pakiety', pricing)

    business = '''<div class="live-business"><figure><img src="images/event.jpg" alt="Sala przygotowana na wydarzenie firmowe — fotografia inspiracyjna" width="1000" height="750" loading="lazy" decoding="async"><figcaption class="photo-note">Fotografia inspiracyjna, nie nasza realizacja.</figcaption></figure><div><p>Szukasz oryginalnej atrakcji na wydarzenie firmowe, która jednocześnie pozostawi uczestnikom trwałą pamiątkę?</p><p>Magnesy fotograficzne tworzone podczas eventu to sposób na połączenie dobrej zabawy z indywidualnym akcentem Twojej marki.</p><p>Możemy przygotować projekt magnesu dopasowany do kolorystyki firmy, z logo, nazwą wydarzenia lub wybranym motywem graficznym.</p><p>Nasza usługa sprawdzi się podczas:</p><ul><li>imprez integracyjnych,</li><li>jubileuszy przedsiębiorstw,</li><li>konferencji i targów,</li><li>pikników firmowych,</li><li>wydarzeń promocyjnych,</li><li>świątecznych spotkań pracowniczych.</li></ul><p><strong>Zadbaj o to, żeby uczestnicy zabrali z Twojego wydarzenia coś, co wywoła uśmiech również następnego dnia.</strong></p><div class="actions"><a class="button" data-package="Pomóżcie mi wybrać" href="#rezerwacja">Poproś o ofertę dla firmy</a></div></div></div>'''
    replace('oferta-firmowa', section('oferta-firmowa', 'Dla firm', 'Twoja marka. Ich wspomnienia.', business, True))
    replace('o-nas', section('o-nas', 'O nas', 'Poznaj Magnesowy Świat', '<div class="live-intro">' + ABOUT + '</div>'))
    replace('faq', section('faq', 'Najczęściej zadawane pytania', 'Dobrze wiedzieć', '<div class="faq">' + ''.join(f'<details><summary>{q}</summary><p>{a}</p></details>' for q, a in FAQ) + '</div>'))

    form = re.search(r'<section\b[^>]*\bid=(?:"rezerwacja"|rezerwacja(?=[\s>]))[^>]*>.*?</section>', markup, re.S).group()
    intro = '''<div class="form-intro"><p class="eyebrow">Kontakt</p><h2>Zatrzymajmy razem Wasze najpiękniejsze chwile!</h2><p>Planujesz wesele, urodziny, jubileusz lub wydarzenie firmowe? Napisz do nas, a pomożemy Ci wybrać pakiet idealnie dopasowany do Twojej uroczystości.</p><p>Opowiedz nam o swoim wydarzeniu, a my zajmiemy się magnesową częścią wspomnień!</p><p><strong>Przesłanie zapytania nie oznacza automatycznej rezerwacji terminu.</strong></p><p>Możesz również skontaktować się z nami bezpośrednio:</p><ul class="live-contact-links"><li><a class="text-link" href="mailto:magnesowyswiat@gmail.com">magnesowyswiat@gmail.com</a></li><li><a class="text-link" href="https://www.instagram.com/magnesowyswiat/" target="_blank" rel="noopener noreferrer">instagram.com/magnesowyswiat</a></li><li><a class="text-link" href="https://www.facebook.com/profile.php?id=61595989786052" target="_blank" rel="noopener noreferrer">Facebook — Magnesowy Świat</a></li></ul><p>Czekamy na Twoją wiadomość!</p></div>'''
    form = re.sub(r'<div class="form-intro">.*?</div>', lambda _: intro, form, count=1, flags=re.S)
    form = form.replace('<label for="f-city">Miejscowość *', '<label for="f-city">Miejscowość / miejsce wydarzenia *')
    replace('rezerwacja', form)
    return markup
