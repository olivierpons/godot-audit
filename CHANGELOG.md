# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.2.0] - 2026-04-18

### Added

- New CLI option `-A` / `--accept-pair SPEC`: declare that two words
  are semantically distinct so that filenames aligned on them are
  not flagged as near-duplicates. Typical use is UI toggle sprite
  pairs such as `checkbox_checked.png` vs `checkbox_unchecked.png`,
  whose edit distance is small but whose meaning is opposite — the
  existing similarity-ratio filter cannot tell them apart from a
  genuine typo (`skeleton` / `skeletton`). `SPEC` accepts four
  equivalent syntaxes so pairs can be passed one per flag or packed
  into a single string: `checked:unchecked` (single pair),
  `checked:unchecked/up:down` (slash-separated list),
  `(checked:unchecked)(up:down)` (paren-delimited), or
  `(checked:unchecked)/(up:down)` (parens + slash). The flag is
  repeatable and every invocation appends to the accumulated list.
  Comparison against filename tokens is case-insensitive and
  order-insensitive. Equivalent kwarg on `ProjectAuditor`:
  `accepted_pairs: Iterable[tuple[str, str]] = ()`. Opt-in: with no
  flag, behaviour is identical to v1.1.0.

### Changed

- The snake_case suggestion generator (`_to_snake_case`) now honours
  the `allow_dashes` setting, not just the acceptance pattern. When
  `allow_dashes=True` (the default, equivalent to not passing
  `-k` / `--no-dashes`), any run of separator characters in the
  source stem is classified before being collapsed: a run made only
  of underscores stays `_`, a run made only of dashes stays `-`,
  and a mixed run (both `_` and `-`, e.g. `_-_`, `__-__`, `-_-_-`)
  collapses to a single `-`. Spaces, dots, and other punctuation are
  normalised to `_` before this classification, so whitespace around
  a dash (`foo - bar`) is also treated as a mixed run. With
  `--no-dashes`, every separator run still collapses to `_` as
  before. This is a **behaviour change**: suggestions for files
  containing `_-_` or similar mixed runs will differ from v1.1.0.
  For example, `Theme_-_Air_Pirates_Return01.mp3` now suggests
  `theme-air_pirates_return01.mp3` in the default mode, where
  v1.1.0 suggested `theme_air_pirates_return01.mp3`. No public API
  signature changed: `ProjectAuditor(allow_dashes=...)` keeps the
  same surface; only the shape of the `Suggested` column is
  different. Callers that use `-k` / `--no-dashes` are unaffected.

## [1.1.0] - 2026-04-18

### Added

- Near-duplicate detection now applies a final word-level filter: after
  the numbered-variant check, if two stems share the same tokenisation
  structure but swap one fully distinct word at an aligned position
  (e.g. `fluttering_breeze_..._with_guitar_1min_20` vs
  `..._with_synth_1min_20`), the pair is treated as semantically
  unrelated assets and is no longer flagged. Implemented via
  `_has_totally_different_word` using `difflib.SequenceMatcher.ratio`
  with a 0.5 cutoff.
- `Issue` dataclass gains three optional structured fields used by the
  renderers: `suggested` (naming and mirroring target), `paired_with`
  (near-duplicate sibling), and `detail` (stale-name suffix, missing
  companion source). The JSON output emits these fields when set.
- New CLI option `-k` / `--no-dashes`: enforce strict snake_case in
  the naming check. By default, stems with a single `-` between
  alphanumeric runs are accepted (e.g. `pixel_operator8-bold`), since
  this is common in font families and third-party asset packs and
  Godot imports them without issue. Pass `--no-dashes` to reject
  dashes and require underscores only. Equivalent kwarg on
  `ProjectAuditor`: `allow_dashes: bool = True`.
- New CLI option `-x` / `--suggested-no-ext`: drop the file extension
  from the naming table's `Suggested` column. Rationale: Godot's
  FileSystem dock and the native rename widget of common desktop
  file managers (GNOME Files / Nautilus, macOS Finder, Windows
  Explorer) select only the stem when renaming with F2 or a
  double-click on the name. Pasting a full `foo.ttf` suggestion over
  that selection produces `foo.ttf.ttf`; a bare `foo` can be pasted
  directly. Off by default. Equivalent kwarg on `AuditRenderer`:
  `strip_extension_in_suggested: bool = False`.

### Changed

- Text and Markdown renderers no longer display the wide `Message`
  column with a repeated long sentence per row. Each category table
  now shows `Sev | Path` plus a single category-specific column:
  - `mirroring` → `Suggested move`
  - `naming` → `Suggested`
  - `stale_name` → `Suffix`
  - `near_duplicate` → `Near-identical to`
  - `orphan_companion` → `Missing source`
  - `backup` → (no third column)
- Category table titles now carry the action verdict that used to be
  repeated in every row's message: `backup` and `orphan_companion`
  advertise "safe to delete"; `stale_name` advertises "promote or
  delete"; `near_duplicate` advertises "confirm which one to keep".
- The human-readable `message` is still populated on every `Issue` and
  preserved in the JSON output, so callers that rely on it keep
  working.

## [1.0.1] - 2026-04-18

### Fixed

- CLI help text, usage line, examples, and `argparse` `prog` now display
  `godot-audit` (the actual command name declared in `project.scripts`)
  instead of the legacy internal name `audit_godot_project`. Affects the
  output of `godot-audit --version`, `-h`, and `--help`.

## [1.0.0] - 2026-04-18

### Added

- Initial public release.
- Audit six categories of project-layout issues in a Godot project:
  `mirroring`, `naming`, `stale_name`, `near_duplicate`, `backup`,
  `orphan_companion`.
- Two supported project layouts driven by `--layout`:
  - `split`: `scenes/` and `scripts/` as parallel trees.
  - `colocated` (default): scene and attached script in the same
    directory.
- Scripts under `autoload/`, `components/`, and `addons/` are exempt
  from the colocation check.
- Rich terminal output with tables and panels. Transparent fallback
  to plain ANSI when Rich is unavailable or when `--no-rich` is set.
- Three output formats: `text`, `json`, `markdown`.
- Summary panel placement controlled by `--summary-position`:
  `top` (default), `bottom`, or `none`.
- Numbered variants (e.g. `v1`/`v2`, `Bird Call 1`/`Bird Call 3`)
  are automatically excluded from near-duplicate detection by
  normalizing digit runs to a placeholder before comparing stems.
- Split `-h` / `--help`: compact memo for experienced users, full
  documentation with examples for discovery.
- CI-friendly exit codes:
  - `0` — no issues at or above the current severity filter.
  - `1` — one or more `WARN`/`ERROR` reported (or any `INFO` with
    `--strict`).
  - `2` — invalid project path.

[Unreleased]: https://github.com/olivierpons/godot-audit/compare/v1.2.0...HEAD
[1.2.0]: https://github.com/olivierpons/godot-audit/releases/tag/v1.2.0
[1.1.0]: https://github.com/olivierpons/godot-audit/releases/tag/v1.1.0
[1.0.1]: https://github.com/olivierpons/godot-audit/releases/tag/v1.0.1
[1.0.0]: https://github.com/olivierpons/godot-audit/releases/tag/v1.0.0

