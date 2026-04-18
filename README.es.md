# godot-audit

**Idiomas**:
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

Audita la estructura de un proyecto Godot contra tus convenciones. Solo lectura: nunca modifica ningún archivo.

`godot-audit` comprueba que tus archivos `.tscn` y `.gd` estén organizados de forma coherente (split o colocated), que los nombres de archivos de assets sean snake_case, que no haya versiones obsoletas `_old`/`_bak` por ahí, y que ningún archivo acompañante `.uid` / `.import` esté huérfano. Los nombres de archivo casi idénticos (typos como `skeleton` vs `skeletton`) se marcan mientras que las variantes numeradas (`v1`, `v2`, ...) se reconocen correctamente y se ignoran.

## Características

- **Dos layouts de proyecto soportados**:
  - `split` — `scenes/entities/slime.tscn` + `scripts/entities/slime.gd` (convención documentada predeterminada de Godot)
  - `colocated` — `features/entities/slime.tscn` + `features/entities/slime.gd` (agrupado por feature, el predeterminado)
- **Seis categorías de comprobaciones**: mirroring, naming, stale names, near-duplicates, backups, orphan companions.
- **Salida de terminal Rich** con fallback a ANSI simple.
- **Separación `-h` / `--help`**: memo corto para usuarios experimentados, documentación completa con ejemplos para descubrimiento.
- **Compatible con CI**: códigos de salida no cero, `--no-color`, `--no-rich`, salida JSON.
- **Múltiples formatos de salida**: texto (tablas Rich), JSON, Markdown.
- **Sugerencias conscientes del layout**: cada advertencia viene con una sugerencia concreta de movimiento.
- **Comprobación de naming ajustable**: acepta `-` como separador por defecto (habitual en asset packs y familias de fuentes); `--no-dashes` impone snake_case estricto; `--suggested-no-ext` quita la extensión de la columna `Suggested` para encajar con el flujo de renombrado F2 de Godot.
- **Filtro near-duplicate consciente de antónimos**: declara pares de toggles de UI como `checked:unchecked` o `up:down` con `--accept-pair` para silenciar falsos positivos que el ratio de similitud por sí solo no puede distinguir de un typo.

## Instalación

Instalar directamente desde GitHub:

```bash
# Última versión
pip install git+https://github.com/olivierpons/godot-audit.git

# Fijar a una release específica
pip install git+https://github.com/olivierpons/godot-audit.git@v1.2.0
```

Esto extrae automáticamente `cli-toolkit[rich]` desde su repositorio GitHub.

Requiere Python 3.14 o superior.

## Inicio rápido

```bash
# Auditar el directorio actual (layout colocated por defecto)
godot-audit

# Auditar un proyecto Godot específico
godot-audit ~/godotprojects/my_game

# Usar el layout split en su lugar
godot-audit ~/godotprojects/my_game --layout split

# Resumen abajo para reportes largos
godot-audit . --summary-position bottom

# Modo CI estricto: falla la build incluso en issues INFO
godot-audit . --strict --no-color --no-rich --quiet

# Exportar a JSON para procesamiento adicional
godot-audit . --format json --output audit.json

# Reporte Markdown para un comentario de PR GitHub
godot-audit . --format markdown > audit.md

# Silenciar un falso positivo near-duplicate en un toggle de UI
godot-audit . --accept-pair checked:unchecked

# Varios pares aceptados en un solo argumento
godot-audit . --accept-pair "(checked:unchecked)(up:down)(open:closed)"

# snake_case estricto (rechaza guiones) y extensiones quitadas en 'Suggested'
godot-audit . --no-dashes --suggested-no-ext
```

## Opciones

Cada opción tiene una forma corta y una larga. `-h` imprime un memo compacto; `--help` imprime la documentación completa con ejemplos.

| Corto | Largo | Descripción |
| --- | --- | --- |
| | `PATH` | Ruta a la raíz del proyecto Godot (predeterminado: directorio actual) |
| `-y` | `--layout` | `split` o `colocated` (predeterminado: `colocated`) |
| `-f` | `--format` | `text`, `json` o `markdown` (predeterminado: `text`) |
| `-o` | `--output` | Escribir a archivo en lugar de stdout |
| `-c` | `--category` | Solo reportar esta categoría (repetible) |
| `-s` | `--severity` | Severidad mínima: `INFO`, `WARN`, `ERROR` (predeterminado: `INFO`) |
| `-t` | `--threshold` | Umbral de similitud para detección de casi-duplicados (predeterminado: `0.88`) |
| `-i` | `--ignore-dir` | Añadir directorio a la lista de ignore (repetible) |
| `-k` | `--no-dashes` | Rechazar `-` como separador en los stems (por defecto: aceptado) |
| `-x` | `--suggested-no-ext` | Quitar la extensión del archivo de la columna `Suggested` del check de naming |
| `-A` | `--accept-pair` | Declarar que dos palabras son semánticamente distintas (`checked:unchecked`); repetible; acepta `/` o `()` para empaquetar varias parejas |
| `-p` | `--summary-position` | `top`, `bottom` o `none` (predeterminado: `top`) |
| `-S` | `--strict` | Salida no cero incluso en issues INFO |
| `-q` | `--quiet` | Ocultar panel de resumen (alias de `-p none`) |
| `-R` | `--no-rich` | Forzar salida en texto plano |
| `-n` | `--no-color` | Deshabilitar colores ANSI |
| `-v` | `--verbosity` | 0=silent, 1=normal, 2=verbose, 3=debug |
| `-l` | `--list-categories` | Listar todas las categorías de comprobación y salir |
| `-L` | `--list-ignored-dirs` | Listar directorios ignorados por defecto y salir |
| `-V` | `--version` | Imprimir versión y salir |
| `-h` | | Memo corto de ayuda |
| | `--help` | Ayuda completa con ejemplos |

## Categorías de comprobaciones

| Categoría | Qué detecta |
| --- | --- |
| `mirroring` | Depende del layout. `split`: scripts en la raíz de `scripts/` mientras la escena está en `scenes/<subdir>/`. `colocated`: scripts cuya escena correspondiente existe en un directorio diferente. |
| `naming` | Nombres de archivo que no son snake_case (espacios, guiones, mayúsculas, caracteres especiales). Sugiere una alternativa snake_case. Severidad: INFO. |
| `stale_name` | Archivos que terminan en `_old`, `_bak`, `_backup`, `_copy`, `_tmp`, `_temp`, `_new`, `_todelete` o `_deprecated`. Promover o eliminar. |
| `near_duplicate` | Pares de archivos con raíces casi idénticas en el mismo directorio (captura typos como `skeleton` vs `skeletton`). Las variantes numeradas (`v1`/`v2`, `01`/`02`, `Bird Call 1` / `Bird Call 3`) se omiten automáticamente. |
| `backup` | Backups del editor: `*.bak`, `*.bak.*`, `*.orig`, nombres que terminan con `~`. |
| `orphan_companion` | Archivos `.uid` o `.import` cuyo archivo fuente (`foo.gd`, `bar.mp3`) falta. Seguro de eliminar. |

## Códigos de salida

| Código | Significado |
| --- | --- |
| `0` | Sin issues al o sobre el filtro de severidad actual |
| `1` | Al menos un `WARN` o `ERROR` fue reportado (o cualquier `INFO` cuando `--strict` está establecido) |
| `2` | Entrada inválida: `PATH` no existe o no es un proyecto Godot |

## Convenciones de layout

### Layout split (documentado por defecto por Godot)

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

Escenas y scripts viven en directorios de nivel superior separados que se reflejan entre sí. Auditar con:

```bash
godot-audit . --layout split
```

### Layout colocated (predeterminado, recomendado)

```
res://
├── features/
│   ├── entities/
│   │   ├── slime.tscn
│   │   └── slime.gd
│   └── levels/
│       ├── level_01.tscn
│       └── level_01.gd
├── autoload/         # singletons, sin .tscn
├── components/       # lógica reutilizable, sin .tscn
└── addons/
```

La escena y su script adjunto viven lado a lado. Los scripts bajo `autoload/`, `components/` y `addons/` están exentos de la comprobación de colocación ya que legítimamente son solo script. Auditar con:

```bash
godot-audit .
```

## Mover archivos de forma segura

Cuando una issue sugiere mover un script o escena, **usa siempre el panel FileSystem de Godot** (drag & drop dentro del editor), nunca `mv` en la línea de comandos. Godot reescribe cada referencia `.tscn` al mover; el `mv` del SO no lo hace, y tus escenas terminan apuntando a scripts faltantes.

## Variables de entorno

| Variable | Efecto |
| --- | --- |
| `NO_COLOR` | Cuando se establece, deshabilita todos los colores ANSI y el estilo Rich. Ver [no-color.org](https://no-color.org/). |

## Desarrollo

```bash
git clone https://github.com/olivierpons/godot-audit.git
cd godot-audit
pip install -e .
pip install pytest pytest-cov ruff mypy

# Tests
pytest

# Lint + formato
ruff check .
ruff format .

# Ejecutar contra un proyecto Godot real
python -m godot_audit.cli ~/my_godot_project
```

## Licencia

MIT — ver [LICENSE](LICENSE).
