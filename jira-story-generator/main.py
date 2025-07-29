# main.py

import streamlit as st
from vertexai.generative_models import GenerativeModel

from config import AppConfig
from utils.vector_store import VectorStore
from utils.confluence_client import ConfluenceClient
from utils.pdf_processor import PDFProcessor
from utils.jira_client import JiraClient
from utils.chunker import Chunker

# Initialize config and dependencies
config = AppConfig()
vector_store = VectorStore(config)
confluence = ConfluenceClient(config)
pdf_processor = PDFProcessor()
jira = JiraClient(config)
chunker = Chunker()
gen_model = GenerativeModel("gemini-2.5-flash")

st.set_page_config(page_title="AI Story + Embedding Ingestor", layout="wide")

# --- Tabs ---
tab1, tab2 = st.tabs(["🧠 Generate Jira Story", "📚 Batch Ingestion"])


# --- UI ---
with tab1:
    st.title("Jira Story Generator with RAG")

    story_input = st.text_input("📝 One-line User Story")
    confluence_input = st.text_area("🔗 Confluence Links (one per line)", height=100)
    uploaded_files = st.file_uploader("📎 Upload PDFs", type=["pdf"], accept_multiple_files=True)
    generate_code = st.checkbox("Generate Code Snippet")

    code_languages = st.multiselect(
        "Select language(s) for sample code (optional):",
        options=["Python", "Java", "C++", "JavaScript"]
    )

    if st.button("🚀 Generate Jira Story"):
        if not story_input:
            st.warning("User story is required.")
            st.stop()

        context_chunks = []

        if confluence_input.strip():
            for raw_input in confluence_input.strip().splitlines():
                page_id = confluence.extract_page_id(raw_input.strip())
                if page_id:
                    raw_text = confluence.fetch_page_text(page_id)
                    chunks = chunker.chunk_text(raw_text)
                    vector_store.embed_and_store_chunks(chunks)
                    context_chunks.extend(chunks[:3])
                else:
                    st.warning(f"❌ Invalid Confluence page URL or ID: {raw_input}")

        pdf_chunks = pdf_processor.extract_text_chunks(uploaded_files, chunker.chunk_text)
        if pdf_chunks:
            vector_store.embed_and_store_chunks(pdf_chunks)
            context_chunks.extend(pdf_chunks[:3])

        prompt_parts = [
            f"User Story: {story_input}",
            "Relevant Documents:\n" + "\n---\n".join(context_chunks),
            "Write a detailed Jira story with clear acceptance criteria."
        ]

        if code_languages:
            lang_str = ", ".join(code_languages)
            prompt_parts.append(f"Also provide sample code implementation in the following language(s): {lang_str}.")

        final_prompt = "\n\n".join(prompt_parts)

        with st.spinner("Thinking..."):
            response = gen_model.generate_content(final_prompt)
            result_text = response.text

        st.subheader("📋 Generated Jira Story")
        st.code(result_text)

        with st.spinner("Creating Jira ticket..."):
            ticket_key = jira.create_story(story_input, result_text)
            if ticket_key:
                jira_url = f"https://diwankarkumar12.atlassian.net/browse/{ticket_key}"
                st.success(f"✅ Jira story created! [View Ticket]({jira_url})")
            else:
                st.error("❌ Failed to create Jira ticket.")
# --- Tab 2: Batch Ingestion ---
with tab2:
    st.title("📚 Batch Ingestion from Confluence URLs")

    url_input = st.text_area("Enter one or more Confluence URLs (one per line)")
    urls = [u.strip() for u in url_input.split("\n") if u.strip()]

    if st.button("🔄 Start Batch Ingestion") and urls:
        for url in urls:
            st.markdown(f"**Processing:** {url}")
            page_id = confluence.extract_page_id(url)
            if not page_id:
                st.warning(f"⚠️ Could not extract page ID from: {url}")
                continue

            content = confluence.fetch_page_text(page_id)
            if not content:
                st.warning(f"⚠️ No content fetched from: {url}")
                continue

            chunks = chunker.chunk_text(content)
            vector_store.embed_and_store_chunks(chunks)
            st.success(f"✅ Uploaded {len(chunks)} chunks for {url}")