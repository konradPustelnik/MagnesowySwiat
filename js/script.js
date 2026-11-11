'use strict';
if (document.body.classList.contains('page-live')) {
  const header = document.querySelector('.site-header');
  const updateLiveHeaderHeight = () => {
    document.documentElement.style.setProperty('--live-header-height', `${Math.ceil(header.getBoundingClientRect().height)}px`);
  };
  updateLiveHeaderHeight();
  new ResizeObserver(updateLiveHeaderHeight).observe(header);
}

// Keep old index.html bookmarks working while showing the directory URL.
if (['http:', 'https:'].includes(location.protocol) && location.pathname.endsWith('/index.html')) {
  history.replaceState(history.state, '', location.pathname.slice(0, -10) + location.search + location.hash);
}

const menu = document.querySelector('.menu-toggle');
const nav = document.querySelector('.main-nav');
const serviceDropdowns = [...document.querySelectorAll('.nav-dropdown')];
function closeMenu() {
  menu.setAttribute('aria-expanded', 'false');
  menu.setAttribute('aria-label', 'Otwórz menu');
  nav.classList.remove('is-open');
  document.body.classList.remove('menu-open');
  serviceDropdowns.forEach(dropdown => { dropdown.open = false; });
}
menu.addEventListener('click', () => {
  const open = menu.getAttribute('aria-expanded') !== 'true';
  menu.setAttribute('aria-expanded', String(open));
  menu.setAttribute('aria-label', open ? 'Zamknij menu' : 'Otwórz menu');
  nav.classList.toggle('is-open', open);
  document.body.classList.toggle('menu-open', open);
});
nav.addEventListener('click', event => { if (event.target.closest('a')) closeMenu(); });
document.addEventListener('keydown', event => {
  if (event.key !== 'Escape') return;
  const openDropdown = serviceDropdowns.find(dropdown => dropdown.open);
  const mobileMenuOpen = menu.getAttribute('aria-expanded') === 'true';
  closeMenu();
  if (mobileMenuOpen) menu.focus();
  else if (openDropdown) openDropdown.querySelector('summary').focus();
});
serviceDropdowns.forEach(dropdown => {
  dropdown.addEventListener('toggle', () => {
    if (dropdown.open) serviceDropdowns.forEach(other => { if (other !== dropdown) other.open = false; });
  });
  dropdown.addEventListener('pointerenter', event => {
    if (event.pointerType === 'mouse' && window.innerWidth > 980) dropdown.open = true;
  });
  dropdown.addEventListener('pointerleave', () => {
    if (window.innerWidth > 980 && !dropdown.matches(':focus-within')) dropdown.open = false;
  });
});
document.addEventListener('click', event => {
  if (!event.target.closest('.nav-dropdown')) serviceDropdowns.forEach(dropdown => { dropdown.open = false; });
});
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
document.querySelectorAll('[data-event]').forEach(link => link.addEventListener('click', () => {
  const eventField = document.getElementById('f-event');
  eventField.value = link.dataset.event;
  eventField.dispatchEvent(new Event('change', { bubbles: true }));
}));
let discountPercent = 0;
const discountInput = document.getElementById('f-discount-code');
if (discountInput) {
  const form = discountInput.closest('form');
  const discountValue = document.createElement('input');
  discountValue.type = 'hidden'; discountValue.name = 'Rabat (%)'; discountValue.value = '0';
  form.append(discountValue);
  let discountNoticeTimer;
  let lastNotifiedCode = '';
  const applyDiscount = () => {
    const code = discountInput.value.trim().toLowerCase();
    const match = (window.MAGNET_DISCOUNTS || []).find(item =>
      typeof item.code === 'string' && item.code.trim().toLowerCase() === code &&
      Number.isFinite(item.percent) && item.percent > 0 && item.percent <= 100);
    discountPercent = match ? match.percent : 0;
    discountValue.value = String(discountPercent);
    const help = document.getElementById('discount-code-help');
    if (help) help.hidden = Boolean(code);
    document.getElementById('discount-status').textContent = match
      ? `Kod ${match.code.trim().toUpperCase()} jest aktywny — ${discountPercent}% rabatu na magnesy.`
      : code ? 'Kod rabatowy jest nieprawidłowy lub nieaktywny.' : '';
    document.dispatchEvent(new Event('magnet-discount-change'));
    return match;
  };
  const showDiscountNotice = () => {
    applyDiscount();
    document.getElementById('info-title').textContent = discountPercent ? `Rabat ${discountPercent}%` : 'Kod rabatowy';
    document.getElementById('info-body').textContent = document.getElementById('discount-status').textContent || 'Wpisz kod rabatowy.';
    const dialog = document.getElementById('info-dialog');
    if (!dialog.open) dialog.showModal();
    if (discountPercent) lastNotifiedCode = discountInput.value.trim().toLowerCase();
  };
  discountInput.addEventListener('input', () => {
    clearTimeout(discountNoticeTimer);
    const match = applyDiscount();
    if (!match) lastNotifiedCode = '';
    if (match && discountInput.value.trim().toLowerCase() !== lastNotifiedCode) {
      discountNoticeTimer = setTimeout(showDiscountNotice, 300);
    }
  });
  document.getElementById('apply-discount')?.addEventListener('click', showDiscountNotice);
  form.addEventListener('submit', () => { clearTimeout(discountNoticeTimer); applyDiscount(); });
  document.querySelectorAll('[data-launch-code]').forEach(button => {
    button.addEventListener('click', () => {
      discountInput.value = button.dataset.launchCode;
      clearTimeout(discountNoticeTimer);
      showDiscountNotice();
    });
  });
  form.addEventListener('reset', () => { clearTimeout(discountNoticeTimer); lastNotifiedCode = ''; setTimeout(applyDiscount, 0); });
  applyDiscount();
}
const magnetSlider = document.getElementById('magnet-quantity');
if (magnetSlider) {
  const bulkQuantity = document.getElementById('magnet-bulk-quantity');
  const formatPrice = value => new Intl.NumberFormat('pl-PL', {minimumFractionDigits: 2, maximumFractionDigits: 2}).format(value) + ' zł';
  const updateMagnetPrice = () => {
    const bulk = Number(magnetSlider.value) === 201;
    document.getElementById('magnet-bulk-field').hidden = !bulk;
    bulkQuantity.disabled = !bulk;
    bulkQuantity.required = bulk;
    const valid = !bulk || bulkQuantity.checkValidity();
    const count = bulk ? Number(bulkQuantity.value) : Number(magnetSlider.value);
    const unitPriceGrosze = bulk ? 1000 : 1200 - Math.ceil((count - 10) / 10) * 10;
    const discountedUnitGrosze = Math.round(unitPriceGrosze * (100 - discountPercent) / 100);
    const unitPrice = discountedUnitGrosze / 100;
    document.getElementById('magnet-count').value = bulk ? '200+' : count;
    document.getElementById('magnet-unit-price').textContent = formatPrice(unitPrice);
    document.getElementById('magnet-total-price').textContent = valid ? formatPrice(count * discountedUnitGrosze / 100) : '—';
    document.getElementById('magnet-discount-note').textContent = discountPercent ? `Cena po rabacie ${discountPercent}%.` : '';
    const order = document.getElementById('magnet-order');
    order.dataset.quantity = valid ? count : '';
    order.textContent = valid ? `Zamów ${count} magnesów` : 'Podaj liczbę magnesów';
    magnetSlider.setAttribute('aria-valuetext', bulk ? 'Powyżej 200 magnesów — podaj konkretną liczbę' : `${count} magnesów, ${unitPrice} zł za sztukę`);
  };
  magnetSlider.addEventListener('input', updateMagnetPrice);
  bulkQuantity.addEventListener('input', updateMagnetPrice);
  document.addEventListener('magnet-discount-change', updateMagnetPrice);
  updateMagnetPrice();
}
document.querySelectorAll('[data-quantity]').forEach(link => link.addEventListener('click', event => {
  if (!link.dataset.quantity) {
    event.preventDefault();
    const bulkQuantity = document.getElementById('magnet-bulk-quantity');
    bulkQuantity.focus(); bulkQuantity.reportValidity();
    return;
  }
  document.getElementById('f-quantity').value = link.dataset.quantity;
}));
const date = document.getElementById('f-date');
if (date) {
  const picker = document.getElementById('date-picker');
  const button = document.getElementById('date-picker-button');
  const now = new Date();
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const pad = value => String(value).padStart(2, '0');
  function validateDate() {
    date.setCustomValidity('');
    if (!date.value) { picker.value = ''; return; }
    const parts = /^(\d{2})\/(\d{2})\/(\d{4})$/.exec(date.value);
    if (!parts) { date.setCustomValidity('Wpisz datę w formacie dd/mm/rrrr.'); picker.value = ''; return; }
    const [, day, month, year] = parts.map(Number);
    const chosen = new Date(year, month - 1, day);
    if (chosen.getFullYear() !== year || chosen.getMonth() !== month - 1 || chosen.getDate() !== day) {
      date.setCustomValidity('Podaj poprawną datę wydarzenia.'); picker.value = ''; return;
    }
    if (chosen < today) { date.setCustomValidity('Data wydarzenia nie może być z przeszłości.'); picker.value = ''; return; }
    picker.value = `${year}-${pad(month)}-${pad(day)}`;
  }
  date.addEventListener('input', () => {
    const digits = date.value.replace(/\D/g, '').slice(0, 8);
    date.value = digits.slice(0, 2) + (digits.length > 2 ? '/' + digits.slice(2, 4) : '') + (digits.length > 4 ? '/' + digits.slice(4) : '');
    validateDate();
  });
  date.addEventListener('change', validateDate);
  picker.addEventListener('change', () => {
    if (!picker.value) return;
    const [year, month, day] = picker.value.split('-');
    date.value = `${day}/${month}/${year}`;
    validateDate();
  });
  validateDate();
  if (typeof createPolishDatePicker === 'function') createPolishDatePicker(date, picker, button, today);
}

const postalCode = document.getElementById('f-postal-code');
if (postalCode) {
  postalCode.addEventListener('input', () => {
    const digits = postalCode.value.replace(/\D/g, '').slice(0, 5);
    postalCode.value = digits.slice(0, 2) + (digits.length > 2 ? '-' + digits.slice(2) : '');
  });
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
