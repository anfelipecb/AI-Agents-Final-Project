"""Tests for extract_rating."""
import pytest

from developing_the_researcher.metrics import extract_rating


def test_extract_rating():
    assert extract_rating("The rating is 5.") == 5
    assert extract_rating("3") == 3
    assert extract_rating("Score: 1 out of 5") == 1
    assert extract_rating("No number") == 3
    assert extract_rating("") == 3
    assert extract_rating("2 and 4") == 2
