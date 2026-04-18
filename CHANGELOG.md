# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

[Unreleased]: https://github.com/olivierpons/godot-audit/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/olivierpons/godot-audit/releases/tag/v1.1.0
[1.0.1]: https://github.com/olivierpons/godot-audit/releases/tag/v1.0.1
[1.0.0]: https://github.com/olivierpons/godot-audit/releases/tag/v1.0.0

