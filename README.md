# 📚 AI-Powered Jira Story Generator with Vector Search

This Streamlit application lets you:
- Upload content from 📄 PDF or Confluence pages
- Split content into chunks
- Embed and deduplicate it using Google Vertex AI Matching Engine
- Use Retrieval-Augmented Generation (RAG) to generate Jira stories ✨

---

## 🚀 Features

- Upload PDF or Confluence Page
- Chunk text for semantic storage
- Embed via `text-embedding-005` Vertex AI model
- Deduplicate embeddings using Matching Engine
- Generate Jira stories using generative AI
- Two-tab UI: Ingest to DB / Generate Stories

---

## 📁 Folder Structure

jira-story-generator/
│
├── main.py # Streamlit entry point
├── .env # Environment variables (never commit this!)
├── requirements.txt # Python dependencies
│
├── utils/
│ ├── config.py # AppConfig class (loads .env and sets up Vertex AI)
│ ├── chunker.py # Text chunking logic
│ ├── vector_store.py # Handles embedding, deduplication, and upserts
│ ├── pdf_processor.py # Extracts text from uploaded PDFs
│ ├── confluence_client.py # Fetches and parses Confluence pages
│ └── jira_client.py # Sends Jira stories via REST API


