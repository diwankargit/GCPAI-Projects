import os
import json
import tempfile
import logging
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from src.llm import LLM
from src.store import VectorStore
from src.chunks import chunk_text_chars, chunk_code_lines
from src.ingest import load_pdf, load_text, fetch_confluence_simple, clone_repo
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

    with st.expander("Ingest Confluence page (simple)"):
        base = st.text_input("Confluence REST base URL (e.g. https://org.atlassian.net/wiki/rest/api/content)")
        pid  = st.text_input("Page ID")
        user = st.text_input("Username (email)")
        token= st.text_input("API token", type="password")
        if st.button("Fetch & ingest page"):
            try:
                res = fetch_confluence_simple(base, pid, user, token)
                chunks = chunk_text_chars(res["text"])
                metas = [{"source": f"confluence:{pid}", "title": res["meta"].get("title")} for _ in chunks]
                n = store.upsert("knowledge_docs", f"confluence:{pid}", chunks, metas)
                st.success(f"Inserted {n} chunks from Confluence page {res['meta'].get('title')}")
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

# ---------- TAB 2: Agentic RAG ----------
with tab2:
    st.header("Generate Jira Story with Agentic RAG & Feedback")

    one_liner = st.text_area("One-liner request", height=100)
    include_code = st.checkbox("Search code collection", value=False)
    code_lang = st.selectbox("Code language for examples (optional)", ["None","Python","Java","Go","JavaScript"])
    temperature = st.slider("Creativity (temperature)", 0.0, 1.0, 0.15, 0.05)

    if st.button("Generate Draft"):
        if not one_liner.strip():
            st.error("Enter a one-liner first.")
        else:
            try:
                result = agent.generate_draft(
                    one_liner=one_liner,
                    include_code=include_code,
                    temperature=temperature,
                    code_lang=None if code_lang=="None" else code_lang
                )
                st.session_state["draft"] = StoryDraft(**result["draft"])
                st.session_state["context"] = result["context"]
                st.success("Draft created. Review below.")
            except Exception as e:
                st.exception(e)

    if "context" in st.session_state:
        with st.expander("Retrieved context"):
            ctx = st.session_state["context"]
            st.write("Docs:")
            for i, d in enumerate(ctx.get("docs", []), 1):
                st.write(d["meta"])
                st.write(d["text"][:800])
            st.write("Code:")
            for i, c in enumerate(ctx.get("code", []), 1):
                st.write(c["meta"])
                st.code(c["text"][:800])

    if "draft" in st.session_state:
        st.subheader("Draft Jira Story (JSON)")
        st.json(st.session_state["draft"].model_dump())

        st.markdown("### 🔁 Reviewer feedback")
        feedback = st.text_area("Write instructions to modify the draft (e.g., make AC testable, split subtasks, add security considerations).", height=140)

        colA, colB, colC = st.columns(3)
        with colA:
            if st.button("Apply feedback (regenerate)"):
                try:
                    new_draft = agent.apply_feedback(st.session_state["draft"].model_dump(), feedback)
                    st.session_state["draft"] = StoryDraft(**new_draft)
                    st.success("Feedback applied. Draft updated.")
                except Exception as e:
                    st.exception(e)
        with colB:
            if st.button("Tighten for Jira (validation pass)"):
                try:
                    valid = agent.validate_and_fix(st.session_state["draft"].model_dump())
                    st.session_state["draft"] = StoryDraft(**valid)
                    st.success("Draft validated & tightened for Jira.")
                except Exception as e:
                    st.exception(e)
        with colC:
            create_sub = st.checkbox("Create subtasks too", value=True)
            if st.button("✅ Create Jira issue now"):
                if not jira.is_configured():
                    st.error("Jira not configured. Set env vars first.")
                else:
                    try:
                        res = jira.create_story(st.session_state["draft"].model_dump(), create_subtasks=create_sub)
                        st.success(f"Created Story: {res['story_key']}")
                        if res["subtasks"]:
                            st.info(f"Subtasks: {', '.join(res['subtasks'])}")
                        with st.expander("Jira request payload"):
                            st.code(json.dumps(res["payload"], indent=2))
                    except Exception as e:
                        st.exception(e)
