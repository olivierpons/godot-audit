"""Tests for the stem normalization helper used by near-duplicate detection."""

from __future__ import annotations

import pytest

from godot_audit.cli import (
    _has_totally_different_word,
)
from godot_audit.cli import (
    _normalize_stem_for_variant_check as normalize,
)


@pytest.mark.parametrize(
    ("a", "b"),
    [
        # Music library variants
        ("Calm_Collection_V1_3min_4s_Loop", "Calm_Collection_V2_3min_5s_Loop"),
        ("Calm_Collection_V1_3min_4s_Loop", "Calm_Collection_V3_3min_4s_Loop"),
        ("Calm_Collection_V1_3min_4s_Loop", "Calm_Collection_V4_3min_5s_Loop"),
        # Numbered sound effects
        ("Bird Call 1", "Bird Call 3"),
        ("Bird Call 1", "Bird Call 42"),
        # Bubble synth series (1 vs 12)
        ("Bubble_Synth_1", "Bubble_Synth_12"),
        # Level files
        ("level_01", "level_02"),
        # Character battle cries
        ("Hero_Alex_Battle_Cry_1", "Hero_Alex_Battle_Cry_6"),
        # Zombie hurt variants (zero-padded)
        ("ZombieWoman001_Hurt_A_001", "ZombieWoman001_Hurt_A_010"),
    ],
)
def test_numbered_variants_normalize_to_same_value(a: str, b: str) -> None:
    """Stems that differ only by digits must collapse to the same value."""
    assert normalize(a) == normalize(b)


@pytest.mark.parametrize(
    ("a", "b"),
    [
        # Real typo on letters
        ("skeleton", "skeletton"),
        # Different word at the same position
        (
            "Fluttering_Breeze_Full_Track_with_Guitar_1min_20",
            "Fluttering_Breeze_Full_Track_with_Synth_1min_20",
        ),
        # Missing letter, not a digit change
        ("slime", "slim"),
        # One has a digit suffix, the other doesn't
        ("player", "player1"),
    ],
)
def test_non_variant_pairs_stay_different(a: str, b: str) -> None:
    """Typos and word-level differences must not be treated as variants."""
    assert normalize(a) != normalize(b)


def test_identical_stems_normalize_identically() -> None:
    """Sanity check: same string in, same normalized string out."""
    assert normalize("foo") == normalize("foo")


def test_normalization_is_case_insensitive() -> None:
    """V1 and v2 must collapse together despite the case difference."""
    assert normalize("Track_V1") == normalize("track_v2")


# ---- _has_totally_different_word --------------------------------------


@pytest.mark.parametrize(
    ("a", "b"),
    [
        # Clean word swap at a fixed position — the motivating case.
        (
            "fluttering_breeze_full_track_with_guitar_1min_20",
            "fluttering_breeze_full_track_with_synth_1min_20",
        ),
        # Instrument vs effect swap.
        ("ambient_piano_loop", "ambient_drums_loop"),
        # Unrelated words of similar length.
        ("red_box_01", "blue_box_01"),
    ],
)
def test_totally_different_word_excludes_unrelated_assets(a: str, b: str) -> None:
    """Pairs swapping one fully distinct alphabetic token are flagged."""
    assert _has_totally_different_word(a, b) is True


@pytest.mark.parametrize(
    ("a", "b"),
    [
        # Real typo — shared prefix/suffix, one extra letter.
        ("skeleton", "skeletton"),
        # Boolean companion assets share a strong core stem.
        ("checkbox_checked", "checkbox_unchecked"),
        # Single-character typo in the middle.
        ("player_idle", "player_iddle"),
        # Case-only difference on otherwise identical tokens.
        ("Main_Menu", "main_menu"),
        # Exactly identical stems.
        ("foo_bar_baz", "foo_bar_baz"),
    ],
)
def test_totally_different_word_keeps_similar_stems(a: str, b: str) -> None:
    """Pairs that are typos or near-siblings must stay flag-eligible."""
    assert _has_totally_different_word(a, b) is False


def test_totally_different_word_skips_pure_numeric_token_diffs() -> None:
    """Digit-only token changes are handled upstream and must not count here."""
    assert _has_totally_different_word("track_01_loop", "track_02_loop") is False


def test_totally_different_word_bails_on_length_mismatch() -> None:
    """Different token counts mean the filter yields to the caller's decision."""
    assert _has_totally_different_word("foo_bar", "foo_bar_baz") is False
