# godot-audit

**Lingue**:
[English](README.md) ·
[Français](README.fr.md) ·
[Deutsch](README.de.md) ·
[中文](README.zh.md) ·
[日本語](README.ja.md) ·
[Italiano](README.it.md) ·
[Español](README.es.md)

[![Python versions](https://img.shields.io/badge/python-3.14+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/olivierpons/godot-audit/actions/workflows/ci.yml/badge.svg)](https://github.com/olivierpons/godot-audit/actions/workflows/ci.yml)

Esegui l'audit della struttura di un progetto Godot rispetto alle tue convenzioni. Sola lettura: non modifica mai alcun file.

`godot-audit` controlla che i tuoi file `.tscn` e `.gd` siano organizzati in modo coerente (split o colocated), che i nomi dei file degli asset siano in snake_case, che non ci siano versioni obsolete `_old`/`_bak` in giro e che nessun file compagno `.uid` / `.import` sia orfano. I nomi di file quasi identici (errori di battitura come `skeleton` vs `skeletton`) vengono segnalati, mentre le varianti numerate (`v1`, `v2`, ...) sono correttamente riconosciute e ignorate.

## Funzionalità

- **Due layout di progetto supportati**:
  - `split` — `scenes/entities/slime.tscn` + `scripts/entities/slime.gd` (convenzione documentata predefinita di Godot)
  - `colocated` — `features/entities/slime.tscn` + `features/entities/slime.gd` (raggruppato per feature, il default)
- **Sei categorie di controlli**: mirroring, naming, stale names, near-duplicates, backups, orphan companions.
- **Output terminale Rich** con fallback a ANSI semplice.
- **Separazione `-h` / `--help`**: memo breve per utenti esperti, documentazione completa con esempi per l'esplorazione.
- **CI-friendly**: codici di uscita non zero, `--no-color`, `--no-rich`, output JSON.
- **Formati di output multipli**: testo (tabelle Rich), JSON, Markdown.
- **Suggerimenti consapevoli del layout**: ogni avviso viene con un suggerimento concreto di spostamento.

## Installazione

Installa direttamente da GitHub:

```bash
# Ultima versione
pip install git+https://github.com/olivierpons/godot-audit.git

# Fissa a una release specifica
pip install git+https://github.com/olivierpons/godot-audit.git@v1.0.0
```

Questo importa automaticamente `cli-toolkit[rich]` dal suo repository GitHub.

Richiede Python 3.14 o superiore.

## Avvio rapido

```bash
# Audit della directory corrente (layout colocated di default)
godot-audit

# Audit di un progetto Godot specifico
godot-audit ~/godotprojects/my_game

# Usa invece il layout split
godot-audit ~/godotprojects/my_game --layout split

# Riepilogo in basso per rapporti lunghi
godot-audit . --summary-position bottom

# Modalità CI rigorosa: fa fallire la build anche su problemi INFO
godot-audit . --strict --no-color --no-rich --quiet

# Esporta in JSON per elaborazione successiva
godot-audit . --format json --output audit.json

# Rapporto Markdown per un commento PR GitHub
godot-audit . --format markdown > audit.md
```

## Opzioni

Ogni opzione ha una forma breve e una lunga. `-h` stampa un memo compatto; `--help` stampa la documentazione completa con esempi.

| Breve | Lungo | Descrizione |
| --- | --- | --- |
| | `PATH` | Percorso alla radice del progetto Godot (default: directory corrente) |
| `-y` | `--layout` | `split` o `colocated` (default: `colocated`) |
| `-f` | `--format` | `text`, `json` o `markdown` (default: `text`) |
| `-o` | `--output` | Scrivi su file invece di stdout |
| `-c` | `--category` | Riporta solo questa categoria (ripetibile) |
| `-s` | `--severity` | Severità minima: `INFO`, `WARN`, `ERROR` (default: `INFO`) |
| `-t` | `--threshold` | Soglia di similarità per il rilevamento di quasi-duplicati (default: `0.88`) |
| `-i` | `--ignore-dir` | Aggiungi una directory alla lista ignore (ripetibile) |
| `-p` | `--summary-position` | `top`, `bottom` o `none` (default: `top`) |
| `-S` | `--strict` | Uscita non zero anche su problemi INFO |
| `-q` | `--quiet` | Nascondi il pannello riepilogo (alias per `-p none`) |
| `-R` | `--no-rich` | Forza output in testo semplice |
| `-n` | `--no-color` | Disabilita i colori ANSI |
| `-v` | `--verbosity` | 0=silent, 1=normal, 2=verbose, 3=debug |
| `-l` | `--list-categories` | Elenca tutte le categorie di controllo ed esci |
| `-L` | `--list-ignored-dirs` | Elenca le directory ignorate di default ed esci |
| `-V` | `--version` | Stampa la versione ed esci |
| `-h` | | Memo di aiuto breve |
| | `--help` | Aiuto completo con esempi |

## Categorie di controlli

| Categoria | Cosa rileva |
| --- | --- |
| `mirroring` | Dipendente dal layout. `split`: script nella radice di `scripts/` mentre la scena è in `scenes/<subdir>/`. `colocated`: script la cui scena corrispondente esiste in una directory diversa. |
| `naming` | Nomi di file non snake_case (spazi, trattini, maiuscole, caratteri speciali). Suggerisce un'alternativa snake_case. Severità: INFO. |
| `stale_name` | File che terminano con `_old`, `_bak`, `_backup`, `_copy`, `_tmp`, `_temp`, `_new`, `_todelete` o `_deprecated`. Promuovi o elimina. |
| `near_duplicate` | Coppie di file con radici quasi identiche nella stessa directory (cattura errori di battitura come `skeleton` vs `skeletton`). Le varianti numerate (`v1`/`v2`, `01`/`02`, `Bird Call 1` / `Bird Call 3`) vengono automaticamente saltate. |
| `backup` | Backup dell'editor: `*.bak`, `*.bak.*`, `*.orig`, nomi che terminano con `~`. |
| `orphan_companion` | File `.uid` o `.import` il cui file sorgente (`foo.gd`, `bar.mp3`) manca. Sicuro da eliminare. |

## Codici di uscita

| Codice | Significato |
| --- | --- |
| `0` | Nessun problema al o sopra il filtro di severità corrente |
| `1` | Almeno un `WARN` o `ERROR` è stato riportato (o qualsiasi `INFO` quando `--strict` è impostato) |
| `2` | Input non valido: `PATH` non esiste o non è un progetto Godot |

## Convenzioni di layout

### Layout split (documentato di default da Godot)

```
res://
├── scenes/
│   ├── entities/
│   │   └── slime.tscn
│   └── levels/
│       └── level_01.tscn
└── scripts/
    ├── entities/
    │   └── slime.gd
    └── levels/
        └── level_01.gd
```

Le scene e gli script vivono in directory di primo livello separate che si rispecchiano a vicenda. Audit con:

```bash
godot-audit . --layout split
```

### Layout colocated (default, raccomandato)

```
res://
├── features/
│   ├── entities/
│   │   ├── slime.tscn
│   │   └── slime.gd
│   └── levels/
│       ├── level_01.tscn
│       └── level_01.gd
├── autoload/         # singleton, no .tscn
├── components/       # logica riutilizzabile, no .tscn
└── addons/
```

Scena e script allegato vivono fianco a fianco. Gli script sotto `autoload/`, `components/` e `addons/` sono esenti dal controllo di colocazione poiché sono legittimamente solo script. Audit con:

```bash
godot-audit .
```

## Spostare i file in sicurezza

Quando un problema suggerisce di spostare uno script o una scena, **usa sempre il pannello FileSystem di Godot** (drag & drop nell'editor), mai `mv` da riga di comando. Godot riscrive ogni riferimento `.tscn` allo spostamento; il `mv` dell'OS no, e le tue scene finiscono per puntare a script mancanti.

## Variabili d'ambiente

| Variabile | Effetto |
| --- | --- |
| `NO_COLOR` | Quando impostata, disabilita tutti i colori ANSI e lo stile Rich. Vedi [no-color.org](https://no-color.org/). |

## Sviluppo

```bash
git clone https://github.com/olivierpons/godot-audit.git
cd godot-audit
pip install -e .
pip install pytest pytest-cov ruff mypy

# Test
pytest

# Lint + formattazione
ruff check .
ruff format .

# Esegui contro un vero progetto Godot
python -m godot_audit.cli ~/my_godot_project
```

## Licenza

MIT — vedi [LICENSE](LICENSE).
