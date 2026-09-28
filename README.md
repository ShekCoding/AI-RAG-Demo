# AI-RAG-Demo

从零手写的 **RAG（检索增强生成）问答系统**，以「接口自动化测试」为知识库。

完整走通了：大模型 API 调用 → 向量检索 → markdown 切块 → 两层评估（检索命中率 + LLM-as-judge）。

## 亮点

- **向量检索替代关键词检索**：用 BGE-M3 把文字转成向量，按语义匹配，解决关键词检索的「同义词失配」问题
- **防幻觉**：检索不到时诚实说「资料里没有相关信息」，不瞎编
- **自带两层评估**：检索命中率 + 答案质量（LLM-as-judge），能用数据衡量「准不准」
- **真实知识库**：知识库是自己的接口自动化测试文档，不是虚构数据

## 技术栈

- Python 3
- DeepSeek（`deepseek-chat`，生成）
- 硅基流动 SiliconFlow + BGE-M3（向量化）
- jieba（教学版关键词检索，用于和向量检索对比）

## 快速开始

1. 设置环境变量（两个 key，注册即可免费获取）

```bash
export DEEPSEEK_API_KEY=sk-xxx
export SILICONFLOW_API_KEY=sk-xxx
```

2. 安装依赖

```bash
pip3 install requests jieba
```

3. 运行

```bash
python3 embed_rag.py      # 交互式问答（标准版 RAG）
python3 eval.py           # 检索评估（命中率）
python3 answer_eval.py    # 答案评估（LLM-as-judge）
```

## 项目结构

```
.
├── chat.py                # 单轮 / 多轮对话（大模型无状态）
├── rag.py                 # 简化版 RAG（jieba 关键词检索，教学）
├── embed.py               # 向量 demo（文字 → 数字、语义相似度）
├── chunker.py             # markdown 切块（按标题、不破坏代码块）
├── embed_rag.py           # 标准版 RAG（向量检索 + 生成）
├── eval_set.py / eval.py  # 检索评估
├── answer_eval_set.py / answer_eval.py  # 答案评估
├── kb/                    # 知识库（markdown 文档）
└── AI-RAG学习笔记.md       # 完整知识沉淀（12 章）
```

## 详细笔记

所有知识点（调 API、RAG 四步、向量检索、评估、面试题）的完整沉淀见 [AI-RAG学习笔记.md](./AI-RAG学习笔记.md)。
