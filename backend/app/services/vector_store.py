import struct

import faiss
import numpy as np


class VectorStore:
    def __init__(self, dimension: int = 1024) -> None:
        self.dimension = dimension
        self.index = faiss.IndexFlatIP(dimension)  # Inner product (cosine after normalization)
        self._id_map: list[int] = []  # position -> chunk_id

    def add(self, vectors: list[list[float]], ids: list[int]) -> None:
        arr = np.array(vectors, dtype=np.float32)
        faiss.normalize_L2(arr)
        self.index.add(arr)
        self._id_map.extend(ids)

    def search(self, query_vector: list[float], top_k: int = 5) -> list[tuple[int, float]]:
        if self.index.ntotal == 0:
            return []
        q = np.array([query_vector], dtype=np.float32)
        faiss.normalize_L2(q)
        scores, indices = self.index.search(q, min(top_k, self.index.ntotal))
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0:
                continue
            results.append((self._id_map[idx], float(score)))
        return results

    def remove(self, ids: list[int]) -> None:
        id_set = set(ids)
        keep_positions = [i for i, cid in enumerate(self._id_map) if cid not in id_set]
        if not keep_positions:
            self.index = faiss.IndexFlatIP(self.dimension)
            self._id_map = []
            return
        keep_vectors = np.vstack([
            faiss.rev_swig_ptr(self.index.get_xb(), self.index.ntotal * self.dimension)[
                pos * self.dimension : (pos + 1) * self.dimension
            ]
            for pos in keep_positions
        ]).astype(np.float32)
        self.index = faiss.IndexFlatIP(self.dimension)
        self._id_map = [self._id_map[pos] for pos in keep_positions]
        self.index.add(keep_vectors)

    def serialize(self) -> bytes:
        index_bytes = faiss.serialize_index(self.index).tobytes()
        id_map_bytes = struct.pack(f"{len(self._id_map)}i", *self._id_map)
        header = struct.pack("I", len(self._id_map))
        return header + id_map_bytes + index_bytes

    def deserialize(self, data: bytes) -> None:
        id_map_len = struct.unpack("I", data[:4])[0]
        id_map_bytes_size = id_map_len * 4
        self._id_map = list(struct.unpack(f"{id_map_len}i", data[4:4 + id_map_bytes_size]))
        self.index = faiss.deserialize_index(np.frombuffer(data[4 + id_map_bytes_size:], dtype=np.uint8))

    def vector_to_bytes(self, vector: list[float]) -> bytes:
        return struct.pack(f"{len(vector)}f", *vector)

    def bytes_to_vector(self, data: bytes) -> list[float]:
        n = len(data) // 4
        return list(struct.unpack(f"{n}f", data))

    @property
    def total(self) -> int:
        return self.index.ntotal
