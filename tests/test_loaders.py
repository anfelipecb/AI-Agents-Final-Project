"""Tests for CorpusLoader.load() fallback and DoublesLoader.load_doubles_from_corpus() structure."""
import json
import tempfile
from pathlib import Path

import pytest

from safe_to_be_challenged.data.loaders import CorpusLoader, DoublesLoader, SAMPLE_ABSTRACTS


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
    """Doubles have thesis, condition, trust_sensitivity, methodology."""
    corpus = CorpusLoader()
    doubles_loader = DoublesLoader(corpus)
    doubles = doubles_loader.load_doubles_from_corpus(n_per_condition=2)
    conditions = {"committee_only", "silent_monitor", "visible_label"}
    for d in doubles:
        assert "thesis" in d
        assert d["condition"] in conditions
        assert d["trust_sensitivity"] in ("low", "high")
        assert "methodology" in d
    assert len(doubles) >= 3
