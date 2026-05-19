# CLAUDE.md

Istruzioni per Claude Code (e qualunque altro assistente AI compatibile) che lavora su questo repo. Questo file viene caricato automaticamente all'inizio di ogni sessione dalla root del progetto, quindi vale come "memoria di progetto" condivisa.

## Regola d'oro: tieni aggiornati CLAUDE.md e README.md

**Ogni volta che modifichi il codice in modo non banale, aggiorna anche questo file (CLAUDE.md)** se la modifica:

- introduce o rimuove una dipendenza, una libreria, un dataset esterno;
- cambia una convenzione (naming, struttura del file, pattern di stato, persistenza in `localStorage`, ecc.);
- cambia il flusso utente principale (selezione famiglie, quiz, risposta, scoring);
- aggiunge una nuova lingua dell'interfaccia, una nuova famiglia di scritture, un nuovo dataset;
- modifica il comportamento di pubblicazione (Pages, CI, workflow);
- introduce un vincolo non ovvio (workaround, bug noto, limite di un'API).

**Aggiorna anche `README.md`** quando una modifica e' significativa per chi legge il repo da fuori (chiunque apra il sorgente su GitHub): nuova feature visibile, cambio dell'URL del sito, requisiti di setup. Il README e' la facciata pubblica del progetto, deve restare sintetico ma aggiornato.

Se la modifica e' una piccola correzione (typo, refactor locale, rinomina di una variabile privata, fix CSS puntuale), **non** serve aggiornare ne' CLAUDE.md ne' README. In dubbio: aggiorna CLAUDE.md (interno) e valuta se anche README (esterno).

Aggiornare significa: modificare la sezione gia' esistente che descrive l'area toccata. Non aggiungere log di modifiche o changelog qui, il `git log` e il `CHANGELOG.md` (gestito da release-please, vedi sotto) sono le fonti di verita' per la cronologia.

## Cos'e' il progetto

"Guess the Char" è un quiz interattivo a singola pagina HTML che mostra un carattere preso da uno dei sistemi di scrittura del mondo (CJK, sud-est asiatico, indiano, mediorientale, ecc.) e chiede all'utente a quale scrittura appartiene. Niente account, niente backend: tutto in-page, persistenza minima via `localStorage` per le opzioni utente. Tono: gioco-quiz, palette dark, design pulito.

## Roadmap: migrazione ad Angular (importante)

**Lo stack attuale, HTML monolitico, e' uno stato provvisorio**. La direzione del progetto e' migrare a un'app Angular vera (Angular 19+, standalone components, signals, OnPush) appena ci sara' la finestra per farlo. Quello che vedi oggi in `index.html` e' un MVP/prototipo, non l'architettura finale: e' "vecchio e va cambiato".

Cosa significa nel concreto per chi lavora sul repo:

- Tutto cio' che metti nel monolite **non deve creare ostacoli** alla futura migrazione. In dubbio, preferisci scelte conservative (nessuna libreria pinned, nessun pattern proprietario, niente trucchi che dipendono dall'essere "tutto in una pagina").
- Se proponi una feature complessa che richiede architettura (stato condiviso non banale, routing, multi-pagina, modular CSS), **questo e' il segnale** che e' meglio iniziare la migrazione invece di stratificare patch sul monolite.
- Il workflow di sviluppo descritto qui sotto (PR per scope, Conventional Commits, release-please, deploy su tag) **NON dipende dallo stack**: e' gia' lo stesso che useremo dopo la migrazione. Cambia solo `deploy.yml` (l'artifact passera' dalla root del repo all'output del build di Angular, tipo `dist/<app>/browser/`).
- Non c'e' una data di migrazione. Quando arriva, sara' descritta in una PR `feat!:` dedicata e questo file va aggiornato di conseguenza (struttura cartelle, comandi npm, lazy loading, ecc.).

In sintesi: tratta questo CLAUDE.md come un documento valido per entrambe le fasi, e tratta `index.html` come temporaneo.

## Stack (oggi)

- **HTML statico monolitico**. Un solo `index.html` alla root contiene markup, stili (`<style>` inline) e logica (`<script>` inline). Nessun build step, nessuna toolchain.
- **Nessuna dipendenza JavaScript**: niente bundler, niente package manager, niente node_modules. Il sito funziona aprendolo come file locale o servendolo da un qualunque server statico.
- **Persistenza**: `localStorage` per la lingua UI e le selezioni di famiglie/scritture. Chiavi con prefisso applicativo (es. `gtc-lang`, `gtc-active`).
- **i18n**: italiano (default) + inglese, switch via toggle nella UI. Le stringhe localizzate vivono in oggetti JS dentro l'`<script>` di `index.html`.

## Struttura

```
.
├── index.html               # tutta l'app: markup, stili, script, dataset caratteri
├── README.md                # facciata pubblica (cosa fa, come si usa)
├── CHANGELOG.md             # generato/aggiornato da release-please
├── LICENSE                  # MIT
├── CLAUDE.md                # questo file
├── release-please-config.json
├── .release-please-manifest.json
└── .github/
    ├── workflows/
    │   ├── release.yml      # release-please + riscrittura body Release/PR
    │   └── deploy.yml       # GitHub Pages al release event
    └── scripts/
        └── release-notes.py # genera "In sintesi + Dettagli" dai commit
```

### Convenzioni

- **Tutto in `index.html`**: non spezzare in file separati prima del passaggio ad Angular. Se nasce la voglia di splittare, e' segno che e' ora di iniziare la migrazione.
- **Stato**: variabili globali o moduli IIFE dentro lo `<script>`, non framework. Se la complessita' giustifica un framework, vedi la nota sul piano Angular.
- **i18n**: stringhe in un dizionario JS organizzato per chiave logica. Italiano e' la lingua di default; chiavi nuove vanno aggiunte sia in IT che in EN.
- **Dataset scritture**: oggetto JS con famiglie e caratteri. Ogni carattere puo' essere una stringa o un oggetto con campi estensibili (etimologia, link Wiktionary, ecc.) per supportare evoluzioni future.

## Comandi

Niente comandi: aprire `index.html` in un browser. Per test rapidi su un server statico:

```bash
python3 -m http.server 8000
# poi http://localhost:8000
```

Non e' configurato lint, ne' test, ne' formatter. La barra qualita' e' "il file e' leggibile" + "il sito funziona".

## Branching e Pull Request

Flow stile GitHub Flow: niente push diretti su `main`, tutto passa da una PR.

### Branch

Crea sempre un branch dal `main` aggiornato. Prefissi convenzionali (servono solo a te per orientarti, non c'e' validazione automatica):

- `feat/<slug>`: feature nuova rivolta all'utente.
- `fix/<slug>`: bugfix.
- `chore/<slug>`: lavori interni (build, CI, dipendenze, riordino).
- `docs/<slug>`: modifiche solo a documentazione (incluso CLAUDE.md).
- `refactor/<slug>`: refactor a comportamento invariato.

Esempi: `feat/script-armenian`, `fix/score-reset-edge-case`, `chore/bump-actions-versions`.

### Scope di una PR

**Una PR copre uno scope logico.** Due bug non correlati, anche piccoli, vanno in due PR separate. Regola pratica: se lo `scope` del Conventional Commit dovrebbe essere diverso tra una modifica e l'altra, sono due PR (es. `fix(ui):` + `fix(scoring):` non si bundlano).

Vale anche se si tocca lo stesso file: se `index.html` riceve un fix UI al menu lingua e uno separato al calcolo del punteggio, due PR. Il refactor "di passaggio" mentre si sistema altro va evitato; se serve, una `refactor:` dedicata.

Eccezione: ritocchi adiacenti che condividono lo stesso "perche'" possono stare in una sola PR. Tipico esempio: una pass di responsiveness mobile che tocca diverse sezioni e ha un solo motivo ("rendere il sito leggibile su iPhone") puo' stare in `fix(ui):` o `fix(mobile):` unico. Ma se i fix sono indipendenti, sono due PR.

Perche': PR piccole e mono-scope sono piu' rapide da revieware, piu' facili da rollbaccare e generano release notes piu' pulite.

### Commit: Conventional Commits + body discorsivo

Tutti i commit (e i titoli delle PR) seguono [Conventional Commits](https://www.conventionalcommits.org/).

- Il **subject** e' la riga breve e tecnica, sempre nel formato `tipo(scope opzionale): cosa`. Serve a release-please per capire il tipo di cambio (bump version) e per generare il **bullet** dell'indice nella GitHub Release (subject ripulito del prefisso e capitalizzato).
- Il **body** e' una **descrizione user-facing breve, 1-2 frasi**, dal punto di vista di chi visita il sito (non dello sviluppatore). Niente nomi di file, regole CSS, dettagli implementativi a meno che non sia il punto. Compare nella sezione "Dettagli" della GitHub Release sotto il titoletto omonimo.

Anti-esempi di body troppo tecnici:

- ❌ `Spostato il toggle "Reset score" da un onclick inline a un addEventListener nel DOMContentLoaded.` (chi visita non sa cosa significhi)
- ✅ `Il pulsante "Reset" ora si attiva subito al caricamento della pagina invece di aspettare il primo click.`

**Niente hard-wrap a 72 caratteri** nel body. La vecchia convenzione "git da terminale" spezza le righe a 72 chars, ma GitHub Flavored Markdown rende ogni newline singolo come `<br>` nelle Release: le frasi appaiono spezzate a metà. Scrivi **una frase per riga lunga** (anche 200 chars, non importa), e separa i paragrafi con una **riga vuota**. Lo step Python nel workflow `release.yml` ha comunque un `unwrap_paragraphs()` che ricongiunge i wrap, ma e' un cerotto: meglio non spezzarle alla fonte.

Tipi e mapping:

| Tipo | Bump | Appare nella Release? | Etichetta |
|---|---|---|---|
| `feat:` | MINOR | si | Novita' |
| `fix:` | PATCH | si | Correzioni |
| `perf:` | PATCH | si | Performance |
| `refactor:` | PATCH | si | Refactor |
| `chore:` | nessuno | no | (storia git) |
| `docs:` | nessuno | no | (storia git) |
| `test:` | nessuno | no | (storia git) |
| `ci:`, `build:`, `style:` | nessuno | no | (storia git) |
| `feat!:` o `BREAKING CHANGE:` nel body | MAJOR | si, in cima | Modifiche incompatibili |

Esempio di commit per una nuova feature (caso tipico, raccomandato). Subject tecnico, body user-facing breve, niente wrap a 72 chars:

```
feat(scripts): aggiungi alfabeto armeno

L'armeno (Հայերեն) entra nelle scritture mediorientali con 38 caratteri base. Disponibile come scrittura selezionabile, con link a Wiktionary per ciascun carattere.
```

Body **consigliato sempre** per `feat:`, `fix:`, `perf:`, `refactor:`. Se proprio manca (cambio piccolissimo e ovvio), il workflow fa un fallback: usa il subject ripulito del prefisso e capitalizzato.

### Merge: squash sempre

Strategia per le PR: **Squash and merge**.

- Il **titolo della PR** = subject del commit squashato = Conventional Commit. release-please lo legge da li'.
- Il **body della PR** = body del commit squashato = descrizione discorsiva. La Release lo prende da qui.

Quindi quando apri la PR cura titolo **e** descrizione: insieme diventano il commit, da cui release-please costruisce la release. La PR e' la fonte di verita'.

### Pulizia branch dopo il merge

Il branch **remoto** viene cancellato in automatico dal repo (setting `delete_branch_on_merge: true`). Lato **locale** invece i branch restano sulla tua macchina anche dopo che la PR e' stata mergiata. Ogni tanto vale la pena ripulire:

```bash
git fetch --prune                       # rimuove i tracking branch (origin/...) gia' scomparsi sul remoto
git branch | grep -vE '^\*|main$' | xargs -r git branch -D
                                        # cancella tutti i branch locali eccetto main e quello corrente
```

Il `-D` (maiuscolo) ignora il check "branch gia' mergiato": serve perche' lo squash merge non lascia una merge-base diretta, quindi `git branch -d` non li riconoscerebbe come mergiati.

### Setup repo

Le impostazioni del repo (merge strategy, commit message di default, auto-delete branch, branch protection su `main`, workflow permissions) vengono applicate via API con un PAT fine-grained. Stato target:

- Merge: solo squash merging. `Allow merge commits` e `Allow rebase merging` disattivati.
- Default commit message dello squash: `PR_TITLE` + `PR_BODY`. Il commit su `main` eredita titolo e descrizione della PR.
- `Automatically delete head branches`: attivo (i branch sono auto-cancellati dopo il merge).
- Branch protection su `main`: PR obbligatoria (0 review richiesti), `Require linear history` attivo, `Allow force pushes` e `Allow deletions` disattivati.
- Workflow permissions: `Read and write` con `Allow GitHub Actions to create and approve pull requests` attivo (serve a release-please per aprire la Release PR).

## Versioning

Schema [SemVer](https://semver.org): `MAJOR.MINOR.PATCH`. La fonte di verita' e' il campo in `.release-please-manifest.json` (il release-type e' `simple`, quindi non c'e' nessun `package.json` da bumpare).

### Rilascio: lo fa release-please, non tu

Il rilascio e' completamente automatizzato dal workflow `.github/workflows/release.yml`, che usa [release-please](https://github.com/googleapis/release-please). Punto importante da tenere a mente: **la Release PR non la apri tu**, te la trovi gia' aperta dal bot. E **il numero di versione non lo scegli tu**, lo calcola il bot in base ai tipi dei commit accumulati dopo l'ultimo tag (`fix:` => PATCH, `feat:` => MINOR, `BREAKING CHANGE` => MAJOR).

Cosa succede in pratica:

1. Mergi su `main` un commit `feat:` o `fix:` (qualunque commit "rilasciabile" secondo Conventional Commits).
2. Il workflow `release.yml` parte ad ogni push su `main`. release-please apre **automaticamente** una PR speciale tipo `chore(main): release X.Y.Z` che contiene:
   - bump di `.release-please-manifest.json`;
   - aggiornamento di `CHANGELOG.md` con i commit dell'ultimo ciclo, raggruppati per tipo (Features, Bug Fixes, ecc.).

   Subito dopo, uno step dello stesso workflow **riscrive il body della Release PR** nello stesso stile "In sintesi" + "Dettagli" che vedrai nella Release pubblicata, cosi' chi la review vede gia' un'anteprima fedele delle release notes. Non serve aprire la PR e ritoccarla a mano: ad ogni nuovo commit rilasciabile la PR viene rigenerata e riscritta automaticamente.
3. Quella Release PR **resta aperta** e **si auto-aggiorna** ogni volta che mergi su `main` un nuovo commit. Se il commit e' rilasciabile, viene incluso nelle note e (se serve) cambia il bump (es. da PATCH a MINOR). Se e' `chore:` / `docs:` / `ci:` / `test:` viene mergiato comunque su `main`, fara' parte del tag finale, ma non comparira' nelle release notes ne' influenzera' il numero di versione.
4. **La tua unica decisione** e' quando rilasciare: quando ti sembra ci sia abbastanza materiale, mergi la Release PR. Solo allora release-please:
   - crea il tag git (`vX.Y.Z` con la `v`);
   - crea la GitHub Release;
   - lo step finale del workflow **riscrive il body della Release** in due sezioni: **In sintesi** in cima (bullet con il subject ripulito per ogni voce, raggruppati per tipo: Novita', Correzioni, Performance, Refactor, Modifiche incompatibili) e **Dettagli** sotto (titoletti `###` con il body discorsivo, solo per le voci che hanno un body).

   La logica di composizione delle note vive in `.github/scripts/release-notes.py` (riceve `--range`, stampa il body su stdout). Lo stesso script alimenta sia la riscrittura della Release pubblicata sia quella della Release PR in attesa di merge.

Cose che **non** devi fare a mano (rispetto a prima):

- Tag git: no, lo fa release-please.
- Modifiche a `CHANGELOG.md`: no, lo riscrive release-please. Eccezione: se vuoi correggere un refuso o aggiungere una nota a posteriori, puoi farlo in una PR separata di tipo `docs:`.

Modi di forzare la prossima versione (raramente serve):

- Commenta nella Release PR con `Release-As: 1.5.0` (o `release-as: 1.5.0`) per forzare un numero di versione preciso.
- `feat!:` o `BREAKING CHANGE:` in body di un commit forza un bump MAJOR.

### Convenzioni tag

- Prefisso `v` (`v1.0.0`, non `1.0.0`).
- Suffisso (`v1.1.0-beta.1`) farebbe prerelease, ma con release-please base non si usa: per prerelease serve config dedicato (non attivo qui).

## Deploy: GitHub Pages

Pubblicazione via GitHub Actions, workflow `.github/workflows/deploy.yml`.

**Trigger: solo Release pubblicata** (`on: release: types: [published]`). Cioe': quando mergi la Release PR di release-please nasce un tag + una GitHub Release; quel `release: published` fa partire il deploy. **I merge su `main` da soli non vanno live**: questa e' una scelta deliberata, cosi' il sito in produzione coincide sempre con un tag.

Conseguenze pratiche:

- Tra una release e l'altra, `main` accumula PR mergiate ma il sito live resta alla versione precedente. Per vedere l'ultimo `main` non rilasciato, apri `index.html` localmente.
- Se proprio serve mostrare a qualcuno un'anteprima di `main` non ancora rilasciato (demo, screenshot), si lancia a mano `Actions > Deploy to GitHub Pages > Run workflow` (trigger `workflow_dispatch`). Va considerato un'eccezione, non la norma.
- Per rilasciare in fretta dopo aver mergiato qualche PR, basta mergiare anche la Release PR che release-please tiene aperta: il deploy parte subito dopo.

Cose da sapere se lo modifichi:

- L'artifact Pages e' l'intera root del repo (eccetto `.github`, `LICENSE`, `README.md`, `CLAUDE.md`, `CHANGELOG.md`, manifest e config di release-please).
- `.nojekyll` (vuoto) e' presente alla root per impedire a Pages di processare i file via Jekyll.
- Prima pubblicazione: in *Settings > Pages* del repo va scelto "Source: GitHub Actions" una volta sola.

## Vincoli e cose da non fare

- **Non** introdurre dipendenze npm o un build step prima di una migrazione esplicita ad Angular: il valore di questo progetto e' "apri e funziona".
- **Non** spezzare `index.html` in file separati JS/CSS senza un motivo dichiarato: pochi file ma piu' grandi sono ok in questa fase.
- **Non** rimuovere `.nojekyll` senza una buona ragione: senza il file Pages prova a interpretare i nomi che iniziano con `_` come Jekyll.
- **Non** committare file generati o cache.

## Note operative per l'assistente

- Quando ti viene chiesto di "fare X" rispondi in italiano (il proprietario lavora in italiano).
- Niente em-dash (`—`) e niente freccia (`→`) nei file di questo repo, ne' nei messaggi: usa virgole, due punti, parentesi, o parole ("a", "verso", "diventa").
- Prima di marcare un task come finito, controlla che il sito funzioni aprendolo localmente.
