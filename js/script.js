'use strict';
if (document.body.classList.contains('page-live')) {
  const header = document.querySelector('.site-header');
  const updateLiveHeaderHeight = () => {
    document.documentElement.style.setProperty('--live-header-height', `${Math.ceil(header.getBoundingClientRect().height)}px`);
  };
  updateLiveHeaderHeight();
  new ResizeObserver(updateLiveHeaderHeight).observe(header);
}
if (document.body.classList.contains('page-order')) {
  const header = document.querySelector('.site-header');
  const updateOrderHeaderHeight = () => {
    document.documentElement.style.setProperty('--order-header-height', `${Math.ceil(header.getBoundingClientRect().height)}px`);
  };
  updateOrderHeaderHeight();
  new ResizeObserver(updateOrderHeaderHeight).observe(header);
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
      privacy: ['Polityka prywatności — do uzupełnienia', 'To wersja demonstracyjna, a nie gotowa polityka prywatności. Przed publikacją trzeba podać dane administratora, podstawy i cele przetwarzania, odbiorców danych, okresy przechowywania i prawa osób. Treść należy dostosować do wybranej integracji formularzy. Zapytania o termin są przesyłane do FormSubmit i na skrzynkę magnesowyswiat@gmail.com. Formularz zamówienia przesyła wybrane zdjęcia i dane do FormSubmit dopiero po kliknięciu przycisku wysyłki. Fonty pobierane są z Google Fonts; przed publikacją rozważ ich lokalne hostowanie.'],
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
const createCenteredSelect = select => {
  const field = select.closest('.field');
  const label = field.querySelector(`label[for="${select.id}"]`);
  const options = [...select.options];
  const control = document.createElement('button');
  const list = document.createElement('div');
  const controlId = `${select.id}-control`;
  let activeIndex = Math.max(select.selectedIndex, 0);
  label.id = `${controlId}-label`;
  field.classList.add('field--custom-select');
  select.classList.add('native-select-hidden');
  select.tabIndex = -1;
  select.setAttribute('aria-hidden', 'true');
  label.htmlFor = controlId;
  control.type = 'button';
  control.id = controlId;
  control.className = 'custom-select-trigger';
  control.setAttribute('role', 'combobox');
  control.setAttribute('aria-haspopup', 'listbox');
  control.setAttribute('aria-expanded', 'false');
  control.setAttribute('aria-labelledby', label.id);
  list.className = 'custom-select-options';
  list.id = `${controlId}-options`;
  list.setAttribute('role', 'listbox');
  list.setAttribute('aria-labelledby', label.id);
  control.setAttribute('aria-controls', list.id);

  const renderOptions = () => {
    list.replaceChildren();
    options.forEach((option, index) => {
      const item = document.createElement('div');
      item.className = 'custom-select-option';
      item.id = `${controlId}-option-${index}`;
      item.setAttribute('role', 'option');
      item.setAttribute('aria-selected', String(option.value === select.value));
      item.tabIndex = -1;
      const optionLabel = document.createElement('span');
      optionLabel.className = 'custom-select-option-label';
      optionLabel.textContent = option.textContent;
      item.append(optionLabel);
      item.addEventListener('click', () => {
        select.value = option.value;
        select.dispatchEvent(new Event('change', { bubbles: true }));
        closeOptions(true);
      });
      list.append(item);
    });
    const selectedIndex = Math.max(select.selectedIndex, 0);
    control.textContent = options[selectedIndex].textContent;
    control.setAttribute('aria-activedescendant', `${controlId}-option-${selectedIndex}`);
  };
  const openOptions = () => {
    field.classList.add('is-open');
    list.hidden = false;
    control.setAttribute('aria-expanded', 'true');
    activeIndex = Math.max(select.selectedIndex, 0);
    control.setAttribute('aria-activedescendant', `${controlId}-option-${activeIndex}`);
    list.querySelectorAll('[role="option"]').forEach((option, index) => {
      option.classList.toggle('is-active', index === activeIndex);
    });
  };
  const closeOptions = focusControl => {
    field.classList.remove('is-open');
    list.hidden = true;
    control.setAttribute('aria-expanded', 'false');
    if (focusControl) control.focus();
  };
  control.addEventListener('click', () => {
    if (control.getAttribute('aria-expanded') === 'true') closeOptions(false);
    else openOptions();
  });
  control.addEventListener('keydown', event => {
    const currentIndex = control.getAttribute('aria-expanded') === 'true'
      ? activeIndex
      : Math.max(select.selectedIndex, 0);
    let nextIndex = currentIndex;
    if (event.key === 'ArrowDown') nextIndex = Math.min(currentIndex + 1, options.length - 1);
    else if (event.key === 'ArrowUp') nextIndex = Math.max(currentIndex - 1, 0);
    else if (event.key === 'Home') nextIndex = 0;
    else if (event.key === 'End') nextIndex = options.length - 1;
    else if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      if (control.getAttribute('aria-expanded') !== 'true') openOptions();
      else list.querySelector(`#${controlId}-option-${activeIndex}`).click();
      return;
    } else if (event.key === 'Escape') {
      closeOptions(false);
      return;
    } else return;
    event.preventDefault();
    if (control.getAttribute('aria-expanded') !== 'true') openOptions();
    activeIndex = nextIndex;
    const activeOption = list.querySelector(`#${controlId}-option-${nextIndex}`);
    list.querySelectorAll('[role="option"]').forEach(option => option.classList.remove('is-active'));
    activeOption.classList.add('is-active');
    control.setAttribute('aria-activedescendant', activeOption.id);
    activeOption.scrollIntoView({ block: 'nearest' });
  });
  document.addEventListener('click', event => {
    if (!field.contains(event.target)) closeOptions(false);
  });
  field.addEventListener('focusout', event => {
    if (!field.contains(event.relatedTarget)) closeOptions(false);
  });
  select.addEventListener('change', renderOptions);
  field.append(control, list);
  renderOptions();
  closeOptions(false);
};
document.querySelectorAll('#f-event, #f-package').forEach(createCenteredSelect);
const packageSelect = document.getElementById('f-package');
document.querySelectorAll('[data-package]').forEach(link => link.addEventListener('click', () => {
  packageSelect.value = link.dataset.package;
  packageSelect.dispatchEvent(new Event('change', { bubbles: true }));
}));
document.querySelectorAll('[data-event]').forEach(link => link.addEventListener('click', () => {
  const eventField = document.getElementById('f-event');
  eventField.value = link.dataset.event;
  eventField.dispatchEvent(new Event('change', { bubbles: true }));
}));
let discountPercent = 0;
let freeDelivery = false;
const discountInput = document.getElementById('f-discount-code');
if (discountInput) {
  const form = discountInput.closest('form');
  const discountValue = document.createElement('input');
  discountValue.type = 'hidden'; discountValue.name = 'Rabat (%)'; discountValue.value = '0';
  form.append(discountValue);
  const deliveryValue = form.dataset.inquiry === 'order' ? document.createElement('input') : null;
  if (deliveryValue) {
    deliveryValue.type = 'hidden'; deliveryValue.name = 'Darmowa dostawa'; deliveryValue.value = 'Nie';
    form.append(deliveryValue);
  }
  let discountNoticeTimer;
  let lastNotifiedCode = '';
  const applyDiscount = () => {
    const code = discountInput.value.trim().toLowerCase();
    const codes = form.dataset.inquiry === 'live' ? window.MAGNET_DISCOUNTS_LIVE
      : form.dataset.inquiry === 'order' ? window.MAGNET_DISCOUNTS_ORDER : [];
    const match = (Array.isArray(codes) ? codes : []).find(item =>
      typeof item.code === 'string' && item.code.trim().toLowerCase() === code &&
      ((Number.isFinite(item.percent) && item.percent > 0 && item.percent <= 100) ||
        (form.dataset.inquiry === 'order' && item.type === 'shipping')));
    freeDelivery = Boolean(match && form.dataset.inquiry === 'order' && match.type === 'shipping');
    discountPercent = match && !freeDelivery ? match.percent : 0;
    discountValue.value = String(discountPercent);
    if (deliveryValue) deliveryValue.value = freeDelivery ? 'Tak' : 'Nie';
    const help = document.getElementById('discount-code-help');
    if (help) help.hidden = Boolean(code);
    discountInput.classList.toggle('discount-valid', Boolean(match));
    discountInput.removeAttribute('aria-invalid');
    document.getElementById('discount-status').textContent = '';
    document.dispatchEvent(new Event('magnet-discount-change'));
    return match;
  };
  const showDiscountNotice = () => {
    const match = applyDiscount();
    document.getElementById('info-title').textContent = freeDelivery ? 'Darmowa dostawa'
      : discountPercent ? `Rabat ${discountPercent}%` : 'Kod rabatowy';
    document.getElementById('info-body').textContent = match
      ? freeDelivery
        ? `Kod ${match.code.trim().toUpperCase()} jest aktywny — darmowa dostawa.`
        : `Kod ${match.code.trim().toUpperCase()} jest aktywny — ${discountPercent}% rabatu na magnesy.`
      : document.getElementById('discount-status').textContent || 'Wpisz kod rabatowy.';
    const dialog = document.getElementById('info-dialog');
    if (!dialog.open) dialog.showModal();
    lastNotifiedCode = discountInput.value.trim().toLowerCase();
  };
  discountInput.addEventListener('input', () => {
    clearTimeout(discountNoticeTimer);
    applyDiscount();
    const code = discountInput.value.trim().toLowerCase();
    if (!code) lastNotifiedCode = '';
  });
  document.getElementById('apply-discount')?.addEventListener('click', showDiscountNotice);
  form.addEventListener('submit', () => {
    clearTimeout(discountNoticeTimer);
    const match = applyDiscount();
    if (discountInput.value.trim() && !match) {
      discountInput.value = '';
      applyDiscount();
    }
  });
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
const magnetUnitPriceGrosze = count => count > 200 ? 1000 : 1200 - Math.ceil((count - 10) / 10) * 10;
const discountedMagnetUnitPriceGrosze = count => Math.round(magnetUnitPriceGrosze(count) * (100 - discountPercent) / 100);
const formatMagnetPrice = cents => new Intl.NumberFormat('pl-PL', {minimumFractionDigits: 2, maximumFractionDigits: 2}).format(cents / 100) + ' zł';
if (magnetSlider) {
  const bulkQuantity = document.getElementById('magnet-bulk-quantity');
  const updateMagnetPrice = () => {
    const bulk = Number(magnetSlider.value) === 201;
    document.getElementById('magnet-bulk-field').hidden = !bulk;
    bulkQuantity.disabled = !bulk;
    bulkQuantity.required = bulk;
    const valid = !bulk || bulkQuantity.checkValidity();
    const count = bulk ? Number(bulkQuantity.value) : Number(magnetSlider.value);
    const discountedUnitGrosze = discountedMagnetUnitPriceGrosze(count);
    const unitPrice = discountedUnitGrosze / 100;
    document.getElementById('magnet-count').value = bulk ? '200+' : count;
    document.getElementById('magnet-unit-price').textContent = formatMagnetPrice(discountedUnitGrosze);
    document.getElementById('magnet-total-price').textContent = valid ? formatMagnetPrice(count * discountedUnitGrosze) : '—';
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

const postalCode = document.getElementById('f-post-office');
if (postalCode) {
  postalCode.addEventListener('input', () => {
    const match = postalCode.value.match(/^(\d{2})-?(\d{1,3})(.*)$/);
    if (match) {
      const town = match[3];
      postalCode.value = `${match[1]}-${match[2]}${town && !/^\s/.test(town) && match[2].length === 3 ? ' ' : ''}${town}`;
    }
  });
}

// Preview files stay in this tab until the user submits the multipart form.
const MAX_PHOTO_BYTES = 10_000_000;
let photos = [];
const input = document.getElementById('photos');
const previews = document.getElementById('photo-previews');
const quantity = document.getElementById('f-quantity');
const sharedCaption = document.getElementById('f-caption');
const photoPicker = document.getElementById('photo-picker');
const photoPickerLabel = document.getElementById('photo-picker-label');
function showPhotoProblem(title, message) {
  document.getElementById('photo-status').textContent = message;
  document.getElementById('info-title').textContent = title;
  document.getElementById('info-body').textContent = message;
  const dialog = document.getElementById('info-dialog');
  if (!dialog.open) dialog.showModal();
}
function renderPhotos() {
  previews.replaceChildren();
  if (photoPickerLabel) photoPickerLabel.textContent = photos.length ? `Wybrano zdjęć: ${photos.length}` : 'Nie wybrano zdjęć';
  photos.forEach((item, index) => {
    const card = document.createElement('div'); card.className = 'photo-preview';
    const image = document.createElement('img'); image.src = item.url; image.alt = `Lokalny podgląd: ${item.file.name}`;
    const name = document.createElement('p'); name.textContent = item.file.name;
    const label = document.createElement('label'); label.textContent = 'Liczba egzemplarzy';
    const count = document.createElement('input'); count.type = 'number'; count.min = '1'; count.max = '10000'; count.value = item.count; count.required = true;
    count.setAttribute('aria-label', `Liczba egzemplarzy zdjęcia ${index + 1}`);
    count.addEventListener('input', () => { item.count = Number(count.value) || 0; });
    label.append(count);
    const captionLabel = document.createElement('label'); captionLabel.textContent = 'Napis';
    const caption = document.createElement('input'); caption.type = 'text'; caption.maxLength = 200; caption.value = item.caption;
    caption.className = 'photo-caption';
    caption.setAttribute('aria-label', `Napis dla zdjęcia ${index + 1}`);
    caption.addEventListener('input', () => { item.caption = caption.value; item.captionCustomized = true; });
    captionLabel.append(caption);
    const remove = document.createElement('button'); remove.type = 'button'; remove.className = 'remove-photo'; remove.textContent = 'Usuń zdjęcie';
    remove.addEventListener('click', () => {
      URL.revokeObjectURL(item.url); photos = photos.filter(photo => photo !== item); renderPhotos();
      input.focus();
    });
    card.append(image, name, label, captionLabel, remove); previews.append(card);
  });
  if (photos.length > 0) {
    const add = document.createElement('button');
    add.type = 'button'; add.className = 'add-photo';
    add.textContent = '+ Dodaj następne zdjęcie';
    add.addEventListener('click', () => input.click());
    previews.append(add);
  }
}
if (input) {
  photoPicker?.addEventListener('click', () => input.click());
  input.addEventListener('change', () => {
    const selectedFiles = [...input.files];
    const unsupported = selectedFiles.some(file => !['image/jpeg', 'image/png', 'image/webp'].includes(file.type));
    const totalBytes = photos.reduce((sum, item) => sum + item.file.size, 0) + selectedFiles.reduce((sum, file) => sum + file.size, 0);
    if (unsupported) {
      input.value = '';
      showPhotoProblem('Nieprawidłowy format zdjęcia', 'Dodaj zdjęcia w formacie JPG, PNG lub WebP. Jeśli potrzebujesz pomocy, napisz na magnesowyswiat@gmail.com lub zadzwoń: 505 606 707.');
      return;
    }
    if (totalBytes > MAX_PHOTO_BYTES) {
      input.value = '';
      showPhotoProblem('Za dużo zdjęć', 'Łączny rozmiar wybranych zdjęć jest za duży. Napisz na magnesowyswiat@gmail.com lub zadzwoń: 505 606 707 — ustalimy wygodny sposób przesłania zdjęć.');
      return;
    }
    for (const file of selectedFiles) {
      photos.push({ file, url: URL.createObjectURL(file), count: 1, caption: sharedCaption?.value.trim() || '', captionCustomized: false });
    }
    input.value = '';
    document.getElementById('photo-status').textContent = `Wybrano zdjęć: ${photos.length}. Łączny rozmiar: ${(photos.reduce((sum, item) => sum + item.file.size, 0) / 1_000_000).toFixed(2)} MB z 10 MB.`;
    renderPhotos();
  });
  window.addEventListener('pagehide', () => {
    photos.forEach(item => URL.revokeObjectURL(item.url)); photos = []; renderPhotos();
    document.querySelector('[data-attachments]')?.replaceChildren();
  });
}
sharedCaption?.addEventListener('input', () => {
  photos.forEach(item => {
    if (!item.captionCustomized) item.caption = sharedCaption.value;
  });
  previews?.querySelectorAll('.photo-caption').forEach((field, index) => {
    if (!photos[index]?.captionCustomized) field.value = sharedCaption.value;
  });
});

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
  const summaryDialog = document.getElementById('order-summary-dialog');
  const summaryContent = document.getElementById('order-summary-content');
  const confirmSubmit = document.getElementById('confirm-order-submit');
  let confirmedSubmission = false;

  const fieldValue = id => document.getElementById(id)?.value.trim() || '';
  const showOrderSummary = () => {
    const captionsDiffer = photos.some(item => item.caption.trim() !== fieldValue('f-caption'));
    const copiesTotal = photos.reduce((sum, item) => sum + item.count, 0);
    const list = document.createElement('dl');
    list.className = 'order-summary-list';
    const rows = [
      ['Imię i nazwisko', fieldValue('f-name')],
      ['Adres e-mail', fieldValue('f-email')],
      ['Telefon', fieldValue('f-phone') || 'Nie podano'],
      ['Liczba magnesów', `${copiesTotal} szt.`],
      ['Razem za magnesy', formatMagnetPrice(copiesTotal * discountedMagnetUnitPriceGrosze(copiesTotal))],
      ...(!captionsDiffer ? [['Napis', fieldValue('f-caption') || 'Nie podano']] : []),
      ['Kod rabatowy', fieldValue('f-discount-code') || 'Nie podano'],
      ['Miejscowość', fieldValue('f-delivery-town') || 'Nie podano'],
      ['Ulica i numer', fieldValue('f-delivery-street') || 'Nie podano'],
      ['Poczta', fieldValue('f-post-office') || 'Nie podano'],
      ['Uwagi', fieldValue('f-message') || 'Brak']
    ];
    rows.forEach(([label, value]) => {
      const term = document.createElement('dt');
      const detail = document.createElement('dd');
      term.textContent = label;
      detail.textContent = value;
      list.append(term, detail);
    });

    const photosTitle = document.createElement('h3');
    photosTitle.textContent = `Zdjęcia (${photos.length})`;
    const photoList = document.createElement('div');
    photoList.className = 'order-summary-photos';
    photos.forEach(item => {
      const card = document.createElement('div');
      card.className = 'order-summary-photo';
      const image = document.createElement('img');
      image.src = item.url;
      image.alt = '';
      const description = document.createElement('p');
      description.textContent = `${item.file.name} — ${item.count} szt.${item.caption ? ` — napis: ${item.caption}` : ''}`;
      card.append(image, description);
      photoList.append(card);
    });
    summaryContent.replaceChildren(list, photosTitle, photoList);
    summaryDialog.showModal();
  };

  summaryDialog?.addEventListener('close', () => { confirmedSubmission = false; });
  confirmSubmit?.addEventListener('click', () => { confirmedSubmission = true; });
  form.addEventListener('submit', event => {
    const status = form.querySelector('.form-status');
    if (!photos.length) {
      event.preventDefault(); confirmedSubmission = false; status.textContent = 'Dodaj przynajmniej jedno zdjęcie.'; input.focus(); return;
    }
    const requestedQuantity = Number(quantity.value);
    const copiesTotal = photos.reduce((sum, item) => sum + item.count, 0);
    if (requestedQuantity < 10 || copiesTotal < 10) {
      event.preventDefault();
      confirmedSubmission = false;
      const message = `Minimalne zamówienie to 10 magnesów. Wpisano ${requestedQuantity} szt., a zdjęcia mają łącznie ${copiesTotal} szt.`;
      status.textContent = message;
      document.getElementById('info-title').textContent = 'Minimalna liczba magnesów';
      document.getElementById('info-body').textContent = message;
      const dialog = document.getElementById('info-dialog');
      if (!dialog.open) dialog.showModal();
      return;
    }
    if (requestedQuantity !== copiesTotal) {
      event.preventDefault();
      confirmedSubmission = false;
      const counts = photos.map(item => item.count);
      const photoWord = photos.length === 1 ? 'zdjęcie' : photos.length >= 2 && photos.length <= 4 ? 'zdjęcia' : 'zdjęć';
      const sameCount = counts.every(count => count === counts[0]);
      const selection = sameCount
        ? `${photos.length} ${photoWord} po ${counts[0]} szt.`
        : `${photos.length} ${photoWord} z liczbą kopii: ${counts.join(' + ')}`;
      const message = `Wybrano ${selection}, czyli łącznie ${copiesTotal} magnesów, a w polu „Liczba magnesów” podano ${requestedQuantity}. Uzupełnij liczbę kopii przy zdjęciach tak, aby ich suma wynosiła ${requestedQuantity}.`;
      status.textContent = message;
      document.getElementById('info-title').textContent = 'Sprawdź liczbę magnesów';
      document.getElementById('info-body').textContent = message;
      const dialog = document.getElementById('info-dialog');
      if (!dialog.open) dialog.showModal();
      return;
    }
    if (photos.reduce((sum, item) => sum + item.file.size, 0) > MAX_PHOTO_BYTES) {
      event.preventDefault();
      confirmedSubmission = false;
      const message = 'Łączny rozmiar wybranych zdjęć jest za duży. Napisz na magnesowyswiat@gmail.com lub zadzwoń: 505 606 707 — ustalimy wygodny sposób przesłania zdjęć.';
      status.textContent = message;
      showPhotoProblem('Za dużo zdjęć', message);
      return;
    }
    if (!confirmedSubmission) {
      event.preventDefault();
      status.textContent = '';
      showOrderSummary();
      return;
    }
    summaryDialog?.close();
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
      event.preventDefault(); confirmedSubmission = false; attachments.replaceChildren();
      status.textContent = 'Nie udało się dołączyć zdjęć. Spróbuj w aktualnej przeglądarce lub napisz na magnesowyswiat@gmail.com.'; return;
    }
    document.getElementById('photo-summary').value = photos.map((item, index) => `${index + 1}. ${item.file.name}: ${item.count} szt.${item.caption ? `; napis: ${item.caption}` : ''}`).join('\n');
    form.setAttribute('aria-busy', 'true');
    status.textContent = 'Przechodzenie do wysyłki zapytania i zdjęć…';
    form.querySelector('[type="submit"]').textContent = 'Przechodzenie do wysyłki…';
  });
  window.addEventListener('pageshow', () => {
    confirmedSubmission = false;
    form.removeAttribute('aria-busy');
    form.querySelector('[type="submit"]').textContent = 'ZOBACZ PODSUMOWANIE';
  });
  if (new URLSearchParams(location.search).get('wyslano') === '1') {
    form.querySelector('.form-status').textContent = 'Dziękujemy za kontakt. Cenę i szczegóły zamówienia potwierdzimy mailowo.';
    showSendConfirmation();
  }
});
