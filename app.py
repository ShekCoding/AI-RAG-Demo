# -*- coding: utf-8 -*-
"""
主入口：交互式问答（标准版 RAG）

运行：python3 app.py

流程：
  1. 加载 data/ 知识库 → 切块 → 全部向量化（启动时做一次）
  2. 之后每输入一个问题：向量化 → 检索 top_k → 生成回答 → 标注出处
"""
from rag.pipeline import RAG


def main():
    rag = RAG()
    if rag.chunk_vecs is None:
        return
    print(f"已加载知识库，切成 {len(rag.chunks)} 段，并全部向量化完成\n")

    while True:
        q = input("\n你：")
        if q.lower() in ("quit", "exit", "q"):
            print("再见！")
            break

        answer, top_matches = rag.ask(q)
        if answer is None:
            break

        print("[检索结果，按相似度从高到低]")
        for score, chunk in top_matches:
            print(f"  {score:+.3f}  <-  {chunk['title']}")

        print(f"\nAI：{answer}")
        # 可溯源：明确列出答案依据的文档与章节
        print("\n📎 参考来源：")
        for score, chunk in top_matches:
            print(f"  · {chunk['source']} · {chunk['title']}")


if __name__ == "__main__":
    main()
