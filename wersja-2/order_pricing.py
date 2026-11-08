"""Quantity choices; retail prices await the owner's cost-based confirmation."""

def order_pricing():
    packages = [(5, 'Kilka ulubionych kadrów'), (20, 'Wspomnienia dla bliskich'),
                (50, 'Pamiątki na wspólną okazję'), (100, 'Większe zamówienie')]
    cards = ''.join(
        f'<article class="quantity-card"><h3><strong>{n}</strong> magnesów</h3>'
        f'<p>{description}</p><a class="button button--outline" data-quantity="{n}" '
        f'href="#zamowienie">Wyceń {n} sztuk</a></article>'
        for n, description in packages)
    return ('<div class="quantity-grid">' + cards + '</div>'
            '<article class="quantity-bulk"><div><h3>100+ magnesów</h3>'
            '<p>Potrzebujesz więcej niż 100 sztuk? Przygotujemy wycenę dopasowaną do liczby magnesów i projektu.</p>'
            '</div><a class="button" data-quantity="101" href="#zamowienie">Zapytaj o większą ilość</a></article>')
