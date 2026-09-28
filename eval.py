# -*- coding: utf-8 -*-
"""
评估（evaluation）—— 用数据回答「我的 RAG 到底准不准」

核心指标：检索命中率（retrieval hit rate）
  = 测试集里，有多少题的「正确答案所在的 chunk」被检索进了 top_k

用法：python3 eval.py
  会输出两部分：
    1. 逐题详细结果（top_k=2）：每题检索到了什么、命没命中
    2. 不同 top_k 的命中率对比（1 / 2 / 3）

为什么先评检索、不评答案？
  检索是 RAG 特有的环节，也是答案质量的「上游」：
  检索错 → 大概率答错；检索对 → 才轮到生成环节发挥。
"""
from embed_rag import KB_DIR, get_embeddings, load_knowledge_base, retrieve
from eval_set import EVAL_SET


def evaluate(chunks, chunk_vecs, question_vecs, top_k, detail=False):
    hits = 0
    for qv, item in zip(question_vecs, EVAL_SET):
        top = retrieve(qv, chunk_vecs, chunks, top_k=top_k)
        # 命中 = top_k 里有任何一段，包含「期望子串」里的任意一个
        hit = any(any(exp in chunk for exp in item["expect"]) for _, chunk in top)
        hits += hit

        if detail:
            mark = "✓" if hit else "✗"
            print(f"  {mark} {item['question']}")
            for score, chunk in top:
                print(f"        {score:+.3f} <- {chunk.split(chr(10), 1)[0]}")

    hit_rate = hits / len(EVAL_SET)
    print(f"top_k={top_k}：命中率 {hits}/{len(EVAL_SET)} = {hit_rate:.0%}")
    return hit_rate


if __name__ == "__main__":
    chunks = load_knowledge_base(KB_DIR)
    chunk_vecs = get_embeddings(chunks)
    if chunk_vecs is None:
        exit(1)
    question_vecs = get_embeddings([item["question"] for item in EVAL_SET])
    if question_vecs is None:
        exit(1)

    print(f"知识库 {len(chunks)} 段，测试集 {len(EVAL_SET)} 题\n")

    # 第一部分：逐题详细结果（top_k=2，生产实际会用的设置）
    print("=" * 60)
    print("逐题详细结果（top_k=2）")
    print("=" * 60)
    evaluate(chunks, chunk_vecs, question_vecs, top_k=2, detail=True)

    # 第二部分：不同 top_k 的命中率对比
    print("\n" + "=" * 60)
    print("不同 top_k 的命中率对比")
    print("=" * 60)
    for k in [1, 2, 3]:
        evaluate(chunks, chunk_vecs, question_vecs, top_k=k)
