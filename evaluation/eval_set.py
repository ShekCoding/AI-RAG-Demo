# -*- coding: utf-8 -*-
"""
评估测试集（golden set）—— 衡量 RAG 好坏的「标准答案」

每一道题：
  question : 用户会怎么问
  expect   : 正确答案应该出现在哪个 chunk 里（用 chunk 标题里的「子串」表示）
             一个题可能有多个正确来源（README 和学习笔记都讲了），所以是 list

注意：这是「检索评估」用的标准——只判断「找没找对段落」。
答案本身对不对、有没有瞎编，是「答案质量评估」，另一回事（下一步做）。
"""

EVAL_SET = [
    {"question": "fixture 里的 yield 前后分别是什么", "expect": ["fixture 与 Session 复用"]},
    {"question": "怎么用 requests 发一个 GET 请求", "expect": ["requests 发请求"]},
    {"question": "一个测试函数怎么跑多组数据", "expect": ["参数化"]},
    {"question": "封装分层的核心思想是什么", "expect": ["封装分层"]},
    {"question": "失败的用例怎么自动重试", "expect": ["失败重试"]},
    {"question": "怎么生成可视化的测试报告", "expect": ["测试报告"]},
    {"question": "怎么切换测试环境", "expect": ["多环境配置"]},
    {"question": "jsonpath 取出来的值是什么类型", "expect": ["jsonpath 断言"]},
    {"question": "pytest.ini 里 addopts 是干嘛的", "expect": ["pytest.ini"]},
    {"question": "GitHub API 不带 User-Agent 会怎样", "expect": ["真实接口的坑", "被测接口"]},
    {"question": "GitHub API 的限流是多少", "expect": ["被测接口", "真实接口的坑", "获取 GitHub Token"]},
    {"question": "怎么把代码推到 GitHub", "expect": ["Git / GitHub"]},
    {"question": "conftest.py 是干嘛的", "expect": ["多环境配置"]},
    {"question": "requests.Session 复用的好处是什么", "expect": ["Session 复用"]},
    {"question": "flaky test 是什么", "expect": ["失败重试"]},
]
