"""Tests for EmbeddingLoader.cosine_sim with known vectors."""
import numpy as np
import pytest

from developing_the_researcher.models.embeddings import EmbeddingLoader


def test_cosine_sim_identical():
    a = np.array([1.0, 0.0, 0.0], dtype=np.float32)
    assert EmbeddingLoader.cosine_sim(a, a) == pytest.approx(1.0)


def test_cosine_sim_orthogonal():
    a = np.array([1.0, 0.0, 0.0], dtype=np.float32)
    b = np.array([0.0, 1.0, 0.0], dtype=np.float32)
    assert EmbeddingLoader.cosine_sim(a, b) == pytest.approx(0.0)


def test_cosine_sim_opposite():
    a = np.array([1.0, 0.0, 0.0], dtype=np.float32)
    b = np.array([-1.0, 0.0, 0.0], dtype=np.float32)
    assert EmbeddingLoader.cosine_sim(a, b) == pytest.approx(-1.0)


def test_cosine_sim_zero_vector():
    a = np.array([0.0, 0.0, 0.0], dtype=np.float32)
    b = np.array([1.0, 0.0, 0.0], dtype=np.float32)
    assert EmbeddingLoader.cosine_sim(a, b) == 0.0
