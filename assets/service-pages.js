const menuToggle = document.getElementById('menuToggle');
const navLinks = document.getElementById('navLinks');
function closeMenu() {
  navLinks.classList.remove('open');
  menuToggle.setAttribute('aria-expanded', 'false');
  menuToggle.setAttribute('aria-label', 'Otwórz menu');
  menuToggle.textContent = '☰';
}
menuToggle.addEventListener('click', function () {
  const open = navLinks.classList.toggle('open');
  menuToggle.setAttribute('aria-expanded', String(open));
  menuToggle.setAttribute('aria-label', open ? 'Zamknij menu' : 'Otwórz menu');
  menuToggle.textContent = open ? '✕' : '☰';
});
navLinks.querySelectorAll('a').forEach(link => link.addEventListener('click', closeMenu));
document.addEventListener('keydown', function (event) {
  if (event.key === 'Escape' && navLinks.classList.contains('open')) {
    closeMenu();
    menuToggle.focus();
  }
});

const orderForm = document.getElementById('orderInquiry');
if (orderForm) {
  orderForm.addEventListener('submit', function (event) {
    event.preventDefault();
    if (!orderForm.reportValidity()) return;
    const body = [
      'Dzień dobry, proszę o wycenę magnesów na zamówienie.',
      '',
      'Imię i nazwisko: ' + document.getElementById('orderName').value,
      'E-mail kontaktowy: ' + document.getElementById('orderEmail').value,
      'Liczba magnesów: ' + document.getElementById('orderQuantity').value,
      'Okazja: ' + document.getElementById('orderOccasion').value,
      '',
      'Dodatkowe informacje:',
      document.getElementById('orderMessage').value
    ].join('\n');
    const subject = 'Zapytanie o magnesy na zamówienie';
    const recipient = 'magnesowyswiat@gmail.com';
    document.getElementById('orderText').value = body;
    document.getElementById('orderMailLink').href = 'mailto:' + recipient + '?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(body);
    const gmail = new URL('https://mail.google.com/mail/');
    gmail.searchParams.set('view', 'cm');
    gmail.searchParams.set('fs', '1');
    gmail.searchParams.set('to', recipient);
    gmail.searchParams.set('su', subject);
    gmail.searchParams.set('body', body);
    document.getElementById('orderGmailLink').href = gmail.href;
    const summary = document.getElementById('orderSummary');
    summary.hidden = false;
    summary.focus();
  });
}
