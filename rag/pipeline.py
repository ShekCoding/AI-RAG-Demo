# -*- coding: utf-8 -*-
"""
RAG 流水线（pipeline）—— 把四步串起来：切块 → 检索 → 增强 → 生成

职责：
  - load_knowledge_base：读 data/ 目录的 markdown，切成带来源的 chunk
  - RAG 类：加载 + 向量化一次，之后每问一句「检索 + 生成」

四步流水线：
  切块（chunker）→ 向量化 + 检索（embedding / retrieval）→ 增强 + 生成（generation）
"""
import os

from .chunker import split_markdown
from .embedding import get_embeddings
from .generation import chat
from .retrieval import retrieve

# 知识库目录：rag/ 的上一级 data/
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")

SYSTEM_PROMPT = (
    "你是一个接口自动化测试知识助手。请只根据下面的【参考资料】回答用户问题。\n"
    "如果资料里没有答案，就诚实地说『资料里没有相关信息』，不要编造。\n\n"
    "【参考资料】\n{context}"
)


def load_knowledge_base(data_dir=None):
    """读目录下所有 .md 文件，按标题切成 chunk，并带上来源信息

    每个 chunk 是一个 dict：text（内容）、source（来自哪个文件）、title（标题行）。
    带来源，是为了回答时「可溯源」——告诉你答案出自哪份文档哪一节。
    """
    data_dir = data_dir or DATA_DIR
    chunks = []
    for name in sorted(os.listdir(data_dir)):
        if not name.endswith(".md"):
            continue
        path = os.path.join(data_dir, name)
        with open(path, encoding="utf-8") as f:
            text = f.read()
        for c in split_markdown(text):
            chunks.append({
                "text": c,
                "source": name,
                "title": c.split("\n", 1)[0],   # 第一行是标题
            })
    return chunks


class RAG:
    """一个 RAG 实例：加载知识库 → 向量化一次 → 之后每问一句检索 + 生成

    把「加载 + 向量化」放到 __init__，是因为它们只要做一次；
    之后每问一句，只做「检索 + 生成」（用 ask 方法）。
    """

    def __init__(self, data_dir=None, top_k=2):
        self.chunks = load_knowledge_base(data_dir)
        self.chunk_vecs = get_embeddings([c["text"] for c in self.chunks])
        self.top_k = top_k

    def ask(self, query, top_k=None):
        """问一句，返回 (answer, top_matches)。

        top_k 可选：Web UI 里用户拖滑块调整检索段数，不必重建 RAG。
        不传则用实例默认的 self.top_k。
        """
        if self.chunk_vecs is None:
            return None, []
        query_vec = get_embeddings([query])
        if query_vec is None:
            return None, []
        k = top_k if top_k is not None else self.top_k
        top_matches = retrieve(query_vec[0], self.chunk_vecs, self.chunks, top_k=k)
        answer = self._generate(query, top_matches)
        return answer, top_matches

    def _generate(self, query, top_matches):
        """增强 + 生成：把检索到的段落塞进 prompt，让模型只根据这些回答"""
        context = "\n\n".join(
            f"[来源：{c['source']} · {c['title']}]\n{c['text']}"
            for _, c in top_matches
        )
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT.format(context=context)},
            {"role": "user", "content": query},
        ]
        return chat(messages)
