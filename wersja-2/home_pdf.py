"""Apply the owner's PDF copy to the home page without changing shared elements."""

import re


HERO = '''<div class="wrap hero-grid">
<div class="hero-copy">
<h1>Wyjątkowe magnesy <em>na każdą okazję</em></h1>
<p class="hero-locations">Limanowa · Nowy Sącz · Kraków</p>
<p class="hero-lead"><strong>✨ Mały magnes. Wielkie wspomnienia.</strong></p>
<p>Są chwile, które zasługują na coś więcej niż miejsce w galerii telefonu! 🤍</p>
<p>W <strong>Magnesowym Świecie</strong> zamieniamy wyjątkowe momenty w niepowtarzalne magnesy ze zdjęciami, które przywołują uśmiech każdego dnia.</p>
<p>📸 <strong>Tworzymy magnesy na żywo</strong> podczas wesel, urodzin i innych wydarzeń, a także <strong>realizujemy indywidualne zamówienia z Twoich ulubionych zdjęć!</strong></p>
<p>Bo najpiękniejsze wspomnienia warto mieć zawsze blisko siebie. ✨</p>
<div class="actions"><a class="button" href="magnesy-na-zywo.html">Magnesy na żywo</a><a class="button button--outline" href="magnesy-na-zamowienie.html">Magnesy na zamówienie</a></div>
</div>
<figure class="hero-image"><img src="images/pdf-wspomnienia.jpg" alt="Fotomagnesy ze zdjęciami bliskich — wizualizacja oferty" loading="eager" width="1627" height="916" decoding="async"><figcaption class="photo-note">Wizualizacja oferty.</figcaption></figure>
</div>'''


OFFERS = '''<div class="wrap">
<div class="section-heading"><p class="eyebrow">Dwie możliwości. Te same emocje.</p><h2>Wybierz swój sposób na zatrzymanie wspomnień</h2><p>Tworzymy wyjątkowe magnesy ze zdjęć — na żywo podczas uroczystości oraz na indywidualne zamówienie. Z Limanowej docieramy do Waszych najpiękniejszych chwil w całej Małopolsce! 🤍</p></div>
<div class="offers-grid">
<article class="offer"><a class="offer-photo" href="magnesy-na-zywo.html" aria-label="Poznaj ofertę magnesów na żywo"><img src="images/pdf-na-zywo.jpg" alt="Fotografowanie gości i wykonywanie magnesów podczas wydarzenia — wizualizacja oferty" loading="lazy" width="1164" height="1164" decoding="async"></a><div class="offer-content"><span class="offer-index">01</span><h3>Magnesy na żywo</h3><p>W Magnesowym Świecie fotografujemy uczestników wesel, urodzin i innych uroczystości, a następnie na miejscu zamieniamy zdjęcia w personalizowane magnesy.</p><p>To nie tylko oryginalna atrakcja, ale również wyjątkowa pamiątka, którą goście mogą zabrać do domu jeszcze podczas wydarzenia!</p><a class="button button--outline" href="magnesy-na-zywo.html">Poznaj ofertę na żywo</a></div></article>
<article class="offer"><a class="offer-photo" href="magnesy-na-zamowienie.html" aria-label="Poznaj ofertę magnesów na zamówienie"><img src="images/pdf-na-zamowienie.jpg" alt="Personalizowane magnesy z ulubionych fotografii — wizualizacja oferty" loading="lazy" width="1179" height="1179" decoding="async"></a><div class="offer-content"><span class="offer-index">02</span><h3>Magnesy na zamówienie</h3><p>Masz ulubione zdjęcia? Zamień je w wyjątkowe magnesy! Prześlij nam swoje fotografie, a my przygotujemy dla Ciebie piękne pamiątki i wyślemy je pod wskazany adres.</p><a class="button button--outline" href="magnesy-na-zamowienie.html">Poznaj ofertę na zamówienie</a></div></article>
</div><p class="photo-note">Wizualizacje oferty.</p></div>'''


ABOUT_COPY = '''<div class="editorial-copy"><p class="eyebrow">O nas</p><h2>Poznaj Magnesowy Świat</h2>
<p>Magnesowy Świat powstał z pomysłu, by zatrzymywać piękne chwile w formie, do której można wracać każdego dnia.</p>
<p>Wierzymy, że najcenniejsze pamiątki nie muszą być duże ani kosztowne. Czasem wystarczy jedno zdjęcie, żeby przypomnieć sobie atmosferę wyjątkowego dnia, wspólny śmiech czy spotkanie z bliskimi.</p>
<p>Dlatego tworzymy personalizowane magnesy fotograficzne, które łączą w sobie fotografię, emocje i odrobinę dobrej zabawy.</p>
<p>Chcemy, aby każdy magnes był czymś więcej niż upominkiem — małą pamiątką z wielką historią.</p>
<p><strong>Magnesowy Świat — magnesy na każdą okazję.</strong></p>
<img class="signature" src="images/logo-header.png" alt="Magnesowy Świat" width="720" height="182" loading="lazy"></div>'''


AREA = '''<div class="wrap"><div class="area"><div><p class="eyebrow">Gdzie się spotkamy?</p><h2>Z Limanowej.<br>Do Twoich wspomnień.</h2></div><div><p>Naszą bazą jest Limanowa. Obsługujemy wydarzenia na terenie Małopolski, a dalsze wyjazdy ustalamy indywidualnie.</p><p><strong>Dojazd do 30 km od Limanowej jest wliczony w cenę każdego pakietu na żywo.</strong> W przypadku dalszych lokalizacji koszt transportu ustalamy indywidualnie, w zależności od odległości, przed rezerwacją.</p><p>Magnesy wykonywane na zamówienie wysyłamy na terenie całej Polski.</p></div></div></div>'''


def _replace_section(markup, marker, replacement):
    matches = [
        match for match in re.finditer(r'<section\b[^>]*>.*?</section>', markup, re.S)
        if marker(match[0])
    ]
    if len(matches) != 1:
        raise ValueError(f'Expected one home page section, found {len(matches)}')
    match = matches[0]
    opening = re.match(r'<section\b[^>]*>', match[0])[0]
    return markup[:match.start()] + opening + replacement + '</section>' + markup[match.end():]


def apply_home_pdf(markup):
    """Update only home-page sections; preserve IDs, navigation and contact actions."""
    markup = _replace_section(markup, lambda section: 'hero--home' in section, HERO)
    markup = _replace_section(markup, lambda section: 'class="offers-grid"' in section, OFFERS)

    about = [
        match for match in re.finditer(r'<section\b[^>]*>.*?</section>', markup, re.S)
        if re.search(r'\bid=(?:"o-nas"|\'o-nas\'|o-nas)(?=[\s>])', match[0])
    ]
    if len(about) != 1:
        raise ValueError(f'Expected one home about section, found {len(about)}')
    current = about[0]
    updated, count = re.subn(
        r'<div class="editorial-copy">.*?</div>',
        lambda match: ABOUT_COPY,
        current[0],
        count=1,
        flags=re.S,
    )
    if count != 1:
        raise ValueError('Home about copy not found')
    markup = markup[:current.start()] + updated + markup[current.end():]
    return _replace_section(markup, lambda section: 'class="area"' in section, AREA)
