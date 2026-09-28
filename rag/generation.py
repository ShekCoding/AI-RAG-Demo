# -*- coding: utf-8 -*-
"""
生成（generation）—— RAG 第 3+4 步：调大模型（DeepSeek）生成回答

这里是「通用」的调用函数 chat()：
  1. 标准 RAG 用它生成回答（pipeline.py）
  2. LLM-as-judge 也用它当裁判（evaluation/answer_eval.py）
统一走这里，就不用到处复制 requests 那段样板代码。
"""
import os

import requests

LLM_URL = "https://api.deepseek.com/chat/completions"
LLM_MODEL = "deepseek-chat"


def chat(messages, json_mode=False):
    """通用的大模型调用：发一段 messages，返回回答文本。

    json_mode=True 时，用 response_format 要求模型只输出 JSON（评估裁判用）。
    """
    api_key = os.environ.get("DEEPSEEK_API_KEY", "")
    if not api_key:
        print("❌ 请先设置环境变量：export DEEPSEEK_API_KEY=你的key")
        return None

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    body = {"model": LLM_MODEL, "messages": messages}
    if json_mode:
        body["response_format"] = {"type": "json_object"}

    r = requests.post(LLM_URL, json=body, headers=headers)
    if r.status_code != 200:
        print(f"❌ 生成失败：状态码 {r.status_code}")
        print(r.text)
        return None
    return r.json()["choices"][0]["message"]["content"]
