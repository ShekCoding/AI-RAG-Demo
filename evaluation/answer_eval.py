# -*- coding: utf-8 -*-
"""
答案质量评估（LLM-as-judge）

思路：让另一个大模型（DeepSeek）当「裁判」，给 RAG 的回答打分。

裁判看三样东西：
  1. 用户问题
  2. 检索到的参考资料
  3. 助手的回答
然后打两个分：
  - correct（对不对）
  - hallucinated（有没有编造资料里没有的内容）

用法（在项目根目录运行）：python3 -m evaluation.answer_eval

⚠️ 裁判的坑（面试常问）：
  1. 裁判自己也会错——它不是「标准答案」，只是近似
  2. 有偏差：位置偏差、长度偏差、自我偏好
  3. 所以要给它「明确的打分标准」，分数才稳定
"""
import json
import re

from evaluation.answer_eval_set import ANSWER_SET
from rag.generation import chat
from rag.pipeline import RAG


def judge(question, context, answer):
    """让 DeepSeek 当裁判，返回 {"correct": 0/1, "hallucinated": 0/1, "reason": ...}"""
    system_prompt = (
        "你是一个严格的评估裁判，评估一个客服助手的回答质量。"
        "只输出一个 JSON 对象，不要输出任何其他内容。\n"
        'JSON 格式：{"correct": 0或1, "hallucinated": 0或1, "reason": "一句话理由"}\n'
        "字段含义：\n"
        "- correct：回答是否给出了用户真正想要的正确结果。"
        "如果资料里有答案但回答错了，或资料里没有答案但回答没有诚实说明，都是 0。\n"
        "- hallucinated：回答是否编造了「参考资料」里没有的内容（1=编造了，0=没有）。\n"
    )
    user_prompt = (
        f"【用户问题】\n{question}\n\n"
        f"【检索到的参考资料】\n{context}\n\n"
        f"【助手的回答】\n{answer}"
    )
    content = chat(
        [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        json_mode=True,
    )
    if content is None:
        return None
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        # 兜底：模型偶尔不按格式，尝试提取 {...}
        m = re.search(r"\{.*\}", content, re.DOTALL)
        if m:
            return json.loads(m.group(0))
        return {"correct": -1, "hallucinated": -1, "reason": content}


if __name__ == "__main__":
    rag = RAG()
    if rag.chunk_vecs is None:
        exit(1)

    pos_total = pos_ok = neg_total = neg_ok = hallucinated = 0

    print("=" * 60)
    print("逐题结果（LLM 裁判打分）")
    print("=" * 60)
    for item in ANSWER_SET:
        q = item["question"]
        kind = item["kind"]
        answer, top = rag.ask(q)
        if answer is None:
            continue
        context = "\n\n".join(c["text"] for _, c in top)
        result = judge(q, context, answer)

        if result is None:
            continue
        correct = result.get("correct", -1)
        hallu = result.get("hallucinated", -1)
        reason = result.get("reason", "")

        tag = "正" if kind == "positive" else "负"
        print(f"\n[{tag}] {q}")
        print(f"    correct={correct}  hallucinated={hallu}")
        print(f"    理由：{reason}")
        print(f"    回答：{answer}")

        if kind == "positive":
            pos_total += 1
            pos_ok += correct == 1
        else:
            neg_total += 1
            neg_ok += correct == 1   # 负样本 correct=1 意味着「正确地说没有」
        hallucinated += hallu == 1

    print("\n" + "=" * 60)
    print("汇总")
    print("=" * 60)
    print(f"正样本正确率：{pos_ok}/{pos_total}")
    print(f"负样本正确拒绝率（防幻觉）：{neg_ok}/{neg_total}")
    print(f"幻觉率：{hallucinated}/{len(ANSWER_SET)}")
