# AI-RAG-Demo

从零手写的 **RAG（检索增强生成）问答系统**，以「接口自动化测试」为知识库。

完整走通了：大模型 API 调用 → 向量检索 → markdown 切块 → 两层评估（检索命中率 + LLM-as-judge）→ Web 界面。

## 亮点

- **向量检索替代关键词检索**：用 BGE-M3 把文字转成向量，按语义匹配，解决关键词检索的「同义词失配」问题
- **防幻觉**：检索不到时诚实说「资料里没有相关信息」，不瞎编
- **自带两层评估**：检索命中率 + 答案质量（LLM-as-judge），能用数据衡量「准不准」
- **可溯源**：回答时标注答案出自哪份文档哪一节
- **Web 界面**：Streamlit 一键起网页，聊天式问答，可调检索段数
- **真实知识库**：知识库是自己的接口自动化测试文档，不是虚构数据
- **模块化**：切块 / 向量化 / 检索 / 生成 / 评估各司其职，可独立替换

## 技术栈

- Python 3
- DeepSeek（`deepseek-chat`，生成）
- 硅基流动 SiliconFlow + BGE-M3（向量化）
- jieba（教学版关键词检索，用于和向量检索对比）
- Streamlit（Web 界面）

## 快速开始

1. 设置环境变量（两个 key，注册即可免费获取）

```bash
export DEEPSEEK_API_KEY=sk-xxx
export SILICONFLOW_API_KEY=sk-xxx
```

2. 安装依赖

```bash
pip3 install -r requirements.txt
```

3. 运行（都在项目根目录）

```bash
# Web 界面（推荐）
streamlit run app_web.py

# 命令行
python3 app.py

# 评估
python3 -m evaluation.retrieve_eval        # 检索命中率
python3 -m evaluation.answer_eval          # 答案质量（LLM-as-judge）

# 教学演示
python3 demos/chat.py                      # 多轮对话（大模型无状态）
python3 demos/rag_keyword.py               # 关键词检索版（对比用）
python3 demos/embed_demo.py                # 向量 demo（感受语义距离）
```

## 项目结构

```
.
├── app.py                  # 入口：命令行交互式问答
├── app_web.py              # 入口：Streamlit Web 界面
├── rag/                    # 核心 RAG 包（四步流水线）
│   ├── chunker.py          #   切块（markdown 按标题切，不破坏代码块）
│   ├── embedding.py        #   向量化（文字 → 向量）
│   ├── retrieval.py        #   检索（余弦相似度取 top_k）
│   ├── generation.py       #   生成（调大模型）
│   └── pipeline.py         #   组装（load_knowledge_base + RAG 类）
├── evaluation/             # 两层评估
│   ├── eval_set.py         #   检索测试集（问题 + 期望段落）
│   ├── retrieve_eval.py    #   检索命中率
│   ├── answer_eval_set.py  #   答案测试集（正/负样本）
│   └── answer_eval.py      #   答案质量（LLM-as-judge）
├── demos/                  # 教学演进脚本（chat → 关键词RAG → 向量demo）
├── data/                   # 知识库（markdown 文档）
├── requirements.txt
└── AI-RAG学习笔记.md        # 完整知识沉淀（13 章）
```

## 详细笔记

所有知识点（调 API、RAG 四步、向量检索、评估、Web UI、面试题）的完整沉淀见 [AI-RAG学习笔记.md](./AI-RAG学习笔记.md)。
