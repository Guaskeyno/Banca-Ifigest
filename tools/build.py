#!/usr/bin/env python3
"""Static page generator for the Banca Ifigest website.

Every page shares the same header, sub-navigation and footer. Edit the content below and run:

    python3 tools/build.py

The generated .html files are written to the repository root, together with
assets/js/search-index.js (used by the search page).
"""
import json
import re
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "Banca Ifigest"

# --------------------------------------------------------------------------
# Navigation
# --------------------------------------------------------------------------
NAV = [
    {
        "label": "Private Banking",
        "href": "private-banking.html",
        "children": [
            ("Servizi Bancari", "servizi-bancari.html"),
            ("Investimenti e Risparmio", "investimenti-e-risparmio.html"),
            ("Wealth Management", "wealth-management.html"),
            ("Collocamento", "collocamento.html"),
            ("Consulenza Finanziaria", "consulenza-finanziaria.html"),
        ],
    },
    {
        "label": "Investment Banking",
        "href": "investment-banking.html",
        "children": [
            ("Finanza Strutturata", "finanza-strutturata.html"),
            ("Lombard Loans", "lombard-loans.html"),
            ("Debt Advisory", "debt-advisory.html"),
        ],
    },
    {
        "label": "Il Gruppo",
        "href": "il-gruppo.html",
        "children": [
            ("Chi Siamo", "chi-siamo.html"),
            ("Governance", "governance.html"),
            ("Info Prodotti", "info-prodotti.html"),
            ("Sostenibilità", "sostenibilita.html"),
            ("Area Soci", "area-soci.html"),
            ("Whistleblowing", "whistleblowing.html"),
        ],
    },
]

BANCA_ONLINE_URL = "https://areariservata.bancaifigest.it/CBL-MITO-WA-2.0/?v=451#!/access/login"
LINKEDIN_URL = "https://www.linkedin.com/company/banca-ifigest/"

FOOTER_LINKS = [
    ("Lavora con noi", "#"),
    ("Schede Prodotto", "info-prodotti.html#schede-prodotto"),
    ("Trasparenza", "trasparenza.html"),
    ("Whistleblowing", "whistleblowing.html"),
    ("Dichiarazione di Accessibilità", "dichiarazione-accessibilita.html"),
    ("Disconoscimento operazioni", "disconoscimento-operazioni.html"),
]

SEDI = [
    [
        ("Firenze", [
            {"name": "Sede Legale e Direzionale", "lines": ["Piazza Santa Maria Soprarno, 1", "50125 Firenze"], "tel": "055.24631", "email": "firenze@bancaifigest.it"},
            {"name": "Filiale S. Trinità", "lines": ["Piazza Santa Trinita, 1", "50123 Firenze"], "tel": "055.277331"},
            {"name": "Filiale V. Giacomini", "lines": ["Via Giacomini, 22 24 26", "50132 Firenze"], "tel": "055.40491"},
        ]),
    ],
    [
        ("Milano", [{"lines": ["Via Durini, 27", "20122 Milano (MI)"], "tel": "02.7788011", "email": "milano@bancaifigest.it"}]),
        ("Roma", [{"lines": ["Via Lima, 10", "00198 Roma"], "tel": "06.8535951", "email": "roma@bancaifigest.it"}]),
    ],
    [
        ("Torino", [{"lines": ["Piazza San Carlo, 183", "10123 Torino (TO)"], "tel": "011.55141", "email": "torino@bancaifigest.it"}]),
        ("Prato", [{"lines": ["Via Valentini, 7", "59100 Prato (PO)"], "tel": "0574.402711", "email": "prato@bancaifigest.it"}]),
    ],
    [
        ("Genova", [{"lines": ["Via XX Settembre, 37 interno 1", "16121 Genova (GE)"], "tel": "010.553741", "email": "genova@bancaifigest.it"}]),
    ],
]

ACTIVE = ' class="uk-active"'
CURRENT = ' aria-current="page"'
SCROLL = ' uk-scroll="offset: 96"'

# --------------------------------------------------------------------------
# Partials
# --------------------------------------------------------------------------
STRIPES = (
    '<svg class="tm-stripes" viewBox="0 0 274 400" preserveAspectRatio="none" aria-hidden="true" focusable="false">'
    + "".join(
        f'<rect x="{x}" y="0" width="{w}" height="400"/>'
        for x, w in [(0, 2), (6, 4), (18, 8), (36, 10), (58, 12), (84, 14), (114, 16), (154, 24), (202, 24), (250, 24)]
    )
    + "</svg>"
)


def tel_href(num):
    return "tel:+39" + re.sub(r"\D", "", num)


def placeholder(cls="", label="Immagine"):
    return (
        f'<div class="tm-placeholder {cls}" role="img" aria-label="{label} segnaposto">'
        '<span uk-icon="icon: image; ratio: 2"></span></div>'
    )


def section_of(slug):
    for item in NAV:
        if slug == item["href"] or slug in [h for _, h in item["children"]]:
            return item
    return None


def header(slug):
    current = section_of(slug)

    def desktop_item(item):
        active = " uk-active" if item is current else ""
        sub = "".join(
            f'<li{ACTIVE if href == slug else ""}><a href="{href}">{escape(label)}</a></li>'
            for label, href in item["children"]
        )
        return (
            f'<li class="uk-parent{active}"><a href="{item["href"]}">{escape(item["label"])} '
            '<span uk-navbar-parent-icon></span></a>'
            '<div class="uk-navbar-dropdown"><ul class="uk-nav uk-navbar-dropdown-nav">'
            f"{sub}</ul></div></li>"
        )

    def mobile_item(item):
        sub = "".join(
            f'<li{ACTIVE if href == slug else ""}><a href="{href}">{escape(label)}</a></li>'
            for label, href in item["children"]
        )
        opened = " uk-open" if item is current else ""
        return (
            f'<li class="uk-parent{opened}"><a href="#">{escape(item["label"])} <span uk-nav-parent-icon></span></a>'
            f'<ul class="uk-nav-sub"><li><a href="{item["href"]}">Panoramica</a></li>{sub}</ul></li>'
        )

    desktop = "".join(desktop_item(i) for i in NAV)
    mobile = "".join(mobile_item(i) for i in NAV)
    return f"""
<a class="tm-skip-link" href="#main">Vai al contenuto</a>
<header class="tm-header uk-visible@l">
  <div uk-sticky="sel-target: .uk-navbar-container; cls-active: uk-navbar-sticky">
    <div class="uk-navbar-container">
      <div class="uk-container uk-container-expand">
        <nav class="uk-navbar" aria-label="Navigazione principale" uk-navbar="align: left; dropbar: true; dropbar-anchor: !.uk-navbar-container; target-y: !.uk-navbar-container; delay-hide: 200">
          <div class="uk-navbar-left">
            <a href="index.html" class="uk-navbar-item uk-logo" aria-label="{SITE} - Torna alla Home">
              <img src="assets/img/logo-ifigest.svg" width="160" height="64" alt="{SITE} - Gruppo Bancario">
            </a>
          </div>
          <div class="uk-navbar-right">
            <ul class="uk-navbar-nav">
              {desktop}
              <li{ACTIVE if slug == "contatti.html" else ""}><a href="contatti.html">Contatti</a></li>
            </ul>
            <div class="uk-navbar-item">
              <a class="uk-button tm-button-online" href="{BANCA_ONLINE_URL}" target="_blank" rel="noopener"><span uk-icon="icon: lock; ratio: .8"></span> Banca Online</a>
            </div>
            <a class="uk-navbar-toggle tm-search-toggle" href="#" uk-search-icon aria-label="Cerca"></a>
            <div class="uk-navbar-dropdown tm-search-drop" uk-drop="mode: click; pos: bottom-right; target-y: !.uk-navbar-container">
              <form class="uk-search uk-search-default uk-width-1-1" action="cerca.html" method="get" role="search">
                <span uk-search-icon></span>
                <input class="uk-search-input" type="search" name="q" placeholder="Cerca" aria-label="Cerca nel sito" required autofocus>
              </form>
            </div>
          </div>
        </nav>
      </div>
    </div>
  </div>
</header>

<header class="tm-header-mobile uk-hidden@l">
  <div uk-sticky="sel-target: .uk-navbar-container; cls-active: uk-navbar-sticky">
    <div class="uk-navbar-container">
      <div class="uk-container uk-container-expand">
        <nav class="uk-navbar" aria-label="Navigazione mobile" uk-navbar>
          <div class="uk-navbar-left">
            <a href="index.html" class="uk-navbar-item uk-logo" aria-label="{SITE} - Torna alla Home">
              <img src="assets/img/logo-ifigest.svg" width="120" height="48" alt="{SITE} - Gruppo Bancario">
            </a>
          </div>
          <div class="uk-navbar-right">
            <a class="uk-navbar-toggle" href="#tm-offcanvas" uk-toggle aria-label="Apri il menu"><span uk-navbar-toggle-icon></span></a>
          </div>
        </nav>
      </div>
    </div>
  </div>
  <div id="tm-offcanvas" uk-offcanvas="flip: true; overlay: true">
    <div class="uk-offcanvas-bar">
      <button class="uk-offcanvas-close" type="button" uk-close aria-label="Chiudi il menu"></button>
      <ul class="uk-nav uk-nav-default" uk-nav="multiple: false">
        {mobile}
        <li{ACTIVE if slug == "contatti.html" else ""}><a href="contatti.html">Contatti</a></li>
      </ul>
      <a class="uk-button tm-button-online uk-width-1-1 uk-margin-medium-top" href="{BANCA_ONLINE_URL}" target="_blank" rel="noopener"><span uk-icon="icon: lock; ratio: .8"></span> Banca Online</a>
      <form class="uk-search uk-search-default uk-width-1-1 uk-margin-top" action="cerca.html" method="get" role="search">
        <span uk-search-icon></span>
        <input class="uk-search-input" type="search" name="q" placeholder="Cerca" aria-label="Cerca nel sito" required>
      </form>
    </div>
  </div>
</header>
"""


def subnav(slug):
    item = section_of(slug)
    if not item:
        return ""
    links = "".join(
        f'<li{ACTIVE if href == slug else ""}><a href="{href}"{CURRENT if href == slug else ""}>{escape(label)}</a></li>'
        for label, href in item["children"]
    )
    return f"""
<nav class="tm-subnav" aria-label="{escape(item['label'])}">
  <div class="uk-container uk-container-large">
    <ul class="tm-subnav-list">{links}</ul>
  </div>
</nav>"""


def hero(title, subtitle="", image=True):
    sub = f'<p class="tm-hero-subtitle">{subtitle}</p>' if subtitle else ""
    media = (
        f'<div class="tm-hero-media">{placeholder("tm-placeholder-cover")}{STRIPES}</div>' if image else ""
    )
    return f"""
<section class="tm-hero{'' if image else ' tm-hero-plain'}">
  {media}
  <div class="tm-hero-title">
    <div class="uk-container uk-container-large" uk-scrollspy="cls: uk-animation-fade; delay: 150">
      <h1 class="tm-hero-heading">{title}</h1>
      {sub}
    </div>
  </div>
</section>"""


def footer():
    # Struttura come il footer del riferimento: logo | link orizzontali | social + copyright
    rows = [FOOTER_LINKS[:3], FOOTER_LINKS[3:]]
    items = []
    for n, row in enumerate(rows):
        for i, (l, h) in enumerate(row):
            sep = ' class="no-separator"' if i == len(row) - 1 else ""
            items.append(f'<li{sep}><a href="{h}">{escape(l)}</a></li>')
        if n < len(rows) - 1:
            items.append('<li class="force-break" aria-hidden="true"></li>')
    return f"""
<footer class="tm-footer">
  <div class="uk-container uk-container-expand">
    <div class="uk-grid tm-footer-grid" uk-grid>
      <div class="uk-width-1-4@m uk-flex uk-flex-middle">
        <div>
          <a href="index.html" aria-label="{SITE} - Torna alla Home"><img src="assets/img/logo-ifigest-footer.svg" width="134" height="32" alt="{SITE} - Gruppo Bancario"></a>
          <p class="tm-footer-small">Banca Ifigest S.p.A.<br>P.za Santa Maria Soprarno, 1 - 50125 Firenze<br>
            <a href="tel:+3905521631">+39 055 21631</a><br>
            <a href="mailto:segreteria.ifigest@legalmail.it">segreteria.ifigest@legalmail.it</a></p>
        </div>
      </div>
      <div class="uk-width-1-2@m uk-flex uk-flex-middle">
        <nav class="tm-footer-small uk-width-1-1" aria-label="Link utili">
          <ul class="tm-list-horizontal">{"".join(items)}</ul>
          <p class="tm-footer-legal">Capitale sociale euro 37.554.277,00 i.v. | Albo delle Banche n. 5485 | Albo dei Gruppi Bancari n. 3185</p>
        </nav>
      </div>
      <div class="uk-width-1-4@m uk-flex uk-flex-middle">
        <div class="uk-width-1-1 uk-text-right@m">
          <a href="{LINKEDIN_URL}" class="tm-footer-social" target="_blank" rel="noopener" aria-label="Banca Ifigest su LinkedIn"><span uk-icon="icon: linkedin; ratio: 1.6"></span></a>
          <p class="tm-footer-small">&copy;2026</p>
        </div>
      </div>
    </div>
  </div>
</footer>"""


def page(slug, title, description, body):
    full_title = SITE if slug == "index.html" else f"{title} – {SITE}"
    return f"""<!doctype html>
<html lang="it">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(full_title)}</title>
  <meta name="description" content="{escape(description)}">
  <link rel="icon" href="assets/img/favicon.svg" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Lato:wght@400;500;700&display=swap">
  <link rel="preload" href="assets/fonts/meghana-webfont.woff2" as="font" type="font/woff2" crossorigin>
  <!-- Libreria: UIkit (MIT) -->
  <link rel="stylesheet" href="assets/vendor/uikit/css/uikit.min.css">
  <!-- Tema Banca Ifigest -->
  <link rel="stylesheet" href="assets/css/theme.css">
</head>
<body class="page-{slug.replace('.html', '')}">
{header(slug)}
{subnav(slug)}
<main id="main">
{body}
</main>
{footer()}
<!-- Libreria: UIkit (MIT) -->
<script src="assets/vendor/uikit/js/uikit.min.js"></script>
<script src="assets/vendor/uikit/js/uikit-icons.min.js"></script>
<!-- Script del sito -->
<script src="assets/js/search-index.js"></script>
<script src="assets/js/main.js"></script>
</body>
</html>
"""


# --------------------------------------------------------------------------
# Content components
# --------------------------------------------------------------------------
def card(title, text, href, external=False):
    target = ' target="_blank" rel="noopener"' if external else ""
    return f"""
      <div>
        <a class="tm-card" href="{href}"{target}>
          <div class="tm-card-body">
            <h3 class="tm-card-title">{title}</h3>
            <p class="tm-card-text">{text}</p>
          </div>
          <span class="tm-card-arrow" aria-hidden="true"><span uk-icon="arrow-right"></span></span>
        </a>
      </div>"""


def cards(items, extra=""):
    return f"""
<section class="uk-section tm-section-cards{extra}">
  <div class="uk-container uk-container-large">
    <div class="uk-grid-small uk-child-width-1-2@s uk-child-width-1-3@m uk-grid-match" uk-grid uk-scrollspy="target: > div; cls: uk-animation-slide-bottom-small; delay: 80">
      {"".join(card(*i) for i in items)}
    </div>
  </div>
</section>"""


def lead(html, color="primary", extra=""):
    return f"""
<section class="uk-section tm-section-lead{extra}">
  <div class="uk-container uk-container-large">
    <div class="tm-lead tm-lead-{color}">{html}</div>
  </div>
</section>"""


def split(content, media_first=False, sid="", extra=""):
    media = f'<div class="tm-split-media">{placeholder("tm-placeholder-square")}</div>'
    text = f'<div class="tm-split-content">{content}</div>'
    inner = media + text if media_first else text + media
    id_attr = f' id="{sid}"' if sid else ""
    return f"""
<section class="uk-section tm-section-split{extra}"{id_attr}>
  <div class="uk-container uk-container-large">
    <div class="tm-split{' tm-split-reverse' if media_first else ''}">{inner}</div>
  </div>
</section>"""


def block(title, body="", level="h2", extra=""):
    return f'<div class="tm-block{extra}"><{level} class="tm-block-title">{title}</{level}>{body}</div>'


def feature(title, text, button, href, media_first=True):
    media = f'<div class="tm-feature-media">{placeholder("tm-placeholder-cover")}</div>'
    content = (
        f'<div class="tm-feature-content"><h2 class="tm-feature-title">{title}</h2><p>{text}</p>'
        f'<a class="uk-button uk-button-default tm-button-light-outline" href="{href}"{SCROLL if href.startswith("#") else ""}>{button}</a></div>'
    )
    inner = media + content if media_first else content + media
    return f"""
<section class="uk-section uk-section-xsmall tm-section-feature">
  <div class="uk-container uk-container-large">
    <div class="tm-feature{'' if media_first else ' tm-feature-reverse'}">{inner}</div>
  </div>
</section>"""


def doc_list(items):
    lis = "".join(
        f'<li><a href="#"><span uk-icon="icon: file-pdf"></span><span>{i}</span></a></li>' for i in items
    )
    return f'<ul class="tm-doc-list">{lis}</ul>'


def link_list(items):
    lis = "".join(f'<li>{i}</li>' for i in items)
    return f'<ul class="tm-bullet-list">{lis}</ul>'


def button(label, href, style="primary"):
    scroll = ' uk-scroll="offset: 96"' if href.startswith("#") else ""
    return f'<a class="uk-button uk-button-{style}" href="{href}"{scroll}>{label}</a>'


# --------------------------------------------------------------------------
# Pages
# --------------------------------------------------------------------------
PAGES = []


def add(slug, title, description, body, keywords=""):
    PAGES.append((slug, title, description, body, keywords))


# Home ----------------------------------------------------------------------
add(
    "index.html",
    "Home",
    "Banca Ifigest: dal 1987 una relazione di fiducia per chi cerca una banca su misura, non di serie.",
    hero(
        "Un nuovo movimento finanziario",
        "Dal 1987, offriamo una relazione di fiducia per chi cerca una banca su misura, non di serie",
    )
    + """
<section class="uk-section uk-section-large tm-section-intro">
  <div class="uk-container uk-container-large">
    <div class="uk-grid-large uk-child-width-1-2@m" uk-grid>
      <div>
        <h2 class="tm-intro-heading">Per noi il patrimonio è molto più di un numero: è il riflesso di una vita di scelte, di un'azienda costruita, di una famiglia da proteggere.</h2>
      </div>
      <div>
        <p>Per questo da quasi quarant'anni lavoriamo nel modo opposto a come si è sviluppata gran parte della finanza italiana: niente call center, niente prodotti standardizzati, niente conflitti d'interesse legati a una casa madre.</p>
        <p>Ogni cliente ha un private banker che lo conosce, a cui risponde personalmente, e che lo accompagna nelle sue decisioni patrimoniali. Questo è il Gruppo Bancario Ifigest: la solidità di un grande gruppo bancario, e la prossimità di un rapporto personale.</p>
        <a class="uk-button uk-button-primary uk-margin-top" href="il-gruppo.html">Scopri il Gruppo</a>
      </div>
    </div>
  </div>
</section>"""
    + cards(
        [
            ("Private Banking", "Un banker dedicato, un conto corrente progettato per esigenze complesse, e un'interlocuzione diretta con la direzione su ogni decisione importante", "private-banking.html"),
            ("Gestioni Patrimoniali", "Oltre 30 linee di gestione attiva, costruite per profilo di rischio e orizzonte. La nostra priorità: proteggere il capitale e generare valore nel tempo", "investimenti-e-risparmio.html#gestioni-patrimoniali"),
            ("Consulenza", "Raccomandazioni personalizzate su tutti i principali strumenti finanziari, con la libertà di scegliere e la trasparenza di chi non vende prodotti propri", "consulenza-finanziaria.html"),
            ("Family Office", "Patrimonio personale, familiare, professionale: una visione d'insieme, con soluzioni di pianificazione successoria, fiscale e immobiliare", "wealth-management.html"),
            ("Corporate Finance", "Con L&amp;B Partners affianchiamo imprenditori e PMI in operazioni di M&amp;A, capital raising e ristrutturazione del capitale. Una sola banca, dal patrimonio all'azienda", "investment-banking.html"),
            ("Fundstore", "La nostra piattaforma per investire in oltre 8.000 fondi, con commissioni trasparenti e un approccio costruito sull'autonomia dell'investitore informato", "https://www.fundstore.it", True),
        ],
        " tm-section-cards-home",
    ),
    "private banking gestioni patrimoniali consulenza family office corporate finance fundstore",
)

# Private Banking -----------------------------------------------------------
add(
    "private-banking.html",
    "Private Banking",
    "La competenza di un gestore dedicato, la libertà di una banca indipendente.",
    hero("Private Banking", "La competenza di un gestore dedicato, la libertà di una banca indipendente")
    + lead(
        "<p>La nostra offerta è costruita attorno alle esigenze reali: dalla gestione del conto quotidiano alla pianificazione patrimoniale di lungo periodo, con soluzioni integrate per il privato, la famiglia e l'imprenditore.</p>",
        "dark",
    )
    + cards(
        [
            ("Servizi Bancari", "Servizi bancari per esigenze complesse, e un'interlocuzione diretta con la direzione su ogni decisione importante", "servizi-bancari.html"),
            ("Investimenti e Risparmio", "Oltre 30 linee di gestione attiva, costruite per profilo di rischio e orizzonte. La nostra priorità: proteggere il capitale e generare valore nel tempo", "investimenti-e-risparmio.html"),
            ("Wealth Management", "Patrimonio personale, familiare, professionale: una visione d'insieme, con soluzioni di pianificazione successoria, fiscale e immobiliare", "wealth-management.html"),
            ("Collocamento", "Assicurazione Vita in partnership con CNP Vita Assicura, per assicurare il futuro del patrimonio", "collocamento.html"),
            ("Consulenza Finanziaria", "Raccomandazioni personalizzate su tutti i principali strumenti finanziari, con la libertà di scegliere e la trasparenza di chi non vende prodotti propri", "consulenza-finanziaria.html"),
        ]
    ),
)

add(
    "servizi-bancari.html",
    "Servizi Bancari",
    "Un conto corrente progettato per esigenze complesse, e un'interlocuzione diretta con la direzione su ogni decisione importante.",
    hero(
        "Servizi Bancari",
        "Un conto corrente progettato per esigenze complesse, e un’interlocuzione diretta con la direzione su ogni decisione importante",
    )
    + lead(
        "<p>I servizi bancari Ifigest sono pensati per una clientela selezionata che richiede qualità, riservatezza e operatività senza compromessi. Dal conto corrente alla carta di credito premium, ogni strumento accompagna la vita quotidiana con la stessa cura che dedichiamo alla gestione del patrimonio.</p>"
    )
    + feature(
        "Conto Corrente",
        "Il Conto Remunerato di Banca Ifigest offre la possibilità di far fruttare la liquidità disponibile, con condizioni trasparenti e competitive, mantenendo la piena disponibilità delle somme depositate.",
        "Apri il conto Ifigest",
        "contatti.html",
    )
    + feature(
        "Carta Ifigest",
        "La carta di credito Banca Ifigest, in partnership con Nexi, offre i massimi livelli di sicurezza e flessibilità per i pagamenti quotidiani e online, con le funzionalità Apple Pay per i pagamenti contactless. Disponibile nelle versioni individuale, aziendale e Black.",
        "Contatta una filiale",
        "contatti.html",
        media_first=False,
    )
    + f"""
<section class="uk-section uk-section-xsmall">
  <div class="uk-container uk-container-large">
    {placeholder("tm-placeholder-wide")}
    <p class="tm-note">Consulta i fogli informativi relativi ai conti correnti e alle carte <a href="info-prodotti.html#trasparenza">qui</a>.</p>
  </div>
</section>""",
    "conto corrente carta di credito nexi apple pay conto remunerato",
)

add(
    "investimenti-e-risparmio.html",
    "Investimenti e Risparmio",
    "Soluzioni costruite sugli obiettivi della nostra clientela.",
    hero("Investimenti e Risparmio", "Soluzioni costruite sugli obiettivi della nostra clientela")
    + lead(
        "<p>L'attività di investimento di Banca Ifigest è focalizzata sulla ricerca della rivalutazione del capitale nel medio-lungo periodo, attraverso strategie di gestione attiva, diversificazione e un'offerta aperta ai migliori strumenti del mercato.</p>"
    )
    + split(
        block(
            "Gestioni Patrimoniali",
            "<p>Le Gestioni Patrimoniali di Banca Ifigest non replicano passivamente la struttura del benchmark, ma operano in modo attivo sulla base di strategie di investimento globali e diversificate sulle principali asset class, con ottimizzazione dei portafogli e utilizzo di tutti gli strumenti del mercato finanziario.</p>"
            "<p>Il team di gestione opera dai desk di Milano, Firenze e Roma, con competenze in analisi dei mercati finanziari, selezione di obbligazioni governative e societarie e stock picking azionario.</p>"
            "<p>In virtù degli obiettivi di investimento del cliente, sono altresì disponibili linee di investimento flessibili e personalizzabili con le specifiche esigenze di ogni investitore.</p>"
            "<p>Grazie alle competenze del proprio team di gestione, Banca Ifigest fornisce altresì consulenza e servizi di asset management per alcune primarie Società di gestione estere, attive su Fondi comuni e SICAV dedicati sia a clientela privata che istituzionale.</p>",
        ),
        sid="gestioni-patrimoniali",
    )
    + split(
        block(
            "Consulenza Evoluta",
            "<p>In sintonia con il profilo e con gli obiettivi di investimento del cliente, il servizio di consulenza di Banca Ifigest fornisce raccomandazioni personalizzate su tutti i principali strumenti finanziari. Un servizio costruito sulla conoscenza approfondita del cliente, libero da condizionamenti di prodotto grazie all'architettura aperta della banca.</p>",
        )
        + block("Piani Individuali di Risparmio (PIR)", level="h3", extra=" tm-block-small")
        + block("Piani di Accumulo del Capitale (PAC)", level="h3", extra=" tm-block-small"),
        media_first=True,
        sid="consulenza-evoluta",
    )
    + split(block("Trading e Negoziazione Titoli"), sid="trading"),
    "gestioni patrimoniali consulenza evoluta pir pac trading negoziazione titoli asset management",
)

add(
    "wealth-management.html",
    "Wealth Management",
    "Un unico punto di riferimento per proteggere, pianificare e ottimizzare il patrimonio personale, familiare e d'impresa.",
    hero(
        "Wealth Management",
        "Un unico punto di riferimento per proteggere, pianificare e ottimizzare il patrimonio personale, familiare e d'impresa.",
    )
    + lead(
        "<p>Sevian Fiduciaria è la società fiduciaria, parte del Gruppo, che affianca la banca con servizi di intestazione fiduciaria, amministrazione e pianificazione successoria, offrendo a clienti privati, famiglie e imprese uno strumento di riservatezza, protezione e continuità nella gestione del patrimonio.</p>"
    )
    + split(
        block(
            "Intestazione Fiduciaria",
            "<p>Gestione di partecipazioni, strumenti finanziari e altri beni tramite intestazione alla fiduciaria, nel pieno rispetto della riservatezza e della titolarità sostanziale del cliente.</p>",
        )
        + block(
            "Amministrazione di Patrimoni",
            "<p>Amministrazione di patrimoni mobiliari, con rendicontazione puntuale e supporto negli adempimenti, anche senza intestazione dei beni.</p>",
        )
    )
    + split(
        block(
            "Pianificazione Successoria",
            "<p>Strutturazione e tutela del patrimonio in ottica di passaggio generazionale, per trasmettere valore tra le generazioni con serenità e continuità.</p>",
        )
        + block(
            "Riservatezza e Protezione",
            "<p>Separazione e protezione degli asset, a garanzia di continuità e riservatezza nella gestione del patrimonio nel tempo.</p>",
        ),
        media_first=True,
    )
    + feature(
        "Valore di Gruppo",
        "Operando all'interno del Gruppo Bancario, Sevian Fiduciaria unisce la propria specializzazione alle competenze bancarie, di gestione e di consulenza della banca.",
        "Parla con un referente",
        "contatti.html",
    ),
    "sevian fiduciaria intestazione fiduciaria amministrazione patrimoni pianificazione successoria family office",
)

CNP = (
    "<p>Banca Ifigest è iscritta nel RUI (Registro Unico Assicurativo tenuto dall'IVASS), alla Sezione D con il n. D000407542. "
    "La Banca è soggetta alla vigilanza dell'IVASS e svolge attività di intermediazione assicurativa in forza di un contratto stipulato in esclusiva con la Società CNP Vita Assicura S.p.A.</p>"
    "<p>Il Gruppo CNP Assurances, compagnia assicurativa dal 1850, vanta 6.500 dipendenti in tutto il mondo e 46 milioni di assicurati. "
    "Apprezzati dai mercati globali per il miglior rating ESG nel settore assicurativo (AAA fonte MSCI) e un rating finanziario: Fitch A+, Standard &amp; Poor's A+ e Moody's A1. "
    "L'Italia rappresenta un mercato strategico per il Gruppo, dove opera da oltre 20 anni ed è oggi il 5° player nel business Vita.</p>"
)
CTA_CONSULENZA = button("Richiedi una consulenza", "contatti.html")

add(
    "collocamento.html",
    "Collocamento",
    "Guarda con serenità al futuro, con soluzioni a capitale garantito e diversificazione.",
    hero("Collocamento", "Guarda con serenità al futuro, con soluzioni a capitale garantito e diversificazione")
    + split(block("CNP Vita Assicura", CNP + CTA_CONSULENZA), sid="cnp-vita-assicura", extra=" tm-section-split-first")
    + split(block("Club Deal", CTA_CONSULENZA), media_first=True, sid="club-deal")
    + split(block("FIA", CTA_CONSULENZA), sid="fia")
    + split(block("Certificati", CTA_CONSULENZA), media_first=True, sid="certificati")
    + split(block("Polizze", CTA_CONSULENZA), sid="polizze"),
    "assicurazione vita cnp club deal fia certificati polizze ivass rui",
)

add(
    "consulenza-finanziaria.html",
    "Consulenza Finanziaria",
    "Consulenza finanziaria Banca Ifigest.",
    hero("Consulenza Finanziaria"),
    "consulenza",
)

# Investment Banking --------------------------------------------------------
add(
    "investment-banking.html",
    "Investment Banking",
    "Soluzioni finanziarie specializzate per imprese, professionisti e istituzioni.",
    hero("Investment Banking", "Soluzioni finanziarie specializzate per imprese, professionisti e istituzioni")
    + lead(
        "<p>Affianchiamo imprese, professionisti e investitori istituzionali con un'offerta di finanza strutturata, finanziamenti su misura e advisory strategico. Un partner bancario indipendente, capace di combinare competenza tecnica e relazioni di lungo termine.</p>",
        "dark",
    )
    + cards(
        [
            ("Finanza Strutturata", "Operazioni di finanza strutturata su misura: project finance, acquisition finance, cartolarizzazioni e cessione del credito d'imposta", "finanza-strutturata.html"),
            ("Lombard Loans", "Finanziamento garantito dal nostro portfolio: liquidità immediata senza liquidare gli investimenti, mantenendo intatta la strategia di investimento.", "lombard-loans.html"),
            ("Debt Advisory", "Supporto a imprese e imprenditori nell'ottimizzazione della struttura finanziaria, nella negoziazione con il sistema bancario e nella ricerca di strumenti alternativi.", "debt-advisory.html"),
        ]
    ),
    "business imprese finanza strutturata lombard debt advisory",
)
add("finanza-strutturata.html", "Finanza Strutturata", "Finanza strutturata Banca Ifigest.", hero("Finanza Strutturata"), "project finance acquisition finance")
add("lombard-loans.html", "Lombard Loans", "Lombard Loans Banca Ifigest.", hero("Lombard Loans"), "finanziamento garantito")
add("debt-advisory.html", "Debt Advisory", "Debt Advisory Banca Ifigest.", hero("Debt Advisory"), "struttura finanziaria")

# Il Gruppo -----------------------------------------------------------------
add(
    "il-gruppo.html",
    "Il Gruppo",
    "Gruppo Bancario Ifigest: dal cuore di Firenze, un nuovo movimento finanziario.",
    hero("Gruppo Bancario Ifigest", "Dal cuore di Firenze, un nuovo movimento finanziario")
    + lead(
        "<p>Il Gruppo Bancario Ifigest, espressione autentica di esperienza e professionalità, nasce per costruire servizi evoluti e interconnessi e generare soluzioni innovative, in grado di rispondere alla complessità dei mercati contemporanei.</p>"
        "<p>Un unico hub al servizio di aziende, famiglie imprenditoriali e privati caratterizzato da un servizio globale in-house a 360° che unisce competenze diversificate per un'offerta su misura di ogni esigenza.</p>",
        "dark",
    )
    + cards(
        [
            ("Chi Siamo", "Gruppo Bancario, storia, management, mission, filosofia di gestione e architettura aperta", "chi-siamo.html"),
            ("Governance", "Dati societari, documentazione, privacy, Modello 231 e BRRD", "governance.html"),
            ("Info Prodotti", "Trasparenza, Reclami, Sede di Esecuzione, PSD2, Schede Prodotto, ACF, FEA", "info-prodotti.html"),
            ("Sostenibilità", "Principi ESG, obiettivi, prodotti sostenibili, governance e policy", "sostenibilita.html"),
            ("Area Soci", "Avvisi, documenti e informazioni sul capitale sociale", "area-soci.html"),
            ("Whistleblowing", "Segnalazione di violazioni, in conformità al D.Lgs. n. 24/2023", "whistleblowing.html"),
        ]
    ),
    "gruppo bancario sevian fundstore soprarno sgr",
)

TIMELINE = [
    ("1987", "Fondazione di Banca Ifigest in Firenze"),
    ("2001", "Autorizzazione della Banca d'Italia all'esercizio dei servizi bancari e di investimento"),
    ("2005", "Apertura delle filiali nelle principali piazze italiane: Milano, Torino, Roma, Prato, Genova, Santa Croce sull'Arno."),
    ("2012", "Costituzione di Sevian Fiduciaria, lancio di Fundstore e costituzione di Soprarno SGR, completando il Gruppo Bancario."),
]
timeline_items = "".join(
    f'<li class="uk-width-1-1 uk-width-1-3@m uk-flex"><div class="tm-timeline-item uk-width-1-1"><h3 class="tm-timeline-year">{y}</h3><p>{t}</p></div></li>'
    for y, t in TIMELINE
)
# Righe verticali decrescenti, come "lines-blue.svg" del riferimento (147x490)
TIMELINE_LINES = (
    '<svg class="tm-timeline-lines" viewBox="0 0 146.5 490" aria-hidden="true" focusable="false">'
    + "".join(f'<rect x="{x}" width="{w}" height="490"/>' for x, w in [(0, 7.41), (28.48, 6.75), (56.96, 6.09), (85.44, 5.43), (113.92, 4.77), (142.39, 4.11)])
    + "</svg>"
)

add(
    "chi-siamo.html",
    "Chi Siamo",
    "Una realtà indipendente, specializzata nella gestione e valorizzazione dei patrimoni privati e istituzionali.",
    hero("Chi Siamo", "Una realtà indipendente, specializzata nella gestione e valorizzazione dei patrimoni privati e istituzionali")
    + split(
        '<p class="tm-lead tm-lead-primary">Il Gruppo Bancario Ifigest è fondato su principi di trasparenza, indipendenza e orientamento al cliente, integrando competenze bancarie, fiduciarie e di gestione del risparmio.</p>'
        "<p>Banca Ifigest è una banca privata e indipendente con sede a Firenze, iscritta all'Albo delle Banche al Num. 5485 e all'Albo dei Gruppi Bancari al num. 3185. Aderente al Fondo Interbancario di tutela dei depositi e al Fondo Nazionale di Garanzia.</p>"
        "<p>Intermediario autorizzato all'esercizio dei servizi bancari e di investimento di collocamento, ricezione e trasmissione di ordini, gestione individuale di portafoglio di investimento e consulenza in materia di investimenti dalla Banca d'Italia con delibera del 19 aprile 2001. Il Gruppo comprende Banca Ifigest S.p.A., Sevian Fiduciaria, Fundstore e Soprarno SGR.</p>",
        extra=" tm-section-split-center",
    )
    + f"""
<section class="uk-section tm-section-timeline-title" id="storia" aria-labelledby="storia-title">
  <div class="uk-container uk-container-large">
    <h2 id="storia-title" class="tm-section-title">La nostra storia</h2>
  </div>
</section>
<section class="tm-section-timeline" aria-label="La nostra storia, cronologia">
  <div class="uk-grid uk-grid-collapse" uk-grid>
    <div class="tm-timeline-lines-col uk-visible@m">{TIMELINE_LINES}</div>
    <div class="uk-width-expand@m">
      <div class="uk-slider-container tm-timeline" uk-slider>
        <div class="uk-position-relative">
          <ul class="uk-slider-items uk-grid uk-grid-divider">{timeline_items}</ul>
          <div class="uk-slidenav-container tm-timeline-nav">
            <a class="tm-slidenav" href="#" uk-slider-item="previous" aria-label="Precedente"><span uk-icon="chevron-left"></span></a>
            <a class="tm-slidenav" href="#" uk-slider-item="next" aria-label="Successivo"><span uk-icon="chevron-right"></span></a>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>"""
    + split(
        block(
            "Filosofia di Gestione",
            "<p>Banca Ifigest, da sempre caratterizzata da una ricerca del \"ritorno assoluto\", si pone come obiettivo primario la crescita dei capitali nel tempo e la tutela dell'investitore dal rischio di perdite. L'attività di gestione è focalizzata sulla ricerca della rivalutazione del capitale investito nel medio-lungo periodo, comparando costantemente il rapporto tra rischio e rendimento ed effettuando un continuo monitoraggio dell'andamento dei mercati.</p>"
            "<p>Le gestioni patrimoniali di Banca Ifigest non replicano passivamente la struttura del benchmark, ma operano in modo attivo sulla base di strategie di investimento globali e diversificate, con ottimizzazione dei portafogli e utilizzo di tutti gli strumenti del mercato finanziario.</p>",
        )
        + block(
            "Architettura Aperta",
            "<p>Banca Ifigest opera in un contesto di architettura aperta: la propria indipendenza da grandi gruppi finanziari consente di selezionare, senza condizionamenti, i migliori strumenti e le migliori soluzioni disponibili sul mercato per ogni esigenza del cliente. Dalla scelta dei fondi collocati tramite Fundstore alla selezione degli strumenti obbligazionari e azionari nelle gestioni patrimoniali, la preferenza va sempre al prodotto più adatto agli obiettivi del cliente.</p>",
        ),
        media_first=True,
        sid="filosofia",
    ),
    "storia 1987 filosofia di gestione architettura aperta indipendente firenze",
)

STATS = [("861.147", "Utile attivo"), ("495.223", "Raccolta diretta da clientela"), ("3.986.234", "Raccolta indiretta da clientela")]
ROWS = [
    ("di cui Gestioni Patrimoniali Individuali", "2.633.943"),
    ("Margine di intermediazione", "51.059"),
    ("Utile d’esercizio", "7.337"),
    ("Patrimonio netto", "159.357"),
    ("Fondi propri", "111.401"),
    ("Total capital ratio", "34,38%"),
]
stats_html = "".join(
    f'<div><div class="tm-stat"><span class="tm-stat-value">{v}</span><span class="tm-stat-label">{l}</span></div></div>'
    for v, l in STATS
)
rows_html = "".join(f"<tr><th scope=\"row\">{l}</th><td>{v}</td></tr>" for l, v in ROWS)

add(
    "governance.html",
    "Governance",
    "Governance di Banca Ifigest: dati societari, documenti, privacy, Modello 231 e BRRD.",
    hero("Governance", "Rigore e trasparenza")
    + f"""
<section class="uk-section tm-section-docs">
  <div class="uk-container uk-container-large">
    <div class="tm-doc-section" id="dati-societari">
      <h2 class="tm-section-title">Dati societari</h2>
      <p class="tm-measure">Capitale sociale euro 37.554.277,00 i.v. Società iscritta all'Albo delle Banche al Num. 5485 ed iscritta all'Albo dei Gruppi Bancari al num. 3185. Aderente al Fondo Interbancario di tutela dei depositi e al Fondo Nazionale di Garanzia. Siamo soggetti sottoposti al controllo di Banca d’Italia.</p>
      <p class="tm-caption">Dati al 31/12/2025 (€ migliaia)</p>
      <div class="uk-grid-small uk-child-width-1-3@s" uk-grid>{stats_html}</div>
      <table class="tm-data-table"><tbody>{rows_html}</tbody></table>
    </div>

    <div class="tm-doc-section" id="documenti">
      <h2 class="tm-section-title">Documenti</h2>
      <div class="uk-grid-large uk-child-width-1-2@m" uk-grid>
        <div>
          <h3 class="tm-doc-group">Bilanci</h3>
          {doc_list(["Bilancio d’esercizio Banca Ifigest SpA 2025", "Bilancio d’esercizio Banca Ifigest SpA 2024", "Bilancio d’esercizio Banca Ifigest SpA 2023"])}
          {doc_list(["Informativa Stato per Stato 2025", "Informativa Stato per Stato 2024", "Informativa Stato per Stato 2023"])}
          {doc_list(["Bilancio consolidato Gruppo Bancario Ifigest 2025", "Bilancio consolidato Gruppo Bancario Ifigest 2024", "Bilancio consolidato Gruppo Bancario Ifigest 2023"])}
        </div>
        <div>
          <h3 class="tm-doc-group">Documentazione Generale</h3>
          {doc_list(["Informazioni Generali", "Terzo Pilastro, Informativa al pubblico", "Patriot Act"])}
        </div>
      </div>
    </div>

    <div class="tm-doc-section" id="privacy">
      <h2 class="tm-section-title">Privacy</h2>
      {doc_list(["Informativa Privacy Utenti Web", "Informativa Privacy Clienti", "Informativa Privacy Fornitori", "Informativa Privacy Videosorveglianza"])}
    </div>

    <div class="tm-doc-section" id="governance">
      <h2 class="tm-section-title">Governance</h2>
      {doc_list(["Statuto", "Informativa sul Governo Societario", "Regolamento per la gestione delle obbligazioni e delle operazioni con i soggetti in conflitto d’interesse", "Policy conflitti"])}
    </div>

    <div class="tm-doc-section" id="modello-231">
      <h2 class="tm-section-title">Modello 231</h2>
      {doc_list(["Modello Organizzativo ai sensi della Legge n.231 del 2001", "Codice Etico", "Code of Conduct"])}
    </div>

    <div class="tm-doc-section" id="brrd">
      <h2 class="tm-section-title">BRRD (Bail-in)</h2>
      {doc_list(["Informativa alla Clientela Bail-In", "Banca d’Italia: che cosa cambia nella gestione delle crisi bancarie", "D.Lgs. n. 180 del 16/11/2015 · D.Lgs. n. 181 del 16/11/2015", "CONSOB: Comunicazione n. 0090430 del 24/11/2015"])}
    </div>
  </div>
</section>""",
    "dati societari bilanci bilancio privacy statuto modello 231 codice etico bail-in brrd",
)

add(
    "info-prodotti.html",
    "Info Prodotti",
    "Informazioni normative e regolamentari relative ai prodotti e servizi offerti da Banca Ifigest.",
    hero("Info Prodotti", "Informazioni normative e regolamentari relative ai prodotti e servizi offerti da Banca Ifigest")
    + f"""
<section class="uk-section tm-section-docs">
  <div class="uk-container uk-container-large">
    <div class="tm-doc-section" id="trasparenza">
      <h2 class="tm-section-title">Trasparenza</h2>
      <div class="uk-grid-large uk-child-width-1-2@m" uk-grid>
        <div>
          <h3 class="tm-doc-group">Guide Pratiche</h3>
          {doc_list(["Guida Pratica Conto Corrente", "Guida Pratica Credito Consumatori", "Guida Arbitro Bancario e Finanziario", "Guida Mutuo", "Guida Centrale dei Rischi", "Guida Pratica ai Pagamenti nel Commercio Elettronico"])}
        </div>
        <div>
          <h3 class="tm-doc-group">Fogli Informativi e FID</h3>
          {doc_list(["Foglio informativo Conto Corrente Ordinario", "Foglio informativo Carte di Credito NEXI", "Foglio informativo Gestione Portafoglio", "10 FID (fascicoli informativi) varianti Conto Corrente", "31 Fogli informativi (elenco completo)"])}
        </div>
      </div>
    </div>

    <div class="tm-doc-section" id="reclami">
      <h2 class="tm-section-title">Reclami</h2>
      {doc_list(["Info Reclami sul Sito", "Rendiconto Reclami Servizi Bancari e Finanziari 2025"])}
    </div>

    <div class="tm-doc-section" id="sede-di-esecuzione">
      <h2 class="tm-section-title">Sede di Esecuzione</h2>
      {doc_list(["RTS 28, Anno 2025 PRO", "RTS 28, Anno 2025 RETAIL", "Tabella Elenco Negoziatori"])}
    </div>

    <div class="tm-doc-section" id="psd2">
      <h2 class="tm-section-title">PSD2</h2>
      <p class="tm-measure">Dal 13 gennaio 2018 è entrata in vigore la nuova Direttiva Europea sui servizi di pagamento (PSD2), nata per promuovere l'innovazione e lo sviluppo dei digital payments, aumentare la protezione degli utenti e favorire la concorrenza nel mercato dei pagamenti. PSD2 introduce l'obbligo di autenticazione forte (SCA — Strong Customer Authentication) per l'accesso ai servizi online e per le operazioni di pagamento, attraverso due o più fattori di autenticazione e un codice autorizzativo univoco (dynamic linking).</p>
      {doc_list(["Strong Customer Authentication MiTO Desktop", "Strong Customer Authentication MiTO Mobile", "Gestione dei consensi alle Terze Parti", "Interfaccia TPP: cabel.it/attivita.openbanking", "Statistiche KPI trimestrali sull’interfaccia (serie 2019-2026)"])}
    </div>

    <div class="tm-doc-section" id="schede-prodotto">
      <h2 class="tm-section-title">Schede Prodotto</h2>
      {link_list(['Per ricercare le schede prodotto MIFID II: <a href="#">Link</a>', 'Per ricercare titoli: <a href="https://www.borsaitaliana.it" target="_blank" rel="noopener">Borsa Italiana</a>'])}
    </div>

    <div class="tm-doc-section" id="collocamento">
      <h2 class="tm-section-title">Collocamento</h2>
      {doc_list(["IT0006775552 — 3Y PHOENIX MEMORY WO"])}
    </div>

    <div class="tm-doc-section" id="acf">
      <h2 class="tm-section-title">ACF</h2>
      <p class="tm-measure">Per qualsiasi controversia con Banca Ifigest in materia di servizi di investimento non risolta tramite reclamo, è possibile ricorrere all’Arbitro per le Controversie Finanziarie (ACF) di CONSOB: <a href="https://www.acf.consob.it" target="_blank" rel="noopener">acf.consob.it</a></p>
    </div>

    <div class="tm-doc-section" id="fea">
      <h2 class="tm-section-title">Firma Elettronica Avanzata</h2>
      {doc_list(["Contratto Firma Elettronica (FEA)", "Elenco dei Documenti Sottoscrivibili con FEA (Aprile 2026)"])}
    </div>
  </div>
</section>""",
    "trasparenza fogli informativi guide pratiche reclami sede di esecuzione psd2 schede prodotto acf fea firma elettronica",
)

add(
    "sostenibilita.html",
    "Sostenibilità",
    "Crediamo nella sostenibilità come fattore di creazione di valore nel lungo periodo per clienti, azionisti e comunità.",
    hero("Sostenibilità", "Crediamo nella sostenibilità come fattore di creazione di valore nel lungo periodo per clienti, azionisti e comunità"),
    "esg sostenibilità",
)
add("area-soci.html", "Area Soci", "Area Soci Banca Ifigest.", hero("Area Soci"), "soci capitale sociale avvisi")

add(
    "whistleblowing.html",
    "Whistleblowing",
    "Segnalazione di violazioni, in conformità al D.Lgs. n. 24/2023.",
    hero("Whistleblowing", "Ci impegniamo a segnalare comportamenti, atti ed omissioni che possono costituire una violazione delle norme", image=False)
    + lead(
        "<p>A tal fine, il Gruppo si è dotato della necessaria organizzazione per definire criteri e modalità per la ricezione, l'analisi e il trattamento delle segnalazioni di violazioni, assicurando un'adeguata riservatezza e protezione dei dati personali del soggetto che effettua la segnalazione e del soggetto segnalato. Sono stabilite le precauzioni adottate a tutela del segnalante, quali la tutela dell'anonimato e il contrasto a ogni possibile discriminazione o ritorsione.</p>",
        "dark",
    )
    + f"""
<section class="uk-section">
  <div class="uk-container uk-container-large">
    <div class="uk-grid-large uk-child-width-1-2@m" uk-grid>
      <div>
        {block("Chi può segnalare", '<p class="tm-caption">ai sensi del D.lgs 24/2023</p>' + link_list(["Dipendenti", "Consulenti, collaboratori e lavoratori autonomi (ex art. 409 c.p.c.)", "Tirocinanti", "Azionisti", "Persone con funzione di amministrazione, direzione, controllo, vigilanza o rappresentanza", "Soggetti che hanno sciolto il rapporto con l’Azienda"]))}
      </div>
      <div>
        {block("Cosa si può segnalare", link_list(["Violazioni delle norme sull'attività bancaria (antiriciclaggio, servizi di investimento, abusi di mercato, distribuzione prodotti assicurativi)", "Illeciti amministrativi, contabili, civili o penali di cui al D.Lgs. n. 24/2023", "Condotte illecite rilevanti ex D.Lgs. n. 231/2001 o violazioni del MOG", "Atti od omissioni che ledono gli interessi finanziari dell'Unione"]))}
      </div>
    </div>
    <div class="tm-cta">
      <h2 class="tm-cta-title">Invia la tua segnalazione</h2>
      <div class="tm-cta-actions">
        <a class="uk-button uk-button-default tm-button-light-outline" href="#">Invia una segnalazione interna</a>
        <a class="tm-link-light" href="https://whistleblowing.anticorruzione.it/" target="_blank" rel="noopener">Invia una segnalazione all’ANAC <span uk-icon="icon: arrow-right"></span></a>
      </div>
    </div>
  </div>
</section>""",
    "segnalazione violazioni anac d.lgs 24/2023",
)

# Footer pages --------------------------------------------------------------
add("trasparenza.html", "Trasparenza", "Trasparenza Banca Ifigest.", hero("Trasparenza", image=False), "trasparenza")
add("dichiarazione-accessibilita.html", "Dichiarazione di Accessibilità", "Dichiarazione di accessibilità del sito Banca Ifigest.", hero("Dichiarazione di Accessibilità", image=False), "accessibilità")
add("disconoscimento-operazioni.html", "Disconoscimento delle operazioni di pagamento", "Disconoscimento delle operazioni di pagamento.", hero("Disconoscimento delle operazioni di pagamento", image=False), "disconoscimento pagamento")

# Contatti -------------------------------------------------------------------
# Pagina costruita come quella del riferimento: colonne con titolo a barra,
# indirizzo e telefono, mappa Google; in fondo i dati societari.
def map_embed(address, label):
    from urllib.parse import quote_plus
    return (
        f'<iframe class="tm-map" src="https://www.google.com/maps?q={quote_plus(address)}&amp;output=embed" '
        f'width="100%" height="450" loading="lazy" referrerpolicy="no-referrer-when-downgrade" '
        f'title="Mappa {escape(label)}" allowfullscreen></iframe>'
    )


def office_dl(o, label="Indirizzo"):
    email = f'<br><a href="mailto:{o["email"]}">{o["email"]}</a>' if o.get("email") else ""
    return (
        f'<dl class="tm-dl"><dt>{escape(o.get("name", label))}:</dt>'
        f'<dd>{" &ndash; ".join(escape(l) for l in o["lines"])}<br>'
        f'Tel. <a href="{tel_href(o["tel"])}">{o["tel"]}</a>{email}</dd></dl>'
    )


def office_column(title, offices, width, city):
    inner = "".join(
        f'<div>{office_dl(o, "Filiale")}{map_embed(", ".join(o["lines"]) + ", Italia", o.get("name", city))}</div>'
        for o in offices
    )
    if len(offices) > 1:
        inner = f'<div class="uk-grid-medium uk-child-width-1-2@m" uk-grid>{inner}</div>'
    return f'<div class="{width}"><h2 class="tm-column-title">{title}</h2>{inner}</div>'


def contact_page():
    offices = {c: o for col in SEDI for c, o in col}
    sede, *filiali_fi = offices["Firenze"]
    others = ["Milano", "Roma", "Torino", "Prato", "Genova"]
    # Riga 1: Sede Legale + Segreteria. Sotto: tutte le filiali su griglia a 3 colonne
    # (le due filiali di Firenze occupano 2/3, così ogni mappa ha la stessa larghezza).
    row1 = (
        office_column("Sede Legale", [sede], "uk-width-1-2@m", "Firenze")
        + '<div class="uk-width-1-2@m"><h2 class="tm-column-title">Segreteria</h2>'
        '<dl class="tm-dl"><dt>Telefono:</dt><dd><a href="tel:+3905521631">+39 055 21631</a></dd>'
        '<dt>PEC:</dt><dd><a href="mailto:segreteria.ifigest@legalmail.it">segreteria.ifigest@legalmail.it</a></dd>'
        f'<dt>Banca Online:</dt><dd><a href="{BANCA_ONLINE_URL}" target="_blank" rel="noopener">Accedi all\'area riservata</a></dd></dl></div>'
    )
    row2 = office_column("Filiali di Firenze", filiali_fi, "uk-width-2-3@m", "Firenze") + "".join(
        office_column(f"Filiale di {c}", offices[c], "uk-width-1-3@m", c) for c in others
    )
    return (
        hero("Contatti", "Tutti i riferimenti utili per entrare in contatto con noi in modo semplice e diretto.")
        + f"""
<section class="uk-section tm-section-contact">
  <div class="uk-container uk-container-large">
    <div class="uk-grid-large" uk-grid>{row1}</div>
    <div class="uk-grid-large tm-contact-row" uk-grid>{row2}</div>
  </div>
</section>
<section class="uk-section tm-section-muted" id="dati-societari" aria-labelledby="dati-societari-title">
  <div class="uk-container uk-container-large">
    <h2 id="dati-societari-title" class="tm-section-title">Dati societari</h2>
    <p><strong>Banca Ifigest S.p.A.</strong></p>
    <p>Sede Legale e Direzionale:<br>Piazza Santa Maria Soprarno, 1 &ndash; 50125 Firenze<br>
      Tel. <a href="{tel_href("055.24631")}">055.24631</a><br>
      PEC <a href="mailto:segreteria.ifigest@legalmail.it">segreteria.ifigest@legalmail.it</a><br>
      Capitale sociale euro 37.554.277,00 i.v.<br>
      Iscritta all'Albo delle Banche al Num. 5485 e all'Albo dei Gruppi Bancari al num. 3185.<br>
      Aderente al Fondo Interbancario di tutela dei depositi e al Fondo Nazionale di Garanzia.<br>
      Soggetta al controllo di Banca d'Italia.</p>
  </div>
</section>"""
    )


add(
    "contatti.html",
    "Contatti",
    "Tutti i riferimenti utili per entrare in contatto con Banca Ifigest: sede, filiali, telefoni, email e dati societari.",
    contact_page(),
    "contatti sede filiali telefono email pec indirizzo firenze milano roma torino prato genova dati societari",
)

# Search --------------------------------------------------------------------
add(
    "cerca.html",
    "Cerca",
    "Cerca nel sito Banca Ifigest.",
    hero("Cerca", image=False)
    + """
<section class="uk-section tm-section-search">
  <div class="uk-container uk-container-large">
    <form class="uk-search uk-search-large tm-search-page" action="cerca.html" method="get" role="search">
      <span uk-search-icon></span>
      <input class="uk-search-input" id="tm-search-input" type="search" name="q" placeholder="Cerca nel sito" aria-label="Cerca nel sito">
    </form>
    <p class="tm-caption" id="tm-search-status" aria-live="polite"></p>
    <ul class="tm-search-results" id="tm-search-results"></ul>
  </div>
</section>""",
)


# --------------------------------------------------------------------------
# Build
# --------------------------------------------------------------------------
def text_of(html):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


def main():
    index = []
    for slug, title, description, body, keywords in PAGES:
        (ROOT / slug).write_text(page(slug, title, description, body), encoding="utf-8")
        if slug != "cerca.html":
            index.append({"url": slug, "title": title, "description": description, "text": f"{keywords} {text_of(body)}"})
    (ROOT / "assets/js/search-index.js").write_text(
        "/* Generato da tools/build.py: non modificare a mano. */\n"
        "window.IFIGEST_SEARCH_INDEX = " + json.dumps(index, ensure_ascii=False, indent=1) + ";\n",
        encoding="utf-8",
    )
    print(f"Built {len(PAGES)} pages")


if __name__ == "__main__":
    main()
