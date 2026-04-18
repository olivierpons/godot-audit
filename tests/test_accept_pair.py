"""Unit tests for the ``--accept-pair`` parser and its runtime effect."""

from __future__ import annotations

import argparse

import pytest

from godot_audit.cli import (
    _has_totally_different_word,
    _normalize_accepted_pairs,
    _parse_accept_pair_spec,
)

# ── _parse_accept_pair_spec: accepted syntaxes ───────────────────


def test_single_pair_syntax() -> None:
    """A bare ``word:word`` string parses to a single pair."""
    assert _parse_accept_pair_spec("checked:unchecked") == (("checked", "unchecked"),)


def test_slash_separated_list() -> None:
    """Slashes split an argument into multiple pairs."""
    parsed = _parse_accept_pair_spec("checked:unchecked/up:down")
    assert parsed == (("checked", "unchecked"), ("up", "down"))


def test_paren_delimited_list() -> None:
    """``(a:b)(c:d)`` normalises to the same two pairs."""
    parsed = _parse_accept_pair_spec("(checked:unchecked)(up:down)")
    assert parsed == (("checked", "unchecked"), ("up", "down"))


def test_parens_with_slash_list() -> None:
    """``(a:b)/(c:d)`` is also accepted and parses identically."""
    parsed = _parse_accept_pair_spec("(checked:unchecked)/(up:down)")
    assert parsed == (("checked", "unchecked"), ("up", "down"))


def test_single_pair_in_parens() -> None:
    """A lone ``(a:b)`` parses to a single pair."""
    assert _parse_accept_pair_spec("(checked:unchecked)") == (("checked", "unchecked"),)


# ── _parse_accept_pair_spec: normalisation ───────────────────────


def test_pairs_are_lowercased() -> None:
    """Parsed tokens are lowercased for case-insensitive comparison."""
    assert _parse_accept_pair_spec("Checked:UnChecked") == (("checked", "unchecked"),)


def test_whitespace_around_tokens_is_stripped() -> None:
    """Leading and trailing whitespace inside a chunk is ignored."""
    parsed = _parse_accept_pair_spec("  checked : unchecked  ")
    assert parsed == (("checked", "unchecked"),)


def test_empty_chunks_are_skipped() -> None:
    """Trailing slashes or empty paren groups do not produce empty pairs."""
    assert _parse_accept_pair_spec("checked:unchecked/") == (("checked", "unchecked"),)
    assert _parse_accept_pair_spec("/checked:unchecked") == (("checked", "unchecked"),)
    assert _parse_accept_pair_spec("()checked:unchecked") == (("checked", "unchecked"),)


def test_empty_input_returns_empty_tuple() -> None:
    """An empty (or whitespace-only) argument yields no pairs."""
    assert _parse_accept_pair_spec("") == ()
    assert _parse_accept_pair_spec("   ") == ()
    assert _parse_accept_pair_spec("()") == ()


# ── _parse_accept_pair_spec: error paths ─────────────────────────


def test_missing_colon_is_rejected() -> None:
    """A chunk without a colon is a user error."""
    with pytest.raises(argparse.ArgumentTypeError, match=r"expected 'word:word'"):
        _parse_accept_pair_spec("checkedunchecked")


def test_multiple_colons_is_rejected() -> None:
    """A chunk with two or more colons is a user error."""
    with pytest.raises(argparse.ArgumentTypeError, match=r"expected 'word:word'"):
        _parse_accept_pair_spec("a:b:c")


def test_empty_left_side_is_rejected() -> None:
    """An empty token on the left raises."""
    with pytest.raises(argparse.ArgumentTypeError, match=r"non-empty"):
        _parse_accept_pair_spec(":unchecked")


def test_empty_right_side_is_rejected() -> None:
    """An empty token on the right raises."""
    with pytest.raises(argparse.ArgumentTypeError, match=r"non-empty"):
        _parse_accept_pair_spec("checked:")


def test_error_reports_the_offending_chunk() -> None:
    """Only the bad chunk in a list is named in the error message."""
    with pytest.raises(argparse.ArgumentTypeError, match=r"bad"):
        _parse_accept_pair_spec("a:b/bad/c:d")


# ── _normalize_accepted_pairs ────────────────────────────────────


def test_normalize_accepted_pairs_lowercases() -> None:
    """Programmatic input is lowercased just like parsed input."""
    assert _normalize_accepted_pairs([("Checked", "Unchecked")]) == (
        ("checked", "unchecked"),
    )


def test_normalize_accepted_pairs_rejects_wrong_arity() -> None:
    """A triple is not a pair and must be rejected."""
    with pytest.raises(ValueError, match=r"exactly two"):
        _normalize_accepted_pairs([("a", "b", "c")])  # type: ignore[list-item]


def test_normalize_accepted_pairs_rejects_empty_side() -> None:
    """An empty token on either side is invalid."""
    with pytest.raises(ValueError, match=r"empty side"):
        _normalize_accepted_pairs([("checked", "")])


# ── Runtime effect: aligned-token short-circuit ──────────────────


def test_has_totally_different_word_without_accepted_pair_flags_checked_unchecked() -> (
    None
):
    """Baseline: 'checked'/'unchecked' ratio is above 0.5, so NOT flagged distinct."""
    assert _has_totally_different_word("checkbox_checked", "checkbox_unchecked") is (
        False
    )


def test_accepted_pair_makes_checked_unchecked_distinct() -> None:
    """With ('checked','unchecked') accepted, the aligned pair is distinct."""
    out: bool = _has_totally_different_word(
        "checkbox_checked",
        "checkbox_unchecked",
        accepted_pairs=(("checked", "unchecked"),),
    )
    assert out is True


def test_accepted_pair_is_order_insensitive() -> None:
    """Reversing the declared order still matches the aligned pair."""
    out: bool = _has_totally_different_word(
        "checkbox_checked",
        "checkbox_unchecked",
        accepted_pairs=(("unchecked", "checked"),),
    )
    assert out is True


def test_accepted_pair_does_not_shadow_genuine_typos() -> None:
    """Typos that do not match the accepted set still go through the ratio test."""
    # skeleton/skeletton: ratio ~0.94, NOT in accepted set, NOT numbered variants.
    # With unrelated accepted pair, decision must be unchanged → ratio-based False.
    out: bool = _has_totally_different_word(
        "skeleton",
        "skeletton",
        accepted_pairs=(("checked", "unchecked"),),
    )
    assert out is False


def test_accepted_pair_does_not_apply_when_token_counts_differ() -> None:
    """Structural divergence (different token counts) still wins over accept-pair."""
    out: bool = _has_totally_different_word(
        "foo_checked",
        "foo_bar_unchecked",
        accepted_pairs=(("checked", "unchecked"),),
    )
    assert out is False
