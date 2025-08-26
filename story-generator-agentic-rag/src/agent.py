import json
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field, validator

from .llm import LLM
from .store import VectorStore

SYSTEM_JSON_SPEC = """
You are an expert Product Owner & Tech Lead. 
You must always output valid JSON for Jira story drafts with keys:
- title: string
- description: string
- acceptance_criteria: array of strings
- subtasks: array of strings
No extra keys.
"""

class StoryDraft(BaseModel):
    title: str = Field(..., min_length=3)
    description: str = Field(..., min_length=10)
    acceptance_criteria: List[str] = Field(default_factory=list)
    subtasks: List[str] = Field(default_factory=list)

    @validator("acceptance_criteria", "subtasks", each_item=True)
    def non_empty(cls, v):
        if isinstance(v, str) and not v.strip():
            raise ValueError("list item must not be empty")
        return v


class AgenticRAG:
    def __init__(self, llm: LLM, store: VectorStore):
        self.llm = llm
        self.store = store

    def _retrieve(self, query: str, include_code: bool, k_docs: int = 6, k_code: int = 4) -> Dict[str, Any]:
        ctx = {"docs": [], "code": []}
        ctx["docs"] = self.store.query("knowledge_docs", query, k=k_docs)
        if include_code:
            ctx["code"] = self.store.query("code_base", query, k=k_code)
        return ctx

    def _context_to_text(self, ctx: Dict[str, Any]) -> str:
        parts = []
        for d in ctx.get("docs", []):
            parts.append(f"[DOC] {d['meta']} :: {d['text']}")
        for c in ctx.get("code", []):
            parts.append(f"[CODE] {c['meta']} ::\n{c['text']}")
        return "\n\n".join(parts)

    def generate_draft(
        self, 
        one_liner: str, 
        include_code: bool, 
        temperature: float = 0.15, 
        code_lang: Optional[str] = None
    ) -> Dict[str, Any]:
        ctx = self._retrieve(one_liner, include_code)
        ctx_text = self._context_to_text(ctx)
        instruction = f"""
Using the following user request and retrieved context, generate a Jira story JSON.

USER REQUEST:
{one_liner}

RETRIEVED CONTEXT:
{ctx_text}

RULES:
- Output strictly JSON with keys: title, description, acceptance_criteria (array), subtasks (array).
- Description should reference the most relevant contextual details.
- Make acceptance criteria testable and unambiguous (Given/When/Then if helpful).
- Subtasks should reflect the actual steps to deliver (breakdown by FE/BE/QA/Docs if appropriate).
{"- Include a small code example in " + code_lang + " within the description." if code_lang else ""}
        """.strip()

        raw = self.llm.generate_json(system=SYSTEM_JSON_SPEC, instruction=instruction, temperature=temperature)
        draft = StoryDraft(**raw)  # validate
        return {"draft": draft.model_dump(), "context": ctx}

    def apply_feedback(
        self, 
        current_draft: Dict[str, Any], 
        feedback: str, 
        temperature: float = 0.15
    ) -> Dict[str, Any]:
        instruction = f"""
Revise the following Jira story JSON according to the feedback. Keep the same schema and output strictly JSON.

CURRENT_JSON:
{json.dumps(current_draft, ensure_ascii=False, indent=2)}

FEEDBACK:
{feedback}
        """.strip()
        out = self.llm.generate_json(system=SYSTEM_JSON_SPEC, instruction=instruction, temperature=temperature)
        return StoryDraft(**out).model_dump()

    def validate_and_fix(self, draft: Dict[str, Any]) -> Dict[str, Any]:
        instruction = f"""
You are a Jira story validator. Ensure the JSON has keys: title, description, acceptance_criteria (array), subtasks (array).
- If something is missing or weak, improve it briefly.
- Keep it concise and enterprise-ready. Output strictly JSON.
CURRENT_JSON:
{json.dumps(draft, ensure_ascii=False, indent=2)}
        """
        out = self.llm.generate_json(system=SYSTEM_JSON_SPEC, instruction=instruction, temperature=0.1)
        return StoryDraft(**out).model_dump()

    def refine_with_feedback_loop(
        self, 
        one_liner: str, 
        feedbacks: List[str], 
        include_code: bool = False, 
        code_lang: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Full loop:
        1. Generate initial draft
        2. Apply feedback iteratively
        3. Validate & return final draft
        """
        result = self.generate_draft(one_liner, include_code, code_lang=code_lang)
        draft = result["draft"]

        for fb in feedbacks:
            draft = self.apply_feedback(draft, fb)

        final_draft = self.validate_and_fix(draft)
        return {"final_draft": final_draft, "context": result["context"]}
