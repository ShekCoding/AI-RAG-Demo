# -*- coding: utf-8 -*-
"""
Web 界面（Streamlit）：把命令行问答变成网页

运行：streamlit run app_web.py

和 app.py（命令行版）的区别，只是多了一层 UI，核心逻辑完全复用 rag.RAG：
  - @st.cache_resource：知识库只加载 + 向量化一次，整个 app 复用
    （否则每次交互都重新 embedding 全部 chunk，又慢又费 API 配额）
  - st.session_state：攒聊天历史（和 chat.py 里自己攒 messages 同理——大模型无状态）
  - 回答下面用 expander 展开「参考来源」+ 相似度分数，可溯源
"""
import streamlit as st

from rag.pipeline import RAG


@st.cache_resource(show_spinner="正在加载知识库并向量化……")
def get_rag():
    """加载 RAG。cache_resource 保证只做一次（知识库 + 向量化都很贵）。"""
    return RAG()


st.set_page_config(page_title="接口测试知识助手", page_icon="🤖")

# ---------- 侧边栏：配置 + 统计 ----------
with st.sidebar:
    st.header("⚙️ 配置")
    top_k = st.slider("检索段落数 top_k", min_value=1, max_value=5, value=2)

    st.divider()
    if st.button("🗑️ 清空对话"):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    rag = get_rag()
    st.markdown(f"📚 知识库：**{len(rag.chunks)}** 段")
    st.caption("数据源：`data/` 下的 markdown 文档")

# ---------- 主区：聊天 ----------
st.title("🤖 接口测试知识助手")
st.caption("基于 RAG（检索增强生成）——只依据资料回答、可溯源。")

if "messages" not in st.session_state:
    st.session_state.messages = []

# 渲染历史
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg.get("sources"):
            with st.expander("📎 参考来源"):
                for s in msg["sources"]:
                    st.markdown(f"- {s}")

# 输入
question = st.chat_input("问我一个接口自动化测试相关的问题…")
if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.write(question)

    answer, top_matches = rag.ask(question, top_k=top_k)

    if answer is None:
        st.error("出错了：请确认已设置 DEEPSEEK_API_KEY 和 SILICONFLOW_API_KEY")
    else:
        sources = [
            f"**{chunk['source']}** · {chunk['title']}（相似度 {score:+.3f}）"
            for score, chunk in top_matches
        ]
        with st.chat_message("assistant"):
            st.write(answer)
            with st.expander("📎 参考来源"):
                for s in sources:
                    st.markdown(f"- {s}")

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer,
            "sources": sources,
        })
