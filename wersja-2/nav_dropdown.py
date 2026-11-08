"""Shared, keyboard-accessible service disclosure navigation."""
import re
from html import escape

def add_live_dropdown(header):
    def replace(match):
        base=escape(match[1],quote=True)
        sections=[('oferta','Oferta'),('jak-dzialamy','Jak działamy'),('okazje','Okazje'),('galeria','Inspiracje'),('wyrozniki','Co nas wyróżnia'),('pakiety','Cennik'),('oferta-firmowa','Dla firm'),('faq','FAQ'),('rezerwacja','Zapytaj o termin')]
        links=f'<a href="{base}">Cała oferta na żywo</a>'+''.join(f'<a href="{base}#{id}">{label}</a>' for id,label in sections)
        return '<details class="nav-dropdown" data-service="live"><summary>Magnesy na żywo <span class="nav-chevron" aria-hidden="true"></span></summary><div class="nav-dropdown-links">'+links+'</div></details>'
    updated,count=re.subn(r'<a href="([^"]+)">\s*Magnesy na żywo\s*</a>',replace,header,count=1)
    if count!=1: raise ValueError('Live service navigation link not found')
    return updated

def add_order_dropdown(header):
    def replace(match):
        base=escape(match[1],quote=True)
        sections=[('jak-zamowic','Jak zamówić'),('produkt','Magnesy ze zdjęć'),('cennik','Cennik'),('zamowienie','Zamów magnesy'),('pomysly','Pomysły na magnesy'),('dostawa','Pakowanie i dostawa'),('faq','FAQ'),('kontakt','Kontakt')]
        links=f'<a href="{base}">Cała oferta na zamówienie</a>'+''.join(f'<a href="{base}#{id}">{label}</a>' for id,label in sections)
        return '<details class="nav-dropdown" data-service="order"><summary>Magnesy na zamówienie <span class="nav-chevron" aria-hidden="true"></span></summary><div class="nav-dropdown-links">'+links+'</div></details>'
    updated,count=re.subn(r'<a href="([^"]+)">\s*Magnesy na zamówienie\s*</a>',replace,header,count=1)
    if count!=1: raise ValueError('Photo order navigation link not found')
    return updated

def add_order_anchors(markup):
    ids=iter(['oferta','jak-zamowic','produkt','cennik','zamowienie','pomysly','dostawa','faq','kontakt'])
    def replace(match):
        attrs=re.sub(r'\s+id=(?:"[^"]*"|\S+)','',match[1])
        return f'<section id="{next(ids)}"{attrs}>'
    updated,count=re.subn(r'<section\b([^>]*)>',replace,markup)
    if count!=9: raise ValueError('Unexpected photo-order section count')
    return updated
