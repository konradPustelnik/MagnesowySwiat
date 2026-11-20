const ACCOUNT = 'magnesowyswiat@gmail.com';
const SUBJECTS = {
  live: '[NA ŻYWO] Zapytanie o termin | Magnesowy Świat',
  order: '[NA ZAMÓWIENIE] Zapytanie o magnesy ze zdjęć | Magnesowy Świat',
};
const REPLY_SUBJECT = 'Dziękujemy za wiadomość | Magnesowy Świat';
const REPLY_BODY = `Dzień dobry,

dziękujemy za kontakt z Magnesowym Światem! Otrzymaliśmy Twoją wiadomość. Zapoznamy się z nią i odezwiemy się najszybciej, jak to będzie możliwe. Szczegóły zamówienia lub rezerwacji potwierdzimy w osobnej wiadomości.

Do usłyszenia!
Zespół Magnesowy Świat`;

// Uzupełnij na podstawie nagłówków obu kontrolnych wiadomości w Gmailu.
const FORMSUBMIT_SENDER = '';
const FORMSUBMIT_DMARC_DOMAIN = '';
const TEST_RECIPIENT = '';

const HANDLED = 'MS-Autoodpowiedz-Obsluzone';
const REVIEW = 'MS-Autoodpowiedz-DoSprawdzenia';
const HEADERS = ['Subject', 'From', 'Reply-To', 'Authentication-Results', 'Auto-Submitted'];

function address(value = '') {
  const match = value.trim().match(/^(?:[^<>,;\r\n]*<([^<>]+)>|([^<>,;\s]+))$/);
  const email = match && (match[1] || match[2]);
  return email && /^[a-z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-z0-9-]+(?:\.[a-z0-9-]+)+$/i.test(email)
    ? email.toLowerCase() : '';
}

function submission(message, sender, domain) {
  const headers = message.payload?.headers || [];
  const values = name => headers.filter(header => header.name.toLowerCase() === name.toLowerCase());
  const single = name => values(name).length === 1 ? values(name)[0].value : '';
  const offer = Object.keys(SUBJECTS).find(key => SUBJECTS[key] === single('Subject'));
  if (!offer || address(single('From')) !== sender) return null;
  const authentication = values('Authentication-Results')[0]?.value || '';
  if (!/^mx\.google\.com\s*;/i.test(authentication)) return null;
  const dmarc = authentication.split(';').find(part => /^\s*dmarc=pass(?:\s|$)/i.test(part));
  const authenticatedDomain = dmarc?.match(/\bheader\.from=([a-z0-9.-]+)(?=\s|$)/i)?.[1].toLowerCase();
  if (authenticatedDomain !== domain) return null;
  const auto = values('Auto-Submitted');
  if (auto.length && single('Auto-Submitted').toLowerCase() !== 'no') return null;
  const recipient = address(single('Reply-To'));
  if (!recipient || [sender, ACCOUNT].includes(recipient) || recipient.endsWith('@' + domain)) return null;
  return { offer, recipient };
}

function configuration() {
  if (Gmail.Users.getProfile('me').emailAddress.toLowerCase() !== ACCOUNT) {
    throw new Error('Uruchom skrypt na firmowym koncie Gmail.');
  }
  const sender = address(FORMSUBMIT_SENDER);
  const domain = FORMSUBMIT_DMARC_DOMAIN.trim().toLowerCase();
  if (!sender || !/^[a-z0-9-]+(?:\.[a-z0-9-]+)+$/.test(domain)
      || !(sender.endsWith('@' + domain) || sender.endsWith('.' + domain))) {
    throw new Error('Uzupełnij zweryfikowanego nadawcę FormSubmit i domenę DMARC.');
  }
  return { sender, domain };
}

function* messages(query) {
  let pageToken;
  do {
    const page = Gmail.Users.Messages.list('me', { q: query, maxResults: 50, pageToken });
    for (const entry of page.messages || []) {
      yield Gmail.Users.Messages.get('me', entry.id, { format: 'metadata', metadataHeaders: HEADERS });
    }
    pageToken = page.nextPageToken;
  } while (pageToken);
}

function previewConfirmations() {
  const { sender, domain } = configuration();
  const expected = address(TEST_RECIPIENT);
  if (!expected) throw new Error('Wpisz kontrolny adres TEST_RECIPIENT.');
  const matches = new Set();
  for (const message of messages(`in:inbox newer_than:2d from:${sender}`)) {
    const result = submission(message, sender, domain);
    if (result?.recipient === expected) matches.add(result.offer);
  }
  return [...matches];
}

function preview() {
  console.log('Zgodne formularze kontrolne: ' + (previewConfirmations().join(', ') || 'brak'));
}

function testReply() {
  if (previewConfirmations().length !== Object.keys(SUBJECTS).length) {
    throw new Error('Brak zgodnych zgłoszeń kontrolnych z obu formularzy.');
  }
  MailApp.sendEmail(address(TEST_RECIPIENT), REPLY_SUBJECT, REPLY_BODY, { name: 'Magnesowy Świat' });
}

function install() {
  const lock = LockService.getScriptLock();
  lock.waitLock(10000);
  try {
    if (previewConfirmations().length !== Object.keys(SUBJECTS).length) {
      throw new Error('Brak zgodnych zgłoszeń kontrolnych z obu formularzy.');
    }
    const properties = PropertiesService.getScriptProperties();
    const triggers = ScriptApp.getProjectTriggers().filter(trigger => trigger.getHandlerFunction() === 'sendConfirmations');
    if (!triggers.length) {
      properties.setProperty('startedAt', String(Date.now()));
      ScriptApp.newTrigger('sendConfirmations').timeBased().everyMinutes(5).create();
    }
  } finally {
    lock.releaseLock();
  }
}

function labelId(name) {
  const existing = (Gmail.Users.Labels.list('me').labels || []).find(label => label.name === name);
  return (existing || Gmail.Users.Labels.create({ name }, 'me')).id;
}

function sendConfirmations() {
  const lock = LockService.getScriptLock();
  if (!lock.tryLock(1000)) return;
  try {
    const startedAt = Number(PropertiesService.getScriptProperties().getProperty('startedAt'));
    if (!startedAt) throw new Error('Najpierw uruchom install.');
    const { sender, domain } = configuration();
    const handled = labelId(HANDLED);
    const review = labelId(REVIEW);
    const query = `in:inbox from:${sender} after:${Math.floor(startedAt / 1000)} -label:${HANDLED} -label:${REVIEW}`;
    let remaining = MailApp.getRemainingDailyQuota();
    for (const message of messages(query)) {
      if (remaining <= 0) break;
      if (Number(message.internalDate) <= startedAt || message.labelIds?.some(id => [handled, review].includes(id))) continue;
      const result = submission(message, sender, domain);
      if (!result) continue;
      // Rezerwacja przed wysyłką. Przerwana lub niejednoznaczna próba wymaga sprawdzenia w Wysłanych.
      Gmail.Users.Messages.modify({ addLabelIds: [review] }, 'me', message.id);
      try {
        remaining--;
        MailApp.sendEmail(result.recipient, REPLY_SUBJECT, REPLY_BODY, { name: 'Magnesowy Świat' });
        Gmail.Users.Messages.modify({ addLabelIds: [handled], removeLabelIds: [review] }, 'me', message.id);
      } catch {
        console.error('Sprawdź wiadomość z etykietą ' + REVIEW + ' przed ponowną próbą.');
      }
    }
  } finally {
    lock.releaseLock();
  }
}
