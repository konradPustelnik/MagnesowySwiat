"""Static live-service page layout, following the original section order."""
import re
from html import escape

LAUNCH_PROMO_ACTIVE = True

LAUNCH_OFFER = '''<aside class="launch-offer" aria-label="Promocja na pierwsze zlecenia"><strong class="launch-discount">−20%</strong><div><p class="eyebrow">Na dobry początek</p><p class="launch-title">20% zniżki dla pierwszych 3 zleceń</p><p class="launch-description">Na magnesy na żywo. Dostępność rabatu potwierdzimy przy rezerwacji.</p><a class="text-link" href="#rezerwacja">Zapytaj o promocję →</a></div></aside>'''

def add_launch_offer(pricing):
    if not LAUNCH_PROMO_ACTIVE:
        return pricing
    return re.sub(r'(<div class="section-heading">.*?</div>)',lambda match:'<div class="pricing-intro">'+match[1]+LAUNCH_OFFER+'</div>',pricing,count=1,flags=re.S)

def section(id, eyebrow, title, content, soft=False):
    return f'<section id="{id}" class="section {"section--soft" if soft else ""}"><div class="wrap"><div class="section-heading"><p class="eyebrow">{eyebrow}</p><h2>{title}</h2></div>{content}</div></section>'

def arrange_live_sections(markup, image_prefix='images/', home='index.html'):
    sections=re.findall(r'<section\b.*?</section>',markup,re.S)
    def find(text):
        matches=[block for block in sections if text in block]
        if len(matches)!=1: raise ValueError(f'Expected one section: {text}')
        return matches[0]
    def identify(block,id):
        return re.sub(r'<section\b([^>]*)>',lambda match:f'<section id="{id}"'+re.sub(r'\s+id=(?:"[^"]*"|\S+)','',match[1])+'>',block,count=1)
    hero=find('hero--service')
    process=identify(find('Od spotkania do pamiątki'),'jak-dzialamy')
    occasions=identify(find('occasion-grid'),'okazje')
    pricing=identify(find('pricing-grid'),'pakiety').replace('Wybierz pakiet dla siebie','Nasze pakiety')
    pricing=add_launch_offer(pricing)
    faq=identify(find('class="faq"'),'faq')
    form=find('data-inquiry="live"')
    offer=section('oferta','Magnesy na Twoim wydarzeniu','Zdjęcia, emocje i pamiątki na miejscu.', '''<p class="live-intro">Fotografujemy gości i podczas uroczystości zamieniamy zdjęcia w personalizowane magnesy. Przyjeżdżamy ze sprzętem i materiałami, a uczestnicy zabierają gotowe pamiątki ze sobą.</p><div class="live-offer-grid"><article><h3>Obsługa na żywo</h3><p>Wesela, urodziny, jubileusze i wydarzenia firmowe — wspólnie dopasujemy zakres do okazji.</p></article><article><h3>Magnesy 6,35 × 6,35 cm</h3><p>Kwadratowe fotomagnesy z miejscem na ulubiony kadr i indywidualną personalizację.</p></article><article><h3>Pakiet dla Ciebie</h3><p>Wybierz liczbę magnesów i czas obsługi. Szczegóły i koszt dojazdu potwierdzimy przed umową.</p></article></div><div class="actions"><a class="button" href="#pakiety">Zobacz cennik i pakiety</a><a class="button button--outline" href="#rezerwacja">Zapytaj o termin</a></div>''')
    photos=[]
    for filename,alt in [('magnesy-rodzinne','Lodówka z magnesami fotograficznymi'),('wspomnienia','Zdjęcia i pamiątki na lodówce'),('kolekcja-zdjec','Kolekcja fotograficznych wspomnień')]:
        src=escape(image_prefix+filename+'.jpg',quote=True)
        photos.append(f'<figure><button class="gallery-photo" type="button" data-lightbox="{src}" data-caption="{alt} — fotografia inspiracyjna" aria-label="Powiększ: {alt}"><img src="{src}" alt="{alt} — fotografia inspiracyjna" width="1000" height="750" loading="lazy" decoding="async"></button></figure>')
    gallery=section('galeria','Małe rzeczy, wielkie emocje','Fotomagnesy — zobacz inspiracje','<p class="live-intro">Każdy magnes opowiada inną historię — od romantycznych kadrów po spontaniczne zdjęcia z przyjaciółmi.</p><div class="gallery">'+''.join(photos)+'</div><p class="section-note">Zdjęcia ilustracyjne z <a class="text-link" href="https://unsplash.com/@squared_one1" target="_blank" rel="noopener noreferrer">Unsplash (Kristyna Squared.one)</a>, nie nasze realizacje. Mogą przedstawiać inne formaty; nasze magnesy mają 6,35 × 6,35 cm.</p>',True)
    features=[('Większy format: 6,35 × 6,35 cm','To około 61% większa powierzchnia niż w formacie 5 × 5 cm — więcej miejsca na Wasze wspomnienia.'),('Pamiątka od razu','Magnesy powstają podczas uroczystości, więc goście zabierają je ze sobą jeszcze tego samego dnia.'),('Coś naprawdę osobistego','Każdy magnes przedstawia wyjątkowy moment i osoby, które są dla Was ważne.'),('Atrakcja dla gości','Wspólne fotografowanie i obserwowanie powstawania pamiątek staje się częścią wydarzenia.'),('Personalizacja','Imiona, data uroczystości lub motyw wydarzenia nadają magnesom indywidualny charakter.'),('Wspomnienia na co dzień','Ulubione zdjęcia mogą towarzyszyć gościom również po zakończeniu spotkania.')]
    benefits=section('wyrozniki','Co nas wyróżnia?','Co zyskują Twoi goście?','<div class="live-benefits">'+''.join(f'<article class="benefit"><span class="eyebrow" aria-hidden="true">{i:02}</span><h3>{title}</h3><p>{text}</p></article>' for i,(title,text) in enumerate(features,1))+'</div>')
    business=section('oferta-firmowa','Również dla biznesu','Twoja marka. Ich wspomnienia.',f'''<div class="live-business"><figure><img src="{image_prefix}event.jpg" alt="Sala przygotowana na wydarzenie firmowe — fotografia inspiracyjna" width="1000" height="750" loading="lazy" decoding="async"><figcaption class="photo-note">Fotografia inspiracyjna, nie nasza realizacja.</figcaption></figure><div><p>Magnesy fotograficzne tworzone podczas eventu łączą wspólne zdjęcia z indywidualnym akcentem Twojej marki.</p><ul><li>Imprezy integracyjne i jubileusze przedsiębiorstw.</li><li>Konferencje, targi i wydarzenia promocyjne.</li><li>Pikniki firmowe i spotkania pracownicze.</li><li>Projekt z logo, nazwą wydarzenia lub dopasowanym motywem.</li></ul><p>Możliwości personalizacji, zakres obsługi i wycenę ustalimy indywidualnie.</p><div class="actions"><a class="button" data-package="Pomóżcie mi wybrać" href="#rezerwacja">Zapytaj o ofertę dla firmy</a></div></div></div>''',True)
    about=section('o-nas','Poznaj Magnesowy Świat','Małe pamiątki, wielkie historie.',f'<div class="live-intro"><p>Tworzymy magnesy fotograficzne, które pozwalają wracać do ważnych chwil każdego dnia. Podczas wydarzeń dbamy o zdjęcia i przygotowanie pamiątek, aby goście mogli cieszyć się spotkaniem.</p><p>Naszą bazą jest Limanowa. Obsługujemy Małopolskę; dalsze wyjazdy i opłatę za dojazd ustalamy indywidualnie.</p><a class="text-link" href="{home}#o-nas">Więcej o Magnesowym Świecie</a></div>')
    return hero+offer+process+occasions+gallery+benefits+pricing+business+about+faq+form
