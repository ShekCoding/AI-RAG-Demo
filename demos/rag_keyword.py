# -*- coding: utf-8 -*-
"""
简化版 RAG：本地知识库问答
运行：python3 demos/rag_keyword.py

RAG 四步流水线：
  1. 切块    → 把文档切成一段段
  2. 检索    → 找出和问题最相关的几段（这里用「关键词匹配」，教学版）
  3. 增强    → 把这几段塞进 prompt
  4. 生成    → 让 DeepSeek 只根据这几段回答

这是教学版，检索用关键词匹配；生产环境用「向量检索」，下一步再升级。
"""
import os

import jieba
import requests

# 关键坑：不要写相对路径 "knowledge.txt"。
# 相对路径找的是「运行命令时所在的目录」(CWD)，不是脚本所在目录。
# 用 __file__ 拿到脚本自己的绝对路径，再拼出 knowledge.txt，这样在哪个目录运行都能找到。
KB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "knowledge.txt")

BASE_URL = "https://api.deepseek.com/chat/completions"


# ========== 第 1 步：切块 ==========

def load_and_split(filepath):
    """把文档按空行切成一段段，每段是一个 chunk"""
    with open(filepath, encoding="utf-8") as f:
        text = f.read()
    chunks = [c.strip() for c in text.split("\n\n") if c.strip()]
    return chunks


# ========== 第 2 步：检索（关键词匹配） ==========

def retrieve(query, chunks, top_k=2):
    """找出和问题最相关的 top_k 个段落。教学版：用 jieba 分词后数关键词命中"""
    keywords = [w for w in jieba.cut(query) if w.strip()]
    scored = []
    for chunk in chunks:
        score = sum(1 for kw in keywords if kw in chunk)
        scored.append((score, chunk))
    scored.sort(key=lambda x: x[0], reverse=True)   # 分数高的排前面
    return [chunk for score, chunk in scored[:top_k] if score > 0]


# ========== 第 3+4 步：增强 + 生成 ==========

def ask_with_context(query, context_chunks):
    """把检索到的段落作为参考资料，让 DeepSeek 只根据这些回答"""
    api_key = os.environ.get("DEEPSEEK_API_KEY", "")
    if not api_key:
        print("❌ 请先设置环境变量：export DEEPSEEK_API_KEY=你的key")
        return None

    context = "\n\n".join(context_chunks)

    # 关键：system 提示词里「塞资料 + 要求只根据资料答、不许编」
    system_prompt = (
        "你是一个客服助手。请只根据下面的【参考资料】回答用户问题。\n"
        "如果资料里没有答案，就诚实地说『资料里没有相关信息』，不要编造。\n\n"
        f"【参考资料】\n{context}"
    )

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    body = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
        ],
    }

    r = requests.post(BASE_URL, json=body, headers=headers)
    if r.status_code != 200:
        print(f"❌ 请求失败：状态码 {r.status_code}")
        print(r.text)
        return None
    return r.json()["choices"][0]["message"]["content"]


if __name__ == "__main__":
    chunks = load_and_split(KB_FILE)
    print(f"已加载知识库 {KB_FILE}，切成 {len(chunks)} 段\n")

    while True:
        q = input("\n你：")
        if q.lower() in ("quit", "exit", "q"):
            print("再见！")
            break

        relevant = retrieve(q, chunks, top_k=2)
        if not relevant:
            print("⚠️ 没检索到相关内容（简化版关键词匹配能力有限）")
            continue

        print(f"[检索到 {len(relevant)} 段相关资料]")
        answer = ask_with_context(q, relevant)
        if answer:
            print(f"\nAI：{answer}")
