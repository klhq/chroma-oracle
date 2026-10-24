"""Test the unknown_solver shared module."""

import json
import os
import tempfile

from chroma_oracle.lib.strategy import find_all_solutions
from chroma_oracle.lib.unknown_solver import (
    MAX_MYSTERY_CANDIDATES,
    TooManyCandidatesError,
    calculate_needed_colors,
    count_unique_permutations,
    generate_candidate_grids,
    load_puzzle_with_unknowns,
    unique_permutations,
)


def test_load_puzzle_with_unknowns():
    """Test loading a puzzle with unknown positions."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump([["?", "?", "RED", "RED"], ["BLUE", "BLUE", "BLUE", "BLUE"], []], f)
        temp_path = f.name

    try:
        data = load_puzzle_with_unknowns(temp_path)
        assert len(data.unknown_indices) == 2
        assert (0, 0) in data.unknown_indices
        assert (0, 1) in data.unknown_indices
        assert len(data.all_items) == 6
    finally:
        os.unlink(temp_path)


def test_calculate_needed_colors():
    """Test calculation of needed colors."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump([["?", "?", "RED", "RED"], ["BLUE", "BLUE", "BLUE", "BLUE"], []], f)
        temp_path = f.name

    try:
        data = load_puzzle_with_unknowns(temp_path)
        needed = calculate_needed_colors(data)
        assert needed is not None
        assert len(needed) == 2
        assert needed.count("RED") == 2
    finally:
        os.unlink(temp_path)


def test_generate_candidate_grids():
    """Test candidate grid generation."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump([["?", "?", "RED", "RED"], ["BLUE", "BLUE", "BLUE", "BLUE"], []], f)
        temp_path = f.name

    try:
        data = load_puzzle_with_unknowns(temp_path)
        needed = calculate_needed_colors(data)
        assert needed is not None
        grids = generate_candidate_grids(data, needed)

        assert len(grids) > 0
        for grid in grids:
            for row in grid:
                for item in row:
                    assert item != "?"
    finally:
        os.unlink(temp_path)


def test_count_unique_permutations():
    """Test counting unique permutations of multisets."""
    assert count_unique_permutations([]) == 1
    assert count_unique_permutations(["RED"]) == 1
    assert count_unique_permutations(["RED", "RED", "RED"]) == 1
    assert count_unique_permutations(["RED", "BLUE", "GREEN"]) == 6
    assert count_unique_permutations(["RED", "RED", "BLUE", "BLUE"]) == 6
    assert count_unique_permutations(["A", "A", "B", "B", "C", "C"]) == 90


def test_unique_permutations():
    """Test generating deduplicated permutations with branch pruning."""
    import itertools

    assert unique_permutations([]) == [()]
    assert unique_permutations(["RED"]) == [("RED",)]
    assert unique_permutations(["RED", "RED", "RED"]) == [("RED", "RED", "RED")]

    # Compare with itertools on a multiset
    items = ["RED", "RED", "BLUE", "GREEN"]
    expected = sorted(set(itertools.permutations(items)))
    actual = unique_permutations(items)
    assert actual == expected
    assert len(actual) == count_unique_permutations(items)


def test_too_many_candidates_error():
    """Test that candidate count exceeding cap raises TooManyCandidatesError."""
    import pytest

    err = TooManyCandidatesError(count=720, cap=MAX_MYSTERY_CANDIDATES)
    assert err.count == 720
    assert err.cap == 200
    assert "720" in str(err)
    assert "200" in str(err)

    # 6 distinct missing colors = 6! = 720 permutations > 200 cap
    puzzle_grid = [
        ["RED", "RED", "RED", "?"],
        ["BLUE", "BLUE", "BLUE", "?"],
        ["GREEN", "GREEN", "GREEN", "?"],
        ["YELLOW", "YELLOW", "YELLOW", "?"],
        ["ORANGE", "ORANGE", "ORANGE", "?"],
        ["PURPLE", "PURPLE", "PURPLE", "?"],
        [],
    ]
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(puzzle_grid, f)
        temp_path = f.name

    try:
        with pytest.raises(TooManyCandidatesError) as exc_info:
            find_all_solutions(temp_path)
        assert exc_info.value.count == 720
        assert exc_info.value.cap == 200
    finally:
        os.unlink(temp_path)
