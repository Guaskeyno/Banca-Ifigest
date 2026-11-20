/* Banca Ifigest — script del sito. Dipende da UIkit (assets/vendor/uikit). */
(function () {
  'use strict';

  /* Offcanvas accessibile: focus sul primo link, Esc gestito da UIkit, focus restituito al trigger */
  function initOffcanvasFocus() {
    var offcanvas = document.getElementById('tm-offcanvas');
    if (!offcanvas || typeof UIkit === 'undefined') return;
    var trigger = null;

    UIkit.util.on(offcanvas, 'beforeshow', function () { trigger = document.activeElement; });
    UIkit.util.on(offcanvas, 'shown', function () {
      var first = offcanvas.querySelector('.uk-offcanvas-bar a[href], .uk-offcanvas-bar button');
      if (first) first.focus();
    });
    UIkit.util.on(offcanvas, 'hidden', function () { if (trigger) trigger.focus(); });
  }

  /* Ricerca: risultati su cerca.html a partire da window.IFIGEST_SEARCH_INDEX */
  function normalize(str) {
    return (str || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');
  }

  function escapeHtml(str) {
    return str.replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  function excerpt(text, terms) {
    var plain = text;
    var lower = normalize(plain);
    var idx = -1;
    for (var i = 0; i < terms.length && idx < 0; i++) idx = lower.indexOf(terms[i]);
    if (idx < 0) return '';
    var start = Math.max(0, idx - 60);
    var snippet = plain.substr(start, 180);
    return (start > 0 ? '… ' : '') + snippet + (start + 180 < plain.length ? ' …' : '');
  }

  function initSearchPage() {
    var results = document.getElementById('tm-search-results');
    var status = document.getElementById('tm-search-status');
    var input = document.getElementById('tm-search-input');
    var index = window.IFIGEST_SEARCH_INDEX || [];
    if (!results || !status) return;

    var query = new URLSearchParams(window.location.search).get('q') || '';
    if (input) input.value = query;

    var terms = normalize(query).split(/\s+/).filter(Boolean);
    if (!terms.length) {
      status.textContent = 'Inserisci una parola chiave per cercare nel sito.';
      return;
    }

    var matches = index
      .map(function (page) {
        var haystack = normalize(page.title + ' ' + page.description + ' ' + page.text);
        var title = normalize(page.title);
        var score = 0;
        for (var i = 0; i < terms.length; i++) {
          if (haystack.indexOf(terms[i]) < 0) return null;
          score += title.indexOf(terms[i]) >= 0 ? 10 : 1;
        }
        return { page: page, score: score };
      })
      .filter(Boolean)
      .sort(function (a, b) { return b.score - a.score; });

    status.textContent = matches.length
      ? matches.length + (matches.length === 1 ? ' risultato' : ' risultati') + ' per “' + query + '”'
      : 'Nessun risultato per “' + query + '”.';

    results.innerHTML = matches
      .map(function (m) {
        var snippet = excerpt(m.page.text, terms) || m.page.description;
        return (
          '<li><a href="' + m.page.url + '">' + escapeHtml(m.page.title) + '</a>' +
          '<p>' + escapeHtml(snippet) + '</p></li>'
        );
      })
      .join('');
  }

  /* Animazione hero: con "riduci movimento" attivo mostra subito l'ultimo fotogramma */
  function initHeroVideo() {
    if (!window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    Array.prototype.forEach.call(document.querySelectorAll('.tm-hero-video'), function (video) {
      video.removeAttribute('autoplay');
      video.pause();
      var toEnd = function () { video.currentTime = Math.max(0, video.duration - 0.05); };
      if (video.readyState >= 1) toEnd(); else video.addEventListener('loadedmetadata', toEnd, { once: true });
    });
  }

  /* Lavora con noi: validazione del modulo e invio (vedi CAREERS_FORM_ENDPOINT in tools/build.py) */
  var MSG_REQUIRED = 'Compilare questo campo';
  var CV_MAX_BYTES = 5 * 1024 * 1024;
  var EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
  var PHONE_RE = /^\+39(3\d{8,9}|0\d{5,10})$/;  // +39 seguito da cellulare (3…) o fisso (0…)

  function initCareersForm() {
    var form = document.getElementById('tm-careers-form');
    if (!form) return;

    var status = document.getElementById('tm-form-status');
    var societa = form.elements.societa;
    var altroWrap = document.getElementById('societa-altro-wrap');
    var altro = form.elements.societa_altro;
    var messaggio = form.elements.messaggio;
    var counter = document.getElementById('messaggio-count');
    var cv = form.elements.cv;
    var submitted = false;
    var cvIsPdf = null;  // esito del controllo sul contenuto del file (intestazione %PDF)

    function phoneDigits(value) { return value.replace(/[\s.\-\/()]/g, ''); }

    var rules = {
      nome: function (el) { return el.value.trim() ? '' : MSG_REQUIRED; },
      cognome: function (el) { return el.value.trim() ? '' : MSG_REQUIRED; },
      email: function (el) {
        var v = el.value.trim();
        if (!v) return MSG_REQUIRED;
        return EMAIL_RE.test(v) ? '' : 'Inserire un indirizzo email valido (es. nome@dominio.it)';
      },
      telefono: function (el) {
        var v = phoneDigits(el.value.trim());
        if (!v) return MSG_REQUIRED;
        if (v.indexOf('+39') !== 0) return 'Il numero deve iniziare con il prefisso +39';
        return PHONE_RE.test(v) ? '' : 'Inserire un numero di telefono valido (es. +39 333 1234567)';
      },
      cv: function (el) {
        var file = el.files && el.files[0];
        if (!file) return MSG_REQUIRED;
        var isPdfName = /\.pdf$/i.test(file.name);
        var isPdfType = !file.type || file.type === 'application/pdf';
        if (!isPdfName || !isPdfType || cvIsPdf === false) return 'Il file deve essere in formato PDF';
        if (file.size > CV_MAX_BYTES) return 'Il file supera la dimensione massima di 5 MB';
        return '';
      },
      societa: function (el) { return el.value ? '' : MSG_REQUIRED; },
      societa_altro: function (el) {
        if (el.disabled) return '';
        return el.value.trim() ? '' : MSG_REQUIRED;
      },
      messaggio: function (el) {
        return el.value.length > el.maxLength ? 'Il messaggio può contenere al massimo ' + el.maxLength + ' caratteri' : '';
      },
      privacy: function (el) { return el.checked ? '' : MSG_REQUIRED; }
    };

    function showError(el, message) {
      var field = el.closest('.tm-field');
      var box = document.getElementById(el.id + '-error');
      if (box) box.textContent = message;
      if (field) field.classList.toggle('tm-invalid', !!message);
      if (message) el.setAttribute('aria-invalid', 'true'); else el.removeAttribute('aria-invalid');
    }

    function check(name) {
      var el = form.elements[name];
      var message = rules[name](el);
      showError(el, message);
      return !message;
    }

    function checkAll() {
      var firstInvalid = null;
      Object.keys(rules).forEach(function (name) {
        if (!check(name) && !firstInvalid) firstInvalid = form.elements[name];
      });
      return firstInvalid;
    }

    // "Altro (specificare)": mostra il campo aggiuntivo e lo rende obbligatorio
    function toggleAltro() {
      var show = societa.value === 'Altro (specificare)';
      altroWrap.hidden = !show;
      altro.disabled = !show;
      altro.required = show;
      if (!show) { altro.value = ''; showError(altro, ''); }
    }

    // Contenuto del CV: un PDF inizia con "%PDF"
    function inspectCv() {
      cvIsPdf = null;
      var file = cv.files && cv.files[0];
      if (!file || !window.FileReader) { check('cv'); return; }
      var reader = new FileReader();
      reader.onload = function () {
        var bytes = new Uint8Array(reader.result);
        cvIsPdf = bytes[0] === 0x25 && bytes[1] === 0x50 && bytes[2] === 0x44 && bytes[3] === 0x46;
        check('cv');
      };
      reader.readAsArrayBuffer(file.slice(0, 4));
    }

    societa.addEventListener('change', function () { toggleAltro(); check('societa'); });
    cv.addEventListener('change', inspectCv);
    messaggio.addEventListener('input', function () { counter.textContent = messaggio.value.length; });

    // Dopo il primo invio i messaggi si aggiornano mentre si scrive; prima, all'uscita da un campo compilato
    Object.keys(rules).forEach(function (name) {
      var el = form.elements[name];
      if (name === 'cv' || name === 'societa') return;
      el.addEventListener(el.type === 'checkbox' ? 'change' : 'input', function () { if (submitted) check(name); });
      el.addEventListener('blur', function () { if (submitted || el.value.trim()) check(name); });
    });

    function setStatus(message, isError) {
      status.hidden = false;
      status.textContent = message;
      status.classList.toggle('tm-status-error', !!isError);
    }

    form.addEventListener('submit', function (event) {
      event.preventDefault();
      submitted = true;
      status.hidden = true;
      var firstInvalid = checkAll();
      if (firstInvalid) {
        var target = firstInvalid.type === 'file' ? firstInvalid.closest('.tm-field') : firstInvalid;
        target.scrollIntoView({ behavior: 'smooth', block: 'center' });
        firstInvalid.focus({ preventScroll: true });
        return;
      }

      // Destinatari: Risorse Umane sempre, L&B Partners solo se scelta
      var recipients = [form.dataset.to];
      if (societa.value === 'L&B Partners SpA') recipients.push(form.dataset.toLbp);
      var data = new FormData(form);
      data.append('destinatari', recipients.join(','));

      var endpoint = form.dataset.endpoint;
      if (!endpoint) {
        setStatus('Il modulo è compilato correttamente. L’invio non è ancora attivo: il servizio di inoltro delle candidature è in fase di configurazione.');
        return;
      }

      var button = form.querySelector('button[type="submit"]');
      button.disabled = true;
      fetch(endpoint, { method: 'POST', body: data, headers: { Accept: 'application/json' } })
        .then(function (response) {
          if (!response.ok) throw new Error(response.status);
          form.reset();
          toggleAltro();
          counter.textContent = '0';
          submitted = false;
          setStatus('Grazie, la tua candidatura è stata inviata.');
        })
        .catch(function () {
          setStatus('Si è verificato un errore durante l’invio. Riprova più tardi.', true);
        })
        .then(function () { button.disabled = false; });
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    initHeroVideo();
    initOffcanvasFocus();
    initSearchPage();
    initCareersForm();
  });
})();
