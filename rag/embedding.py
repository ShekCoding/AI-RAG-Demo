# -*- coding: utf-8 -*-
"""
向量化（embedding）—— RAG 第 2 步的前半：把文字变成向量

用硅基流动的 BGE-M3（免费、中文好、OpenAI 兼容）。
「意思相近 → 向量相近」，这是向量检索能听懂语义的根本。
"""
import os

import requests

EMBED_URL = "https://api.siliconflow.cn/v1/embeddings"
EMBED_MODEL = "BAAI/bge-m3"


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
