import hashlib
import uuid
import streamlit as st
from google.cloud.aiplatform_v1 import IndexServiceClient
from google.cloud.aiplatform_v1.types import IndexDatapoint, UpsertDatapointsRequest
from vertexai.language_models import TextEmbeddingModel

class VectorStore:
    def __init__(self, config):
        self.config = config
        self.client = IndexServiceClient(
            client_options={"api_endpoint": f"{self.config.REGION}-aiplatform.googleapis.com"},
            credentials=self.config.credentials
        )
        self.index = self.client.get_index(name=self.config.INDEX_ID)
        self.embed_model = TextEmbeddingModel.from_pretrained("text-embedding-005")

    def _hash_text(self, text):
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def _get_existing_ids(self, query_vectors):
        from  google.cloud.aiplatform.matching_engine import MatchingEngineIndexEndpoint 

        index_endpoint = MatchingEngineIndexEndpoint(
            index_endpoint_name=f"projects/{self.config.PROJECT_ID}/locations/{self.config.REGION}/indexEndpoints/{self.config.ENDPOINT_ID}"
        )

        existing_ids = set()
        for vec in query_vectors:
            results = index_endpoint.find_neighbors(
            deployed_index_id=self.config.DEPLOYED_INDEX_ID,
            queries=[vec],
            num_neighbors=1,
            return_full_datapoint=True,
        )
            if not results:
                continue  # No results returned, skip

            first_result = results[0]

            if not hasattr(first_result, "neighbors") or not first_result.neighbors:
                continue  # No neighbors found, skip

            for neighbor in first_result.neighbors:
            # adjust the threshold for "distance" depending on similarity metric
                if hasattr(neighbor, 'distance') and neighbor.distance < 0.001:
                    existing_ids.add(neighbor.datapoint.datapoint_id)
        return existing_ids

    def embed_and_store_chunks(self, chunks):
        valid_chunks = [chunk for chunk in chunks if chunk.strip()]
        if not valid_chunks:
            st.warning("⚠️ No valid content to embed.")
            return

        embeddings = []
        for chunk in valid_chunks:
            try:
                embedding = self.embed_model.get_embeddings(texts=[chunk])[0]
                embeddings.append((chunk, embedding))
            except Exception as e:
                st.error(f"❌ Failed to embed chunk: {e}")
                return

        query_vectors = [e[1].values for e in embeddings]
        existing_ids = self._get_existing_ids(query_vectors)

        datapoints = []
        for chunk, embed in embeddings:
            vector_id = self._hash_text(chunk)
            if vector_id in existing_ids:
                continue

            if not embed.values or len(embed.values) != self.config.EXPECTED_DIM:
                st.error(f"❌ Invalid embedding dimension for chunk: '{chunk[:30]}...'")
                continue

            datapoints.append(
                IndexDatapoint(
                    datapoint_id=vector_id,
                    feature_vector=embed.values,
                    restricts=[]
                )
            )

        if not datapoints:
            st.info("ℹ️ No new datapoints to insert (all are duplicates).")
            return

        upsert_request = UpsertDatapointsRequest(
            index=self.config.INDEX_ID,
            datapoints=datapoints
        )

        try:
            self.client.upsert_datapoints(request=upsert_request)
            st.success(f"✅ Successfully upserted {len(datapoints)} new datapoints.")
        except Exception as e:
            st.error(f"🚫 Failed to upsert datapoints: {e}")