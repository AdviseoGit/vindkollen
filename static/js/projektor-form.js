(function () {
  var form = document.getElementById('projektor-form');
  if (!form) return;
  var errBox = document.getElementById('pj-error');
  var okBox = document.getElementById('pj-success');
  var btn = document.getElementById('pj-submit');

  function showError(msg) {
    errBox.textContent = msg;
    errBox.classList.remove('hidden');
  }

  function checked(name) {
    return Array.prototype.map.call(
      form.querySelectorAll('input[name="' + name + '"]:checked'),
      function (el) { return el.value; }
    );
  }

  function detailMessage(data) {
    var d = data && data.detail;
    if (Array.isArray(d) && d.length) {
      var m = d[0].msg || '';
      return m.replace(/^Value error, /, '');
    }
    return typeof d === 'string' ? d : '';
  }

  form.addEventListener('submit', function (ev) {
    ev.preventDefault();
    errBox.classList.add('hidden');

    var fd = new FormData(form);
    var counties = checked('county');
    var technologies = checked('technology');
    var org = (fd.get('organisation') || '').trim();
    var email = (fd.get('email') || '').trim();

    if (org.length < 2) return showError('Ange bolagets namn.');
    if (!email || !form.elements.email.checkValidity()) return showError('Ange en giltig e-postadress.');
    if (!counties.length) return showError('Välj minst ett län.');
    if (!technologies.length) return showError('Välj minst en teknik.');
    if (!form.elements.consent_contact.checked) return showError('Vi behöver ditt samtycke för att få kontakta dig om leads.');

    var payload = {
      organisation: org,
      email: email,
      name: (fd.get('name') || '').trim() || null,
      phone: (fd.get('phone') || '').trim() || null,
      counties: counties,
      technologies: technologies,
      wants_free_first_lead: fd.get('free_first') !== 'nej',
      message: (fd.get('message') || '').trim() || null,
      consent_contact: true
    };

    btn.disabled = true;
    fetch('/api/lead/projektor', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
      .then(function (r) {
        return r.json().catch(function () { return {}; }).then(function (data) {
          return { ok: r.ok, data: data };
        });
      })
      .then(function (res) {
        if (!res.ok) {
          btn.disabled = false;
          return showError(detailMessage(res.data) || 'Något gick fel. Försök igen eller mejla sales@adviseo.se.');
        }
        if (typeof gtag === 'function') {
          gtag('event', 'generate_lead', { segment: 'projektor', source: 'for_projektorer' });
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
