'use strict';

// This calendar is deliberately independent of the browser's UI language.
function createPolishDatePicker(date, picker, trigger, today) {
  const months = ['Styczeń', 'Luty', 'Marzec', 'Kwiecień', 'Maj', 'Czerwiec', 'Lipiec', 'Sierpień', 'Wrzesień', 'Październik', 'Listopad', 'Grudzień'];
  const weekdays = [['Pon', 'Poniedziałek'], ['Wt', 'Wtorek'], ['Śr', 'Środa'], ['Czw', 'Czwartek'], ['Pt', 'Piątek'], ['Sob', 'Sobota'], ['Nd', 'Niedziela']];
  const fullDate = new Intl.DateTimeFormat('pl-PL', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' });
  const pad = value => String(value).padStart(2, '0');
  const iso = value => `${value.getFullYear()}-${pad(value.getMonth() + 1)}-${pad(value.getDate())}`;
  const fromISO = value => { const [year, month, day] = value.split('-').map(Number); return new Date(year, month - 1, day); };
  let year = today.getFullYear();
  let month = today.getMonth();
  const dialog = document.createElement('dialog');
  dialog.id = 'event-calendar';
  dialog.className = 'event-calendar';
  dialog.lang = 'pl';
  dialog.setAttribute('aria-labelledby', 'event-calendar-title');
  dialog.innerHTML = '<div class="calendar-heading"><h2 id="event-calendar-title">Wybierz datę wydarzenia</h2><button class="calendar-close" type="button" aria-label="Zamknij kalendarz">×</button></div><div class="calendar-controls"><button class="calendar-prev" type="button" aria-label="Poprzedni miesiąc">‹</button><label>Miesiąc<select class="calendar-month" aria-label="Miesiąc"></select></label><label>Rok<input class="calendar-year" type="number" inputmode="numeric" aria-label="Rok" max="9999"></label><button class="calendar-next" type="button" aria-label="Następny miesiąc">›</button></div><p class="calendar-period" aria-live="polite"></p><table class="calendar-table"><thead><tr></tr></thead><tbody></tbody></table><p class="calendar-hint">Wybierz dzień. Daty z przeszłości są niedostępne.</p><button class="calendar-today text-link" type="button">Przejdź do dzisiaj</button>';
  document.body.append(dialog);
  trigger.setAttribute('aria-haspopup', 'dialog');
  trigger.setAttribute('aria-controls', dialog.id);
  trigger.setAttribute('aria-expanded', 'false');
  const monthSelect = dialog.querySelector('.calendar-month');
  const yearInput = dialog.querySelector('.calendar-year');
  const previous = dialog.querySelector('.calendar-prev');
  const next = dialog.querySelector('.calendar-next');
  const body = dialog.querySelector('tbody');
  const weekdayRow = dialog.querySelector('thead tr');
  yearInput.min = today.getFullYear();
  months.forEach((label, index) => { const option = document.createElement('option'); option.value = index; option.textContent = label; monthSelect.append(option); });
  weekdays.forEach(([short, full]) => { const th = document.createElement('th'); th.scope = 'col'; th.textContent = short; th.setAttribute('aria-label', full); weekdayRow.append(th); });

  function render(focusDate) {
    year = Math.max(today.getFullYear(), Math.min(9999, year || today.getFullYear()));
    if (year === today.getFullYear() && month < today.getMonth()) month = today.getMonth();
    monthSelect.value = month;
    yearInput.value = year;
    [...monthSelect.options].forEach(option => { option.disabled = year === today.getFullYear() && Number(option.value) < today.getMonth(); });
    previous.disabled = year === today.getFullYear() && month === today.getMonth();
    next.disabled = year === 9999 && month === 11;
    const period = `${months[month]} ${year}`;
    dialog.querySelector('.calendar-period').textContent = period;
    dialog.querySelector('table').setAttribute('aria-label', period);
    body.replaceChildren();
    const offset = (new Date(year, month, 1).getDay() + 6) % 7;
    const days = new Date(year, month + 1, 0).getDate();
    const cells = Math.ceil((offset + days) / 7) * 7;
    let row;
    for (let index = 0; index < cells; index += 1) {
      if (index % 7 === 0) { row = document.createElement('tr'); body.append(row); }
      const cell = document.createElement('td'); row.append(cell);
      const day = index - offset + 1;
      if (day < 1 || day > days) continue;
      const value = new Date(year, month, day);
      const dayButton = document.createElement('button');
      dayButton.type = 'button'; dayButton.className = 'calendar-day'; dayButton.textContent = day;
      dayButton.dataset.date = iso(value); dayButton.setAttribute('aria-label', fullDate.format(value));
      dayButton.disabled = value < today;
      if (iso(value) === iso(today)) dayButton.setAttribute('aria-current', 'date');
      if (iso(value) === picker.value) { dayButton.classList.add('is-selected'); dayButton.setAttribute('aria-label', fullDate.format(value) + ', wybrana data'); }
      cell.append(dayButton);
    }
    if (focusDate) dialog.querySelector(`[data-date="${iso(focusDate)}"]:not(:disabled)`)?.focus();
  }
  function moveMonth(change) {
    const value = new Date(year, month + change, 1);
    year = value.getFullYear(); month = value.getMonth(); render();
  }
  previous.addEventListener('click', () => moveMonth(-1));
  next.addEventListener('click', () => moveMonth(1));
  monthSelect.addEventListener('change', () => { month = Number(monthSelect.value); render(); });
  yearInput.addEventListener('change', () => { year = Math.trunc(Number(yearInput.value)); render(); });
  dialog.querySelector('.calendar-close').addEventListener('click', () => dialog.close());
  dialog.addEventListener('close', () => { trigger.setAttribute('aria-expanded', 'false'); trigger.focus(); });
  dialog.querySelector('.calendar-today').addEventListener('click', () => { year = today.getFullYear(); month = today.getMonth(); render(today); });
  body.addEventListener('click', event => {
    const day = event.target.closest('.calendar-day');
    if (!day || day.disabled) return;
    picker.value = day.dataset.date;
    picker.dispatchEvent(new Event('change', { bubbles: true }));
    date.dispatchEvent(new Event('change', { bubbles: true }));
    dialog.close();
  });
  body.addEventListener('keydown', event => {
    const day = event.target.closest('.calendar-day');
    if (!day) return;
    const value = fromISO(day.dataset.date);
    const delta = { ArrowLeft: -1, ArrowRight: 1, ArrowUp: -7, ArrowDown: 7, Home: -((value.getDay() + 6) % 7), End: 6 - ((value.getDay() + 6) % 7) };
    if (Object.hasOwn(delta, event.key)) value.setDate(value.getDate() + delta[event.key]);
    else if (['PageUp', 'PageDown'].includes(event.key)) {
      const originalDay = value.getDate(); value.setDate(1); value.setMonth(value.getMonth() + (event.key === 'PageUp' ? -1 : 1));
      value.setDate(Math.min(originalDay, new Date(value.getFullYear(), value.getMonth() + 1, 0).getDate()));
    } else return;
    event.preventDefault();
    if (value < today) value.setTime(today.getTime());
    if (value.getFullYear() > 9999) return;
    year = value.getFullYear(); month = value.getMonth(); render(value);
  });
  trigger.disabled = false;
  trigger.addEventListener('click', () => {
    const value = picker.value ? fromISO(picker.value) : today;
    year = value.getFullYear(); month = value.getMonth(); render();
    trigger.setAttribute('aria-expanded', 'true'); dialog.showModal(); render(value);
  });
}
