"""Tests for corpus utilities: extract_year, infer_methodology."""
import pytest

from developing_the_researcher.data.corpus import extract_year, infer_methodology


def test_extract_year():
    assert extract_year("Submitted 2023") == 2023
    assert extract_year("2021-05-15") == 2021
    assert extract_year("1999 and 2000") == 1999
    assert extract_year("no year") is None
    assert extract_year("") is None
    assert extract_year(None) is None


def test_infer_methodology():
    assert infer_methodology("Network analysis of Twitter", "We use machine learning") == "computational"
    assert infer_methodology("", "Regression and survey experiment") == "quantitative"
    assert infer_methodology("Case study", "Qualitative interviews and ethnography") == "qualitative"
    assert infer_methodology("Random title", "Some abstract") == "unknown"
