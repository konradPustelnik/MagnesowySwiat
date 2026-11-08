"""Shared, keyboard-accessible service disclosure navigation."""
import re
from html import escape

def add_live_dropdown(header):
    def replace(match):
        base=escape(match[1],quote=True)
        sections=[('oferta','Oferta'),('jak-dzialamy','Jak działamy'),('okazje','Okazje'),('galeria','Inspiracje'),('wyrozniki','Co nas wyróżnia'),('pakiety','Cennik'),('oferta-firmowa','Dla firm'),('faq','FAQ'),('rezerwacja','Zapytaj o termin')]
        links=f'<a href="{base}">Cała oferta na żywo</a>'+''.join(f'<a href="{base}#{id}">{label}</a>' for id,label in sections)
        return '<details class="nav-dropdown"><summary>Magnesy na żywo <span class="nav-chevron" aria-hidden="true"></span></summary><div class="nav-dropdown-links">'+links+'</div></details>'
    updated,count=re.subn(r'<a href="([^"]+)">\s*Magnesy na żywo\s*</a>',replace,header,count=1)
    if count!=1: raise ValueError('Live service navigation link not found')
    return updated
