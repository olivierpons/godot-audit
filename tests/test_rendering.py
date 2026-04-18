"""Tests for :class:`AuditRenderer`, :func:`_filter_report`, and dispatch."""

from __future__ import annotations

import json
from pathlib import Path

from cli_toolkit import OutputHandler

from godot_audit.cli import (
    AuditRenderer,
    AuditReport,
    Category,
    Issue,
    ProjectAuditor,
    Severity,
    SummaryPosition,
    _filter_report,
)

# ── Fixtures helpers ────────────────────────────────────────────


def _make_populated_report(tmp_path: Path) -> AuditReport:
    """Return an ``AuditReport`` covering every category and severity."""
    (tmp_path / "project.godot").touch()
    (tmp_path / "Bad Name.tscn").touch()  # naming (INFO)
    (tmp_path / "scenes" / "entities").mkdir(parents=True)
    (tmp_path / "scenes" / "entities" / "slime.tscn").touch()
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "slime.gd").touch()  # mirroring (WARN, split)
    sounds: Path = tmp_path / "assets" / "sounds"
    sounds.mkdir(parents=True)
    (sounds / "skeleton.tscn").touch()
    (sounds / "skeletton.tscn").touch()  # near_duplicate (WARN)
    (tmp_path / "level_old.tscn").touch()  # stale_name (WARN)
    (tmp_path / "theme.tscn.bak").touch()  # backup (WARN)
    (tmp_path / "scripts" / "gone.gd.uid").touch()  # orphan_companion (WARN)

    from godot_audit.cli import Layout

    return ProjectAuditor(tmp_path, layout=Layout.SPLIT).run()


# ── _filter_report ──────────────────────────────────────────────


def test_filter_report_drops_issues_below_minimum_severity(tmp_path: Path) -> None:
    """Issues below the requested severity are excluded from the output."""
    report: AuditReport = _make_populated_report(tmp_path)
    filtered: AuditReport = _filter_report(report, categories=None, min_severity="WARN")
    severities: set[str] = {i.severity.value for i in filtered.issues}
    assert "INFO" not in severities


def test_filter_report_drops_issues_outside_requested_categories(
    tmp_path: Path,
) -> None:
    """Only issues whose category is in the allow-list are kept."""
    report: AuditReport = _make_populated_report(tmp_path)
    filtered: AuditReport = _filter_report(
        report, categories=["naming"], min_severity="INFO"
    )
    categories: set[str] = {i.category.value for i in filtered.issues}
    assert categories == {"naming"}


# ── AuditRenderer.render_text: summary placement ────────────────


def test_render_text_with_top_summary(tmp_path: Path) -> None:
    """Default summary placement runs the summary renderer once."""
    report: AuditReport = _make_populated_report(tmp_path)
    out = OutputHandler(use_rich=False)
    renderer: AuditRenderer = AuditRenderer(out)
    renderer.render_text(report, summary_position=SummaryPosition.TOP)


def test_render_text_with_bottom_summary_on_populated_report(tmp_path: Path) -> None:
    """Bottom placement runs the summary renderer after the category tables."""
    report: AuditReport = _make_populated_report(tmp_path)
    out = OutputHandler(use_rich=False)
    renderer: AuditRenderer = AuditRenderer(out)
    renderer.render_text(report, summary_position=SummaryPosition.BOTTOM)


def test_render_text_with_bottom_summary_on_empty_report(tmp_path: Path) -> None:
    """Bottom placement on an empty report still emits the summary."""
    (tmp_path / "project.godot").touch()
    report: AuditReport = ProjectAuditor(tmp_path).run()
    out = OutputHandler(use_rich=False)
    renderer: AuditRenderer = AuditRenderer(out)
    renderer.render_text(report, summary_position=SummaryPosition.BOTTOM)


def test_render_text_with_rich_enabled(tmp_path: Path) -> None:
    """When Rich is available, the severity cell goes through Rich.Text."""
    report: AuditReport = _make_populated_report(tmp_path)
    out = OutputHandler(use_rich=True)
    renderer: AuditRenderer = AuditRenderer(out)
    renderer.render_text(report, summary_position=SummaryPosition.TOP)


# ── AuditRenderer.render_text: extra=None column (backup) ───────


def test_render_text_handles_backup_category_without_extra_column(
    tmp_path: Path,
) -> None:
    """Backup issues render with only Sev and Path (no extra column)."""
    (tmp_path / "project.godot").touch()
    (tmp_path / "theme.tscn.bak").touch()
    report: AuditReport = ProjectAuditor(tmp_path).run()
    out = OutputHandler(use_rich=False)
    AuditRenderer(out).render_text(report, summary_position=SummaryPosition.NONE)


# ── AuditRenderer.render_markdown: empty + backup branches ──────


def test_render_markdown_on_empty_report(tmp_path: Path) -> None:
    """An issue-less report renders the 'no issues found' placeholder line."""
    (tmp_path / "project.godot").touch()
    report: AuditReport = ProjectAuditor(tmp_path).run()
    out = OutputHandler(use_rich=False)
    rendered: str = AuditRenderer(out).render_markdown(report)
    assert "_No issues found._" in rendered


def test_render_markdown_backup_table_has_two_columns(tmp_path: Path) -> None:
    """Markdown backup table has only Severity and Path, no extra column."""
    (tmp_path / "project.godot").touch()
    (tmp_path / "theme.tscn.bak").touch()
    report: AuditReport = ProjectAuditor(tmp_path).run()
    out = OutputHandler(use_rich=False)
    rendered: str = AuditRenderer(out).render_markdown(report)
    assert "| Severity | Path |" in rendered
    # No suggestion column for backup:
    assert "| Severity | Path | Suggested |" not in rendered


# ── AuditRenderer.render_json: optional-field branches ──────────


def test_render_json_preserves_backup_issue_without_optional_fields() -> None:
    """A backup issue has no structured extras; JSON output must skip them."""
    report: AuditReport = AuditReport(project_root=Path("/tmp/fake"))
    report.add(
        Issue(
            severity=Severity.WARNING,
            category=Category.BACKUP,
            path="theme.tscn.bak",
            message="Backup-style file (editor leftover). Safe to delete.",
        )
    )
    payload: dict = json.loads(AuditRenderer.render_json(report))
    entry: dict = payload["issues"][0]
    assert "suggested" not in entry
    assert "paired_with" not in entry
    assert "detail" not in entry


def test_render_json_includes_all_optional_fields_when_set() -> None:
    """An issue carrying every optional field exposes all of them in JSON."""
    report: AuditReport = AuditReport(project_root=Path("/tmp/fake"))
    report.add(
        Issue(
            severity=Severity.WARNING,
            category=Category.NEAR_DUPLICATE,
            path="a/skeleton.tscn",
            message="near-duplicate",
            suggested="a/skeleton.tscn",
            paired_with="a/skeletton.tscn",
            detail="ratio=0.94",
        )
    )
    payload: dict = json.loads(AuditRenderer.render_json(report))
    entry: dict = payload["issues"][0]
    assert entry["suggested"] == "a/skeleton.tscn"
    assert entry["paired_with"] == "a/skeletton.tscn"
    assert entry["detail"] == "ratio=0.94"


# ── _format_extra_value: empty-raw branch ───────────────────────


def test_format_extra_value_returns_empty_string_for_empty_raw() -> None:
    """An empty ``raw`` short-circuits independently of the category."""
    out = OutputHandler(use_rich=False)
    renderer: AuditRenderer = AuditRenderer(out, strip_extension_in_suggested=True)
    assert renderer._format_extra_value(Category.NAMING, "") == ""


def test_format_extra_value_keeps_extension_when_flag_is_off() -> None:
    """With the strip flag off, the raw value is returned unchanged."""
    out = OutputHandler(use_rich=False)
    renderer: AuditRenderer = AuditRenderer(out, strip_extension_in_suggested=False)
    assert renderer._format_extra_value(Category.NAMING, "foo.ttf") == "foo.ttf"


def test_format_extra_value_keeps_extension_for_non_naming_category() -> None:
    """Even with the strip flag on, non-NAMING categories keep their value."""
    out = OutputHandler(use_rich=False)
    renderer: AuditRenderer = AuditRenderer(out, strip_extension_in_suggested=True)
    assert (
        renderer._format_extra_value(Category.MIRRORING, "scripts/entities/slime.gd")
        == "scripts/entities/slime.gd"
    )
