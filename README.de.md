# godot-audit

**Sprachen**:
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

Prüfen Sie die Struktur eines Godot-Projekts gegen Ihre Konventionen. Nur-Lesen: ändert niemals eine Datei.

`godot-audit` prüft, ob Ihre `.tscn`- und `.gd`-Dateien konsistent organisiert sind (split oder colocated), ob Asset-Dateinamen snake_case sind, ob keine veralteten `_old`/`_bak`-Versionen herumliegen und ob keine `.uid`/`.import`-Begleitdateien verwaist sind. Nahezu identische Dateinamen (Tippfehler wie `skeleton` vs `skeletton`) werden gemeldet, während nummerierte Varianten (`v1`, `v2`, ...) korrekt erkannt und ignoriert werden.

## Funktionen

- **Zwei Projekt-Layouts unterstützt**:
  - `split` — `scenes/entities/slime.tscn` + `scripts/entities/slime.gd` (Godots Standard-dokumentierte Konvention)
  - `colocated` — `features/entities/slime.tscn` + `features/entities/slime.gd` (feature-gruppiert, der Standard)
- **Sechs Prüfkategorien**: mirroring, naming, stale names, near-duplicates, backups, orphan companions.
- **Rich-Terminalausgabe** mit Fallback auf reines ANSI.
- **Geteiltes `-h` / `--help`**: kurzes Memo für erfahrene Benutzer, vollständige Dokumentation mit Beispielen zur Erkundung.
- **CI-freundlich**: Exit-Codes ungleich null, `--no-color`, `--no-rich`, JSON-Ausgabe.
- **Mehrere Ausgabeformate**: Text (Rich-Tabellen), JSON, Markdown.
- **Layout-bewusste Vorschläge**: Jede Warnung kommt mit einem konkreten Vorschlag zum Verschieben.
- **Anpassbare Namensprüfung**: Akzeptiert standardmäßig `-` als Trenner (häufig in Asset-Packs und Schriftfamilien); `--no-dashes` erzwingt striktes snake_case; `--suggested-no-ext` entfernt die Dateiendung aus der `Suggested`-Spalte, passend zum F2-Umbenennen in Godot.
- **Antonym-bewusster Near-Duplicate-Filter**: UI-Toggle-Paare wie `checked:unchecked` oder `up:down` via `--accept-pair` deklarieren, um False Positives zu unterdrücken, die der Ähnlichkeitswert allein nicht von einem Tippfehler unterscheiden kann.

## Installation

Direkt von GitHub installieren:

```bash
# Neueste Version
pip install git+https://github.com/olivierpons/godot-audit.git

# Auf ein bestimmtes Release festlegen
pip install git+https://github.com/olivierpons/godot-audit.git@v1.2.0
```

Dies zieht `cli-toolkit[rich]` automatisch aus seinem GitHub-Repository.

Benötigt Python 3.14 oder neuer.

## Schnellstart

```bash
# Aktuelles Verzeichnis prüfen (standardmäßig colocated-Layout)
godot-audit

# Ein bestimmtes Godot-Projekt prüfen
godot-audit ~/godotprojects/my_game

# Stattdessen das split-Layout verwenden
godot-audit ~/godotprojects/my_game --layout split

# Zusammenfassung unten für lange Berichte
godot-audit . --summary-position bottom

# Strikter CI-Modus: Build auch bei INFO-Problemen fehlschlagen lassen
godot-audit . --strict --no-color --no-rich --quiet

# In JSON exportieren zur weiteren Verarbeitung
godot-audit . --format json --output audit.json

# Markdown-Bericht für einen GitHub-PR-Kommentar
godot-audit . --format markdown > audit.md

# Ein Near-Duplicate-Falschpositiv eines UI-Toggles stummschalten
godot-audit . --accept-pair checked:unchecked

# Mehrere akzeptierte Paare in einem einzigen Argument
godot-audit . --accept-pair "(checked:unchecked)(up:down)(open:closed)"

# Striktes snake_case (Bindestriche ablehnen) und Endungen aus 'Suggested' entfernen
godot-audit . --no-dashes --suggested-no-ext
```

## Optionen

Jede Option hat eine Kurz- und eine Langform. `-h` druckt ein kompaktes Memo; `--help` druckt die vollständige Dokumentation mit Beispielen.

| Kurz | Lang | Beschreibung |
| --- | --- | --- |
| | `PATH` | Pfad zum Godot-Projektstamm (Standard: aktuelles Verzeichnis) |
| `-y` | `--layout` | `split` oder `colocated` (Standard: `colocated`) |
| `-f` | `--format` | `text`, `json` oder `markdown` (Standard: `text`) |
| `-o` | `--output` | In Datei statt stdout schreiben |
| `-c` | `--category` | Nur diese Kategorie melden (wiederholbar) |
| `-s` | `--severity` | Mindestschweregrad: `INFO`, `WARN`, `ERROR` (Standard: `INFO`) |
| `-t` | `--threshold` | Ähnlichkeitsschwelle für Near-Duplicate-Erkennung (Standard: `0.88`) |
| `-i` | `--ignore-dir` | Verzeichnis zur Ignore-Liste hinzufügen (wiederholbar) |
| `-k` | `--no-dashes` | `-` als Trenner in Stems ablehnen (Standard: akzeptiert) |
| `-x` | `--suggested-no-ext` | Dateiendung aus der `Suggested`-Spalte der Naming-Prüfung entfernen |
| `-A` | `--accept-pair` | Zwei Wörter als semantisch verschieden deklarieren (`checked:unchecked`); wiederholbar; akzeptiert `/` oder `()` zum Bündeln mehrerer Paare |
| `-p` | `--summary-position` | `top`, `bottom` oder `none` (Standard: `top`) |
| `-S` | `--strict` | Exit ungleich null auch bei INFO-Problemen |
| `-q` | `--quiet` | Zusammenfassung ausblenden (Alias für `-p none`) |
| `-R` | `--no-rich` | Nur-Text-Ausgabe erzwingen |
| `-n` | `--no-color` | ANSI-Farben deaktivieren |
| `-v` | `--verbosity` | 0=silent, 1=normal, 2=verbose, 3=debug |
| `-l` | `--list-categories` | Alle Prüfkategorien auflisten und beenden |
| `-L` | `--list-ignored-dirs` | Standardmäßig ignorierte Verzeichnisse auflisten und beenden |
| `-V` | `--version` | Version drucken und beenden |
| `-h` | | Kurzes Hilfe-Memo |
| | `--help` | Vollständige Hilfe mit Beispielen |

## Prüfkategorien

| Kategorie | Was sie erkennt |
| --- | --- |
| `mirroring` | Layout-abhängig. `split`: Skripte im `scripts/`-Stamm, während die Szene in `scenes/<subdir>/` liegt. `colocated`: Skripte, deren passende Szene in einem anderen Verzeichnis existiert. |
| `naming` | Dateinamen, die nicht snake_case sind (Leerzeichen, Bindestriche, Großbuchstaben, Sonderzeichen). Schlägt eine snake_case-Alternative vor. Schweregrad: INFO. |
| `stale_name` | Dateien, die auf `_old`, `_bak`, `_backup`, `_copy`, `_tmp`, `_temp`, `_new`, `_todelete` oder `_deprecated` enden. Zu promoten oder zu löschen. |
| `near_duplicate` | Paare von Dateien mit nahezu identischen Stämmen im selben Verzeichnis (fängt Tippfehler wie `skeleton` vs `skeletton`). Nummerierte Varianten (`v1`/`v2`, `01`/`02`, `Bird Call 1` / `Bird Call 3`) werden automatisch übersprungen. |
| `backup` | Editor-Backups: `*.bak`, `*.bak.*`, `*.orig`, Namen, die auf `~` enden. |
| `orphan_companion` | `.uid`- oder `.import`-Dateien, deren Quelldatei (`foo.gd`, `bar.mp3`) fehlt. Kann sicher gelöscht werden. |

## Exit-Codes

| Code | Bedeutung |
| --- | --- |
| `0` | Keine Probleme auf oder über dem aktuellen Schweregradfilter |
| `1` | Mindestens ein `WARN` oder `ERROR` gemeldet (oder irgendein `INFO`, wenn `--strict` gesetzt ist) |
| `2` | Ungültige Eingabe: `PATH` existiert nicht oder ist kein Godot-Projekt |

## Layout-Konventionen

### Split-Layout (Godots Standard-dokumentiert)

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

Szenen und Skripte leben in separaten Top-Level-Verzeichnissen, die sich gegenseitig spiegeln. Prüfen mit:

```bash
godot-audit . --layout split
```

### Colocated-Layout (Standard, empfohlen)

```
res://
├── features/
│   ├── entities/
│   │   ├── slime.tscn
│   │   └── slime.gd
│   └── levels/
│       ├── level_01.tscn
│       └── level_01.gd
├── autoload/         # Singletons, keine .tscn
├── components/       # wiederverwendbare Logik, keine .tscn
└── addons/
```

Szene und angehängtes Skript leben nebeneinander. Skripte unter `autoload/`, `components/` und `addons/` sind von der Kolokationsprüfung ausgenommen, da sie legitimerweise nur Skript sind. Prüfen mit:

```bash
godot-audit .
```

## Dateien sicher verschieben

Wenn ein Problem vorschlägt, ein Skript oder eine Szene zu verschieben, **verwenden Sie immer Godots FileSystem-Panel** (Drag & Drop im Editor), niemals `mv` auf der Kommandozeile. Godot schreibt jede `.tscn`-Referenz beim Verschieben um; das OS-`mv` tut das nicht, und Ihre Szenen zeigen am Ende auf fehlende Skripte.

## Umgebungsvariablen

| Variable | Wirkung |
| --- | --- |
| `NO_COLOR` | Wenn gesetzt, werden alle ANSI-Farben und das Rich-Styling deaktiviert. Siehe [no-color.org](https://no-color.org/). |

## Entwicklung

```bash
git clone https://github.com/olivierpons/godot-audit.git
cd godot-audit
pip install -e .
pip install pytest pytest-cov ruff mypy

# Tests
pytest

# Lint + Formatierung
ruff check .
ruff format .

# Gegen ein echtes Godot-Projekt ausführen
python -m godot_audit.cli ~/my_godot_project
```

## Lizenz

MIT — siehe [LICENSE](LICENSE).
