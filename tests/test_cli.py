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
