# godot-audit

**Languages**:
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

Audit a Godot project layout against your conventions. Read-only: never modifies any file.

`godot-audit` checks that your `.tscn` and `.gd` files are organized consistently (split or colocated), that asset filenames are snake_case, that no stale `_old`/`_bak` versions are lying around, and that no `.uid` / `.import` companion files are orphaned. Near-duplicate filenames (typos like `skeleton` vs `skeletton`) are flagged while numbered variants (`v1`, `v2`, ...) are correctly recognized and ignored.

## Features

- **Two project layouts supported**:
  - `split` — `scenes/entities/slime.tscn` + `scripts/entities/slime.gd` (Godot's default-documented convention)
  - `colocated` — `features/entities/slime.tscn` + `features/entities/slime.gd` (feature-grouped, the default)
- **Six check categories**: mirroring, naming, stale names, near-duplicates, backups, orphan companions.
- **Rich terminal output** with fallback to plain ANSI.
- **Split `-h` / `--help`**: short memo for experienced users, full documentation with examples for discovery.
- **CI-friendly**: non-zero exit codes, `--no-color`, `--no-rich`, JSON output.
- **Multiple output formats**: text (Rich tables), JSON, Markdown.
- **Layout-aware suggestions**: each warning comes with a concrete move suggestion.
- **Tunable naming check**: accept `-` as a separator by default (common in asset packs and font families), with `--no-dashes` for strict snake_case; strip the extension from the `Suggested` column with `--suggested-no-ext` to match Godot's F2 rename flow.
- **Antonym-aware near-duplicate filter**: declare UI toggle pairs like `checked:unchecked` or `up:down` with `--accept-pair` to silence false positives that the similarity ratio alone cannot distinguish from a typo.

## Installation

Install directly from GitHub:

```bash
# Latest version
pip install git+https://github.com/olivierpons/godot-audit.git

# Pin to a specific release
pip install git+https://github.com/olivierpons/godot-audit.git@v1.2.0
```

This automatically pulls in `cli-toolkit[rich]` from its GitHub repository.

Requires Python 3.14 or newer.

## Quick start

```bash
# Audit the current directory (colocated layout by default)
godot-audit

# Audit a specific Godot project
godot-audit ~/godotprojects/my_game

# Use the split layout instead
godot-audit ~/godotprojects/my_game --layout split

# Summary at the bottom for long reports
godot-audit . --summary-position bottom

# Strict CI mode: fail the build even on INFO issues
godot-audit . --strict --no-color --no-rich --quiet

# Export to JSON for further processing
godot-audit . --format json --output audit.json

# Markdown report for a GitHub PR comment
godot-audit . --format markdown > audit.md

# Silence a UI-toggle near-duplicate false positive
godot-audit . --accept-pair checked:unchecked

# Multiple accepted pairs in a single argument
godot-audit . --accept-pair "(checked:unchecked)(up:down)(open:closed)"

# Strict snake_case (reject dashes) and strip extensions in 'Suggested'
godot-audit . --no-dashes --suggested-no-ext
```

## Options

Every option has a short and a long form. `-h` prints a compact memo; `--help` prints full documentation with examples.

| Short | Long | Description |
| --- | --- | --- |
| | `PATH` | Path to the Godot project root (default: current directory) |
| `-y` | `--layout` | `split` or `colocated` (default: `colocated`) |
| `-f` | `--format` | `text`, `json`, or `markdown` (default: `text`) |
| `-o` | `--output` | Write to file instead of stdout |
| `-c` | `--category` | Only report this category (repeatable) |
| `-s` | `--severity` | Minimum severity: `INFO`, `WARN`, `ERROR` (default: `INFO`) |
| `-t` | `--threshold` | Similarity threshold for near-duplicate detection (default: `0.88`) |
| `-i` | `--ignore-dir` | Add directory to ignore list (repeatable) |
| `-k` | `--no-dashes` | Reject `-` as a separator in stems (default: accepted) |
| `-x` | `--suggested-no-ext` | Strip the file extension from the naming `Suggested` column |
| `-A` | `--accept-pair` | Declare that two words are semantically distinct (`checked:unchecked`); repeatable; accepts `/` or `()` to pack multiple pairs |
| `-p` | `--summary-position` | `top`, `bottom`, or `none` (default: `top`) |
| `-S` | `--strict` | Non-zero exit even on INFO issues |
| `-q` | `--quiet` | Hide summary panel (alias for `-p none`) |
| `-R` | `--no-rich` | Force plain-text output |
| `-n` | `--no-color` | Disable ANSI colors |
| `-v` | `--verbosity` | 0=silent, 1=normal, 2=verbose, 3=debug |
| `-l` | `--list-categories` | List all check categories and exit |
| `-L` | `--list-ignored-dirs` | List default ignored directories and exit |
| `-V` | `--version` | Print version and exit |
| `-h` | | Short help memo |
| | `--help` | Full help with examples |

## Check categories

| Category | What it detects |
| --- | --- |
| `mirroring` | Layout-dependent. `split`: scripts at `scripts/` root while the scene is in `scenes/<subdir>/`. `colocated`: scripts whose matching scene exists in a different directory. |
| `naming` | Filenames that are not snake_case (spaces, dashes, capitals, special characters). Suggests a snake_case alternative. Severity: INFO. |
| `stale_name` | Files ending with `_old`, `_bak`, `_backup`, `_copy`, `_tmp`, `_temp`, `_new`, `_todelete`, or `_deprecated`. Promote or delete. |
| `near_duplicate` | Pairs of files with near-identical stems in the same directory (catches typos like `skeleton` vs `skeletton`). Numbered variants (`v1`/`v2`, `01`/`02`, `Bird Call 1` / `Bird Call 3`) are automatically skipped. |
| `backup` | Editor backups: `*.bak`, `*.bak.*`, `*.orig`, names ending with `~`. |
| `orphan_companion` | `.uid` or `.import` files whose source file (`foo.gd`, `bar.mp3`) is missing. Safe to delete. |

## Exit codes

| Code | Meaning |
| --- | --- |
| `0` | No issues at or above the current severity filter |
| `1` | At least one `WARN` or `ERROR` was reported (or any `INFO` when `--strict` is set) |
| `2` | Invalid input: `PATH` does not exist or is not a Godot project |

## Layout conventions

### Split layout (Godot default-documented)

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

Scenes and scripts live in separate top-level directories that mirror each other. Audit with:

```bash
godot-audit . --layout split
```

### Colocated layout (default, recommended)

```
res://
├── features/
│   ├── entities/
│   │   ├── slime.tscn
│   │   └── slime.gd
│   └── levels/
│       ├── level_01.tscn
│       └── level_01.gd
├── autoload/         # singletons, no .tscn
├── components/       # reusable logic, no .tscn
└── addons/
```

Scene and attached script live side by side. Scripts under `autoload/`, `components/`, and `addons/` are exempt from the colocation check since they are legitimately script-only. Audit with:

```bash
godot-audit .
```

## Moving files safely

When an issue suggests moving a script or scene, **always use Godot's FileSystem panel** (drag & drop inside the editor), never `mv` on the command line. Godot rewrites every `.tscn` reference on move; the OS `mv` does not, and your scenes end up pointing to missing scripts.

## Environment variables

| Variable | Effect |
| --- | --- |
| `NO_COLOR` | When set, disables all ANSI colors and Rich styling. See [no-color.org](https://no-color.org/). |

## Development

```bash
git clone https://github.com/olivierpons/godot-audit.git
cd godot-audit
pip install -e .
pip install pytest pytest-cov ruff mypy

# Tests
pytest

# Lint + format
ruff check .
ruff format .

# Run against a real Godot project
python -m godot_audit.cli ~/my_godot_project
```

## License

MIT — see [LICENSE](LICENSE).
