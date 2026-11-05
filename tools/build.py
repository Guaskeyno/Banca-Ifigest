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
BANCA_ONLINE_URL = "https://areariservata.bancaifigest.it/CBL-MITO-WA/"

NAV = [
    {
        "label": "La Banca",
        "href": "chi-siamo.html",
        "overview": "Chi Siamo",  # etichetta della pagina principale nel menu mobile
        "children": [
            ("Dati e Documenti Societari", "governance.html"),
            ("Informazioni", "info-prodotti.html"),
            ("Sostenibilità", "sostenibilita.html"),
            ("Area Soci", "area-soci.html"),
            ("Collocamento", "collocamento.html"),
        ],
    },
    {
        "label": "Il Gruppo",
        "href": "il-gruppo.html",
        "overview": "Il Gruppo",
        # ancore alle sezioni della pagina Il Gruppo
        "children": [
            ("Private Banking", "il-gruppo.html#private-banking"),
            ("Corporate & Investment Banking", "il-gruppo.html#corporate-investment-banking"),
            ("Asset Management", "il-gruppo.html#asset-management"),
            ("Treasury & ALM", "il-gruppo.html#treasury-alm"),
        ],
    },
    {
        "label": "Prodotti e Servizi",
        "href": "investimenti-e-risparmio.html",  # la voce apre la prima pagina della sezione
        "children": [
            ("Consulenza e Servizi d'Investimento", "investimenti-e-risparmio.html"),
            ("Servizi Bancari", "servizi-bancari.html"),
            ("Prodotti Assicurativi", "prodotti-assicurativi.html"),
            ("Wealth Management", "wealth-management.html"),
            ("Richiedi il tuo POS", "richiedi-pos.html"),
        ],
    },
]
# Gestioni Patrimoniali, Private Banking e Investment Banking (con Finanza Strutturata, Lombard Loans, Debt Advisory)
# restano online ma fuori dal menu.

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
SCROLL = ' uk-scroll="offset: 120"'

# --------------------------------------------------------------------------
# Partials
# --------------------------------------------------------------------------
def tel_href(num):
    return "tel:+39" + re.sub(r"\D", "", num)


# Estensioni accettate per le immagini. Se il file non c'è con l'estensione prevista,
# la pagina prova le altre una alla volta; se mancano tutte, toglie l'<img> e resta il segnaposto.
IMG_EXTS = ["jpeg", "jpg", "png", "svg", "webp"]
IMG_ONERROR = (
    "var x=['jpeg','jpg','png','svg','webp'],t=(this.dataset.t||'')+this.src.split('.').pop()+',';"
    "this.dataset.t=t;var n=x.filter(function(e){return t.indexOf(e+',')<0})[0];"
    "if(n){this.src=this.src.replace(/\\.[a-z]+$/,'.'+n)}else{this.remove()}"
)


def placeholder(cls="", label="Immagine", hint=""):
    """Segnaposto immagine. Contiene già il percorso dell'immagine definitiva
    (assets/img/pages/<pagina>-<hint>.jpg o .jpeg, assegnato in add()): finché il file
    non esiste resta il segnaposto; appena caricato, compare."""
    return (
        f'<div class="tm-placeholder {cls}">'
        f'<img class="tm-photo" src="__IMG:{hint}__" alt="" loading="lazy" decoding="async" onerror="{IMG_ONERROR}">'
        '<span uk-icon="icon: image; ratio: 2"></span></div>'
    )


def is_banca(slug):
    """Marchio Banca Ifigest e tema chiaro (#DDE9EE) su tutte le pagine tranne Il Gruppo."""
    return slug != "il-gruppo.html"


def logo(slug, where):
    """Logo per header ('desktop' | 'mobile') e footer: Banca Ifigest ovunque, Gruppo solo nella pagina Il Gruppo."""
    if is_banca(slug):
        if where == "footer":  # footer sempre scuro: versione bianca del logo
            return '<img src="assets/img/logo-banca-ifigest-white.png" width="200" height="18" alt="Banca Ifigest">'
        w = {"desktop": 240, "mobile": 190}[where]
        return f'<img src="assets/img/logo-banca-ifigest.png" width="{w}" height="{round(w * 88 / 960)}" alt="Banca Ifigest">'
    if where == "footer":
        return f'<img src="assets/img/logo-ifigest-footer.svg" width="134" height="32" alt="{SITE} - Gruppo Bancario">'
    w, h = (160, 64) if where == "desktop" else (120, 48)
    return f'<img src="assets/img/logo-ifigest.svg" width="{w}" height="{h}" alt="{SITE} - Gruppo Bancario">'


def nav_link(label, href, slug):
    """<li><a> di una voce di menu: esterna in nuova scheda, corrente evidenziata."""
    if href.startswith("http"):
        return f'<li><a href="{href}" target="_blank" rel="noopener">{escape(label)}</a></li>'
    return f'<li{ACTIVE if href == slug else ""}><a href="{href}">{escape(label)}</a></li>'


def section_of(slug):
    for item in NAV:
        if slug == item["href"] or slug in [h for _, h in item["children"]]:
            return item
    return None


def header(slug):
    current = section_of(slug)

    def desktop_item(item):
        active = " uk-active" if item is current else ""
        if not item["children"]:
            return f'<li class="{active.strip()}"><a href="{item["href"]}">{escape(item["label"])}</a></li>'
        sub = "".join(nav_link(label, href, slug) for label, href in item["children"])
        return (
            f'<li class="uk-parent{active}"><a href="{item["href"]}">{escape(item["label"])} '
            '<span uk-navbar-parent-icon></span></a>'
            '<div class="uk-drop uk-navbar-dropdown"><ul class="uk-nav uk-navbar-dropdown-nav">'
            f"{sub}</ul></div></li>"
        )

    def mobile_item(item):
        sub = "".join(nav_link(label, href, slug) for label, href in item["children"])
        opened = " uk-open" if item is current else ""
        if not item["children"]:
            return f'<li{ACTIVE if item is current else ""}><a href="{item["href"]}">{escape(item["label"])}</a></li>'
        overview = ""
        if item["href"] not in [h for _, h in item["children"]]:
            label = item.get("overview", "Panoramica")
            overview = f'<li{ACTIVE if item["href"] == slug else ""}><a href="{item["href"]}">{label}</a></li>'
        return (
            f'<li class="uk-parent{opened}"><a href="#">{escape(item["label"])} <span uk-nav-parent-icon></span></a>'
            f'<ul class="uk-nav-sub">{overview}{sub}</ul></li>'
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
              {logo(slug, "desktop")}
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
              {logo(slug, "mobile")}
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


# Barra sotto l'header con ancore alle sezioni della pagina (al posto dei link ad altre pagine)
PAGE_ANCHORS = {
    "il-gruppo.html": [
        ("Le Società", "societa"),
        ("Private Banking", "private-banking"),
        ("Corporate & Investment Banking", "corporate-investment-banking"),
        ("Asset Management", "asset-management"),
        ("Treasury & ALM", "treasury-alm"),
        ("La nostra Storia", "storia"),
    ],
}


def subnav(slug):
    if slug in PAGE_ANCHORS:
        links = "".join(
            f'<li><a href="#{sid}"{SCROLL}>{escape(label)}</a></li>' for label, sid in PAGE_ANCHORS[slug]
        )
        return f"""
<nav class="tm-subnav" aria-label="Sezioni della pagina">
  <div class="uk-container uk-container-large">
    <ul class="tm-subnav-list">{links}</ul>
  </div>
</nav>"""
    item = section_of(slug)
    if not item or not item["children"]:
        return ""
    links = "".join(
        nav_link(label, href, slug).replace('<a href="' + slug + '">', '<a href="' + slug + '"' + CURRENT + ">")
        for label, href in item["children"]
    )
    return f"""
<nav class="tm-subnav" aria-label="{escape(item['label'])}">
  <div class="uk-container uk-container-large">
    <ul class="tm-subnav-list">{links}</ul>
  </div>
</nav>"""


def hero_video(name):
    """Animazione del logo al posto della foto, formati come il riferimento: 9:16 sotto i 640px,
    3:4 fino a 959px, 16:9 oltre. Parte una volta e si ferma sull'ultimo fotogramma."""
    return (
        f'<div class="tm-hero-media tm-hero-media-video tm-hero-video-{name}">'
        '<video class="tm-hero-video" autoplay muted playsinline preload="auto" aria-hidden="true">'
        f'<source media="(max-width: 639px)" src="assets/video/{name}-9x16.mp4" type="video/mp4">'
        f'<source media="(max-width: 959px)" src="assets/video/{name}-3x4.mp4" type="video/mp4">'
        f'<source src="assets/video/{name}-16x9.mp4" type="video/mp4">'
        "</video></div>"
    )


def hero(title, subtitle="", image=True, video=""):
    sub = f'<p class="tm-hero-subtitle">{subtitle}</p>' if subtitle else ""
    if video:
        media = hero_video(video)
    else:
        media = (
            f'<div class="tm-hero-media">{placeholder("tm-placeholder-cover", hint="hero")}</div>' if image else ""
        )
    return f"""
<section class="tm-hero{'' if image or video else ' tm-hero-plain'}"{'' if not (image or video) else ' uk-height-viewport="offset-top: true"'}>
  {media}
  <div class="tm-hero-title">
    <div class="uk-container uk-container-large" uk-scrollspy="cls: uk-animation-fade; delay: 150">
      <h1 class="tm-hero-heading">{title}</h1>
      {sub}
    </div>
  </div>
</section>"""


def footer(slug=""):
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
          <a href="index.html" aria-label="{SITE} - Torna alla Home">{logo(slug, "footer")}</a>
          <p class="tm-footer-small">Banca Ifigest S.p.A.<br>P.za Santa Maria Soprarno, 1 - 50125 Firenze<br>
            <a href="tel:+3905521631">+39 055 21631</a><br>
            <a href="mailto:segreteria.ifigest@legalmail.it">segreteria.ifigest@legalmail.it</a></p>
        </div>
      </div>
      <div class="uk-width-1-2@m uk-flex uk-flex-middle">
        <nav class="tm-footer-small uk-width-1-1" aria-label="Link utili">
          <ul class="tm-list-horizontal">{"".join(items)}</ul>
          <ul class="tm-list-horizontal tm-footer-secondary"><li class="no-separator"><a href="privacy-policy.html">Privacy Policy</a></li></ul>
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



def asset(path):
    """Percorso dell'asset con versione basata sul contenuto, per invalidare la cache del browser."""
    import hashlib
    digest = hashlib.md5((ROOT / path).read_bytes()).hexdigest()[:8]
    return f"{path}?v={digest}"


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
  <link rel="stylesheet" href="{asset("assets/vendor/uikit/css/uikit.min.css")}">
  <!-- Tema Banca Ifigest -->
  <link rel="stylesheet" href="{asset("assets/css/theme.css")}">
</head>
<body class="page-{slug.replace('.html', '')}{' tm-brand-banca' if is_banca(slug) else ''}">
{header(slug)}
{subnav(slug)}
<main id="main">
{body}
</main>
{footer(slug)}
<!-- Libreria: UIkit (MIT) -->
<script src="{asset("assets/vendor/uikit/js/uikit.min.js")}"></script>
<script src="{asset("assets/vendor/uikit/js/uikit-icons.min.js")}"></script>
<!-- Script del sito -->
<script src="{asset("assets/js/search-index.js")}"></script>
<script src="{asset("assets/js/main.js")}"></script>
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
          <span class="tm-card-arrow" aria-hidden="true">&gt;</span>
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


def text_section(content, sid="", extra=""):
    id_attr = f' id="{sid}"' if sid else ""
    return f"""
<section class="uk-section tm-section-text{extra}"{id_attr}>
  <div class="uk-container uk-container-large">{content}</div>
</section>"""


def split(content, media_first=False, sid="", extra=""):
    media = f'<div class="tm-split-media">{placeholder("tm-placeholder-square", hint=sid)}</div>'
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


def doc_list(items):
    """items: etichette (link "#" provvisorio) oppure coppie (etichetta, url)."""
    lis = []
    for i in items:
        label, href = i if isinstance(i, tuple) else (i, "#")
        path = href.lower().split("?")[0]
        icon = "file-text" if path.endswith((".doc", ".docx")) else "file-pdf" if path.endswith(".pdf") or href == "#" else "link"
        target = ' target="_blank" rel="noopener"' if href.startswith("http") else ""
        lis.append(f'<li><a href="{href}"{target}><span uk-icon="icon: {icon}"></span><span>{label}</span></a></li>')
    return '<ul class="tm-doc-list">' + "".join(lis) + "</ul>"


def doc_accordion(groups):
    """Documenti a fisarmonica, come la pagina Documentazione del riferimento.
    groups: [(titolo, [etichetta | (etichetta, url)])]"""
    items = "".join(
        f'<li><a class="uk-accordion-title" href="#">{escape(title)}<span uk-accordion-icon></span></a>'
        f'<div class="uk-accordion-content">{doc_list(docs)}</div></li>'
        for title, docs in groups
    )
    return f'<ul class="tm-doc-accordion" uk-accordion="multiple: true">{items}</ul>'


def link_list(items):
    lis = "".join(f'<li>{i}</li>' for i in items)
    return f'<ul class="tm-bullet-list">{lis}</ul>'


def button(label, href, style="primary"):
    scroll = ' uk-scroll="offset: 120"' if href.startswith("#") else ""
    return f'<a class="uk-button uk-button-{style}" href="{href}"{scroll}>{label}</a>'


# --------------------------------------------------------------------------
# Pages
# --------------------------------------------------------------------------
PAGES = []


def slugify(text):
    import unicodedata
    t = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


def add(slug, title, description, body, keywords=""):
    page_name = slug.replace(".html", "")
    page_name = "home" if page_name == "index" else page_name
    used, counter = set(), [0]

    def name(m):
        hint = m.group(1)
        if hint.startswith(page_name + "-"):
            hint = hint[len(page_name) + 1:]
        if not hint or hint in used:
            counter[0] += 1
            hint = f"immagine-{counter[0]}"
        used.add(hint)
        base = f"assets/img/pages/{page_name}-{hint}"
        found = [e for e in IMG_EXTS if (ROOT / f"{base}.{e}").exists()]
        return f"{base}.{found[0] if found else 'jpg'}"

    body = re.sub(r"__IMG:([^_]*)__", name, body)
    PAGES.append((slug, title, description, body, keywords))


# Home ----------------------------------------------------------------------
add(
    "index.html",
    "Home",
    "Banca Ifigest: dal 1987 una relazione di fiducia per chi cerca una banca su misura, non di serie.",
    hero(
        "Un nuovo movimento finanziario",
        "Dal 1987, offriamo una relazione di fiducia per chi cerca una banca su misura, non di serie",
        video="banca-ifigest",
    )
    + """
<section class="uk-section tm-section-intro">
  <div class="uk-container uk-container-large">
    <h2 class="tm-intro-heading">Per noi il patrimonio è molto più di un numero: è il riflesso di una vita di scelte, di un'azienda costruita, di una famiglia da proteggere.</h2>
    <div class="tm-intro-text">
      <p>Per questo da quasi quarant'anni lavoriamo nel modo opposto a come si è sviluppata gran parte della finanza italiana: <strong>niente call center, niente prodotti standardizzati, niente conflitti d'interesse</strong> legati a una casa madre.</p>
      <p>Ogni cliente ha un private banker che lo conosce, a cui risponde personalmente, e che lo accompagna nelle sue decisioni patrimoniali. Questo è il Gruppo Bancario Ifigest: <strong>la solidità di un grande gruppo bancario, e la prossimità di un rapporto personale.</strong></p>
    </div>
    <div class="uk-text-center tm-intro-cta">
      <a class="uk-button uk-button-primary" href="il-gruppo.html">Scopri il Gruppo</a>
    </div>
  </div>
</section>"""
    + cards(
        [
            ("Private Banking", "Un banker dedicato, un conto corrente progettato per esigenze complesse, e un'interlocuzione diretta con la direzione su ogni decisione importante", "private-banking.html"),
            ("Gestioni Patrimoniali", "Oltre 30 linee di gestione attiva, costruite per profilo di rischio e orizzonte. La nostra priorità: proteggere il capitale e generare valore nel tempo", "gestioni-patrimoniali.html"),
            ("Consulenza", "Raccomandazioni personalizzate su tutti i principali strumenti finanziari, con la libertà di scegliere e la trasparenza di chi non vende prodotti propri", "investimenti-e-risparmio.html#consulenza-evoluta"),
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
            ("Gestioni Patrimoniali", "Oltre 30 linee di gestione attiva, costruite per profilo di rischio e orizzonte. La nostra priorità: proteggere il capitale e generare valore nel tempo", "gestioni-patrimoniali.html"),
        ]
    ),
)

# Layout "prodotti" (come https://www.lbcapitalsgr.it/prodotti/) ----------------
# Sezioni alternate bianco/grigio: icona + titolo, testo introduttivo, eventuali
# pilastri numerati, elenchi prodotto con titolo a pillola e righe con bottone ">".
def category(sid, icon, title, body="", muted=False, extra=""):
    intro = f'<div class="tm-category-intro">{body}</div>' if body else ""
    return f"""
<section class="uk-section tm-category{' tm-category-muted' if muted else ''}" id="{sid}">
  <div class="uk-container uk-container-large">
    <div class="tm-category-head"><span class="tm-category-icon" uk-icon="icon: {icon}; ratio: 1.6"></span><h2 class="tm-category-title">{title}</h2></div>
    {intro}{extra}
  </div>
</section>"""


def product_lists(columns):
    """columns: [(titolo pillola, [(nome, href)])]"""
    widths = {1: "uk-child-width-1-3@m", 2: "uk-child-width-1-2@m", 3: "uk-child-width-1-3@m", 4: "uk-child-width-1-2@s uk-child-width-1-4@l"}
    cols = []
    for pill, items in columns:
        rows = "".join(
            f'<li class="tm-product-row"><span>{name}</span>'
            f'<a class="tm-product-btn" href="{href}" aria-label="{escape(name)}">&gt;</a></li>'
            for name, href in items
        )
        cols.append(f'<div><h3 class="tm-products-title">{pill}</h3><ul class="tm-product-list">{rows}</ul></div>')
    return f'<div class="uk-grid-large tm-products {widths[len(columns)]}" uk-grid>{"".join(cols)}</div>'


def pillars(items):
    """Pilastri numerati in slider, 4 per riga su desktop. items: [(etichetta, testo)]"""
    lis = "".join(
        f'<li class="uk-width-1-1 uk-width-1-2@s uk-width-1-4@m"><div class="tm-pillar">'
        f'<h3 class="tm-pillar-num">{i}.</h3><p><strong>{label}</strong><br>{text}</p></div></li>'
        for i, (label, text) in enumerate(items, 1)
    )
    return f"""
    <div class="uk-slider-container tm-pillars" uk-slider="finite: true">
      <div class="uk-position-relative">
        <ul class="uk-slider-items uk-grid">{lis}</ul>
        <div class="tm-pillars-nav">
          <a class="tm-slidenav" href="#" uk-slider-item="previous" aria-label="Precedente"><span uk-icon="chevron-left"></span></a>
          <a class="tm-slidenav" href="#" uk-slider-item="next" aria-label="Successivo"><span uk-icon="chevron-right"></span></a>
        </div>
      </div>
    </div>"""


def info_columns(items):
    """Colonne con titolo a pillola e descrizione (come gli elenchi prodotto). items: [(sottotitolo, descrizione)]"""
    widths = {1: "uk-child-width-1-3@m", 2: "uk-child-width-1-2@m", 3: "uk-child-width-1-3@m", 4: "uk-child-width-1-2@s uk-child-width-1-4@l"}
    cols = "".join(
        f'<div><h3 class="tm-products-title">{sub}</h3><p class="tm-info-text">{desc}</p></div>'
        for sub, desc in items
    )
    return f'<div class="uk-grid-large tm-products tm-info-columns {widths[len(items)]}" uk-grid>{cols}</div>'


def centered_cta(label, href):
    return f'<div class="tm-category-cta uk-text-center">{button(label, href)}</div>'


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
    + category(
        "conto-corrente", "lock", "Conto Corrente",
        "<p>Il <strong>Conto Remunerato di Banca Ifigest</strong> offre la possibilità di far fruttare la liquidità disponibile, con condizioni trasparenti e competitive, mantenendo la piena disponibilità delle somme depositate.</p>",
        muted=True,
        extra=button("Apri il conto Ifigest", "contatti.html"),
    )
    + category(
        "carta-ifigest", "credit-card", "Carta Ifigest",
        "<p>La carta di credito Banca Ifigest, <strong>in partnership con Nexi</strong>, offre i massimi livelli di sicurezza e flessibilità per i pagamenti quotidiani e online, con le funzionalità Apple Pay per i pagamenti contactless. Disponibile nelle versioni <strong>individuale, aziendale e Black</strong>.</p>",
        extra=button("Contatta una filiale", "contatti.html")
        + '<p class="tm-note">Consulta i fogli informativi relativi ai conti correnti e alle carte <a href="info-prodotti.html#trasparenza">qui</a>.</p>',
    ),
    "conto corrente carta di credito nexi apple pay conto remunerato",
)

add(
    "investimenti-e-risparmio.html",
    "Consulenza e Servizi d'Investimento",
    "Soluzioni costruite sugli obiettivi della nostra clientela.",
    hero("Consulenza e Servizi d'Investimento", "Soluzioni costruite sugli obiettivi della nostra clientela")
    + lead(
        "<p>L'attività di investimento di Banca Ifigest è focalizzata sulla ricerca della rivalutazione del capitale nel medio-lungo periodo, attraverso strategie di gestione attiva, diversificazione e un'offerta aperta ai migliori strumenti del mercato.</p>"
    )
    + category(
        "gestioni-patrimoniali", "album", "Gestioni Patrimoniali",
        "<p>Le Gestioni Patrimoniali di Banca Ifigest <strong>non replicano passivamente la struttura del benchmark</strong>, ma operano in modo attivo sulla base di strategie di investimento globali e diversificate sulle principali asset class, con ottimizzazione dei portafogli e utilizzo di tutti gli strumenti del mercato finanziario.</p>"
        "<p>Il team di gestione opera dai desk di Milano, Firenze e Roma, con competenze in analisi dei mercati finanziari, selezione di obbligazioni governative e societarie e stock picking azionario.</p>"
        "<p>In virtù degli obiettivi di investimento del cliente, sono altresì disponibili <strong>linee di investimento flessibili e personalizzabili</strong> con le specifiche esigenze di ogni investitore.</p>"
        "<p>Grazie alle competenze del proprio team di gestione, Banca Ifigest fornisce altresì consulenza e servizi di asset management per alcune primarie Società di gestione estere, attive su Fondi comuni e SICAV dedicati sia a clientela privata che istituzionale.</p>",
        muted=True,
    )
    + category(
        "consulenza-evoluta", "commenting", "Consulenza Evoluta",
        "<p>In sintonia con il profilo e con gli obiettivi di investimento del cliente, il servizio di consulenza di Banca Ifigest fornisce <strong>raccomandazioni personalizzate su tutti i principali strumenti finanziari</strong>. Un servizio costruito sulla conoscenza approfondita del cliente, libero da condizionamenti di prodotto grazie all'architettura aperta della banca.</p>",
        extra=product_lists([
            ("Piani di investimento", [
                ("Piani Individuali di Risparmio (PIR)", "contatti.html"),
                ("Piani di Accumulo del Capitale (PAC)", "contatti.html"),
            ]),
        ]),
    )
    + category("trading", "table", "Trading e Negoziazione Titoli", muted=True),
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
    + category(
        "sevian-fiduciaria", "users", "Sevian Fiduciaria",
        "<p>Sevian Fiduciaria è la società fiduciaria, parte del Gruppo, che affianca la banca con servizi di <strong>intestazione fiduciaria, amministrazione e pianificazione successoria</strong>, offrendo a clienti privati, famiglie e imprese uno strumento di riservatezza, protezione e continuità nella gestione del patrimonio.</p>",
        extra=pillars([
            ("INTESTAZIONE FIDUCIARIA", "Gestione di partecipazioni, strumenti finanziari e altri beni tramite intestazione alla fiduciaria, nel pieno rispetto della riservatezza e della titolarità sostanziale del cliente."),
            ("AMMINISTRAZIONE DI PATRIMONI", "Amministrazione di patrimoni mobiliari, con rendicontazione puntuale e supporto negli adempimenti, anche senza intestazione dei beni."),
            ("PIANIFICAZIONE SUCCESSORIA", "Strutturazione e tutela del patrimonio in ottica di passaggio generazionale, per trasmettere valore tra le generazioni con serenità e continuità."),
            ("RISERVATEZZA E PROTEZIONE", "Separazione e protezione degli asset, a garanzia di continuità e riservatezza nella gestione del patrimonio nel tempo."),
        ]),
    )
    + category(
        "valore-di-gruppo", "git-branch", "Valore di Gruppo",
        "<p>Operando all'interno del Gruppo Bancario, Sevian Fiduciaria <strong>unisce la propria specializzazione alle competenze bancarie, di gestione e di consulenza della banca</strong>.</p>",
        muted=True,
        extra=centered_cta("Scopri il Gruppo", "il-gruppo.html"),
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
LOREM = "<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p>"  # TODO: testo definitivo
CTA_CONSULENZA = button("Richiedi una consulenza", "contatti.html")


def placeholder_blocks(prefix, cta=True, images=True):
    """Due blocchi immagine + testo provvisorio, alternati (come Collocamento). TODO: testi definitivi."""
    body = LOREM + (CTA_CONSULENZA if cta else "")
    if not images:
        return text_section(block("Lorem ipsum", LOREM), sid="blocco-1") + text_section(
            block("Lorem ipsum", body), sid="blocco-2", extra=" tm-section-muted"
        )
    return split(block("Lorem ipsum", body), sid="blocco-1", extra=" tm-section-split-first") + split(
        block("Lorem ipsum", body), media_first=True, sid="blocco-2"
    )

add(
    "collocamento.html",
    "Collocamento",
    "Guarda con serenità al futuro, con soluzioni a capitale garantito e diversificazione.",
    hero("Collocamento", "Guarda con serenità al futuro, con soluzioni a capitale garantito e diversificazione")
    + category("cnp-vita-assicura", "lifesaver", "CNP Vita Assicura", CNP)
    + category("club-deal", "users", "Club Deal", LOREM, muted=True)
    + category("fia", "database", "FIA", LOREM)
    + category("certificati", "file-text", "Certificati", LOREM, muted=True)
    + category("polizze", "file-edit", "Polizze", LOREM, extra=centered_cta("Richiedi una consulenza", "contatti.html")),
    "assicurazione vita cnp club deal fia certificati polizze ivass rui",
)

add(
    "gestioni-patrimoniali.html",
    "Gestioni Patrimoniali",
    "Gestioni Patrimoniali Banca Ifigest.",
    hero("Gestioni Patrimoniali")
    # TODO: testi definitivi
    + category("blocco-1", "album", "Lorem ipsum", LOREM)
    + category("blocco-2", "future", "Lorem ipsum", LOREM, muted=True, extra=centered_cta("Richiedi una consulenza", "contatti.html")),
    "gestioni patrimoniali linee di gestione",
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
add("prodotti-assicurativi.html", "Prodotti Assicurativi", "Prodotti assicurativi Banca Ifigest.", hero("Prodotti Assicurativi") + placeholder_blocks("prodotti-assicurativi"), "assicurazioni polizze")
add("richiedi-pos.html", "Richiedi il tuo POS", "Richiedi il POS di Banca Ifigest per la tua attività.", hero("Richiedi il tuo POS") + placeholder_blocks("richiedi-pos"), "pos esercenti pagamenti")
add("finanza-strutturata.html", "Finanza Strutturata", "Finanza strutturata Banca Ifigest.", hero("Finanza Strutturata") + placeholder_blocks("finanza-strutturata"), "project finance acquisition finance")
add("lombard-loans.html", "Lombard Loans", "Lombard Loans Banca Ifigest.", hero("Lombard Loans") + placeholder_blocks("lombard-loans"), "finanziamento garantito")
add("debt-advisory.html", "Debt Advisory", "Debt Advisory Banca Ifigest.", hero("Debt Advisory") + placeholder_blocks("debt-advisory"), "struttura finanziaria")

# Il Gruppo -----------------------------------------------------------------
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


def timeline_section():
    """La nostra storia: cronologia a slider (dimensioni e comportamento come il riferimento)."""
    return f"""
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


# Loghi delle società del Gruppo: (sito, nome) oppure None se il logo non ha link (sito corrente)
GROUP_LOGOS = [
    None,
    ("https://www.lbcapitalsgr.it/", "L&B Capital SGR"),
    ("https://lbpartners.it/", "L&B Partners"),
    None,  # Sevian Fiduciaria
    ("https://www.fundstore.it/", "Fundstore"),
]


def group_logo(i, link):
    media = placeholder("tm-placeholder-square tm-placeholder-logo", hint=f"logo-{i}")
    if link:
        url, name = link
        media = (
            f'<a class="tm-logo-link" href="{url}" target="_blank" rel="noopener" '
            f'aria-label="{escape(name)} (si apre in una nuova scheda)">{media}</a>'
        )
    return f'<div><div class="tm-logo-media">{media}</div></div>'


group_logos = "".join(group_logo(i, link) for i, link in enumerate(GROUP_LOGOS, 1))

add(
    "il-gruppo.html",
    "Il Gruppo",
    "Gruppo Bancario Ifigest: un nuovo movimento finanziario.",
    hero("Gruppo Bancario Ifigest", "Un nuovo movimento finanziario", video="gruppo-ifigest")
    + lead(LOREM, "dark")  # TODO: testo definitivo
    + f"""
<section class="uk-section tm-section-logos" id="societa" aria-labelledby="societa-title">
  <div class="uk-container uk-container-large">
    <h2 id="societa-title" class="tm-section-title">Le Società del Gruppo Bancario Ifigest</h2>
    <div class="uk-grid-small uk-child-width-1-2 uk-child-width-1-3@s uk-child-width-1-5@m" uk-grid>{group_logos}</div>
  </div>
</section>"""
    # Le aree di attività del Gruppo (layout come la pagina Prodotti del riferimento)
    + category(
        "private-banking", "users", "PRIVATE BANKING", muted=True,
        extra=info_columns([
            ("<strong>Banca Ifigest</strong>", "Rete di 82 Private Banker per la gestione patrimoniale, consulenza ad alto contatto e conservazione intergenerazionale del capitale"),
            ("<strong>Fundstore</strong>", "Canale nativo digitale e marketplace in architettura aperta che agisce come motore di Digital Banking a servizio del segmento retail/self-directed e IFA"),
            ("<strong>Sevian Srl</strong>", "Società fiduciaria di Gruppo integrata verticalmente per erogare i servizi di Wealth Planning, intestazione fiduciaria e protezione del patrimonio familiare"),
        ]),
    )
    + category(
        "corporate-investment-banking", "world", "CORPORATE &amp; INVESTMENT BANKING (CIB)",
        extra=info_columns([
            ("<strong>L&amp;B Partners SpA</strong>", "Boutique di Financial Advisory per servizi alle imprese (M&amp;A, Debt Advisory, Valuations) e Project Finance"),
            ("<strong>Club Deal</strong>", "Veicoli d'investimento e strutturazione di operazioni in Private Equity / Venture riservate a clienti HNWI e famiglie imprenditoriali"),
            ("<strong>Finanza Strutturata (O&amp;D)</strong>", "Soluzioni di finanziamento su misura, Project Finance e origination/distribuzione sul mercato"),
        ]),
    )
    + category(
        "asset-management", "album", "ASSET MANAGEMENT", muted=True,
        extra=info_columns([
            ("<strong>L&amp;B Capital SGR SpA</strong>", "La Società di Gestione del Risparmio del Gruppo, nata dall'unione di Soprarno SGR e MIP SGR"),
            ("<strong>Gamma Prodotti</strong>", "Gestione di Fondi Comuni UCITS (azionari, obbligazionari, flessibili), Fondi Alternativi FIA (Italian Renewable Resources) e linee di gestione per la Rete"),
        ]),
    )
    + category(
        "treasury-alm", "database", "TREASURY &amp; ALM",
        extra=info_columns([
            ("<strong>Banca Ifigest</strong>", "Gestione integrata dell'Asset &amp; Liability Management del Gruppo"),
            ("<strong>Operatività</strong>", "Ottimizzazione della liquidità di bilancio, gestione del portafoglio titoli di proprietà, copertura dei rischi finanziari e stabilizzazione del margine d'interesse"),
        ]),
    )
    + timeline_section(),
    "gruppo bancario sevian fundstore soprarno sgr storia 1987 private banking corporate investment banking cib asset management treasury alm l&b partners l&b capital club deal",
)

add(
    "chi-siamo.html",
    "Chi Siamo",
    "Una realtà indipendente, specializzata nella gestione e valorizzazione dei patrimoni privati e istituzionali.",
    hero("Chi Siamo", "Una realtà indipendente, specializzata nella gestione e valorizzazione dei patrimoni privati e istituzionali")
    # Titolo a sinistra, testo a destra (come "La nostra esperienza, la vostra crescita" del riferimento)
    + """
<section class="uk-section tm-section-two-col" id="chi-siamo">
  <div class="uk-container uk-container-large">
    <div class="uk-grid-large uk-child-width-1-2@m" uk-grid>
      <div>
        <h2 class="tm-two-col-heading">Il Gruppo Bancario Ifigest è fondato su principi di trasparenza, indipendenza e orientamento al cliente, integrando competenze bancarie, fiduciarie e di gestione del risparmio.</h2>
      </div>
      <div class="tm-two-col-text">
        <p>Banca Ifigest è una banca privata e indipendente con sede a Firenze, iscritta all'Albo delle Banche al Num. 5485 e all'Albo dei Gruppi Bancari al num. 3185. Aderente al Fondo Interbancario di tutela dei depositi e al Fondo Nazionale di Garanzia.</p>
        <p>Intermediario autorizzato all'esercizio dei servizi bancari e di investimento di collocamento, ricezione e trasmissione di ordini, gestione individuale di portafoglio di investimento e consulenza in materia di investimenti dalla Banca d'Italia con delibera del 19 aprile 2001. Il Gruppo comprende Banca Ifigest S.p.A., Sevian Fiduciaria, Fundstore e Soprarno SGR.</p>
      </div>
    </div>
  </div>
</section>"""
    + text_section(
        block(
            "Filosofia di Gestione",
            "<p>Banca Ifigest, da sempre caratterizzata da una ricerca del \"ritorno assoluto\", si pone come obiettivo primario la crescita dei capitali nel tempo e la tutela dell'investitore dal rischio di perdite. L'attività di gestione è focalizzata sulla ricerca della rivalutazione del capitale investito nel medio-lungo periodo, comparando costantemente il rapporto tra rischio e rendimento ed effettuando un continuo monitoraggio dell'andamento dei mercati.</p>"
            "<p>Le gestioni patrimoniali di Banca Ifigest non replicano passivamente la struttura del benchmark, ma operano in modo attivo sulla base di strategie di investimento globali e diversificate, con ottimizzazione dei portafogli e utilizzo di tutti gli strumenti del mercato finanziario.</p>",
        )
        + block(
            "Architettura Aperta",
            "<p>Banca Ifigest opera in un contesto di architettura aperta: la propria indipendenza da grandi gruppi finanziari consente di selezionare, senza condizionamenti, i migliori strumenti e le migliori soluzioni disponibili sul mercato per ogni esigenza del cliente. Dalla scelta dei fondi collocati tramite Fundstore alla selezione degli strumenti obbligazionari e azionari nelle gestioni patrimoniali, la preferenza va sempre al prodotto più adatto agli obiettivi del cliente.</p>",
        ),
        sid="filosofia",
        extra=" tm-section-primary",
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
    "Dati e Documenti Societari",
    "Dati e documenti societari di Banca Ifigest: dati societari, documenti, privacy, Modello 231 e BRRD.",
    hero("Dati e Documenti Societari", "Rigore e trasparenza")
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
      {doc_accordion([
          ("Bilanci", [
              "Bilancio d’esercizio Banca Ifigest SpA 2025", "Bilancio d’esercizio Banca Ifigest SpA 2024", "Bilancio d’esercizio Banca Ifigest SpA 2023",
              "Informativa Stato per Stato 2025", "Informativa Stato per Stato 2024", "Informativa Stato per Stato 2023",
              "Bilancio consolidato Gruppo Bancario Ifigest 2025", "Bilancio consolidato Gruppo Bancario Ifigest 2024", "Bilancio consolidato Gruppo Bancario Ifigest 2023",
          ]),
          ("Documentazione Generale", ["Informazioni Generali", "Terzo Pilastro, Informativa al pubblico", "Patriot Act"]),
      ])}
    </div>
    <div class="tm-doc-section" id="privacy">
      <h2 class="tm-section-title">Privacy</h2>
      <div class="tm-docs-plain">{doc_list(['Informativa Privacy Utenti Web', 'Informativa Privacy Clienti', 'Informativa Privacy Fornitori', 'Informativa Privacy Videosorveglianza'])}</div>
    </div>
    <div class="tm-doc-section" id="governance">
      <h2 class="tm-section-title">Governance</h2>
      <div class="tm-docs-plain">{doc_list(['Statuto', 'Informativa sul Governo Societario', 'Regolamento per la gestione delle obbligazioni e delle operazioni con i soggetti in conflitto d’interesse', 'Policy conflitti'])}</div>
    </div>
    <div class="tm-doc-section" id="modello-231">
      <h2 class="tm-section-title">Modello 231</h2>
      <div class="tm-docs-plain">{doc_list(['Modello Organizzativo ai sensi della Legge n.231 del 2001', 'Codice Etico', 'Code of Conduct'])}</div>
    </div>
    <div class="tm-doc-section" id="brrd">
      <h2 class="tm-section-title">BRRD (Bail-In)</h2>
      <div class="tm-docs-plain">{doc_list(['Informativa alla Clientela Bail-In', 'Banca d’Italia: che cosa cambia nella gestione delle crisi bancarie', 'D.Lgs. n. 180 del 16/11/2015 · D.Lgs. n. 181 del 16/11/2015', 'CONSOB: Comunicazione n. 0090430 del 24/11/2015'])}</div>
    </div>
  </div>
</section>""",
    "dati societari bilanci bilancio privacy statuto modello 231 codice etico bail-in brrd",
)

# Informazioni: contenuti 1:1 con bancaifigest.com/informazioni-e-link-utili/
T = "https://www.bancaifigest.com/PDF/Trasparenza/"
FI = T + "Fogli-informativi/"
FID = T + "fid/"
COLL = "https://bancaifigest.com/PDF/Collocamento/"
CABEL = '<a href="https://www.cabel.it/attivita/openbanking/" target="_blank" rel="noopener"><strong>https://www.cabel.it/attivita/openbanking/</strong></a>'
US_PERSON = "<p>Le notizie, i documenti e le informazioni contenuti nella presente sezione del sito non sono destinati a soggetti qualificabili come U.S. Person ai sensi della normativa statunitense applicabile, né possono essere trasmessi, diffusi o resi disponibili negli Stati Uniti d’America o a favore di U.S. Person.</p>"

INFO_TRASPARENZA = [
    ("Guide pratiche", [
        ("GUIDA PRATICA CONTO CORRENTE", T + "Guide-pratiche/guida-conto-corrente.pdf"),
        ("GUIDA PRATICA CREDITO CONSUMATORI", T + "Guide-pratiche/guida-credito-consumatori.pdf"),
        ("GUIDA ARBITRO BANCARIO E FINANZIARIO", T + "Guide-pratiche/guida-arbitro-bancario-finanziario.pdf"),
        ("GUIDA MUTUO", T + "Guide-pratiche/guida-mutuo.pdf"),
        ("GUIDA CENTRALE DEI RISCHI", T + "Guide-pratiche/guida-centrale-dei-rischi.pdf"),
        ("GUIDA PRATICA AI PAGAMENTI NEL COMMERCIO ELETTRONICO", T + "Guide-pratiche/guida-pratica-pagamenti-commercio-elettronico.pdf"),
    ]),
    ("Altre guide", [
        ("I TUOI DIRITTI QUANDO EFFETTUI UN PAGAMENTO IN EUROPA", T + "Altre-guide/leaflet-your-rights-payments-eu_it.pdf"),
        ("BONIFICO ISTANTANEO – LE NOVITA’", T + "Altre-guide/guida-abi-bonifici-istantanei-2026.pdf"),
        ("DALLA TELEFONATA SOSPETTA ALL’EMAIL INGANNEVOLE: SCOPRI COME DIFENDERTI", T + "Altre-guide/truffe-online.pdf"),
    ]),
    ("Piano di sostituzione degli indici di riferimento", [
        ("PIANO DI SOSTITUZIONE DEGLI INDICI DI RIFERIMENTO", T + "087.pdf"),
    ]),
    ("Tassi effettivi globali medi ai fini della legge antiusura (Art.2 Legge 108/96)", [
        ("TASSI D’INTERESSE EFFETTIVI GLOBALI MEDI PER IL TRIMESTRE IN CORSO", "http://www.bancaditalia.it/compiti/vigilanza/compiti-vigilanza/tegm/"),
    ]),
    ("Fogli informativi", [(label, FI + f) for label, f in [
        ("FOGLIO INFORMATIVO CASSETTE DI SICUREZZA", "001-3.pdf"),
        ("FOGLIO INFORMATIVO CONTO CORRENTE IPOTECARIO", "003-3.pdf"),
        ("FOGLIO INFORMATIVO CONTO DI BASE", "005-3.pdf"),
        ("FOGLIO INFORMATIVO CONTO CORRENTE ORDINARIO", "006-3.pdf"),
        ("FOGLIO INFORMATIVO SERVIZI ACCESSORI CONTO CORRENTE ORDINARIO", "007-5.pdf"),
        ("FOGLIO INFORMATIVO CONTO CORRENTE TITOLI", "008-3.pdf"),
        ("FOGLIO INFORMATIVO CREDITO DI FIRMA", "009-2.pdf"),
        ("FOGLIO INFORMATIVO MANDATO A VENDERE", "010-2.pdf"),
        ("FOGLIO INFORMATIVO MUTUO IPOTECARIO", "011-2.pdf"),
        ("FOGLIO INFORMATIVO PEGNO", "012-2.pdf"),
        ("FOGLIO INFORMATIVO FIDEIUSSIONE", "013-2.pdf"),
        ("FOGLIO INFORMATIVO PRESTITO CHIROGRAFICO A TASSO VARIABILE", "014-2.pdf"),
        ("FOGLIO INFORMATIVO VERSAMENTO DECIMI DI CAPITALE PER COSTITUZIONE SOCIETA’", "015-3.pdf"),
        ("FOGLIO INFORMATIVO APERTURA DI CREDITO IN CONTO CORRENTE", "016-2.pdf"),
        ("FOGLIO INFORMATIVO APERTURA DI CREDITO IPOTECARIA", "017-2.pdf"),
        ("FOGLIO INFORMATIVO SERVIZI HOME BANKING MITO", "018-3.pdf"),
        ("FOGLIO INFORMATIVO SERVIZI POS ESERCENTI", "019-2.pdf"),
        ("FOGLIO INFORMATIVO ESERCENTI NEXI", "020-3.pdf"),
        ("FOGLIO INFORMATIVO APERTURA DI CREDITO (CREDITO IMMOBILIARE A CONSUMATORI)", "021-1.pdf"),
        ("FOGLIO INFORMATIVO MUTUO IPOTECARIO (CREDITO IMMOBILIARE A CONSUMATORI)", "022-1.pdf"),
        ("FOGLIO INFORMATIVO PRESTITO PERSONALE (CREDITO IMMOBILIARE A CONSUMATORI)", "023-2.pdf"),
        ("FOGLIO INFORMATIVO CARTE DI CREDITO INDIVIDUALI NEXI", "024-3.pdf"),
        ("FOGLIO INFORMATIVO CARTE DI CREDITO AZIENDALI NEXI", "025-3.pdf"),
        ("FOGLIO INFORMATIVO CARTA DI CREDITO BLACK", "026-3.pdf"),
        ("FOGLIO INFORMATIVO CASELLA POSTALE", "027-3.pdf"),
        ("FOGLIO INFORMATIVO CESSIONE DEL CREDITO DI IMPOSTA DA SUPERBONUS, ECOBONUS E ALTRI BONUS FISCALI EDILIZI", "028-4.pdf"),
        ("FOGLIO INFORMATIVO CONTO CORRENTE SERVIZI DI PAGAMENTO E DEPOSITO TITOLI A CUSTODIA ED AMMINISTRAZIONE", "031-2.pdf"),
        ("FOGLIO INFORMATIVO CARTA DI DEBITO INTERNAZIONALE INSTANT ISSUING", "032-3.pdf"),
        ("FOGLIO INFORMATIVO CARTA DI DEBITO INTERNAZIONALE ON DEMAND", "033-3.pdf"),
        ("FOGLIO INFORMATIVO CARTA DI DEBITO NEXI BUSINESS", "034-3.pdf"),
        ("FOGLIO INFORMATIVO CASH POOLING", "035-3.pdf"),
    ]]),
    ("FID", [(label, FID + f) for label, f in [
        ("FID CONTO CORRENTE IPOTECARIO", "IPOTECARIO.pdf"),
        ("FID CONTO CORRENTE TITOLI", "TITOLI.pdf"),
        ("FID CONTO CORRENTE ORDINARIO", "ORDINARIO.pdf"),
        ("FID CONTO CORRENTE GOLD", "GOLD.pdf"),
        ("FID CONTO CORRENTE PLATINUM", "PLATINUM.pdf"),
        ("FID CONTO CORRENTE WEB", "WEB.pdf"),
        ("FID CONTO DI BASE GENERICO ISEE", "ISEE.pdf"),
        ("FID CONTO DI BASE GENERICO PER PENSIONATI", "PENSIONATI.pdf"),
        ("FID CONTO DI BASE GENERICO PER PENSIONATI GRATUITO", "PENSIONATI-GRATUITO.pdf"),
        ("FID CONTO DI BASE GENERICO", "CONTO.pdf"),
    ]]),
]

KPI_PERIODS = [
    "2019_06-2019_08", "2019_09-2019_11", "2019_12-2020_02", "2020_03-2020_05", "2020_06-2020_08",
    "2020_09-2020_11", "2020_12-2021_02", "2021_03-2021_05", "2021_06-2021_08", "2021_09-2021_11",
    "2021_12-2022_02", "2022_03-2022_05", "2022_06-2022_08", "2022_09-2022_11", "2022_12-2023_03",
    "2023_04-2023_06", "2023_07-2023_09", "2023_10-2023_12", "2024_01-2024_03", "2024_04-2024_06",
    "2024_07-2024_09", "2024_10-2024_12", "2025_01-2025_03", "2025_04-2025_06", "2025_07-2025_09",
    "2025_10-2025_12", "2026_01-2026_03",
]
INFO_KPI = [
    ("KPI " + p.replace("_", "/").replace("-", " – "), f"https://www.bancaifigest.com/PDF/kpi/KPI-{p}.pdf")
    for p in KPI_PERIODS
]

INFO_COLLOCAMENTO = [
    ("IT0006775552_3Y PHOENIX MEMORY WO", [
        ("Fast Cash Collect IT0006775552 1.pdf", COLL + "IT0006775552_3Y/Fast%20Cash%20Collect%20IT0006775552%201.pdf"),
        ("FT P68923.pdf", COLL + "IT0006775552_3Y/FT%20P68923.pdf"),
        ("KID_3Y PHOENIX MEMORY WO on BMPS IM BAMI IM UCG IM BPE IM.pdf", COLL + "IT0006775552_3Y/KID_3Y%20PHOENIX%20MEMORY%20WO%20on%20BMPS%20IM%20BAMI%20IM%20UCG%20IM%20BPE%20IM.pdf"),
        ("Product Term Sheet_3Y PHOENIX MEMORY WO on BMPS IM BAMI IM UCG IM BPE IM_vfinal.pdf", COLL + "IT0006775552_3Y/Product%20Term%20Sheet_3Y%20PHOENIX%20MEMORY%20WO%20on%20BMPS%20IM%20BAMI%20IM%20UCG%20IM%20BPE%20IM_vfinal.pdf"),
    ]),
    ("XS3127850645", [
        ("FT_XS3127850645.pdf", COLL + "XS3127850645/FT_XS3127850645.pdf"),
        ("KID XS3127850645.pdf", COLL + "XS3127850645/KID%20XS3127850645.pdf"),
        ("Scheda Prodotto_XS3127850645 1.pdf", COLL + "XS3127850645/Scheda%20Prodotto_XS3127850645%201.pdf"),
        ("TS_Ind XS3127850645.pdf", COLL + "XS3127850645/TS_Ind%20XS3127850645.pdf"),
    ]),
    ("XS3184499963", [
        ("FT XS3184499963 1.pdf", COLL + "XS3184499963/FT%20XS3184499963%201.pdf"),
        ("KID XS3184499963.pdf", COLL + "XS3184499963/KID%20XS3184499963.pdf"),
        ("Scheda Prodotto ISIN XS3184499963.pdf", COLL + "XS3184499963/Scheda%20Prodotto%20ISIN%20XS3184499963.pdf"),
        ("TS XS3184499963.pdf", COLL + "XS3184499963/TS%20XS3184499963.pdf"),
    ]),
]


def doc_group(title, docs, intro=""):
    """Gruppo di documenti senza fisarmonica: sottotitolo + elenco."""
    return f'<div class="tm-doc-group-block"><h3 class="tm-doc-group">{title}</h3>{intro}<div class="tm-docs-plain">{doc_list(docs)}</div></div>'


def doc_accordion_html(groups):
    """Come doc_accordion, ma il contenuto di ogni voce è HTML già pronto."""
    items = "".join(
        f'<li><a class="uk-accordion-title" href="#">{escape(title)}<span uk-accordion-icon></span></a>'
        f'<div class="uk-accordion-content">{content}</div></li>'
        for title, content in groups
    )
    return f'<ul class="tm-doc-accordion" uk-accordion="multiple: true">{items}</ul>'


def info_section(sid, title, content):
    return f'<div class="tm-doc-section" id="{sid}"><h2 class="tm-section-title">{title}</h2>{content}</div>'


PSD2_HTML = (
    '<div class="tm-prose">'
    "<p>Dal 13 gennaio 2018 è entrata in vigore la nuova Direttiva Europea sui servizi di pagamento, meglio conosciuta come PSD2. Questa direttiva è nata per promuovere l’innovazione e lo sviluppo dei digital payments, aumentare la protezione e la sicurezza degli utenti nei servizi di pagamento online e favorire più alti livelli di concorrenza all’interno del mercato dei pagamenti.</p>"
    "<h3 class=\"tm-doc-group\">PERCHÉ É STATA INTRODOTTA?</h3>"
    "<p>PSD2 si pone l’obiettivo di armonizzare il mercato europeo dei servizi di pagamento, rendendolo efficiente, competitivo e più sicuro per gli utenti.</p>"
    "<p>In base a quanto previsto dalla normativa, per accedere e operare con i servizi online sarà necessario utilizzare strumenti che:</p>"
    "<ul class=\"tm-bullet-list\"><li>verifichino l’identità del Cliente, attraverso due o più fattori di autenticazione (autenticazione forte).</li>"
    "<li>certifichino l’operazione di pagamento attraverso un codice autorizzativo univoco (collegamento dinamico – dynamic linking).</li></ul>"
    "</div>"
    + doc_group("Scopri il nuovo sistema di sicurezza", [
        ("Strong Customer Authentication MiTO Desktop (3 MB .PDF)", "https://bancaifigest.com/wp-content/uploads/2025/05/STRONG-CUSTOMER-AUTHENTICATION-MiTO-DESKTOP.pdf"),
        ("Strong Customer Authentication MiTO Mobile (6 MB .PDF)", "https://bancaifigest.com/wp-content/uploads/2025/05/STRONG-CUSTOMER-AUTHENTICATION-MiTO-MOBILE.pdf"),
    ])
    + '<div class="tm-prose">'
    "<p>PDS2 estende il proprio ambito di applicazione anche a player diversi dalle Banche, noti come Operatori Terzi, definendone diritti e obblighi, anche nei confronti degli utenti finali.</p>"
    "<p>In sintesi, i principi fondanti di PSD2 sono i seguenti:</p>"
    "<ul class=\"tm-bullet-list\"><li>trasparenza nei servizi di pagamento;</li>"
    "<li>sicurezza nelle transazioni, con il rafforzamento dei diritti degli utenti e l’introduzione di requisiti più stringenti per i prestatori di servizi di pagamento;</li>"
    "<li>innovazione nei servizi di pagamento online;</li>"
    "<li>aumento della competitività tra i soggetti che offrono servizi di pagamento online.</li></ul>"
    "<h3 class=\"tm-doc-group\">OPERATORI TERZI: CHI SONO E QUALI SERVIZI OFFRONO?</h3>"
    "<p>PSD2 disciplina nuovi servizi di pagamento prestati anche da operatori diversi dalle Banche, i c.d. Operatori Terzi. Questi i principali:</p>"
    "<p><strong>PISP (Payment Initiation Service Providers):</strong><br>sono soggetti che, su espressa autorizzazione del cliente, prestano a favore dell’utente stesso il servizio di disposizione di ordini di pagamento; fanno ossia da tramite tra la Banca ed il titolare del conto di pagamento – accessibile online – e avviano il pagamento a favore di un terzo soggetto, beneficiario della disposizione.</p>"
    "<p>I PISP, ad esempio, permettono all’utente di effettuare un pagamento dal proprio conto ad un venditore, attraverso l’utilizzo di un software ‘ponte’ tra i due account.</p>"
    "<p><strong>AISP (Account Information Services Providers):</strong><br>sono operatori che consentono all’utente, titolare di conti accessibili online, di ottenere un’informativa completa relativa ai servizi di pagamento dei rapporti a lui intestati. Ad esempio, l’utente potrà usare gli AISP per avere una visione di insieme della propria situazione finanziaria, analizzare le proprie abitudini di spesa e le proprie esigenze finanziarie future.</p>"
    "<p><strong>PIISP (Payment Issuer Instrument Service Providers):</strong><br>sono soggetti che emettono carte di pagamento, regolate su un conto di pagamento accessibile online, di un istituto di credito diverso da quello che ha emesso la carta. I CISP non detengono direttamente fondi dei clienti, ma possono interrogare preventivamente la Banca presso cui il conto è attivo, per verificare la disponibilità dei fondi oggetto della transazione disposta dall’utente.</p>"
    "</div>"
    + '<div class="tm-docs-plain">' + doc_list([("Gestione dei consensi alle Terze Parti", "https://www.bancaifigest.com/wp-content/uploads/2019/08//THIRD%20PARTY%20PROVIDER%20MiTO.pdf")]) + "</div>"
    + '<div class="tm-prose">'
    "<h3 class=\"tm-doc-group\">SEZIONE DEDICATA AGLI OPERATORI TERZI</h3>"
    "<p>La documentazione sulle specifiche tecniche per l’utilizzo delle funzionalità di accesso ai conti online da parte degli Operatori Terzi è disponibile <a href=\"https://www.bancaifigest.com/psd2\" target=\"_blank\" rel=\"noopener\">in questa pagina dedicata</a>. Allo stesso indirizzo è disponibile uno strumento che permette agli Operatori Terzi di eseguire dei test sulle funzionalità.</p>"
    "</div>"
)

PSD2_TPP_HTML = (
    '<div class="tm-prose">'
    "<h3 class=\"tm-doc-group\">PSD2 – Payment Service Directive 2 (UE 2015/2366)</h3>"
    "<p>Interfaccia dedicata per le Terze Parti (TPP) ex art. 30 e ss. RTS (regolamento delegato UE 2018/389)</p>"
    f"<p>Ai fini delle operazioni connesse alla PSD2 si mette a disposizione delle Terze Parti autorizzate un’interfaccia dedicata per la componente home banking (ad es. bonifici) (Cabel Industry SPA – PSD2 Portal). Per collegarsi al servizio, consultare la relativa documentazione tecnica e richiedere maggiori informazioni, è sufficiente accedere al sito {CABEL} e seguire le istruzioni riportate.</p>"
    f"<p>Per le specifiche tecniche degli standard API utilizzati è possibile consultare il sito {CABEL}.</p>"
    "<h3 class=\"tm-doc-group\">PSD2 – Payment Service Directive 2 (UE 2015/2366) [English version]</h3>"
    f"<p>For PSD2 purposes, to connect to home banking services (i.e. SCT) a dedicated interface (Cabel Industry SPA – PSD2 Portal) is provided to authorized TPPs. To connect to such services, consult technical documentation and require more information please visit the website {CABEL} and follow the instructions.</p>"
    f"<p>For API standard’s technical specifications, please visit the website {CABEL}.</p>"
    "</div>"
    + doc_accordion_html([("Statistiche trimestrali sulla disponibilità e le prestazioni dell’interfaccia", doc_list(INFO_KPI))])
)

INFO_HTML = (
    info_section("trasparenza", "Trasparenza", doc_accordion(INFO_TRASPARENZA))
    + info_section("reclami", "Reclami",
        doc_group("Informativa gestione reclami", [("INFO RECLAMI SUL SITO", "https://www.bancaifigest.com/PDF/Reclami/info-reclami-sul-sito-2026-1.pdf")])
        + doc_group("Rendiconto annuale dei reclami servizi bancari e finanziari", [("RENDICONTO RECLAMI SERVIZI BANCARI E FINANZIARI 2025", "https://www.bancaifigest.com/PDF/Reclami/rendiconto-reclami-servizi-bancari-e-finanziari-2025.pdf")]))
    + info_section("sedi-di-esecuzione", "Sedi di esecuzione",
        doc_group("Informativa sedi di esecuzione", [
            ("RTS 28 – ANNO 2025 PRO", "https://www.bancaifigest.com/PDF/sesecuzione/RTS28_2025_PRO.pdf"),
            ("RTS 28 – ANNO 2025 RETAIL", "https://www.bancaifigest.com/PDF/sesecuzione/RTS28_2025_RET.pdf"),
            ("Tabella Elenco Negoziatori", "https://www.bancaifigest.com/PDF/sesecuzione/Tabella_elenco_negoziatori_2024.pdf"),
        ]))
    + info_section("psd2", "PSD2", '<h3 class="tm-doc-group">Informativa PSD2</h3>' + PSD2_HTML)
    + info_section("psd2-tpp", "PSD2-TPP", PSD2_TPP_HTML)
    + info_section("schede-prodotto", "Schede prodotto",
        '<h3 class="tm-doc-group">Informativa schede prodotto</h3><div class="tm-prose">'
        '<p>Per ricercare titoli cliccare sul seguente link: <a href="https://www.borsaitaliana.it/homepage/homepage.htm" target="_blank" rel="noopener"><strong>Borsa Italiana</strong></a></p>'
        '<p>Per ricercare schede prodotto MIFID II cliccare sul seguente link: <a href="https://bancaifigest.com/schede_prodotto/" target="_blank" rel="noopener"><strong>Schede prodotto</strong></a></p></div>')
    + info_section("collocamento", "Collocamento",
        doc_accordion_html([(title, US_PERSON + doc_list(docs)) for title, docs in INFO_COLLOCAMENTO]))
    + info_section("acf", "ACF", doc_group("Informativa ACF", [("ACF", "https://www.acf.consob.it/")]))
    + info_section("fea", "FEA", doc_group("Informativa FEA", [
        ("CONTRATTO FIRMA ELETTRONICA AVANZATA (FEA)", "https://www.bancaifigest.com/PDF/FEA/contratto-1.pdf"),
        ("ELENCO DEI DOCUMENTI SOTTOSCRIVIBILI CON FEA", "https://www.bancaifigest.com/PDF/FEA/documenti-04-2026.pdf"),
    ]))
)
add(
    "info-prodotti.html",
    "Informazioni",
    "Informazioni e link utili: trasparenza, reclami, sedi di esecuzione, PSD2, schede prodotto, collocamento, ACF e FEA.",
    hero("Informazioni", "Informazioni normative e regolamentari relative ai prodotti e servizi offerti da Banca Ifigest")
    + f"""
<section class="uk-section tm-section-docs">
  <div class="uk-container uk-container-large">
    {INFO_HTML}
  </div>
</section>""",
    "trasparenza guide pratiche fogli informativi fid antiusura reclami sedi di esecuzione rts 28 psd2 tpp kpi schede prodotto mifid collocamento acf fea firma elettronica",
)

add(
    "sostenibilita.html",
    "Sostenibilità",
    "Crediamo nella sostenibilità come fattore di creazione di valore nel lungo periodo per clienti, azionisti e comunità.",
    hero("Sostenibilità", "Crediamo nella sostenibilità come fattore di creazione di valore nel lungo periodo per clienti, azionisti e comunità")
    + placeholder_blocks("sostenibilita", images=False),
    "esg sostenibilità",
)
# Contenuti da bancaifigest.com/avvisi-per-i-soci/ (schede: Avvisi, Documenti, Aumento di capitale)
SOCI_DOCS = doc_list([
    ("Relazione finanziaria semestrale consolidata", "https://www.bancaifigest.com/PDF/areasoci/relazione-finanziaria-semestrale-consolidata-BANCA-IFIGEST_%20IAS-34.pdf"),
])
SOCI_CAPITALE = doc_list([
    ("Prospetto Ifigest aumento di capitale", "https://www.bancaifigest.com/PDF/areasoci/PROSPETTO-IFIGEST-AUMENTO-CAPITALE-2024.pdf"),
    ("Avviso agli Azionisti di Offerta in Opzione ai sensi 2441", "https://www.bancaifigest.com/PDF/areasoci/avviso-azionisti.docx"),
])
add(
    "area-soci.html",
    "Area Soci",
    "Avvisi, documenti e informazioni sul capitale sociale per i soci di Banca Ifigest.",
    hero("Area Soci", "Avvisi, documenti e informazioni sul capitale sociale")
    + f"""
<section class="uk-section tm-section-tabs">
  <div class="uk-container uk-container-large">
    <ul class="tm-tabs" uk-tab="connect: #tm-soci-panels; animation: uk-animation-fade">
      <li><a href="#">Avvisi</a></li>
      <li><a href="#">Documenti</a></li>
      <li><a href="#">Aumento di capitale</a></li>
    </ul>
    <div id="tm-soci-panels" class="uk-switcher tm-tab-panels">
      <div>
        <h2 class="tm-section-title">Avviso ai signori soci</h2>
        <div>
          <p>Si comunica che sono state poste in vendita n. 2.721 azioni Banca Ifigest spa al prezzo unitario di Euro 5,50.</p>
          <p>Il controvalore dovrà essere corrisposto contestualmente al trasferimento dei titoli azionari.</p>
          <p>Con lettera datata 1° aprile 2025 questa società ha provveduto, ai sensi di Statuto, ad inviare ad ogni Socio specifica comunicazione per l’esercizio del diritto di prelazione.</p>
          <p>I soci interessati all’esercizio del diritto di prelazione potranno contattare l’ufficio di Presidenza allo <a href="tel:+390552463201">055/2463201</a> per ogni ulteriore informazione.</p>
        </div>
      </div>
      <div>
        <h2 class="tm-section-title">Documenti area soci</h2>
        {SOCI_DOCS}
      </div>
      <div>
        <h2 class="tm-section-title">Documenti aumento di capitale</h2>
        {SOCI_CAPITALE}
      </div>
    </div>
  </div>
</section>""",
    "soci azionisti avvisi prelazione azioni documenti aumento di capitale relazione semestrale prospetto",
)

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
add("trasparenza.html", "Trasparenza", "Trasparenza Banca Ifigest.", hero("Trasparenza", image=False) + placeholder_blocks("trasparenza", cta=False), "trasparenza")
add("dichiarazione-accessibilita.html", "Dichiarazione di Accessibilità", "Dichiarazione di accessibilità del sito Banca Ifigest.", hero("Dichiarazione di Accessibilità", image=False) + placeholder_blocks("accessibilita", cta=False), "accessibilità")
add("disconoscimento-operazioni.html", "Disconoscimento delle operazioni di pagamento", "Disconoscimento delle operazioni di pagamento.", hero("Disconoscimento delle operazioni di pagamento", image=False) + placeholder_blocks("disconoscimento", cta=False), "disconoscimento pagamento")

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

# Privacy Policy --------------------------------------------------------------
# Impaginata come la privacy policy del riferimento (titolo, sottotitolo, testo).
# Testo copiato dalla privacy policy Iubenda di Banca Ifigest
# (https://www.iubenda.com/privacy-policy/58439536): non si aggiorna da solo,
# va risincronizzato a mano in content/privacy-policy.html quando cambia.
PRIVACY_HTML = (ROOT / "content/privacy-policy.html").read_text(encoding="utf-8")
add(
    "privacy-policy.html",
    "Privacy Policy",
    "Privacy policy del sito Banca Ifigest: quali dati raccogliamo, perché li raccogliamo e quali sono i diritti degli utenti.",
    f"""
<section class="uk-section tm-section-policy">
  <div class="uk-container uk-container-large">
    <h1 class="tm-policy-title">Privacy Policy</h1>
    <p class="tm-policy-intro">Benvenuto nella privacy policy di bancaifigest.com. Questa policy ti aiuterà a comprendere quali dati raccogliamo, perché li raccogliamo e quali sono i tuoi diritti in merito.</p>
    <p class="tm-caption">Ultima modifica: 24 febbraio 2026</p>
    <div class="tm-policy">{PRIVACY_HTML}</div>
  </div>
</section>""",
    "privacy policy gdpr dati personali cookie trattamento diritti titolare",
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


IMAGE_SPECS = {
    "hero": ("Testata (hero)", "2880 × 1106 px (circa 2,6:1)"),
    "tm-placeholder-square": ("Blocco immagine + testo", "1312 × 1312 px (1:1)"),
    "tm-placeholder-square tm-placeholder-logo": ("Logo società del Gruppo (non viene ritagliato)", "800 × 800 px (1:1), sfondo bianco o trasparente"),
}


def write_image_manifest():
    """Elenco delle immagini attese, pagina per pagina, in assets/img/pages/README.md."""
    lines = [
        "# Immagini delle pagine",
        "",
        "Generato da `tools/build.py`: non modificare a mano.",
        "",
        "Caricare qui i file con **esattamente** questi nomi (minuscolo). Estensioni accettate: `.jpg`, `.jpeg`, `.png`, `.svg`, `.webp` (per i loghi meglio `.png` o `.svg`). Il nome qui sotto indica l'estensione attesa, ma vanno bene anche le altre.",
        "Finché un file manca, la pagina mostra il segnaposto; appena caricato, l'immagine compare da sola.",
        "",
    ]
    for slug, title, *_ in PAGES:
        html = (ROOT / slug).read_text(encoding="utf-8")
        found = []
        for m in re.finditer(r'<div class="(tm-hero-media|tm-split-media|tm-logo-media)">(?:<a [^>]*>)?<div class="tm-placeholder ([^"]+)"><img class="tm-photo" src="assets/img/pages/([^"]+)"', html):
            kind = "hero" if m.group(1) == "tm-hero-media" else m.group(2).strip()
            found.append((m.group(3), *IMAGE_SPECS[kind]))
        if found:
            lines += [f"## {title} (`{slug}`)", "", "| File | Uso | Dimensioni consigliate |", "|---|---|---|"]
            lines += [f"| `{f}` | {use} | {size} |" for f, use, size in found]
            lines.append("")
    (ROOT / "assets/img/pages").mkdir(parents=True, exist_ok=True)
    (ROOT / "assets/img/pages/README.md").write_text("\n".join(lines), encoding="utf-8")


def main():
    index = [
        {"url": slug, "title": title, "description": description, "text": f"{keywords} {text_of(body)}"}
        for slug, title, description, body, keywords in PAGES
        if slug != "cerca.html"
    ]
    (ROOT / "assets/js/search-index.js").write_text(
        "/* Generato da tools/build.py: non modificare a mano. */\n"
        "window.IFIGEST_SEARCH_INDEX = " + json.dumps(index, ensure_ascii=False, indent=1) + ";\n",
        encoding="utf-8",
    )
    for slug, title, description, body, keywords in PAGES:
        (ROOT / slug).write_text(page(slug, title, description, body), encoding="utf-8")
    write_image_manifest()
    print(f"Built {len(PAGES)} pages")


if __name__ == "__main__":
    main()
