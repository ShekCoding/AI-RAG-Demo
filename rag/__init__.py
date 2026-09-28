# -*- coding: utf-8 -*-
"""rag 包：RAG 四步流水线（切块 → 向量化 → 检索 → 生成）

模块分工：
  chunker.py    切块（markdown 按标题切，不破坏代码块）
  embedding.py  向量化（文字 → 向量）
  retrieval.py  检索（余弦相似度取 top_k）
  generation.py 生成（调大模型）
  pipeline.py   组装（load_knowledge_base + RAG 类）
"""
