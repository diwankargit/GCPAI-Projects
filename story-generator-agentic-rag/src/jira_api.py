import json
from typing import Dict, List, Tuple
import requests

def _adf_paragraph(text: str) -> dict:
    return {"type":"paragraph","content":[{"type":"text","text": text or ""}]}

def _adf_bullet_list(items: List[str]) -> dict:
    return {"type":"bulletList","content":[{"type":"listItem","content":[{"type":"paragraph","content":[{"type":"text","text":i}]}]} for i in items]}

def build_adf(description: str, acceptance: List[str]) -> dict:
    content = []
    for para in (description or "").split("\n"):
        if para.strip():
            content.append(_adf_paragraph(para.strip()))
    if acceptance:
        content.append({"type":"heading","attrs":{"level":3},"content":[{"type":"text","text":"Acceptance Criteria"}]})
        content.append(_adf_bullet_list(acceptance))
    return {"type":"doc","version":1,"content":content}

class JiraClient:
    def __init__(self, base_url: str, email: str, api_token: str, project_key: str):
        self.base = (base_url or "").rstrip("/")
        self.email = email
        self.token = api_token
        self.project = project_key

    def is_configured(self) -> bool:
        return all([self.base, self.email, self.token, self.project])

    def _headers(self) -> Dict[str,str]:
        return {"Accept":"application/json","Content-Type":"application/json"}

    def _auth(self) -> Tuple[str,str]:
        return (self.email, self.token)

    def create_story(self, story_json: Dict, create_subtasks: bool = True) -> Dict:
        title = story_json.get("title") or "Auto-generated Story"
        desc = story_json.get("description") or ""
        ac   = story_json.get("acceptance_criteria") or []
        subs = story_json.get("subtasks") or []

        payload = {
            "fields": {
                "project": {"key": self.project},
                "summary": title,
                "issuetype": {"name": "Story"},
                "description": build_adf(desc, ac)
            }
        }
        url = f"{self.base}/rest/api/3/issue"
        r = requests.post(url, auth=self._auth(), headers=self._headers(), data=json.dumps(payload))
        if r.status_code not in (200, 201):
            raise RuntimeError(f"Jira create failed: {r.status_code} {r.text}")
        story = r.json()
        story_key = story.get("key")

        created_subtasks = []
        if create_subtasks and subs:
            for s in subs:
                sp = {
                    "fields": {
                        "project": {"key": self.project},
                        "summary": s if isinstance(s, str) else str(s),
                        "issuetype": {"name": "Sub-task"},
                        "parent": {"key": story_key},
                    }
                }
                rs = requests.post(url, auth=self._auth(), headers=self._headers(), data=json.dumps(sp))
                if rs.status_code in (200, 201):
                    created_subtasks.append(rs.json().get("key"))
                else:
                    created_subtasks.append(f"ERROR:{rs.status_code}")

        return {"story_key": story_key, "subtasks": created_subtasks, "payload": payload}
