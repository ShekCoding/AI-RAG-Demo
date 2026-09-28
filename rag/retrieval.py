# -*- coding: utf-8 -*-
"""
检索（retrieval）—— RAG 第 2 步的后半：用向量相似度找最相关的段落

把问题向量和所有 chunk 向量算一遍余弦相似度，取最像的 top_k 段。
"""


def cosine_similarity(v1, v2):
    """余弦相似度，越接近 1 越像"""
    dot = sum(a * b for a, b in zip(v1, v2))
    n1 = sum(a * a for a in v1) ** 0.5
    n2 = sum(b * b for b in v2) ** 0.5
    return dot / (n1 * n2)


def retrieve(query_vec, chunk_vecs, chunks, top_k=2):
    """找出和问题语义最接近的 top_k 段"""
    scored = []
    for chunk, vec in zip(chunks, chunk_vecs):
        score = cosine_similarity(query_vec, vec)
        scored.append((score, chunk))
    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[:top_k]
