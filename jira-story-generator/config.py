import os
from dotenv import load_dotenv
from google.oauth2 import service_account
import vertexai
from google.cloud import aiplatform

class AppConfig:
    def __init__(self):
        load_dotenv()

        self.PROJECT_ID = os.getenv("PROJECT_ID")
        self.REGION = os.getenv("REGION")
        self.API_KEY_PATH = os.getenv("API_KEY_PATH")
        self.INDEX_ID = os.getenv("INDEX_ID")
        self.ENDPOINT_ID = os.getenv("ENDPOINT_ID")
        self.DEPLOYED_INDEX_ID = os.getenv("DEPLOYED_INDEX_ID")
        self.JIRA_API_URL = os.getenv("JIRA_API_URL")
        self.JIRA_EMAIL = os.getenv("JIRA_EMAIL")
        self.JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
        self.JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY")
        self.EXPECTED_DIM = 768

        self.credentials = service_account.Credentials.from_service_account_file(self.API_KEY_PATH)

        vertexai.init(project=self.PROJECT_ID, location=self.REGION, credentials=self.credentials)
        aiplatform.init(project=self.PROJECT_ID, location=self.REGION, credentials=self.credentials)