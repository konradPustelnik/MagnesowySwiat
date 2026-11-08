'use strict';

const menu = document.querySelector('.menu-toggle');
const nav = document.querySelector('.main-nav');
function closeMenu() {
  menu.setAttribute('aria-expanded', 'false');
  menu.setAttribute('aria-label', 'Otwórz menu');
  nav.classList.remove('is-open');
  document.body.classList.remove('menu-open');
}
menu.addEventListener('click', () => {
  const open = menu.getAttribute('aria-expanded') !== 'true';
  menu.setAttribute('aria-expanded', String(open));
  menu.setAttribute('aria-label', open ? 'Zamknij menu' : 'Otwórz menu');
  nav.classList.toggle('is-open', open);
  document.body.classList.toggle('menu-open', open);
});
nav.addEventListener('click', event => { if (event.target.closest('a')) closeMenu(); });
document.addEventListener('keydown', event => { if (event.key === 'Escape') closeMenu(); });
window.matchMedia('(min-width: 981px)').addEventListener('change', closeMenu);
const normalizePath = path => path.replace(/index\.html$/, '').replace(/\/$/, '');
nav.querySelectorAll('a').forEach(link => {
  const url = new URL(link.href);
  if (!url.hash && !link.classList.contains('nav-cta') && normalizePath(url.pathname) === normalizePath(location.pathname)) {
    link.setAttribute('aria-current', 'page');
  }
});

document.querySelectorAll('[data-close]').forEach(button => {
  button.addEventListener('click', () => button.closest('dialog').close());
});
document.querySelectorAll('[data-info]').forEach(button => {
  button.addEventListener('click', () => {
    const info = {
      social: ['Nasze profile społecznościowe', 'Prawdziwe adresy profili Instagram i Facebook należy uzupełnić przed publikacją. Nie dodajemy zastępczych linków do cudzych kont.'],
      privacy: ['Polityka prywatności — do uzupełnienia', 'To wersja demonstracyjna, a nie gotowa polityka prywatności. Przed publikacją trzeba podać dane administratora, podstawy i cele przetwarzania, odbiorców danych, okresy przechowywania i prawa osób. Treść należy dostosować do wybranej integracji formularzy. Lokalny podgląd zdjęć nie wysyła plików. Fonty pobierane są z Google Fonts; przed publikacją rozważ ich lokalne hostowanie.'],
      terms: ['Regulamin — do uzupełnienia', 'Przed uruchomieniem zamówień potrzebny jest regulamin z prawdziwymi danymi usługodawcy, zasadami zawierania umów, płatności, dostawy i reklamacji oraz informacjami konsumenckimi odpowiednimi dla personalizowanych produktów. Formularz demonstracyjny nie przyjmuje zamówień ani płatności.']
    }[button.dataset.info];
    document.getElementById('info-title').textContent = info[0];
    document.getElementById('info-body').textContent = info[1];
    document.getElementById('info-dialog').showModal();
  });
});
document.querySelectorAll('[data-lightbox]').forEach(button => {
  button.addEventListener('click', () => {
    const img = document.getElementById('lightbox-image');
    img.src = button.dataset.lightbox;
    img.alt = button.dataset.caption;
    document.getElementById('lightbox-caption').textContent = button.dataset.caption;
    document.getElementById('lightbox').showModal();
  });
});
document.querySelectorAll('[data-package]').forEach(link => link.addEventListener('click', () => {
  document.getElementById('f-package').value = link.dataset.package;
}));
document.querySelectorAll('[data-quantity]').forEach(link => link.addEventListener('click', () => {
  document.getElementById('f-quantity').value = link.dataset.quantity;
}));
const date = document.getElementById('f-date');
if (date) {
  const now = new Date();
  date.min = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`;
}

// Zdjęcia przechowujemy tylko w pamięci tej karty. Brak fetch, uploadu i localStorage.
let photos = [];
const input = document.getElementById('photos');
const previews = document.getElementById('photo-previews');
const quantity = document.getElementById('f-quantity');
function updateQuantity() {
  if (quantity && photos.length) quantity.value = photos.reduce((sum, item) => sum + item.count, 0);
}
function renderPhotos() {
  previews.replaceChildren();
  photos.forEach((item, index) => {
    const card = document.createElement('div'); card.className = 'photo-preview';
    const image = document.createElement('img'); image.src = item.url; image.alt = `Lokalny podgląd: ${item.file.name}`;
    const name = document.createElement('p'); name.textContent = item.file.name;
    const label = document.createElement('label'); label.textContent = 'Liczba egzemplarzy';
    const count = document.createElement('input'); count.type = 'number'; count.min = '1'; count.max = '10000'; count.value = item.count; count.required = true;
    count.setAttribute('aria-label', `Liczba egzemplarzy zdjęcia ${index + 1}`);
    count.addEventListener('input', () => { item.count = Number(count.value) || 0; updateQuantity(); });
    label.append(count);
    const remove = document.createElement('button'); remove.type = 'button'; remove.className = 'remove-photo'; remove.textContent = 'Usuń zdjęcie';
    remove.addEventListener('click', () => {
      URL.revokeObjectURL(item.url); photos = photos.filter(photo => photo !== item); renderPhotos(); updateQuantity();
      if (!photos.length) quantity.value = '';
      input.focus();
    });
    card.append(image, name, label, remove); previews.append(card);
  });
}
if (input) {
  input.addEventListener('change', () => {
    const errors = [];
    for (const file of input.files) {
      if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type)) { errors.push(`${file.name}: wybierz JPEG, PNG lub WebP.`); continue; }
      if (file.size > 10 * 1024 * 1024) { errors.push(`${file.name}: przekroczono 10 MB.`); continue; }
      if (photos.length >= 20) { errors.push('Maksymalnie 20 zdjęć.'); break; }
      photos.push({ file, url: URL.createObjectURL(file), count: 1 });
    }
    input.value = '';
    document.getElementById('photo-status').textContent = errors.join(' ') || `Wybrano zdjęć: ${photos.length}. Nie zostały wysłane.`;
    renderPhotos(); updateQuantity();
  });
  window.addEventListener('pagehide', () => {
    photos.forEach(item => URL.revokeObjectURL(item.url)); photos = []; renderPhotos();
  });
}

document.querySelectorAll('form[data-inquiry]').forEach(form => {
  form.addEventListener('submit', event => {
    event.preventDefault();
    const status = form.querySelector('.form-status');
    if (form.dataset.inquiry === 'order') {
      if (!photos.length) { status.textContent = 'Dodaj przynajmniej jedno zdjęcie do lokalnego podglądu.'; input.focus(); return; }
      if (Number(quantity.value) !== photos.reduce((sum, item) => sum + item.count, 0)) {
        status.textContent = 'Liczba magnesów musi być równa sumie egzemplarzy przy zdjęciach.'; quantity.focus(); return;
      }
    }
    const lines = [form.dataset.inquiry === 'order' ? 'Zapytanie o magnesy ze zdjęć' : 'Zapytanie o dostępność terminu', ''];
    form.querySelectorAll('[name]').forEach(field => {
      if (field.name === 'consent') return;
      const label = form.querySelector(`label[for="${field.id}"]`);
      if (label && field.value.trim()) lines.push(`${label.textContent.replace(' *', '')}: ${field.value.trim()}`);
    });
    if (photos.length) lines.push('', 'Zdjęcia (załącz ręcznie w programie pocztowym):', ...photos.map((item, index) => `${index + 1}. ${item.file.name}: ${item.count} szt.`));
    const text = lines.join('\n');
    document.getElementById('draft-text').value = text;
    document.getElementById('email-draft').href = `mailto:magnesowyswiat@gmail.com?subject=${encodeURIComponent(lines[0])}&body=${encodeURIComponent(text)}`;
    document.getElementById('copy-status').textContent = '';
    status.textContent = 'Przygotowano lokalny podgląd. Zapytanie nie zostało wysłane.';
    document.getElementById('draft-dialog').showModal();
  });
});
document.getElementById('copy-draft').addEventListener('click', async () => {
  const draft = document.getElementById('draft-text');
  const status = document.getElementById('copy-status');
  try { await navigator.clipboard.writeText(draft.value); status.textContent = 'Skopiowano treść. Wiadomość nie została wysłana.'; }
  catch { draft.focus(); draft.select(); status.textContent = 'Treść zaznaczona — skopiuj ją skrótem Ctrl+C lub z menu urządzenia.'; }
});
