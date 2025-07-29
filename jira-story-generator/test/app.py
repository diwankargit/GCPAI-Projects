#imports 

from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
import vertexai
from vertexai.generative_models import GenerativeModel

api_key_path="keys/llmdemo-466101-bdc97cc1624c.json"

credentials= Credentials.from_service_account_file(api_key_path)

PROJECT_ID="llmdemo-466101"
REGION="us-east1"

vertexai.init(project=PROJECT_ID,location=REGION,credentials=credentials)

model=GenerativeModel("gemini-2.5-flash")
res=model.generate_content("What is LLM ?")
print(res.text)

## generation config 
from vertexai.generative_models import GenerationConfig

generation_config=GenerationConfig(
     temperature=0.9,
     top_p=1.0,
     top_k=32,
     candidate_count=1,
     #max_output_token=8192,
)

res=model.generate_content("Why do sunsets appear red and orange?",generation_config=generation_config)
print(res.text)