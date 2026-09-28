# -*- coding: utf-8 -*-
"""
答案质量评估的测试集

和 eval_set.py 的区别：
  - eval_set.py 测「检索」：找没找对段落
  - 本文件测「生成」：答没答对、有没有瞎编

两类题：
  - positive：答案在知识库里，应该答对
  - negative：答案不在知识库里，应该诚实说「资料里没有相关信息」（不能瞎编）

negative 尤其重要——它测的是「防幻觉」，而这是 RAG 最核心的价值。
故意选了几个「模型训练时早就知道答案」的问题（比如单元测试 vs 接口测试），
因为这种题最容易诱导模型「跳出资料、用训练知识作答」。
"""

ANSWER_SET = [
    # —— 正样本：应该答对 ——
    {"question": "fixture 里的 yield 前后分别是什么", "kind": "positive"},
    {"question": "怎么生成可视化的测试报告", "kind": "positive"},
    {"question": "GitHub API 的限流是多少", "kind": "positive"},
    {"question": "jsonpath 取单个值时返回什么类型", "kind": "positive"},

    # —— 负样本：应该诚实说「资料里没有」——
    {"question": "接口测试和单元测试有什么区别", "kind": "negative"},
    {"question": "怎么用 pytest 做性能测试", "kind": "negative"},
    {"question": "怎么用 Jenkins 做持续集成", "kind": "negative"},
    {"question": "pytest 和 unittest 哪个更好", "kind": "negative"},
]
