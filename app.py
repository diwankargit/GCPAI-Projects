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

