import base64
import requests

class JiraClient:
    def __init__(self, config):
        self.config = config

    def create_story(self, summary, description):
        headers = {
            "Authorization": "Basic " + base64.b64encode(f"{self.config.JIRA_EMAIL}:{self.config.JIRA_API_TOKEN}".encode()).decode(),
            "Content-Type": "application/json"
        }
        payload = {
            "fields": {
                "project": {"key": self.config.JIRA_PROJECT_KEY},
                "summary": summary,
                "description": description,
                "issuetype": {"name": "Story"}
            }
        }
        response = requests.post(self.config.JIRA_API_URL, headers=headers, json=payload)
        if response.status_code == 201:
            return response.json().get("key")
        return None
