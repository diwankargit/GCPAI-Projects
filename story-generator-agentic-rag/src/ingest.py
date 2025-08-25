from pathlib import Path
from typing import Dict, Any, Optional
import tempfile
import requests
from PyPDF2 import PdfReader
from bs4 import BeautifulSoup
from git import Repo

def load_pdf(path: str) -> str:
    r = PdfReader(path)
    out = []
    for p in r.pages:
        out.append(p.extract_text() or "")
    return "\n\n".join(out)

def load_text(path: str) -> str:
    return Path(path).read_text(encoding="utf-8", errors="ignore")

def fetch_confluence_simple(base_url: str, page_id: str, username: str, token: str) -> Dict[str, Any]:
    url = f"{base_url.rstrip('/')}/{page_id}?expand=body.storage,version"
    resp = requests.get(url, auth=(username, token))
    resp.raise_for_status()
    data = resp.json()
    html = data.get("body", {}).get("storage", {}).get("value", "")
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text("\n")
    return {"text": text, "meta": {"title": data.get("title"), "version": data.get("version", {}).get("number")}}

def clone_repo(repo_url: str, branch: Optional[str] = None) -> Path:
    tmp = Path(tempfile.mkdtemp(prefix="repo_"))
    if branch:
        Repo.clone_from(repo_url, str(tmp), depth=1, branch=branch)
    else:
        Repo.clone_from(repo_url, str(tmp), depth=1)
    return tmp
