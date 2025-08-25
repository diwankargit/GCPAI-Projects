from typing import List

def chunk_text_chars(text: str, max_chars: int = 1500, overlap: int = 200) -> List[str]:
    text = text or ""
    chunks = []
    i, n = 0, len(text)
    while i < n:
        j = min(n, i + max_chars)
        chunks.append(text[i:j])
        i = max(i + max_chars - overlap, i + 1)
    return chunks

def chunk_code_lines(text: str, max_lines: int = 180, overlap: int = 20) -> List[str]:
    lines = (text or "").splitlines()
    chunks = []
    i, n = 0, len(lines)
    while i < n:
        part = lines[i:i + max_lines]
        chunks.append("\n".join(part))
        i += max_lines - overlap
    return chunks
