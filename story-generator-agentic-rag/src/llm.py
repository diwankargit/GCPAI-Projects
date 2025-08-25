import logging
from typing import List, Dict, Any

from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

import vertexai
from vertexai.generative_models import GenerativeModel, SafetySetting
from vertexai.language_models import TextEmbeddingModel

logger = logging.getLogger(__name__)

class LLM:
    def __init__(self, project: str, location: str, model_name: str = "gemini-1.5-flash", embed_model: str = "text-embedding-004"):
        if not project:
            raise RuntimeError("GOOGLE_CLOUD_PROJECT not set.")
        vertexai.init(project=project, location=location or "us-central1")
        self.model_name = model_name
        self.embed_model_name = embed_model
        self.model = GenerativeModel(model_name)
        self.embed_model = TextEmbeddingModel.from_pretrained(embed_model)

        # Permissive safety settings for enterprise use
        self.safety = [
            SafetySetting(category=SafetySetting.HarmCategory.HATE_SPEECH, threshold=SafetySetting.HarmBlockThreshold.BLOCK_NONE),
            SafetySetting(category=SafetySetting.HarmCategory.HARASSMENT, threshold=SafetySetting.HarmBlockThreshold.BLOCK_NONE),
            SafetySetting(category=SafetySetting.HarmCategory.SEXUAL, threshold=SafetySetting.HarmBlockThreshold.BLOCK_NONE),
            SafetySetting(category=SafetySetting.HarmCategory.DANGEROUS, threshold=SafetySetting.HarmBlockThreshold.BLOCK_NONE),
        ]

    # -------- Embeddings --------
    @retry(
        reraise=True,
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=1, max=8),
    )
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        vectors = []
        batch_size = 32
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            res = self.embed_model.get_embeddings(batch)
            vectors.extend([r.values for r in res])
        return vectors

    # -------- Generation --------
    @retry(
        reraise=True,
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=1, max=8),
    )
    def generate(self, prompt: str, temperature: float = 0.15, max_output_tokens: int = 2048) -> str:
        resp = self.model.generate_content(
            prompt,
            generation_config={"temperature": temperature, "max_output_tokens": max_output_tokens},
            safety_settings=self.safety
        )
        return resp.text or ""

    def generate_json(self, system: str, instruction: str, temperature: float = 0.15) -> Dict[str, Any]:
        """
        Ask the model to output strictly JSON. Includes a fixer pass if JSON is invalid.
        """
        prompt = f"""You are a strictly-JSON responder. 
Return ONLY valid JSON. Do not add explanations.

SYSTEM:
{system}

TASK:
{instruction}"""
        out = self.generate(prompt, temperature=temperature)
        import json
        try:
            return json.loads(out)
        except Exception:
            try:
                first, last = out.index("{"), out.rindex("}") + 1
                return json.loads(out[first:last])
            except Exception:
                logger.error("Failed to parse JSON from model. Output was:\n%s", out)
                raise
