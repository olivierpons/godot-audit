"""Unit tests for the :func:`_to_snake_case` helper."""

from __future__ import annotations

from godot_audit.cli import _to_snake_case

# ── Spec example from the v1.2.0 brief ───────────────────────────


def test_theme_dash_example_allow_dashes_true() -> None:
    """Mixed ``_-_`` run collapses to ``-`` when dashes are allowed."""
    assert (
        _to_snake_case("Theme_-_Air_Pirates_Return01", allow_dashes=True)
        == "theme-air_pirates_return01"
    )


def test_theme_dash_example_allow_dashes_false() -> None:
    """Mixed ``_-_`` run collapses to ``_`` when dashes are not allowed."""
    assert (
        _to_snake_case("Theme_-_Air_Pirates_Return01", allow_dashes=False)
        == "theme_air_pirates_return01"
    )


# ── Pure separator runs ──────────────────────────────────────────


def test_pure_underscore_run_stays_underscore_regardless_of_mode() -> None:
    """A run made only of underscores collapses to a single ``_``."""
    assert _to_snake_case("foo___bar", allow_dashes=True) == "foo_bar"
    assert _to_snake_case("foo___bar", allow_dashes=False) == "foo_bar"


def test_pure_dash_run_becomes_dash_when_allowed() -> None:
    """A run made only of dashes collapses to ``-`` when allowed."""
    assert _to_snake_case("foo---bar", allow_dashes=True) == "foo-bar"


def test_pure_dash_run_becomes_underscore_when_forbidden() -> None:
    """A run made only of dashes collapses to ``_`` when forbidden."""
    assert _to_snake_case("foo---bar", allow_dashes=False) == "foo_bar"


# ── Mixed separator runs ─────────────────────────────────────────


def test_long_mixed_run_allow_dashes_true() -> None:
    """Long mixed run ``__-__`` collapses to ``-`` when dashes allowed."""
    assert _to_snake_case("foo__-__bar", allow_dashes=True) == "foo-bar"


def test_long_mixed_run_allow_dashes_false() -> None:
    """Long mixed run ``__-__`` collapses to ``_`` when dashes forbidden."""
    assert _to_snake_case("foo__-__bar", allow_dashes=False) == "foo_bar"


def test_alternating_mixed_run_allow_dashes_true() -> None:
    """Alternating ``-_-_-`` run collapses to ``-`` when dashes allowed."""
    assert _to_snake_case("foo-_-_-bar", allow_dashes=True) == "foo-bar"


def test_alternating_mixed_run_allow_dashes_false() -> None:
    """Alternating ``-_-_-`` run collapses to ``_`` when dashes forbidden."""
    assert _to_snake_case("foo-_-_-bar", allow_dashes=False) == "foo_bar"


def test_short_mixed_run_dash_first() -> None:
    """``-_`` (dash then underscore) is still mixed."""
    assert _to_snake_case("foo-_bar", allow_dashes=True) == "foo-bar"
    assert _to_snake_case("foo-_bar", allow_dashes=False) == "foo_bar"


def test_short_mixed_run_underscore_first() -> None:
    """``_-`` (underscore then dash) is still mixed."""
    assert _to_snake_case("foo_-bar", allow_dashes=True) == "foo-bar"
    assert _to_snake_case("foo_-bar", allow_dashes=False) == "foo_bar"


# ── Whitespace and punctuation ───────────────────────────────────


def test_spaces_become_underscores() -> None:
    """Spaces are converted to ``_`` and collapse as underscores."""
    assert _to_snake_case("Bird Call 1", allow_dashes=True) == "bird_call_1"
    assert _to_snake_case("Bird Call 1", allow_dashes=False) == "bird_call_1"


def test_space_padded_dash_is_a_mixed_run() -> None:
    """``foo - bar`` normalises to ``foo_-_bar`` then collapses per mode."""
    assert _to_snake_case("foo - bar", allow_dashes=True) == "foo-bar"
    assert _to_snake_case("foo - bar", allow_dashes=False) == "foo_bar"


def test_punctuation_converts_to_underscore() -> None:
    """Dots, parens, and similar punctuation become ``_`` before collapse."""
    assert _to_snake_case("foo.bar", allow_dashes=True) == "foo_bar"
    assert _to_snake_case("foo.(bar)", allow_dashes=True) == "foo_bar"
    assert _to_snake_case("foo!bar", allow_dashes=False) == "foo_bar"


def test_punctuation_adjacent_to_dash_forms_mixed_run() -> None:
    """``foo.-bar`` normalises to ``foo_-bar``, a mixed run."""
    assert _to_snake_case("foo.-bar", allow_dashes=True) == "foo-bar"
    assert _to_snake_case("foo.-bar", allow_dashes=False) == "foo_bar"


# ── camelCase preservation ───────────────────────────────────────


def test_camel_case_splits_into_snake_case() -> None:
    """``BadName`` splits into ``bad_name`` regardless of mode."""
    assert _to_snake_case("BadName") == "bad_name"
    assert _to_snake_case("BadName", allow_dashes=True) == "bad_name"


def test_camel_case_with_dash_allow_dashes_true() -> None:
    """``fooBar-baz`` becomes ``foo_bar-baz`` when dashes allowed."""
    assert _to_snake_case("fooBar-baz", allow_dashes=True) == "foo_bar-baz"


def test_camel_case_with_dash_allow_dashes_false() -> None:
    """``fooBar-baz`` becomes ``foo_bar_baz`` when dashes forbidden."""
    assert _to_snake_case("fooBar-baz", allow_dashes=False) == "foo_bar_baz"


def test_camel_case_with_digits() -> None:
    """Camel split applies to ``[a-z0-9][A-Z]`` boundaries, including digits."""
    assert _to_snake_case("foo1Bar") == "foo1_bar"


# ── Edge cases ───────────────────────────────────────────────────


def test_empty_stem_returns_placeholder() -> None:
    """An empty input returns the ``unnamed`` fallback."""
    assert _to_snake_case("") == "unnamed"
    assert _to_snake_case("", allow_dashes=True) == "unnamed"


def test_only_underscores_returns_placeholder() -> None:
    """A stem made only of underscores strips to empty."""
    assert _to_snake_case("___", allow_dashes=True) == "unnamed"
    assert _to_snake_case("___", allow_dashes=False) == "unnamed"


def test_only_dashes_returns_placeholder() -> None:
    """A stem made only of dashes strips to empty in both modes."""
    assert _to_snake_case("---", allow_dashes=True) == "unnamed"
    assert _to_snake_case("---", allow_dashes=False) == "unnamed"


def test_only_mixed_separators_returns_placeholder() -> None:
    """A stem made only of mixed separators strips to empty."""
    assert _to_snake_case("-_-_-", allow_dashes=True) == "unnamed"
    assert _to_snake_case("-_-_-", allow_dashes=False) == "unnamed"


def test_only_whitespace_returns_placeholder() -> None:
    """Whitespace normalises to underscores, which then strip to empty."""
    assert _to_snake_case("   ", allow_dashes=True) == "unnamed"


def test_only_punctuation_returns_placeholder() -> None:
    """Pure punctuation normalises to underscores and strips to empty."""
    assert _to_snake_case("...", allow_dashes=True) == "unnamed"
    assert _to_snake_case("!!!", allow_dashes=False) == "unnamed"


def test_leading_and_trailing_separators_are_stripped() -> None:
    """Leading and trailing ``_`` or ``-`` are removed from the result."""
    assert _to_snake_case("_foo_", allow_dashes=True) == "foo"
    assert _to_snake_case("-foo-", allow_dashes=True) == "foo"
    assert _to_snake_case("-_foo_-", allow_dashes=True) == "foo"
    assert _to_snake_case("-foo-", allow_dashes=False) == "foo"


# ── Default kwarg behaviour ──────────────────────────────────────


def test_default_mode_is_strict_snake_case() -> None:
    """Calling without the kwarg never emits a dash."""
    result: str = _to_snake_case("Theme_-_Air_Pirates_Return01")
    assert "-" not in result
    assert result == "theme_air_pirates_return01"
