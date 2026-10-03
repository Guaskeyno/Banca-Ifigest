/* Banca Ifigest — script del sito. Dipende da UIkit (assets/vendor/uikit). */
(function () {
  'use strict';

  var HEADER_OFFSET = 96;

  /* Menu mobile: "Contatti" chiude l'offcanvas e scorre alla sezione Sedi e Contatti */
  function initOffcanvasContacts() {
    var link = document.querySelector('.tm-offcanvas-contatti');
    var offcanvas = document.getElementById('tm-offcanvas');
    var target = document.getElementById('contatti');
    if (!link || !offcanvas || !target || typeof UIkit === 'undefined') return;

    link.addEventListener('click', function (e) {
      e.preventDefault();
      UIkit.util.once(offcanvas, 'hidden', function () {
        UIkit.scroll(link, { offset: 72 }).scrollTo(target);
      });
      UIkit.offcanvas(offcanvas).hide();
    });
  }

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

  /* Su pagine con hash (#contatti) caricate da un'altra pagina, compensa l'header fisso */
  function initHashOffset() {
    if (window.location.hash !== '#contatti') return;
    var target = document.getElementById('contatti');
    if (!target) return;
    window.addEventListener('load', function () {
      var top = target.getBoundingClientRect().top + window.pageYOffset - HEADER_OFFSET;
      window.scrollTo(0, top);
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    initOffcanvasContacts();
    initOffcanvasFocus();
    initSearchPage();
    initHashOffset();
  });
})();
