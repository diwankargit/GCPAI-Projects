from pathlib import Path
from typing import Dict, Any, Optional, List, Union
import tempfile
import requests
from PyPDF2 import PdfReader
from bs4 import BeautifulSoup
from git import Repo
import fnmatch

# -------- PDF --------
def load_pdf(path: str) -> str:
    r = PdfReader(path)
    out = []
    for p in r.pages:
        out.append(p.extract_text() or "")
    return "\n\n".join(out)

# -------- Text --------
def load_text(path: str) -> str:
    return Path(path).read_text(encoding="utf-8", errors="ignore")

# -------- Confluence: single page --------
def fetch_confluence_simple(base_url: str, page_id: str, username: str, token: str) -> Dict[str, Any]:
    url = f"{base_url.rstrip('/')}/rest/api/content/{page_id}?expand=body.storage,version"
    resp = requests.get(url, auth=(username, token))
    resp.raise_for_status()
    data = resp.json()
    html = data.get("body", {}).get("storage", {}).get("value", "")
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text("\n")
    return {
        "text": text,
        "meta": {
            "title": data.get("title"),
            "id": page_id,
            "version": data.get("version", {}).get("number")
        }
    }

# -------- Confluence: batch ingestion with regex --------
def fetch_confluence_bulk(base_url: str, parent_page_id: str, username: str, token: str, pattern: str = "*") -> List[Dict[str, Any]]:
    """
    Fetch all child pages under a parent in Confluence.
    Supports filtering with fnmatch-style regex (e.g., "*" or "Design*").
    """
    url = f"{base_url.rstrip('/')}/rest/api/content/{parent_page_id}/child/page?expand=body.storage,version"
    resp = requests.get(url, auth=(username, token))
    resp.raise_for_status()
    data = resp.json()

    results = []
    for child in data.get("results", []):
        title = child.get("title", "")
        if fnmatch.fnmatch(title, pattern):  # regex filtering
            child_id = child.get("id")
            results.append(fetch_confluence_simple(base_url, child_id, username, token))
    return results

# -------- Git Repos --------
def clone_repo(repo_url: str, branch: Optional[str] = None) -> Path:
    tmp = Path(tempfile.mkdtemp(prefix="repo_"))
    if branch:
        Repo.clone_from(repo_url, str(tmp), depth=1, branch=branch)
    else:
        Repo.clone_from(repo_url, str(tmp), depth=1)
    return tmp

# -------- Batch ingestion (files) --------
def load_files_bulk(paths: List[Union[str, Path]]) -> List[Dict[str, Any]]:
    """
    Ingest multiple files (PDF, TXT) in bulk.
    Returns list of dicts with text + metadata.
    """
    results = []
    for path in paths:
        path = Path(path)
        if path.suffix.lower() == ".pdf":
            text = load_pdf(str(path))
        else:
            text = load_text(str(path))
        results.append({"text": text, "meta": {"file": str(path)}})
    return results
