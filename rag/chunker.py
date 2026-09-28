# -*- coding: utf-8 -*-
"""
markdown 切块（chunking）—— RAG 第 1 步的正确姿势

为什么不能按空行切？
- markdown 文档里，一个「知识单元」的边界是「标题」，不是空行。
- 按空行切，会把一个知识点切成碎片，或把不相干的拼在一起。

这个文件做两件事：
1. 按标题切：每遇到 # / ## / ### 标题，就是一个新 chunk 的开头
2. 不破坏代码块：代码块里可能出现 "# 1. 安装依赖" 这种行，
   不能误当成标题（所以要跟踪 ``` 围栏，只在代码块外识别标题）
"""
import re

# 匹配 1~3 级标题行：# 标题 / ## 标题 / ### 标题
HEADING_RE = re.compile(r"^#{1,3}\s+.*$")


def split_markdown(text):
    """把 markdown 文本按标题切成一段段，每段 = 标题 + 它的正文"""
    chunks = []
    cur_title = None
    cur_body = []
    in_code_block = False   # 是否正处在 ``` 代码块里

    def flush():
        """把当前攒着的标题 + 正文，合并成一个 chunk 存起来"""
        nonlocal cur_title, cur_body
        parts = []
        if cur_title is not None:
            parts.append(cur_title)
        body = "\n".join(cur_body).strip()
        if body:
            parts.append(body)
        if parts:
            chunks.append("\n".join(parts))
        cur_title = None
        cur_body = []

    for line in text.split("\n"):
        s = line.strip()

        # 遇到 ``` 围栏，切换「在/不在代码块」状态
        if s.startswith("```"):
            in_code_block = not in_code_block
            cur_body.append(line)
            continue

        # 只有「不在代码块里、且是标题」的行，才当作新 chunk 的开头
        if not in_code_block and HEADING_RE.match(s):
            flush()
            cur_title = s
        else:
            cur_body.append(line)

    flush()
    return chunks
