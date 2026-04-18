# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

[Unreleased]: https://github.com/olivierpons/godot-audit/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/olivierpons/godot-audit/releases/tag/v1.0.0
