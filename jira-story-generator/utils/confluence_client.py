import requests
from bs4 import BeautifulSoup
from requests.auth import HTTPBasicAuth

class ConfluenceClient:
    def __init__(self, config):
        self.config = config

    def extract_page_id(self, url_or_id):
        import re
        if url_or_id.isdigit():
            return url_or_id
        match = re.search(r'/pages/(\d+)', url_or_id)
        if match:
            return match.group(1)
        return None

    def fetch_page_text(self, page_id):
        url = f"https://diwankarkumar12.atlassian.net/wiki/rest/api/content/{page_id}?expand=body.storage"
        auth = HTTPBasicAuth(self.config.JIRA_EMAIL, self.config.JIRA_API_TOKEN)
        headers = {"Accept": "application/json"}
        response = requests.get(url, auth=auth, headers=headers)
        if response.status_code == 200:
            data = response.json()
            content_html = data['body']['storage']['value']
            soup = BeautifulSoup(content_html, "html.parser")
            return soup.get_text()
        else:
            return ""