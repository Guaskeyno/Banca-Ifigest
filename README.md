# Banca Ifigest — sito web

Sito statico in HTML, CSS e JavaScript. Il linguaggio visivo (tipografia Lato + Meghana, set di icone UIkit, bottoni a pillola, navigazione con dropbar, fasce colore con righe verticali) è ripreso dal sito di riferimento; colore principale `#005A7C`, testi e immagini specifici di Banca Ifigest.

## Struttura

```
*.html                      pagine generate (non modificare a mano)
assets/
  css/theme.css             tema del sito
  js/main.js                script del sito (menu mobile, ricerca)
  js/search-index.js        indice di ricerca (generato)
  fonts/                    Meghana (webfont)
  img/                      logo e favicon
  vendor/uikit/             libreria UIkit 3.25.25 (MIT), css e js separati
tools/build.py              generatore delle pagine
```

## Modificare i contenuti

Header, sotto-navigazione, sezione "Sedi e Contatti" e footer sono condivisi da tutte le pagine. Le pagine si generano da `tools/build.py`:

```bash
python3 tools/build.py
```

## Anteprima locale

```bash
python3 -m http.server 8000
```

Poi apri http://localhost:8000.

## Segnaposto da completare

- Immagini: tutte le immagini sono segnaposto (`.tm-placeholder`).
- Link senza destinazione (`#`): Lavora con noi, documenti PDF, segnalazione interna whistleblowing, schede prodotto MIFID II.
- Testo provvisorio (Lorem ipsum): Collocamento (Club Deal, FIA, Certificati, Polizze); due blocchi ciascuna su Gestioni Patrimoniali, Finanza Strutturata, Lombard Loans, Debt Advisory, Sostenibilità, Trasparenza, Dichiarazione di Accessibilità, Disconoscimento operazioni.
- Area Soci: i documenti puntano ai file su bancaifigest.com.

## Privacy Policy

Il testo di `privacy-policy.html` è copiato dalla privacy policy Iubenda di Banca Ifigest (https://www.iubenda.com/privacy-policy/58439536) e salvato in `content/privacy-policy.html`. Non si aggiorna automaticamente: quando la policy su Iubenda cambia, aggiornare quel file (e la data "Ultima modifica" in `tools/build.py`) e rigenerare le pagine.
