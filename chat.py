# -*- coding: utf-8 -*-
"""
多轮对话 Demo：调用 DeepSeek，并让它「记住」上下文
运行：python3 chat.py

核心认知：大模型没有记忆！每一轮都是全新的。
要让它「记得」之前聊了什么，就得自己把历史攒进 messages，每轮完整发回去。
"""
import os

import requests

BASE_URL = "https://api.deepseek.com/chat/completions"
MODEL = "deepseek-chat"


def ask_deepseek(messages):
    """把「完整对话历史」发给 DeepSeek，返回它的回答"""
    api_key = os.environ.get("DEEPSEEK_API_KEY", "")
    if not api_key:
        print("❌ 请先设置环境变量：export DEEPSEEK_API_KEY=你的key")
        return None

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    body = {
        "model": MODEL,
        "messages": messages,   # ← 关键：发的是整段历史，不是单句
    }

    r = requests.post(BASE_URL, json=body, headers=headers)
    if r.status_code != 200:
        print(f"❌ 请求失败：状态码 {r.status_code}")
        print(r.text)
        return None

    return r.json()["choices"][0]["message"]["content"]


if __name__ == "__main__":
    print("=" * 46)
    print("DeepSeek 多轮对话 Demo（输入 quit 退出）")
    print("测试：先告诉它你叫什么，再问它你叫什么")
    print("=" * 46)

    # 历史记录：先放一个 system（人设），之后每轮都往里追加
    messages = [
        {"role": "system", "content": "你是一个有帮助的助手"},
    ]

    while True:
        q = input("\n你：")
        if q.lower() in ("quit", "exit", "q"):
            print("再见！")
            break

        # 1. 把用户这句话追加进历史
        messages.append({"role": "user", "content": q})

        # 2. 把整段历史发出去（模型自己没记忆，靠我们喂历史）
        answer = ask_deepseek(messages)
        if answer is None:
            break

        # 3. 把模型的回答也追加进历史，下一轮它才能「记得」自己说过啥
        messages.append({"role": "assistant", "content": answer})

        print(f"\nAI：{answer}")
