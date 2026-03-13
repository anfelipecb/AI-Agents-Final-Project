"""Tests for CorpusLoader.load() fallback and DoublesLoader.load_doubles_from_corpus() structure."""
import json
import tempfile
from pathlib import Path

import pytest

from developing_the_researcher.data.loaders import CorpusLoader, DoublesLoader, SAMPLE_ABSTRACTS


def test_corpus_loader_fallback(tmp_path):
    """When path missing or empty, load() returns sample abstracts."""
    loader = CorpusLoader(path=tmp_path / "nonexistent.json")
    out = loader.load()
    assert len(out) >= 1
    assert out == SAMPLE_ABSTRACTS


def test_corpus_loader_load_real(tmp_path):
    """When file exists with theses, load() returns them."""
    path = tmp_path / "macs_theses.json"
    data = {"theses": [{"id": "1", "abstract": "Foo", "title": "T", "methodology": "computational"}]}
    path.write_text(json.dumps(data), encoding="utf-8")
    loader = CorpusLoader(path=path)
    out = loader.load()
    assert len(out) == 1
    assert out[0]["abstract"] == "Foo"


def test_doubles_loader_structure():
    """Doubles have thesis, condition, student_profile, weak_dims, methodology."""
    corpus = CorpusLoader()
    doubles_loader = DoublesLoader(corpus)
    doubles = doubles_loader.load_doubles_from_corpus(n_per_condition=2)
    conditions = {"single_agent", "random_committee", "prescribed_committee"}
    profiles = {"passive_accepter", "methods_weak", "descriptive_reporter"}
    for d in doubles:
        assert "thesis" in d
        assert d["condition"] in conditions
        assert d["student_profile"] in profiles
        assert "weak_dims" in d
        assert "methodology" in d
    assert len(doubles) >= 3
