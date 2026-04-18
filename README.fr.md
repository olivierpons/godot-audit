# godot-audit

**Langues** :
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

Auditez la structure d'un projet Godot par rapport à vos conventions. Lecture seule : ne modifie jamais aucun fichier.

`godot-audit` vérifie que vos fichiers `.tscn` et `.gd` sont organisés de manière cohérente (split ou colocated), que les noms de fichiers d'assets sont en snake_case, qu'aucune version obsolète `_old`/`_bak` ne traîne, et qu'aucun fichier compagnon `.uid` / `.import` n'est orphelin. Les noms de fichiers quasi-identiques (typos comme `skeleton` vs `skeletton`) sont signalés tandis que les variantes numérotées (`v1`, `v2`, ...) sont correctement reconnues et ignorées.

## Fonctionnalités

- **Deux layouts de projet supportés** :
  - `split` — `scenes/entities/slime.tscn` + `scripts/entities/slime.gd` (convention documentée par défaut de Godot)
  - `colocated` — `features/entities/slime.tscn` + `features/entities/slime.gd` (groupé par feature, c'est le défaut)
- **Six catégories de vérifications** : mirroring, naming, stale names, near-duplicates, backups, orphan companions.
- **Sortie terminal Rich** avec fallback en ANSI brut.
- **Split `-h` / `--help`** : mémo court pour les utilisateurs expérimentés, documentation complète avec exemples pour la découverte.
- **CI-friendly** : exit codes non-zéro, `--no-color`, `--no-rich`, sortie JSON.
- **Plusieurs formats de sortie** : texte (tables Rich), JSON, Markdown.
- **Suggestions adaptées au layout** : chaque avertissement vient avec une suggestion de déplacement concrète.

## Installation

Installation directe depuis GitHub :

```bash
# Dernière version
pip install git+https://github.com/olivierpons/godot-audit.git

# Fixer à une release spécifique
pip install git+https://github.com/olivierpons/godot-audit.git@v1.0.0
```

Cela tire automatiquement `cli-toolkit[rich]` depuis son dépôt GitHub.

Nécessite Python 3.14 ou supérieur.

## Démarrage rapide

```bash
# Auditer le répertoire courant (layout colocated par défaut)
godot-audit

# Auditer un projet Godot spécifique
godot-audit ~/godotprojects/my_game

# Utiliser le layout split à la place
godot-audit ~/godotprojects/my_game --layout split

# Résumé en bas pour les longs rapports
godot-audit . --summary-position bottom

# Mode CI strict : fait échouer le build même sur les issues INFO
godot-audit . --strict --no-color --no-rich --quiet

# Exporter en JSON pour traitement ultérieur
godot-audit . --format json --output audit.json

# Rapport Markdown pour un commentaire de PR GitHub
godot-audit . --format markdown > audit.md
```

## Options

Chaque option a une forme courte et une forme longue. `-h` imprime un mémo compact ; `--help` imprime la documentation complète avec exemples.

| Court | Long | Description |
| --- | --- | --- |
| | `PATH` | Chemin vers la racine du projet Godot (défaut : répertoire courant) |
| `-y` | `--layout` | `split` ou `colocated` (défaut : `colocated`) |
| `-f` | `--format` | `text`, `json`, ou `markdown` (défaut : `text`) |
| `-o` | `--output` | Écrire dans un fichier au lieu de stdout |
| `-c` | `--category` | Ne rapporter que cette catégorie (répétable) |
| `-s` | `--severity` | Sévérité minimale : `INFO`, `WARN`, `ERROR` (défaut : `INFO`) |
| `-t` | `--threshold` | Seuil de similarité pour la détection de quasi-doublons (défaut : `0.88`) |
| `-i` | `--ignore-dir` | Ajouter un répertoire à la liste d'ignore (répétable) |
| `-p` | `--summary-position` | `top`, `bottom`, ou `none` (défaut : `top`) |
| `-S` | `--strict` | Exit non-zéro même sur les issues INFO |
| `-q` | `--quiet` | Cacher le panel de résumé (alias de `-p none`) |
| `-R` | `--no-rich` | Forcer la sortie en texte brut |
| `-n` | `--no-color` | Désactiver les couleurs ANSI |
| `-v` | `--verbosity` | 0=silent, 1=normal, 2=verbose, 3=debug |
| `-l` | `--list-categories` | Lister toutes les catégories de vérifications et quitter |
| `-L` | `--list-ignored-dirs` | Lister les répertoires ignorés par défaut et quitter |
| `-V` | `--version` | Imprimer la version et quitter |
| `-h` | | Mémo d'aide court |
| | `--help` | Aide complète avec exemples |

## Catégories de vérifications

| Catégorie | Ce qu'elle détecte |
| --- | --- |
| `mirroring` | Dépend du layout. `split` : scripts à la racine de `scripts/` alors que la scène est dans `scenes/<subdir>/`. `colocated` : scripts dont la scène correspondante existe dans un répertoire différent. |
| `naming` | Noms de fichiers qui ne sont pas snake_case (espaces, tirets, majuscules, caractères spéciaux). Suggère une alternative snake_case. Sévérité : INFO. |
| `stale_name` | Fichiers se terminant par `_old`, `_bak`, `_backup`, `_copy`, `_tmp`, `_temp`, `_new`, `_todelete`, ou `_deprecated`. À promouvoir ou supprimer. |
| `near_duplicate` | Paires de fichiers avec des racines quasi-identiques dans le même répertoire (attrape les typos comme `skeleton` vs `skeletton`). Les variantes numérotées (`v1`/`v2`, `01`/`02`, `Bird Call 1` / `Bird Call 3`) sont automatiquement ignorées. |
| `backup` | Backups d'éditeur : `*.bak`, `*.bak.*`, `*.orig`, noms se terminant par `~`. |
| `orphan_companion` | Fichiers `.uid` ou `.import` dont le fichier source (`foo.gd`, `bar.mp3`) est manquant. Peuvent être supprimés sans risque. |

## Exit codes

| Code | Signification |
| --- | --- |
| `0` | Aucune issue au-dessus du filtre de sévérité courant |
| `1` | Au moins un `WARN` ou `ERROR` rapporté (ou n'importe quel `INFO` si `--strict` est défini) |
| `2` | Input invalide : `PATH` n'existe pas ou n'est pas un projet Godot |

## Conventions de layout

### Layout split (documenté par défaut par Godot)

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

Scènes et scripts vivent dans des répertoires de premier niveau séparés qui se reflètent mutuellement. Audit avec :

```bash
godot-audit . --layout split
```

### Layout colocated (défaut, recommandé)

```
res://
├── features/
│   ├── entities/
│   │   ├── slime.tscn
│   │   └── slime.gd
│   └── levels/
│       ├── level_01.tscn
│       └── level_01.gd
├── autoload/         # singletons, pas de .tscn
├── components/       # logique réutilisable, pas de .tscn
└── addons/
```

La scène et son script attaché vivent côte à côte. Les scripts sous `autoload/`, `components/`, et `addons/` sont exemptés de la vérification de colocation puisqu'ils sont légitimement uniquement du code. Audit avec :

```bash
godot-audit .
```

## Déplacer les fichiers en sécurité

Quand une issue suggère de déplacer un script ou une scène, **utilisez toujours le panneau FileSystem de Godot** (drag & drop dans l'éditeur), jamais `mv` en ligne de commande. Godot réécrit toutes les références `.tscn` lors du déplacement ; `mv` de l'OS ne le fait pas, et vos scènes finissent par pointer vers des scripts manquants.

## Variables d'environnement

| Variable | Effet |
| --- | --- |
| `NO_COLOR` | Quand définie, désactive toutes les couleurs ANSI et le style Rich. Voir [no-color.org](https://no-color.org/). |

## Développement

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

# Lancer contre un vrai projet Godot
python -m godot_audit.cli ~/my_godot_project
```

## Licence

MIT — voir [LICENSE](LICENSE).
