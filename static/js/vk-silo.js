/*
 * vk-silo.js — gemensam logik för Vindkollens lead-silor.
 *
 * Sajten har tre publiker (markägare, närboende, kommun) med olika värde per
 * lead. Den här filen ser till att varje formulär skickar med vilken silo
 * besökaren befinner sig i, härleder elområde ur länet, och rapporterar en
 * GA4-händelse per silo så att konverteringen kan mätas separat.
 *
 * Användning i HTML — inga id:n behövs, bara name-attribut:
 *
 *   <form data-vk-lead-form data-segment="markagare" data-source="markagare_silo">
 *     <input name="name"> <input name="email" type="email" required>
 *     <select name="county">…</select>
 *     <input type="checkbox" name="wants_legal_help">
 *     <button type="submit">Skicka</button>
 *   </form>
 *   <div data-vk-success hidden>Tack!</div>
 */
(function () {
    'use strict';

    // Elområdesgränserna följer inte länsgränserna exakt — det här är en
    // förifyllning som besökaren kan ändra, inte en sanning.
    var COUNTY_TO_ELAREA = {
        'Norrbotten': 'SE1',
        'Västerbotten': 'SE2', 'Jämtland': 'SE2', 'Västernorrland': 'SE2',
        'Gävleborg': 'SE3', 'Dalarna': 'SE3', 'Värmland': 'SE3', 'Örebro': 'SE3',
        'Västmanland': 'SE3', 'Uppsala': 'SE3', 'Stockholm': 'SE3',
        'Södermanland': 'SE3', 'Östergötland': 'SE3', 'Västra Götaland': 'SE3',
        'Jönköping': 'SE3', 'Gotland': 'SE3', 'Halland': 'SE3',
        'Kalmar': 'SE4', 'Kronoberg': 'SE4', 'Blekinge': 'SE4', 'Skåne': 'SE4'
    };

    // Ungefärligt värde per silo, används som GA4-`value` så att kanalerna kan
    // jämföras på intäkt i stället för på antal formulär.
    var SEGMENT_VALUE = { markagare: 800, kommun: 300, narboende: 60, ovrig: 20 };

    var BOOLEAN_FIELDS = ['wants_legal_help', 'wants_projector_contact', 'consent_partner_share'];
    var NUMBER_FIELDS = ['land_hectares', 'distance_m', 'estimated_compensation_sek'];

    var STORAGE_KEY = 'vk_segment';

    function track(name, params) {
        if (typeof window.gtag === 'function') {
            try { window.gtag('event', name, params || {}); } catch (e) { /* non-fatal */ }
        }
    }

    function rememberSegment(segment) {
        if (!segment) return;
        try { window.localStorage.setItem(STORAGE_KEY, segment); } catch (e) { /* private mode */ }
    }

    function rememberedSegment() {
        try { return window.localStorage.getItem(STORAGE_KEY); } catch (e) { return null; }
    }

    function elareaForCounty(county) {
        return COUNTY_TO_ELAREA[county] || null;
    }

    /* --- Formulärhantering ------------------------------------------------ */

    function collect(form) {
        var payload = {};
        Array.prototype.forEach.call(form.querySelectorAll('[name]'), function (el) {
            var key = el.name;
            if (!key) return;
            if (el.type === 'checkbox') {
                payload[key] = el.checked;
                return;
            }
            if (el.type === 'radio') {
                if (el.checked) payload[key] = el.value;
                return;
            }
            var value = (el.value || '').trim();
            if (!value) return;
            payload[key] = NUMBER_FIELDS.indexOf(key) !== -1 ? Number(value) : value;
        });

        BOOLEAN_FIELDS.forEach(function (k) {
            if (payload[k] === undefined) payload[k] = false;
        });
        NUMBER_FIELDS.forEach(function (k) {
            if (payload[k] !== undefined && (isNaN(payload[k]) || payload[k] < 0)) delete payload[k];
        });

        // Ett fält som heter "segment" (t.ex. en radioknapp "Jag är markägare")
        // vinner över formulärets data-segment — besökaren vet bäst.
        payload.segment = payload.segment || form.dataset.segment || rememberedSegment() || 'ovrig';
        payload.source = form.dataset.source || 'silo_form';
        if (!payload.elarea && payload.county) {
            var derived = elareaForCounty(payload.county);
            if (derived) payload.elarea = derived;
        }
        return payload;
    }

    function showSuccess(form) {
        var target = form.dataset.successTarget
            ? document.querySelector(form.dataset.successTarget)
            : form.parentElement.querySelector('[data-vk-success]');
        form.hidden = true;
        form.classList.add('hidden');
        if (target) {
            target.hidden = false;
            target.classList.remove('hidden');
            target.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }

    function showError(form, message) {
        var box = form.querySelector('[data-vk-error]');
        if (box) {
            box.textContent = message;
            box.hidden = false;
            box.classList.remove('hidden');
        } else {
            window.alert(message);
        }
    }

    async function submitForm(form) {
        var button = form.querySelector('button[type="submit"]');
        var originalLabel = button ? button.innerHTML : null;
        var payload = collect(form);

        if (!payload.email || payload.email.indexOf('@') === -1) {
            showError(form, 'Ange en giltig e-postadress.');
            return;
        }

        if (button) {
            button.disabled = true;
            button.innerHTML = 'Skickar…';
        }

        try {
            var res = await fetch('/api/lead/qualify', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            if (!res.ok) throw new Error('HTTP ' + res.status);

            rememberSegment(payload.segment);
            track('generate_lead', {
                segment: payload.segment,
                elarea: payload.elarea || 'okand',
                county: payload.county || 'okand',
                wants_legal_help: !!payload.wants_legal_help,
                wants_projector_contact: !!payload.wants_projector_contact,
                currency: 'SEK',
                value: SEGMENT_VALUE[payload.segment] || 20
            });
            showSuccess(form);
        } catch (err) {
            console.error('Lead submit failed', err);
            if (button) {
                button.disabled = false;
                button.innerHTML = originalLabel;
            }
            showError(form, 'Något gick fel. Försök igen om en stund.');
        }
    }

    /* --- Villkorade fält --------------------------------------------------- */
    // Ett fält med data-vk-show-when="segment=markagare" visas bara när
    // motsvarande radio/select har det värdet. Så slipper närboende svara på
    // frågor om markareal, och markägare slipper frågor om avstånd.

    function applyConditionals(root) {
        Array.prototype.forEach.call(root.querySelectorAll('[data-vk-show-when]'), function (el) {
            var parts = el.dataset.vkShowWhen.split('=');
            var field = parts[0];
            var wanted = (parts[1] || '').split('|');
            var input = root.querySelector('[name="' + field + '"]:checked')
                || root.querySelector('select[name="' + field + '"]');
            var current = input ? input.value : null;
            var visible = current !== null && wanted.indexOf(current) !== -1;
            el.hidden = !visible;
            el.classList.toggle('hidden', !visible);
            Array.prototype.forEach.call(el.querySelectorAll('[required]'), function (req) {
                req.disabled = !visible;
            });
        });
    }

    /* --- Silo-väljare ------------------------------------------------------ */

    function wireSegmentPicker() {
        Array.prototype.forEach.call(document.querySelectorAll('[data-vk-segment]'), function (el) {
            el.addEventListener('click', function () {
                var segment = el.dataset.vkSegment;
                rememberSegment(segment);
                track('select_segment', { segment: segment });
            });
        });
    }

    function init() {
        Array.prototype.forEach.call(document.querySelectorAll('[data-vk-lead-form]'), function (form) {
            form.addEventListener('submit', function (ev) {
                ev.preventDefault();
                submitForm(form);
            });
            form.addEventListener('change', function () { applyConditionals(form); });
            applyConditionals(form);

            var segment = form.dataset.segment;
            if (segment) {
                track('view_lead_form', { segment: segment });
            }
        });
        wireSegmentPicker();
    }

    window.VKSilo = {
        elareaForCounty: elareaForCounty,
        rememberSegment: rememberSegment,
        rememberedSegment: rememberedSegment,
        track: track,
        counties: Object.keys(COUNTY_TO_ELAREA)
    };

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
