"""Tests for the stem normalization helper used by near-duplicate detection."""

from __future__ import annotations

import pytest

from godot_audit.cli import _normalize_stem_for_variant_check as normalize


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
