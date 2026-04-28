import struct

import numpy as np
import pytest

from app.services.vector_store import VectorStore


@pytest.fixture
def vector_store():
    return VectorStore(dimension=4)


class TestVectorStore:
    def test_init_creates_empty_index(self, vector_store):
        assert vector_store.index is not None
        assert vector_store.index.ntotal == 0

    def test_add_vectors(self, vector_store):
        vectors = [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0]]
        ids = [10, 20]
        vector_store.add(vectors, ids)
        assert vector_store.index.ntotal == 2

    def test_search_returns_nearest(self, vector_store):
        vectors = [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.9, 0.1, 0.0, 0.0]]
        ids = [1, 2, 3]
        vector_store.add(vectors, ids)

        results = vector_store.search([1.0, 0.0, 0.0, 0.0], top_k=2)
        assert len(results) == 2
        assert results[0][0] == 1  # nearest id
        assert results[0][1] > results[1][1]  # higher score first

    def test_search_empty_returns_empty(self, vector_store):
        results = vector_store.search([1.0, 0.0, 0.0, 0.0], top_k=5)
        assert results == []

    def test_remove_by_ids(self, vector_store):
        vectors = [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0]]
        ids = [1, 2]
        vector_store.add(vectors, ids)
        vector_store.remove([1])
        results = vector_store.search([1.0, 0.0, 0.0, 0.0], top_k=5)
        returned_ids = [r[0] for r in results]
        assert 1 not in returned_ids

    def test_serialize_deserialize(self, vector_store):
        vectors = [[1.0, 0.0, 0.0, 0.0]]
        ids = [42]
        vector_store.add(vectors, ids)

        data = vector_store.serialize()
        new_store = VectorStore(dimension=4)
        new_store.deserialize(data)
        assert new_store.index.ntotal == 1
        results = new_store.search([1.0, 0.0, 0.0, 0.0], top_k=1)
        assert results[0][0] == 42

    def test_vector_to_bytes_and_back(self, vector_store):
        vec = [0.1, 0.2, 0.3, 0.4]
        data = vector_store.vector_to_bytes(vec)
        assert isinstance(data, bytes)
        restored = vector_store.bytes_to_vector(data)
        assert len(restored) == 4
        assert abs(restored[0] - 0.1) < 1e-6
