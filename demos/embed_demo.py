# -*- coding: utf-8 -*-
"""
向量检索 Demo：把文字变成向量，感受「语义距离」
运行：python3 demos/embed_demo.py

为什么需要它？
刚才 jieba 关键词检索输在「手机APP」和「iOS Android」字面不同、意思相同，
它只会数字面命中，所以「手机APP」一个字都没匹配上。

embedding 干的事：把文字变成一串数字（向量），
「意思相近」的句子，数字也相近 —— 不用再管字面一样不一样。

BGE-M3 把每段文字变成 1024 个数字（1024 维向量）。
"""
import os

import requests

BASE_URL = "https://api.siliconflow.cn/v1/embeddings"
MODEL = "BAAI/bge-m3"


def get_embedding(text):
    """把一段文字变成一个向量（1024 个 float）"""
    api_key = os.environ.get("SILICONFLOW_API_KEY", "")
    if not api_key:
        print("❌ 请先设置环境变量：export SILICONFLOW_API_KEY=你的key")
        return None

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    body = {
        "model": MODEL,
        "input": text,   # 注意：这里的字段是 input，不是 messages
    }
    r = requests.post(BASE_URL, json=body, headers=headers)
    if r.status_code != 200:
        print(f"❌ 请求失败：状态码 {r.status_code}")
        print(r.text)
        return None
    # 返回结构：{"data": [{"embedding": [...], "index": 0}], ...}
    return r.json()["data"][0]["embedding"]


def cosine_similarity(v1, v2):
    """两个向量的余弦相似度，范围 -1 到 1，越接近 1 越「像」"""
    dot = sum(a * b for a, b in zip(v1, v2))
    norm1 = sum(a * a for a in v1) ** 0.5
    norm2 = sum(b * b for b in v2) ** 0.5
    return dot / (norm1 * norm2)


if __name__ == "__main__":
    # 关键对比：问题问「手机APP」，候选 A 里根本没有「手机APP」这几个字
    query = "闪记支持手机APP吗？"
    candidates = [
        "支持 iOS、Android、Windows、Mac 和网页版。",  # 意思 = 支持手机，但字面没「手机APP」
        "专业版每月 29 元，支持多端同步。",           # 跟手机无关
    ]

    qv = get_embedding(query)
    if qv is None:
        exit(1)

    print(f"模型：{MODEL}")
    print(f"向量维度：{len(qv)} 个数字\n")

    # 1. 先看看「文字 → 数字」长什么样（只显示前 10 个，否则刷屏）
    print(f"「{query}」的前 10 个数字：")
    print("  ", [round(x, 4) for x in qv[:10]])
    print("  ...（后面还有 1000 多个数字）\n")

    # 2. 算它和每个候选句子的相似度
    print("语义相似度对比（1 = 完全同义，0 = 无关）：")
    for c in candidates:
        cv = get_embedding(c)
        sim = cosine_similarity(qv, cv)
        print(f"  {sim:+.3f}  <-  「{c}」")

    print("\n👉 看懂了吗：候选 A 里没有「手机APP」这几个字，")
    print("   但它的相似度应该明显高于候选 B —— 这就是「语义匹配」")
    print("   正好补上了 jieba 关键词检索补不了的那块。")
