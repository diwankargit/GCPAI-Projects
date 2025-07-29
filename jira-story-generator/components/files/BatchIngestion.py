import uuid
import requests
from bs4 import BeautifulSoup
from google.cloud import aiplatform
from google.cloud.aiplatform.matching_engine.matching_engine_index_datapoint import MatchingEngineIndexDatapoint
from vertexai.language_models import TextEmbeddingModel
import time

# --- CONFIG ---
PROJECT_ID = "llmdemo-466101"
REGION = "us-east1"
MODEL = "gemini-1.5-pro"
EMBED_MODEL = "gemini-embedding-001"
INDEX_ID = "confulence_embeddings_1753142558399"
SERVICE_ACCOUNT_JSON = "/Users/bhavanakajal/Documents/GitHub/GCPAI-Projects/keys/llmdemo-466101-3acdef328b4a.json"

# Initialize clients
aiplatform.init(project=PROJECT_ID, location=REGION, credentials=aiplatform.gapic.helpers.from_service_account_file(SERVICE_ACCOUNT_JSON))
embed_model = TextEmbeddingModel.from_pretrained(EMBED_MODEL)
index_endpoint = aiplatform.MatchingEngineIndexEndpoint(index_endpoint_name=f"projects/{PROJECT_ID}/locations/{REGION}/indexEndpoints/{INDEX_ID}")

def extract_confluence_text(url):
    try:
        res = requests.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        return soup.get_text(separator=' ', strip=True)
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return ""

def chunk_text(text, max_words=200):
    words = text.split()
    return [" ".join(words[i:i + max_words]) for i in range(0, len(words), max_words)]

def embed_and_upload_chunks(chunks):
    embeddings = embed_model.get_embeddings(chunks)
    datapoints = []
    for chunk, embedding in zip(chunks, embeddings):
        dp = MatchingEngineIndexDatapoint(
            datapoint_id=str(uuid.uuid4()),
            feature_vector=embedding.values,
            metadata={"text": chunk}
        )
        datapoints.append(dp)
    # Upload in batches (if large, you can chunk here)
    index_endpoint.upsert_datapoints(deployed_index_id=INDEX_ID, datapoints=datapoints)

def batch_ingest_confluence(url_list):
    for url in url_list:
        print(f"Processing: {url}")
        text = extract_confluence_text(url)
        if text:
            chunks = chunk_text(text)
            embed_and_upload_chunks(chunks)
            print(f"Uploaded {len(chunks)} chunks for {url}")
        else:
            print(f"No content found for {url}")
        # Optional sleep to avoid rate limits
        time.sleep(1)

if __name__ == "__main__":
    # Example: load URLs from file or hardcode here
    urls = [
        "https://confluence.example.com/display/PROJECT/Page1",
        "https://confluence.example.com/display/PROJECT/Page2",
        # add more URLs
    ]
    batch_ingest_confluence(urls)
