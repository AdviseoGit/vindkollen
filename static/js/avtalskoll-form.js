(function () {
  var form = document.getElementById('avtalskoll-form');
  if (!form) return;
  var errBox = document.getElementById('ak-error');
  var okBox = document.getElementById('ak-success');
  var btn = document.getElementById('ak-submit');
  var text = document.getElementById('ak-text');
  var MAX = 60000;

  function showError(msg) {
    errBox.textContent = msg;
    errBox.classList.remove('hidden');
  }

  function detailMessage(data) {
    var d = data && data.detail;
    if (Array.isArray(d) && d.length) {
      return (d[0].msg || '').replace(/^Value error, /, '');
    }
    return typeof d === 'string' ? d : '';
  }

  document.getElementById('ak-file').addEventListener('change', function (ev) {
    var file = ev.target.files && ev.target.files[0];
    if (!file) return;
    var reader = new FileReader();
    reader.onload = function () {
      text.value = String(reader.result || '').slice(0, MAX);
      errBox.classList.add('hidden');
      if ((reader.result || '').length > MAX) {
        showError('Filen var längre än ' + MAX + ' tecken och har kortats av. Skicka resten som PDF via mejl.');
      }
    };
    reader.onerror = function () { showError('Kunde inte läsa filen. Klistra in texten istället.'); };
    reader.readAsText(file);
  });

  form.addEventListener('submit', function (ev) {
    ev.preventDefault();
    errBox.classList.add('hidden');

    var fd = new FormData(form);
    var name = (fd.get('name') || '').trim();
    var email = (fd.get('email') || '').trim();
    var county = fd.get('county') || '';
    var technology = fd.get('technology') || '';
    var contract = (text.value || '').trim();
    var sendsPdf = form.elements.sends_pdf.checked;

    if (name.length < 2) return showError('Ange ditt namn.');
    if (!email || !form.elements.email.checkValidity()) return showError('Ange en giltig e-postadress.');
    if (!county) return showError('Välj län.');
    if (!technology) return showError('Välj teknik: vind, sol eller batteri.');
    if (!sendsPdf && contract.length < 20) return showError('Klistra in avtalstexten, ladda upp en .txt-fil eller kryssa i att du skickar avtalet som PDF.');
    if (!form.elements.consent.checked) return showError('Vi behöver ditt samtycke för att kunna leverera avtalskollen.');

    btn.disabled = true;
    fetch('/api/lead/avtalskoll', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: name,
        email: email,
        county: county,
        technology: technology,
        contract_text: contract,
        sends_pdf: sendsPdf,
        consent: true
      })
    })
      .then(function (r) {
        return r.json().catch(function () { return {}; }).then(function (data) {
          return { ok: r.ok, data: data };
        });
      })
      .then(function (res) {
        if (!res.ok) {
          btn.disabled = false;
          return showError(detailMessage(res.data) || 'Något gick fel. Försök igen eller mejla info@vindkoll.se.');
        }
        if (typeof gtag === 'function') {
          gtag('event', 'avtalskoll_order', { technology: technology, county: county, value: 695, currency: 'SEK' });
        }
        form.classList.add('hidden');
        okBox.classList.remove('hidden');
        okBox.scrollIntoView({ behavior: 'smooth', block: 'center' });
      })
      .catch(function () {
        btn.disabled = false;
        showError('Kunde inte nå servern. Försök igen om en stund.');
      });
  });
})();
