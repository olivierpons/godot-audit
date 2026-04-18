"""Integration tests for ProjectAuditor against real directory fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest

from godot_audit.cli import (
    Category,
    Layout,
    ProjectAuditor,
    Severity,
)


@pytest.fixture
def godot_project(tmp_path: Path) -> Path:
    """Create a minimal fake Godot project with no issues."""
    (tmp_path / "project.godot").touch()
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scenes").mkdir()
    return tmp_path


def test_auditor_rejects_non_godot_directory(tmp_path: Path) -> None:
    """Auditor must refuse to run on a directory without project.godot."""
    with pytest.raises(ValueError, match=r"No project\.godot"):
        ProjectAuditor(tmp_path)


def test_auditor_rejects_missing_directory(tmp_path: Path) -> None:
    """Auditor must report a missing root with a clear FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        ProjectAuditor(tmp_path / "does-not-exist")


def test_clean_project_produces_no_issues(godot_project: Path) -> None:
    """A minimal valid project should yield zero findings."""
    report = ProjectAuditor(godot_project).run()
    assert report.issues == []


def test_split_layout_detects_script_at_root(godot_project: Path) -> None:
    """Under SPLIT layout, a script at scripts/ root with a scene in a subdir must be flagged."""
    (godot_project / "scenes" / "entities").mkdir()
    (godot_project / "scenes" / "entities" / "slime.tscn").touch()
    (godot_project / "scripts" / "slime.gd").touch()

    report = ProjectAuditor(godot_project, layout=Layout.SPLIT).run()
    mirroring: list = [i for i in report.issues if i.category is Category.MIRRORING]
    assert len(mirroring) == 1
    assert "scripts/entities/slime.gd" in mirroring[0].message


def test_colocated_layout_detects_split_scene_and_script(
    godot_project: Path,
) -> None:
    """Under COLOCATED layout, a scene and its script in different directories must be flagged."""
    (godot_project / "features" / "entities").mkdir(parents=True)
    (godot_project / "features" / "entities" / "slime.tscn").touch()
    (godot_project / "scripts" / "slime.gd").touch()

    report = ProjectAuditor(godot_project, layout=Layout.COLOCATED).run()
    mirroring: list = [i for i in report.issues if i.category is Category.MIRRORING]
    assert len(mirroring) == 1
    assert "features/entities/slime.gd" in mirroring[0].message


def test_colocated_layout_accepts_colocated_files(godot_project: Path) -> None:
    """Scene and script in the same directory must not be flagged."""
    (godot_project / "features" / "entities").mkdir(parents=True)
    (godot_project / "features" / "entities" / "slime.tscn").touch()
    (godot_project / "features" / "entities" / "slime.gd").touch()

    report = ProjectAuditor(godot_project, layout=Layout.COLOCATED).run()
    mirroring: list = [i for i in report.issues if i.category is Category.MIRRORING]
    assert mirroring == []


def test_colocated_layout_ignores_autoload_and_components(
    godot_project: Path,
) -> None:
    """Scripts under autoload/ and components/ must never be flagged by mirroring."""
    (godot_project / "autoload").mkdir()
    (godot_project / "autoload" / "global.gd").touch()
    (godot_project / "components" / "movement").mkdir(parents=True)
    (godot_project / "components" / "movement" / "chase.gd").touch()
    (godot_project / "features" / "entities").mkdir(parents=True)
    (godot_project / "features" / "entities" / "global.tscn").touch()

    report = ProjectAuditor(godot_project, layout=Layout.COLOCATED).run()
    mirroring: list = [i for i in report.issues if i.category is Category.MIRRORING]
    assert mirroring == []


def test_orphan_companion_is_detected(godot_project: Path) -> None:
    """A .uid without a matching source file is flagged."""
    (godot_project / "scripts" / "clock.gd.uid").touch()

    report = ProjectAuditor(godot_project).run()
    orphans: list = [
        i for i in report.issues if i.category is Category.ORPHAN_COMPANION
    ]
    assert len(orphans) == 1
    assert "clock.gd" in orphans[0].message


def test_stale_suffix_is_detected(godot_project: Path) -> None:
    """A filename ending with _old is flagged."""
    (godot_project / "scenes" / "slime_old.tscn").touch()

    report = ProjectAuditor(godot_project).run()
    stale: list = [i for i in report.issues if i.category is Category.STALE_NAME]
    assert len(stale) == 1


def test_backup_files_are_detected(godot_project: Path) -> None:
    """Editor backup files like .bak.tscn are flagged."""
    (godot_project / "scenes" / "level.bak.tscn").touch()

    report = ProjectAuditor(godot_project).run()
    backups: list = [i for i in report.issues if i.category is Category.BACKUP]
    assert len(backups) == 1


def test_near_duplicate_detects_typo(godot_project: Path) -> None:
    """skeleton / skeletton in the same directory must be flagged."""
    scenes: Path = godot_project / "scenes" / "entities"
    scenes.mkdir(parents=True)
    (scenes / "skeleton.tscn").touch()
    (scenes / "skeletton.tscn").touch()

    report = ProjectAuditor(godot_project).run()
    dupes: list = [i for i in report.issues if i.category is Category.NEAR_DUPLICATE]
    assert len(dupes) == 1


def test_near_duplicate_skips_distinct_word_swap(godot_project: Path) -> None:
    """Filenames that swap one fully distinct word must not be flagged.

    Regression test for the word-level filter: two audio takes whose
    stems only differ by one unrelated instrument name (guitar/synth)
    describe different assets and must not be reported as a typo.
    """
    music: Path = godot_project / "assets" / "music"
    music.mkdir(parents=True)
    (music / "fluttering_breeze_full_track_with_guitar_1min_20.mp3").touch()
    (music / "fluttering_breeze_full_track_with_synth_1min_20.mp3").touch()

    report = ProjectAuditor(godot_project).run()
    dupes: list = [i for i in report.issues if i.category is Category.NEAR_DUPLICATE]
    assert dupes == []


def test_near_duplicate_keeps_checkbox_pair(godot_project: Path) -> None:
    """checkbox_checked / checkbox_unchecked must still be flagged.

    The filter only bails out on *fully distinct* words; ``checked``
    and ``unchecked`` share most of their characters and should still
    surface as a potential near-identical pair.
    """
    theme: Path = godot_project / "assets" / "theme"
    theme.mkdir(parents=True)
    (theme / "checkbox_checked.png").touch()
    (theme / "checkbox_unchecked.png").touch()

    report = ProjectAuditor(godot_project).run()
    dupes: list = [i for i in report.issues if i.category is Category.NEAR_DUPLICATE]
    assert len(dupes) == 1


def test_near_duplicate_skips_numbered_variants(godot_project: Path) -> None:
    """Numbered variants must not be flagged as duplicates.

    Regression test: Calm_Collection_V1, V2, V3, V4 must produce zero
    near-duplicate findings.
    """
    music: Path = godot_project / "assets" / "music"
    music.mkdir(parents=True)
    for version in (1, 2, 3, 4):
        (music / f"Calm_Collection_V{version}_3min_4s_Loop.mp3").touch()

    report = ProjectAuditor(godot_project).run()
    dupes: list = [i for i in report.issues if i.category is Category.NEAR_DUPLICATE]
    assert dupes == []


def test_naming_detects_non_snake_case(godot_project: Path) -> None:
    """Filenames with spaces or capitals must be flagged at INFO severity."""
    sounds: Path = godot_project / "assets" / "sounds"
    sounds.mkdir(parents=True)
    (sounds / "Bird Call 1.mp3").touch()

    report = ProjectAuditor(godot_project).run()
    naming: list = [i for i in report.issues if i.category is Category.NAMING]
    assert len(naming) == 1
    assert naming[0].severity is Severity.INFO


def test_report_counts_by_severity(godot_project: Path) -> None:
    """The report helper must tally issues by severity correctly."""
    sounds: Path = godot_project / "assets" / "sounds"
    sounds.mkdir(parents=True)
    (sounds / "Bird Call 1.mp3").touch()  # INFO naming
    (godot_project / "scenes" / "slime_old.tscn").touch()  # WARN stale

    report = ProjectAuditor(godot_project).run()
    counts = report.counts_by_severity()
    assert counts.get("INFO", 0) == 1
    assert counts.get("WARN", 0) >= 1


def test_extra_ignored_dirs_are_excluded(godot_project: Path) -> None:
    """Directories passed via extra_ignored_dirs must not be scanned."""
    build: Path = godot_project / "my_build"
    build.mkdir()
    (build / "leftover_old.tscn").touch()  # would normally be flagged

    report = ProjectAuditor(godot_project, extra_ignored_dirs={"my_build"}).run()
    stale: list = [i for i in report.issues if i.category is Category.STALE_NAME]
    assert stale == []


def test_naming_issue_exposes_snake_case_suggestion(godot_project: Path) -> None:
    """NAMING issues must carry the snake_case suggestion in `suggested`."""
    sounds: Path = godot_project / "assets" / "sounds"
    sounds.mkdir(parents=True)
    (sounds / "Bird Call 1.mp3").touch()

    report = ProjectAuditor(godot_project).run()
    naming: list = [i for i in report.issues if i.category is Category.NAMING]
    assert len(naming) == 1
    assert naming[0].suggested == "bird_call_1.mp3"


def test_allow_dashes_accepts_kebab_snake_stems(godot_project: Path) -> None:
    """With allow_dashes=True (default), 'pixel_operator8-bold' must pass."""
    fonts: Path = godot_project / "assets" / "fonts"
    fonts.mkdir(parents=True)
    (fonts / "pixel_operator8-bold.ttf").touch()

    report = ProjectAuditor(godot_project).run()
    naming: list = [i for i in report.issues if i.category is Category.NAMING]
    assert naming == []


def test_allow_dashes_false_flags_kebab_snake_stems(godot_project: Path) -> None:
    """With allow_dashes=False, 'pixel_operator8-bold' must be flagged."""
    fonts: Path = godot_project / "assets" / "fonts"
    fonts.mkdir(parents=True)
    (fonts / "pixel_operator8-bold.ttf").touch()

    report = ProjectAuditor(godot_project, allow_dashes=False).run()
    naming: list = [i for i in report.issues if i.category is Category.NAMING]
    assert len(naming) == 1
    # strict-mode suggestion replaces the dash with an underscore
    assert naming[0].suggested == "pixel_operator8_bold.ttf"


def test_stale_name_issue_exposes_suffix(godot_project: Path) -> None:
    """STALE_NAME issues must carry the offending suffix in `detail`."""
    (godot_project / "scenes" / "slime_old.tscn").touch()

    report = ProjectAuditor(godot_project).run()
    stale: list = [i for i in report.issues if i.category is Category.STALE_NAME]
    assert len(stale) == 1
    assert stale[0].detail == "_old"


def test_orphan_companion_issue_exposes_missing_source(godot_project: Path) -> None:
    """ORPHAN_COMPANION issues must carry the missing source name in `detail`."""
    (godot_project / "scripts" / "clock.gd.uid").touch()

    report = ProjectAuditor(godot_project).run()
    orphans: list = [
        i for i in report.issues if i.category is Category.ORPHAN_COMPANION
    ]
    assert len(orphans) == 1
    assert orphans[0].detail == "clock.gd"


def test_near_duplicate_issue_exposes_paired_path(godot_project: Path) -> None:
    """NEAR_DUPLICATE issues must carry the sibling path in `paired_with`."""
    scenes: Path = godot_project / "scenes" / "entities"
    scenes.mkdir(parents=True)
    (scenes / "skeleton.tscn").touch()
    (scenes / "skeletton.tscn").touch()

    report = ProjectAuditor(godot_project).run()
    dupes: list = [i for i in report.issues if i.category is Category.NEAR_DUPLICATE]
    assert len(dupes) == 1
    # pair is sorted, so path points at one stem and paired_with at the other
    assert dupes[0].paired_with is not None
    assert dupes[0].paired_with != dupes[0].path
    assert {dupes[0].path, dupes[0].paired_with} == {
        "scenes/entities/skeleton.tscn",
        "scenes/entities/skeletton.tscn",
    }


def test_mirroring_split_issue_exposes_suggested_path(godot_project: Path) -> None:
    """MIRRORING issues must carry the proposed move target in `suggested`."""
    (godot_project / "scenes" / "entities").mkdir()
    (godot_project / "scenes" / "entities" / "slime.tscn").touch()
    (godot_project / "scripts" / "slime.gd").touch()

    report = ProjectAuditor(godot_project, layout=Layout.SPLIT).run()
    mirroring: list = [i for i in report.issues if i.category is Category.MIRRORING]
    assert len(mirroring) == 1
    assert mirroring[0].suggested == "scripts/entities/slime.gd"


def test_markdown_strips_extension_in_naming_suggested(godot_project: Path) -> None:
    """``strip_extension_in_suggested=True`` must drop '.ext' in the naming table."""
    from cli_toolkit import OutputHandler

    from godot_audit.cli import AuditRenderer

    fonts: Path = godot_project / "assets" / "fonts"
    fonts.mkdir(parents=True)
    (fonts / "Bad Font.ttf").touch()

    report = ProjectAuditor(godot_project).run()
    out = OutputHandler(use_rich=False)

    plain: str = AuditRenderer(out).render_markdown(report)
    assert "bad_font.ttf" in plain  # default behaviour: extension kept

    stripped: str = AuditRenderer(
        out, strip_extension_in_suggested=True
    ).render_markdown(report)
    # The suggested cell must now read 'bad_font' without the extension.
    assert "| bad_font |" in stripped
    assert "bad_font.ttf" not in stripped


def test_markdown_strip_extension_does_not_affect_mirroring(
    godot_project: Path,
) -> None:
    """Mirroring target paths must keep their extension even when stripping."""
    from cli_toolkit import OutputHandler

    from godot_audit.cli import AuditRenderer

    (godot_project / "scenes" / "entities").mkdir()
    (godot_project / "scenes" / "entities" / "slime.tscn").touch()
    (godot_project / "scripts" / "slime.gd").touch()

    report = ProjectAuditor(godot_project, layout=Layout.SPLIT).run()
    out = OutputHandler(use_rich=False)

    rendered: str = AuditRenderer(
        out, strip_extension_in_suggested=True
    ).render_markdown(report)
    assert "scripts/entities/slime.gd" in rendered
