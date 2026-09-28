# -*- coding: utf-8 -*-
"""
标准版 RAG：向量检索 + 生成（真实知识库 = 你的接口自动化测试文档）
运行：python3 embed_rag.py

和 rag.py（简化版）相比，三处升级：
  1. 知识库：虚构的「闪记」→ 你真实的 README.md + 学习笔记.md
  2. 切块：按空行硬切 → 按 markdown 标题切（chunker.py，不破坏代码块）
  3. 检索：jieba 关键词 → 向量相似度（语义匹配）

四步流水线没变：切块 → 检索(向量) → 增强 → 生成
"""
import os

import requests

from chunker import split_markdown

# 知识库目录：里面放 markdown 文档，启动时统一读入切块
KB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kb")

EMBED_URL = "https://api.siliconflow.cn/v1/embeddings"
EMBED_MODEL = "BAAI/bge-m3"

LLM_URL = "https://api.deepseek.com/chat/completions"
LLM_MODEL = "deepseek-chat"


# ========== 第 1 步：切块 ==========

def load_knowledge_base(kb_dir):
    """读目录下所有 .md 文件，按 markdown 标题切成 chunk"""
    chunks = []
    for name in sorted(os.listdir(kb_dir)):
        if not name.endswith(".md"):
            continue
        path = os.path.join(kb_dir, name)
        with open(path, encoding="utf-8") as f:
            text = f.read()
        chunks.extend(split_markdown(text))
    return chunks


# ========== 第 2 步：向量化 + 检索 ==========

def get_embeddings(texts):
    """把一批文字一次性变成向量。input 传 list，一次调用搞定。"""
    api_key = os.environ.get("SILICONFLOW_API_KEY", "")
    if not api_key:
        print("❌ 请先设置环境变量：export SILICONFLOW_API_KEY=你的key")
        return None

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    body = {"model": EMBED_MODEL, "input": texts}

    r = requests.post(EMBED_URL, json=body, headers=headers)
    if r.status_code != 200:
        print(f"❌ 向量化失败：状态码 {r.status_code}")
        print(r.text)
        return None
    return [item["embedding"] for item in r.json()["data"]]


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


# ========== 第 3+4 步：增强 + 生成 ==========

def ask_with_context(query, top_matches):
    """把检索到的段落作为参考资料，让 DeepSeek 只根据这些回答"""
    api_key = os.environ.get("DEEPSEEK_API_KEY", "")
    if not api_key:
        print("❌ 请先设置环境变量：export DEEPSEEK_API_KEY=你的key")
        return None

    context = "\n\n".join(chunk for _, chunk in top_matches)
    system_prompt = (
        "你是一个接口自动化测试知识助手。请只根据下面的【参考资料】回答用户问题。\n"
        "如果资料里没有答案，就诚实地说『资料里没有相关信息』，不要编造。\n\n"
        f"【参考资料】\n{context}"
    )

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    body = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
        ],
    }
    r = requests.post(LLM_URL, json=body, headers=headers)
    if r.status_code != 200:
        print(f"❌ 生成失败：状态码 {r.status_code}")
        print(r.text)
        return None
    return r.json()["choices"][0]["message"]["content"]


if __name__ == "__main__":
    # 启动时：读知识库 → 切块 → 一次性全部向量化（只做一次）
    chunks = load_knowledge_base(KB_DIR)
    print(f"已从 kb/ 目录加载知识库，按标题切成 {len(chunks)} 段")
    chunk_vecs = get_embeddings(chunks)
    if chunk_vecs is None:
        exit(1)
    print("已全部向量化完成\n")

    while True:
        q = input("\n你：")
        if q.lower() in ("quit", "exit", "q"):
            print("再见！")
            break

        query_vec = get_embeddings([q])[0]
        top_matches = retrieve(query_vec, chunk_vecs, chunks, top_k=2)

        print("[检索结果，按相似度从高到低]")
        for score, chunk in top_matches:
            # 只显示 chunk 第一行（通常是标题），避免刷屏
            head = chunk.split("\n", 1)[0]
            print(f"  {score:+.3f}  <-  {head}")

        answer = ask_with_context(q, top_matches)
        if answer:
            print(f"\nAI：{answer}")
