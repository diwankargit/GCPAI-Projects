import streamlit as st
import os
from dotenv import load_dotenv
import vertexai
#from vertexai.language_models import TextEmbeddingModel
from vertexai.preview.language_models import TextEmbeddingModel
from vertexai.generative_models import GenerativeModel
from google.oauth2 import service_account
from google.cloud import aiplatform
from google.cloud.aiplatform_v1 import IndexServiceClient
from google.cloud.aiplatform_v1.types import IndexDatapoint, UpsertDatapointsRequest
from google.cloud.aiplatform.matching_engine.matching_engine_index_endpoint import MatchingEngineIndexEndpoint
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader
import base64
import requests
import uuid
import requests
from requests.auth import HTTPBasicAuth

# --- LOAD .env ---
load_dotenv()

PROJECT_ID = os.getenv("PROJECT_ID")
REGION = os.getenv("REGION")
API_KEY_PATH = os.getenv("API_KEY_PATH")
INDEX_ID = os.getenv("INDEX_ID")
ENDPOINT_ID = os.getenv("ENDPOINT_ID")
DEPLOYED_INDEX_ID = os.getenv("DEPLOYED_INDEX_ID")
JIRA_API_URL = os.getenv("JIRA_API_URL")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY")

EMBED_MODEL = "gemini-embedding-001"
MODEL = "gemini-2.5-flash"
EXPECTED_DIM = 768
page_id=65861

# --- INIT ---
creds = service_account.Credentials.from_service_account_file(API_KEY_PATH)
vertexai.init(project=PROJECT_ID, location=REGION, credentials=creds)
aiplatform.init(project=PROJECT_ID, location=REGION, credentials=creds)
embed_model = TextEmbeddingModel.from_pretrained(EMBED_MODEL)
gen_model = GenerativeModel(MODEL)

index_endpoint = MatchingEngineIndexEndpoint(index_endpoint_name=f"projects/{PROJECT_ID}/locations/{REGION}/indexEndpoints/{ENDPOINT_ID}")

# --- FUNCTIONS ---
import re

def extract_page_id_from_url(confluence_url_or_id):
    # If it's a numeric ID already
    if confluence_url_or_id.isdigit():
        return confluence_url_or_id

    # Try to extract page ID from full Confluence URL
    match = re.search(r'/pages/(\d+)', confluence_url_or_id)
    if match:
        return match.group(1)

    return None  # Invalid format


def extract_confluence_text(page_id):
    url = f"https://diwankarkumar12.atlassian.net/wiki/rest/api/content/{page_id}?expand=body.storage"
    auth = HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)
    headers = {"Accept": "application/json"}
    response = requests.get(url, auth=auth, headers=headers)
    if response.status_code == 200:
        data = response.json()
        # The content in storage format (HTML-like)
        content_html = data['body']['storage']['value']
        soup = BeautifulSoup(content_html, "html.parser")
        return soup.get_text()
    else:
        st.error(f"Failed to fetch Confluence page content: {response.status_code} {response.text}")
        return ""

def chunk_text(text, max_words=200):
    words = text.split()
    return [" ".join(words[i:i + max_words]) for i in range(0, len(words), max_words) if words[i:i + max_words]]


from vertexai.language_models import TextEmbeddingModel

def embed_and_store_chunks(chunks):
    valid_chunks = [chunk for chunk in chunks if chunk.strip()]
    if not valid_chunks:
        st.warning("⚠️ No valid content to embed.")
        return

    model = TextEmbeddingModel.from_pretrained("text-embedding-005")

    embeddings = []
    for chunk in valid_chunks:
        try:
            embedding = model.get_embeddings(texts=[chunk])[0]  # ✅ Call one-by-one (batch size = 1)
            embeddings.append(embedding)
        except Exception as e:
            st.error(f"❌ Failed to embed chunk: {e}")
            return

    # 🔍 Check for any embedding issues
    invalid_dims = []
    for i, embed in enumerate(embeddings):
        if not embed.values or len(embed.values) != EXPECTED_DIM:
            invalid_dims.append((i, len(embed.values) if embed.values else 0))

    if invalid_dims:
        for i, dim in invalid_dims:
            st.error(f"❌ Embedding {i} has dimension {dim}, expected {EXPECTED_DIM}")
        return

    # ✅ All embeddings valid, proceed to upsert
    datapoints = [
        IndexDatapoint(
            datapoint_id=f"chunk-{uuid.uuid4()}",
            feature_vector=embed.values,
            restricts=[]
        )
        for embed in embeddings
    ]

    client = IndexServiceClient(
    client_options={"api_endpoint": "us-east1-aiplatform.googleapis.com"},
    credentials=creds
    )
    index = client.get_index(name=INDEX_ID)
    print(index)
    INDEX_ID2="projects/885301403345/locations/us-east1/indexes/4784151014313820160"
    upsert_request = UpsertDatapointsRequest(
        index=INDEX_ID2,
        datapoints=datapoints
    )

    try:
        client.upsert_datapoints(request=upsert_request)
        st.success(f"✅ Successfully upserted {len(datapoints)} datapoints.")
    except Exception as e:
        st.error(f"🚫 Failed to upsert datapoints: {e}")
    

def query_relevant_chunks(query, top_k=3):
    query_vec = embed_model.get_embeddings([query])[0].values
    return [
        neighbor.datapoint.datapoint_id
        for neighbor in index_endpoint.find_neighbors(
            deployed_index_id=DEPLOYED_INDEX_ID,
            queries=[query_vec],
            num_neighbors=top_k,
            return_full_datapoint=True,
        )[0].neighbors
    ]

# --- UI ---
st.title("Jira Story Generator with RAG")

story_input = st.text_input("📝 One-line User Story")
confluence_input = st.text_area("🔗 Confluence Links (one per line)", height=100)
uploaded_files = st.file_uploader("📎 Upload PDFs or Images", type=["pdf", "png", "jpg"], accept_multiple_files=True)
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
            page_id = extract_page_id_from_url(raw_input.strip())
            if page_id:
                raw_text = extract_confluence_text(page_id)
                chunks = chunk_text(raw_text)
                st.write("🧪 Chunks for embedding:", chunks)
                embed_and_store_chunks(chunks)
                context_chunks.extend(chunks[:3])  # Optional: tune the number of chunks used
            else:
                st.warning(f"❌ Invalid Confluence page URL or ID: {raw_input}")
        

    # Process PDFs
    for file in uploaded_files or []:
        if file.type == "application/pdf":
            pdf_reader = PdfReader(file)
            full_text = " ".join(page.extract_text() or "" for page in pdf_reader.pages)
            chunks = chunk_text(full_text)
            embed_and_store_chunks(chunks)
            context_chunks.extend(chunks[:3])

    # Final Prompt
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

    # st.subheader("📋 Generated Jira Story")
    # st.code(result_text)

    # Optional Jira Ticket Creation
    with st.spinner("Creating Jira ticket..."):
        headers = {
            "Authorization": "Basic " + base64.b64encode(f"{JIRA_EMAIL}:{JIRA_API_TOKEN}".encode()).decode(),
            "Content-Type": "application/json"
        }
        payload = {
            "fields": {
                "project": {"key": JIRA_PROJECT_KEY},
                "summary": story_input,
                "description": result_text,
                "issuetype": {"name": "Story"}
            }
        }
        res = requests.post(JIRA_API_URL, headers=headers, json=payload)
        if res.status_code == 201:
            ticket_key = res.json().get("key")
            jira_url = f"https://diwankarkumar12.atlassian.net/browse/{ticket_key}"
            st.success(f"✅ Jira story created! [View Ticket]({jira_url})")
        else:
            st.error(f"Failed to create Jira ticket: {res.text}")
