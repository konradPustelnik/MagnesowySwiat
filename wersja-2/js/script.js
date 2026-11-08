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
const current = location.pathname.split('/').pop() || 'index.html';
nav.querySelectorAll('a').forEach(link => {
  if (link.getAttribute('href') === current) link.setAttribute('aria-current', 'page');
});

document.querySelectorAll('[data-close]').forEach(button => {
  button.addEventListener('click', () => button.closest('dialog').close());
});
document.querySelectorAll('[data-info]').forEach(button => {
  button.addEventListener('click', () => {
    const info = {
      social: ['Nasze profile społecznościowe', 'Prawdziwe adresy profili Instagram i Facebook należy uzupełnić przed publikacją. Nie dodajemy zastępczych linków do cudzych kont.'],
      privacy: ['Polityka prywatności — do uzupełnienia', 'To wersja demonstracyjna, a nie gotowa polityka prywatności. Przed publikacją trzeba podać dane administratora, podstawy i cele przetwarzania, odbiorców danych, okresy przechowywania i prawa osób. Treść należy dostosować do wybranej integracji formularzy. Zapytania o termin są przesyłane do FormSubmit i na skrzynkę magnesowyswiat@gmail.com. Formularz zamówienia przesyła wybrane zdjęcia i dane do FormSubmit dopiero po kliknięciu przycisku wysyłki i wyrażeniu zgody. Fonty pobierane są z Google Fonts; przed publikacją rozważ ich lokalne hostowanie.'],
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

// Preview files stay in this tab until the user submits the multipart form.
const MAX_PHOTO_BYTES = 10_000_000;
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
      if (file.size + photos.reduce((sum, item) => sum + item.file.size, 0) > MAX_PHOTO_BYTES) {
        errors.push(`${file.name}: łączny rozmiar zdjęć nie może przekraczać 10 MB. Usuń część zdjęć lub wybierz mniejsze pliki.`); continue;
      }
      if (photos.length >= 20) { errors.push('Maksymalnie 20 zdjęć.'); break; }
      photos.push({ file, url: URL.createObjectURL(file), count: 1 });
    }
    input.value = '';
    document.getElementById('photo-status').textContent = errors.join(' ') || `Wybrano zdjęć: ${photos.length}. Łączny rozmiar: ${(photos.reduce((sum, item) => sum + item.file.size, 0) / 1_000_000).toFixed(2)} MB z 10 MB.`;
    renderPhotos(); updateQuantity();
  });
  window.addEventListener('pagehide', () => {
    photos.forEach(item => URL.revokeObjectURL(item.url)); photos = []; renderPhotos();
    document.querySelector('[data-attachments]')?.replaceChildren();
  });
}

function showSendConfirmation() {
  const clean = new URL(location.href);
  clean.searchParams.delete('wyslano');
  history.replaceState(history.state, '', clean.pathname + clean.search + clean.hash);
  const dialog = document.createElement('dialog');
  dialog.className = 'send-confirmation';
  dialog.setAttribute('aria-labelledby', 'send-confirmation-title');
  dialog.setAttribute('aria-describedby', 'send-confirmation-description');
  dialog.innerHTML = '<div class="confirmation-mark" aria-hidden="true">✓</div><h2 id="send-confirmation-title">Dziękujemy za kontakt!</h2><p id="send-confirmation-description">Rezerwację terminu lub przyjęcie zamówienia potwierdzimy osobno.</p><p>Powrót na stronę główną za <strong id="send-countdown">5</strong> s.</p><button class="button" type="button" autofocus>Wróć teraz</button>';
  document.body.append(dialog);
  let seconds = 5;
  const goHome = () => {
    window.clearInterval(timer);
    location.replace(document.querySelector('.brand').href);
  };
  const timer = window.setInterval(() => {
    seconds -= 1;
    dialog.querySelector('#send-countdown').textContent = seconds;
    if (seconds <= 0) goHome();
  }, 1000);
  dialog.querySelector('button').addEventListener('click', goHome);
  dialog.addEventListener('cancel', event => { event.preventDefault(); goHome(); });
  window.addEventListener('pagehide', () => window.clearInterval(timer), { once: true });
  dialog.showModal();
}

const liveForm = document.querySelector('form[data-inquiry="live"]');
if (liveForm) {
  liveForm.addEventListener('submit', () => {
    liveForm.setAttribute('aria-busy', 'true');
    liveForm.querySelector('.form-status').textContent = 'Przechodzenie do wysyłki…';
    liveForm.querySelector('[type="submit"]').textContent = 'Przechodzenie do wysyłki…';
  });
  window.addEventListener('pageshow', () => {
    liveForm.removeAttribute('aria-busy');
    liveForm.querySelector('[type="submit"]').textContent = 'ZAPYTAJ O DOSTĘPNOŚĆ TERMINU';
  });
  if (new URLSearchParams(location.search).get('wyslano') === '1') {
    liveForm.querySelector('.form-status').textContent = 'Dziękujemy za kontakt. Rezerwację terminu potwierdzimy indywidualnie.';
    showSendConfirmation();
  }
}

document.querySelectorAll('form[data-inquiry="order"]').forEach(form => {
  form.addEventListener('submit', event => {
    const status = form.querySelector('.form-status');
    if (!photos.length) {
      event.preventDefault(); status.textContent = 'Dodaj przynajmniej jedno zdjęcie.'; input.focus(); return;
    }
    if (Number(quantity.value) !== photos.reduce((sum, item) => sum + item.count, 0)) {
      event.preventDefault(); status.textContent = 'Liczba magnesów musi być równa sumie egzemplarzy przy zdjęciach.'; quantity.focus(); return;
    }
    if (photos.reduce((sum, item) => sum + item.file.size, 0) > MAX_PHOTO_BYTES) {
      event.preventDefault(); status.textContent = 'Łączny rozmiar zdjęć nie może przekraczać 10 MB.'; input.focus(); return;
    }
    const attachments = form.querySelector('[data-attachments]');
    attachments.replaceChildren();
    try {
      photos.forEach((item, index) => {
        const transfer = new DataTransfer(); transfer.items.add(item.file);
        const fileInput = document.createElement('input');
        fileInput.type = 'file'; fileInput.name = index === 0 ? 'attachment' : `attachment${index + 1}`;
        fileInput.files = transfer.files;
        attachments.append(fileInput);
      });
    } catch {
      event.preventDefault(); attachments.replaceChildren();
      status.textContent = 'Nie udało się dołączyć zdjęć. Spróbuj w aktualnej przeglądarce lub napisz na magnesowyswiat@gmail.com.'; return;
    }
    document.getElementById('photo-summary').value = photos.map((item, index) => `${index + 1}. ${item.file.name}: ${item.count} szt.`).join('\n');
    form.setAttribute('aria-busy', 'true');
    status.textContent = 'Przechodzenie do wysyłki zapytania i zdjęć…';
    form.querySelector('[type="submit"]').textContent = 'Przechodzenie do wysyłki…';
  });
  window.addEventListener('pageshow', () => {
    form.removeAttribute('aria-busy');
    form.querySelector('[type="submit"]').textContent = 'WYŚLIJ ZAPYTANIE O ZAMÓWIENIE';
  });
  if (new URLSearchParams(location.search).get('wyslano') === '1') {
    form.querySelector('.form-status').textContent = 'Dziękujemy za kontakt. Cenę i szczegóły zamówienia potwierdzimy mailowo.';
    showSendConfirmation();
  }
});
