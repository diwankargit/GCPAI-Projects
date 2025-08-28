import os
import json
import tempfile
import logging
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from streamlit_extras.colored_header import colored_header
from streamlit_extras.stylable_container import stylable_container
from streamlit_extras.let_it_rain import rain

from src.llm import LLM
from src.store import VectorStore
from src.chunks import chunk_text_chars, chunk_code_lines
from src.ingest import load_pdf, load_text, fetch_confluence_simple, clone_repo, fetch_confluence_bulk
from src.agent import AgenticRAG, StoryDraft
from src.jira_api import JiraClient

# ---------- Bootstrap ----------
load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
CHROMA_PATH = os.getenv("CHROMA_PATH", "./chroma_data")

JIRA_BASE_URL = os.getenv("JIRA_BASE_URL", "").rstrip("/")
JIRA_EMAIL = os.getenv("JIRA_EMAIL", "")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN", "")
JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY", "")

# Initialize core services (GCP ONLY)
llm = LLM(project=PROJECT, location=LOCATION, model_name="gemini-1.5-flash", embed_model="text-embedding-004")
store = VectorStore(persist_path=CHROMA_PATH, embedder=llm.embed_texts)
agent = AgenticRAG(llm=llm, store=store)
jira = JiraClient(JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN, JIRA_PROJECT_KEY)

st.set_page_config(page_title="Agentic RAG Jira Generator", layout="wide")
st.title("🧠 Agentic RAG Jira Generator (Vertex AI + Chroma + Jira)")

tab1, tab2 = st.tabs(["📥 Batch Ingestion", "📝 Story Generator"])

# ---------- TAB 1: Ingestion ----------

with tab1:
    st.header("Batch Ingestion")

    with st.expander("Upload files (pdf, txt, md, code)"):
        files = st.file_uploader("Upload multiple files", accept_multiple_files=True)
        if st.button("Ingest uploaded files"):
            if not files:
                st.warning("Upload at least one file.")
            else:
                total = 0
                for f in files:
                    tmp = tempfile.NamedTemporaryFile(delete=False)
                    tmp.write(f.read()); tmp.flush(); tmp.close()
                    name = f.name.lower()

                    try:
                        if name.endswith(".pdf"):
                            text = load_pdf(tmp.name)
                            chunks = chunk_text_chars(text)
                            metas = [{"source": f.name, "type": "pdf"} for _ in chunks]
                            total += store.upsert("knowledge_docs", f"pdf:{f.name}", chunks, metas)
                        else:
                            text = load_text(tmp.name)
                            if any(name.endswith(ext) for ext in [".py",".js",".ts",".java",".go",".cpp",".c",".rb",".cs"]):
                                chunks = chunk_code_lines(text)
                                metas = [{"source": f.name, "type": "code"} for _ in chunks]
                                total += store.upsert("code_base", f"code:{f.name}", chunks, metas)
                            else:
                                chunks = chunk_text_chars(text)
                                metas = [{"source": f.name, "type": "text"} for _ in chunks]
                                total += store.upsert("knowledge_docs", f"text:{f.name}", chunks, metas)
                        st.success(f"Ingested {f.name}")
                    except Exception as e:
                        st.exception(e)
                st.info(f"Total chunks inserted: {total}")

    with st.expander("Ingest Confluence page(s)"):
        base = st.text_input("Confluence REST base URL (e.g. https://org.atlassian.net/wiki/rest/api/content)")
        user = st.text_input("Username (email)")
        token= st.text_input("API token", type="password")

        st.subheader("Single Page Ingest")
        pid  = st.text_input("Page ID (single)")
        if st.button("Fetch & ingest page"):
            try:
                res = fetch_confluence_simple(base, pid, user, token)
                chunks = chunk_text_chars(res["text"])
                metas = [{"source": f"confluence:{pid}", "title": res["meta"].get("title")} for _ in chunks]
                n = store.upsert("knowledge_docs", f"confluence:{pid}", chunks, metas)
                st.success(f"Inserted {n} chunks from Confluence page {res['meta'].get('title')}")
            except Exception as e:
                st.exception(e)

        st.subheader("Bulk Ingest (all child pages)")
        parent_pid = st.text_input("Parent Page ID (for bulk ingest)")
        pattern = st.text_input("Page title filter (e.g. *, Design*, API*)", value="*")
        if st.button("Fetch & ingest all child pages"):
            try:
                pages = fetch_confluence_bulk(base, parent_pid, user, token, pattern=pattern)
                total = 0
                for page in pages:
                    pid = page["meta"]["id"]
                    chunks = chunk_text_chars(page["text"])
                    metas = [{"source": f"confluence:{pid}", "title": page["meta"].get("title")} for _ in chunks]
                    total += store.upsert("knowledge_docs", f"confluence:{pid}", chunks, metas)
                    st.success(f"Ingested {len(chunks)} chunks from {page['meta'].get('title')}")
                st.info(f"Total chunks inserted from bulk Confluence ingest: {total}")
            except Exception as e:
                st.exception(e)


    with st.expander("Clone GitHub repo and ingest (public)"):
        repo_url = st.text_input("GitHub repo URL (https://github.com/owner/repo)")
        branch   = st.text_input("Branch (optional)")
        if st.button("Clone & ingest repo"):
            try:
                path = clone_repo(repo_url, branch or None)
                code_cnt, doc_cnt = 0, 0
                for p in Path(path).rglob("*"):
                    if p.is_file():
                        ext = p.suffix.lower()
                        if ext in {".png",".jpg",".jpeg",".gif",".pdf",".exe",".class",".zip",".bin"}:
                            continue
                        try:
                            txt = p.read_text(encoding="utf-8", errors="ignore")
                        except Exception:
                            continue
                        if ext in {".py",".java",".js",".ts",".go",".cpp",".c",".rb",".cs"}:
                            chunks = chunk_code_lines(txt)
                            metas = [{"source": str(p), "repo": repo_url, "path": str(p.relative_to(path))} for _ in chunks]
                            code_cnt += store.upsert("code_base", f"repo:{Path(path).name}", chunks, metas)
                        else:
                            chunks = chunk_text_chars(txt)
                            metas = [{"source": str(p), "repo": repo_url} for _ in chunks]
                            doc_cnt += store.upsert("knowledge_docs", f"repo:{Path(path).name}", chunks, metas)
                st.success(f"Ingested {code_cnt} code chunks, {doc_cnt} doc chunks.")
            except Exception as e:
                st.exception(e)

    with st.expander("Collections & sanity check"):
        cols = store.list_collections()
        st.write("Collections:", cols)
        q = st.text_input("Sample retrieval query", value="login with OAuth2")
        if st.button("Test retrieval"):
            docs = store.query("knowledge_docs", q, k=3)
            code = store.query("code_base", q, k=3)
            st.write("Docs:", [d["text"][:300] for d in docs])
            st.write("Code:", [d["text"][:300] for d in code])

# ---------- TAB 2: Agentic RAG----------

with tab1:
    with st.tab("Jira Story Generator"):
        st.header("AI-Powered Jira Story Generator")

        st.write("Provide a feature, bug, or task and let AI generate the Jira story.")

        one_liner = st.text_area(
            "Describe your feature/bug/task",
            placeholder="E.g., Create login with OAuth2, enhance search with filters, fix checkout bug...",
            height=120,
        )

        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"])
        with col2:
            story_type = st.selectbox("Type", ["Story", "Bug", "Task", "Epic"])
        with col3:
            generate_btn = st.button("Generate Jira Story", use_container_width=True)

        if generate_btn and one_liner.strip():
            with st.spinner("Generating with AI..."):
                try:
                    result = agent.generate_draft(
                        one_liner=one_liner,
                        include_code=False,
                        temperature=0.2,
                        code_lang=None,
                    )
                    st.session_state["draft"] = StoryDraft(**result["draft"])
                    st.session_state["context"] = result["context"]
                    st.success("Draft created. Review below.")
                except Exception as e:
                    st.exception(e)

        if "draft" in st.session_state:
            st.subheader("Generated Jira Story")

            draft = st.session_state["draft"]
            st.markdown(f"### {draft.title}")
            st.markdown(draft.description)
            st.markdown(f"**Priority:** {priority}  |  **Type:** {story_type}")

            st.write("")
            feedback_col1, feedback_col2 = st.columns(2)
            with feedback_col1:
                if st.button("Approve", use_container_width=True):
                    st.success("Story approved and ready to push to Jira.")

            with feedback_col2:
                feedback = st.text_area("Request Edit", height=120, placeholder="E.g., Add acceptance criteria for edge cases...")
                if st.button("Apply Feedback", use_container_width=True):
                    try:
                        new_draft = agent.apply_feedback(draft.model_dump(), feedback)
                        st.session_state["draft"] = StoryDraft(**new_draft)
                        st.success("Feedback applied. Draft updated.")
                    except Exception as e:
                        st.exception(e)

            if st.button("Create Jira Issue"):
                if not jira.is_configured():
                    st.error("Jira not configured. Set env vars first.")
                else:
                    try:
                        res = jira.create_story(draft.model_dump(), create_subtasks=True)
                        st.success(f"Created Story: {res['story_key']}")
                        if res["subtasks"]:
                            st.info(f"Subtasks: {', '.join(res['subtasks'])}")
                        with st.expander("Jira request payload"):
                            st.code(json.dumps(res["payload"], indent=2))
                    except Exception as e:
                        st.exception(e)
