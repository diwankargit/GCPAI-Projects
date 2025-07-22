# app.py (Streamlit frontend + backend logic + RAG with GCP Vector Search)

import streamlit as st
import requests
import vertexai
from vertexai.language_models import TextEmbeddingModel
from vertexai.generative_models import GenerativeModel
from google.oauth2 import service_account
import base64
import json
import uuid
from bs4 import BeautifulSoup
import requests as req
from google.cloud import aiplatform
from google.cloud.aiplatform.matching_engine.matching_engine_index_endpoint import MatchingEngineIndexEndpoint
from google.cloud.aiplatform.matching_engine.matching_engine_index import MatchingEngineIndex
from google.cloud.aiplatform.matching_engine import MatchingEngineIndexEndpoint
from vertexai.language_models import TextEmbeddingModel
from google.cloud.aiplatform_v1 import IndexServiceClient
from google.cloud.aiplatform_v1.types import IndexDatapoint, UpsertDatapointsRequest



# --- CONFIG ---
PROJECT_ID = "llmdemo-466101"
REGION = "us-east1"
MODEL = "gemini-1.5-pro"
EMBED_MODEL = "gemini-embedding-001"
JIRA_API_URL = "https://diwankarkumar12.atlassian.net/rest/api/2/issue"
JIRA_EMAIL = "diwankarkumar12@gmail.com"
JIRA_API_TOKEN_SECRET = ""
INDEX_ENDPOINT_NAME = "projects/885301403345/locations/us-east1/indexEndpoints/5306089184019087360"
INDEX_ID = "confulence_embeddings_1753142558399"
api_key_path="/Users/bhavanakajal/Documents/GitHub/GCPAI-Projects/keys/llmdemo-466101-bdc97cc1624c.json"
ENDPOINT_ID="5306089184019087360"

# --- INIT SERVICES ---
creds = service_account.Credentials.from_service_account_file(api_key_path)
vertexai.init(project=PROJECT_ID, location=REGION, credentials=creds)
embed_model = TextEmbeddingModel.from_pretrained(EMBED_MODEL)
gen_model = GenerativeModel(MODEL)
aiplatform.init(project=PROJECT_ID, location=REGION, credentials=creds)
#index_endpoint = MatchingEngineIndexEndpoint(index_endpoint_name=INDEX_ENDPOINT_NAME)

index = MatchingEngineIndex(
    index_name="projects/PROJECT_ID/locations/us-east1/indexes/INDEX_ID"
)

index_endpoint = MatchingEngineIndexEndpoint(
    index_endpoint_name="projects/PROJECT_ID/locations/us-east1/indexEndpoints/ENDPOINT_ID"
)


# --- FUNCTIONS ---
def extract_confluence_text(url):
    try:
        res = req.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        return soup.get_text()
    except Exception:
        return ""

def chunk_text(text, max_words=200):
    words = text.split()
    return [" ".join(words[i:i + max_words]) for i in range(0, len(words), max_words)]

def embed_and_store_chunks(chunks):
    model = TextEmbeddingModel.from_pretrained(EMBED_MODEL)
    embeddings = model.get_embeddings(chunks)

    datapoints = []
    for i, chunk in enumerate(chunks):
        datapoints.append(IndexDatapoint(
            datapoint_id=f"chunk-{i}",
            feature_vector=embeddings[i].values,
            restricts=[]
        ))

    client = IndexServiceClient()
    upsert_request = UpsertDatapointsRequest(
        index=f"projects/{PROJECT_ID}/locations/{REGION}/indexes/{INDEX_ID}",
        datapoints=datapoints
    )
    client.upsert_datapoints(request=upsert_request)


def query_relevant_chunks(query, top_k=3):
    query_vec = embed_model.get_embeddings([query])[0].values
    res = index_endpoint.find_neighbors(
        deployed_index_id=INDEX_ID,
        queries=[query_vec],
        num_neighbors=top_k,
        approximate_neighbors_count=1000,
        return_full_datapoint=True
    )
    neighbors = res[0].neighbors
    return [neighbor.datapoint.metadata["text"] for neighbor in neighbors]

# --- STREAMLIT UI ---
st.title("🧠 AI + RAG Jira Story Generator (GCP)")
st.markdown("Enter your story and supporting documentation.")

story_input = st.text_input("📝 One-line User Story")
confluence_links_input = st.text_area("🔗 Confluence Page Links (one per line)", height=100)
uploaded_files = st.file_uploader("📄 Upload PDFs or Diagrams (optional)", type=["pdf", "png", "jpg", "jpeg"], accept_multiple_files=True)
generate_code = st.checkbox("💻 Generate Code")

if st.button("🚀 Generate Jira Story"):
    if not story_input:
        st.warning("Story is required!")
        st.stop()

    context_chunks = []

    # Process all Confluence links
    if confluence_links_input.strip():
        for url in confluence_links_input.strip().splitlines():
            full_text = extract_confluence_text(url.strip())
            if full_text:
                chunks = chunk_text(full_text)
                embed_and_store_chunks(chunks)
                context_chunks.extend(query_relevant_chunks(story_input))

    # Process all uploaded PDFs and images
    image_summaries = []
    for file in uploaded_files or []:
        if file.type == "application/pdf":
            pdf_reader = PdfReader(file)
            full_text = " ".join(page.extract_text() or "" for page in pdf_reader.pages)
            if full_text:
                chunks = chunk_text(full_text)
                embed_and_store_chunks(chunks)
                context_chunks.extend(query_relevant_chunks(story_input))
        else:
            content = file.read()
            base64_img = base64.b64encode(content).decode("utf-8")
            image_summaries.append(f"{file.name} (base64): {base64_img[:200]}...")

    # Construct prompt
    prompt_parts = [
        f"User Story: {story_input}",
        "\nRelevant Docs:\n" + "\n---\n".join(context_chunks) if context_chunks else "",
        "\n".join(image_summaries) if image_summaries else "",
        "\nWrite a detailed Jira story with clear acceptance criteria."
    ]

    if generate_code:
        prompt_parts.append("Also generate sample implementation code.")

    full_prompt = "\n\n".join([part for part in prompt_parts if part])

    with st.spinner("Thinking with Gemini..."):
        result = gen_model.generate_content(full_prompt)
        story_result = result.text

    st.subheader("📋 Generated Jira Story")
    st.code(story_result)

    # Create Jira issue
    with st.spinner("Creating Jira issue..."):
        headers = {
            "Authorization": "Basic " + base64.b64encode(f"{JIRA_EMAIL}:{JIRA_API_TOKEN_SECRET}".encode()).decode(),
            "Content-Type": "application/json"
        }
        payload = {
            "fields": {
                "project": {"key": "YOURPROJECTKEY"},
                "summary": story_input,
                "description": story_result,
                "issuetype": {"name": "Story"}
            }
        }
        jira_res = requests.post(JIRA_API_URL, headers=headers, json=payload)
        if jira_res.status_code == 201:
            st.success("✅ Jira ticket created!")
        else:
            st.error(f"❌ Failed to create Jira issue: {jira_res.text}")
