"""Tests for the godot-audit CLI entry points."""

from __future__ import annotations

from pathlib import Path

import pytest

from godot_audit import __version__
from godot_audit.cli import (
    EXIT_INVALID_INPUT,
    EXIT_ISSUES_FOUND,
    EXIT_OK,
    _build_cli_parser,
    main,
)


def test_version_action_uses_package_version(capsys: pytest.CaptureFixture) -> None:
    """--version must print the version sourced from __init__.py."""
    parser = _build_cli_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["--version"])
    captured = capsys.readouterr()
    assert __version__ in captured.out


def test_list_categories_exits_cleanly(
    capsys: pytest.CaptureFixture,
) -> None:
    """--list-categories must print and return exit code 0."""
    code: int = main(["--list-categories"])
    captured = capsys.readouterr()
    assert code == EXIT_OK
    assert "mirroring" in captured.out
    assert "naming" in captured.out


def test_invalid_path_returns_exit_code_2(
    tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    """A missing path must return exit code 2, not 1."""
    code: int = main([str(tmp_path / "does_not_exist")])
    assert code == EXIT_INVALID_INPUT


def test_clean_project_returns_exit_code_zero(tmp_path: Path) -> None:
    """A clean project must return exit code 0."""
    (tmp_path / "project.godot").touch()
    code: int = main([str(tmp_path), "--quiet", "--no-rich"])
    assert code == EXIT_OK


def test_project_with_warnings_returns_exit_code_one(tmp_path: Path) -> None:
    """A project with WARN-level issues must return exit code 1."""
    (tmp_path / "project.godot").touch()
    (tmp_path / "level_old.tscn").touch()
    code: int = main([str(tmp_path), "--quiet", "--no-rich"])
    assert code == EXIT_ISSUES_FOUND


def test_strict_mode_treats_info_as_failure(tmp_path: Path) -> None:
    """--strict must make INFO-only findings return exit code 1."""
    (tmp_path / "project.godot").touch()
    (tmp_path / "Bad Name.tscn").touch()  # INFO: not snake_case
    code_default: int = main([str(tmp_path), "--quiet", "--no-rich", "-c", "naming"])
    code_strict: int = main(
        [str(tmp_path), "--quiet", "--no-rich", "-c", "naming", "--strict"]
    )
    assert code_default == EXIT_OK
    assert code_strict == EXIT_ISSUES_FOUND


def test_short_and_long_options_are_equivalent(tmp_path: Path) -> None:
    """-y and --layout must accept the same values and produce the same result."""
    (tmp_path / "project.godot").touch()
    short = main([str(tmp_path), "-y", "split", "--quiet", "--no-rich"])
    long_ = main([str(tmp_path), "--layout", "split", "--quiet", "--no-rich"])
    assert short == long_


def test_json_output_to_file(tmp_path: Path) -> None:
    """--format json --output must write a valid JSON file."""
    import json

    (tmp_path / "project.godot").touch()
    report_path: Path = tmp_path / "report.json"
    main(
        [
            str(tmp_path),
            "--format",
            "json",
            "--output",
            str(report_path),
            "--no-rich",
        ]
    )
    assert report_path.is_file()
    parsed: dict = json.loads(report_path.read_text())
    assert "issues" in parsed
    assert "files_scanned" in parsed


def test_accept_pair_flag_silences_checked_unchecked_near_duplicate(
    tmp_path: Path,
) -> None:
    """``--accept-pair checked:unchecked`` must clear the near-duplicate finding."""
    import json

    (tmp_path / "project.godot").touch()
    theme: Path = tmp_path / "assets" / "theme"
    theme.mkdir(parents=True)
    (theme / "checkbox_checked.png").touch()
    (theme / "checkbox_unchecked.png").touch()

    baseline_path: Path = tmp_path / "baseline.json"
    main(
        [
            str(tmp_path),
            "--format",
            "json",
            "--output",
            str(baseline_path),
            "--no-rich",
        ]
    )
    baseline: dict = json.loads(baseline_path.read_text())
    baseline_near: list = [
        issue for issue in baseline["issues"] if issue["category"] == "near_duplicate"
    ]
    assert len(baseline_near) == 1

    with_pair_path: Path = tmp_path / "with_pair.json"
    main(
        [
            str(tmp_path),
            "--format",
            "json",
            "--output",
            str(with_pair_path),
            "--no-rich",
            "--accept-pair",
            "checked:unchecked",
        ]
    )
    with_pair: dict = json.loads(with_pair_path.read_text())
    with_pair_near: list = [
        issue for issue in with_pair["issues"] if issue["category"] == "near_duplicate"
    ]
    assert with_pair_near == []


def test_accept_pair_short_flag_is_equivalent(tmp_path: Path) -> None:
    """``-A`` must be equivalent to ``--accept-pair`` and combine multiple pairs."""
    import json

    (tmp_path / "project.godot").touch()
    theme: Path = tmp_path / "assets" / "theme"
    theme.mkdir(parents=True)
    (theme / "checkbox_checked.png").touch()
    (theme / "checkbox_unchecked.png").touch()

    out_path: Path = tmp_path / "out.json"
    main(
        [
            str(tmp_path),
            "--format",
            "json",
            "--output",
            str(out_path),
            "--no-rich",
            "-A",
            "(checked:unchecked)(up:down)",
        ]
    )
    data: dict = json.loads(out_path.read_text())
    near: list = [
        issue for issue in data["issues"] if issue["category"] == "near_duplicate"
    ]
    assert near == []


def test_list_ignored_dirs_exits_cleanly(
    capsys: pytest.CaptureFixture,
) -> None:
    """``--list-ignored-dirs`` prints the default ignore list and returns 0."""
    code: int = main(["--list-ignored-dirs"])
    captured = capsys.readouterr()
    assert code == EXIT_OK
    assert ".git" in captured.out
    assert ".godot" in captured.out


def test_text_format_to_file_writes_markdown(tmp_path: Path) -> None:
    """Text format written to a file falls back to the Markdown view."""
    (tmp_path / "project.godot").touch()
    (tmp_path / "Bad Name.tscn").touch()
    report_path: Path = tmp_path / "report.txt"
    code: int = main(
        [
            str(tmp_path),
            "--format",
            "text",
            "--output",
            str(report_path),
            "--no-rich",
        ]
    )
    assert code == EXIT_OK
    body: str = report_path.read_text()
    # Markdown-style header must appear in the file.
    assert body.startswith("# Godot project audit")


def test_json_format_to_stdout(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    """JSON format without --output writes a parseable payload to stdout."""
    import json

    (tmp_path / "project.godot").touch()
    main([str(tmp_path), "--format", "json", "--no-rich", "--quiet"])
    captured = capsys.readouterr()
    payload: dict = json.loads(captured.out)
    assert "issues" in payload
    assert "files_scanned" in payload


def test_markdown_format_to_stdout(
    tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    """Markdown format without --output writes the rendered markdown to stdout."""
    (tmp_path / "project.godot").touch()
    main([str(tmp_path), "--format", "markdown", "--no-rich", "--quiet"])
    captured = capsys.readouterr()
    assert captured.out.startswith("# Godot project audit")


def test_markdown_format_to_file(tmp_path: Path) -> None:
    """Markdown format with --output writes the rendered markdown to the file."""
    (tmp_path / "project.godot").touch()
    report_path: Path = tmp_path / "report.md"
    code: int = main(
        [
            str(tmp_path),
            "--format",
            "markdown",
            "--output",
            str(report_path),
            "--no-rich",
        ]
    )
    assert code == EXIT_OK
    body: str = report_path.read_text()
    assert body.startswith("# Godot project audit")


def test_text_output_to_stdout_with_top_summary(
    tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    """Text format without --quiet exercises the TOP summary branch."""
    (tmp_path / "project.godot").touch()
    (tmp_path / "Bad Name.tscn").touch()
    code: int = main([str(tmp_path), "--no-rich", "-p", "top"])
    captured = capsys.readouterr()
    assert code == EXIT_OK  # INFO-only finding, not strict
    assert "Audit summary" in captured.out or "Files scanned" in captured.out
