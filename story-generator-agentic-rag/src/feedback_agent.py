# feedback_agent.py
import logging
from typing import Dict, Any
from google import genai

logger = logging.getLogger(__name__)

class FeedbackAgent:
    """
    AI-powered agent that decides what to do with feedback and executes the action.
    Possible actions:
    - approve: Keep as is
    - edit: Apply targeted feedback edits
    - regenerate: Create a fresh draft from scratch
    - reject: Flag draft as unsuitable
    """

    def __init__(self, credentials, model="gemini-1.5-flash"):
        self.client = genai.Client(credentials=credentials)
        self.model = model

    def _decide_action(self, draft: Dict[str, Any], feedback: str) -> str:
        """Decide whether to approve, edit, regenerate, or reject."""
        prompt = f"""
        You are a Jira story reviewer.
        Given the draft and feedback, decide ONLY one action:
        - "approve": Feedback is minor or not needed, keep as is.
        - "edit": Small improvements requested (add acceptance criteria, reword title, etc.)
        - "regenerate": Feedback implies a full rewrite is better.
        - "reject": Story is invalid and should not be used.

        Draft:
        Title: {draft.get("title")}
        Description: {draft.get("description")}

        Feedback: {feedback}

        Respond with just the action word.
        """

        resp = self.client.models.generate_content(
            model=self.model,
            contents=prompt
        )
        decision = resp.text.strip().lower()
        logger.info(f"FeedbackAgent decision: {decision}")
        return decision

    def _apply_edit(self, draft: Dict[str, Any], feedback: str) -> Dict[str, Any]:
        """Apply targeted edits to the draft."""
        prompt = f"""
        Edit the following Jira story based on feedback. Keep structure intact.
        Draft:
        {draft}

        Feedback: {feedback}

        Return JSON with keys: title, description.
        """

        resp = self.client.models.generate_content(
            model=self.model,
            contents=prompt
        )
        return self._safe_parse(resp.text, draft)

    def _regenerate(self, feedback: str) -> Dict[str, Any]:
        """Regenerate a fresh draft based on feedback."""
        prompt = f"""
        Generate a new Jira story from scratch. 
        Follow agile story best practices.
        Incorporate the feedback:
        {feedback}

        Return JSON with keys: title, description.
        """
        resp = self.client.models.generate_content(
            model=self.model,
            contents=prompt
        )
        return self._safe_parse(resp.text, {"title": "Untitled", "description": ""})

    def _safe_parse(self, text: str, fallback: Dict[str, Any]) -> Dict[str, Any]:
        import json
        try:
            return json.loads(text)
        except Exception:
            logger.warning("Failed to parse JSON from model, falling back.")
            return fallback

    def process_feedback(self, draft: Dict[str, Any], feedback: str) -> Dict[str, Any]:
        """Main entry: decides and executes the action."""
        action = self._decide_action(draft, feedback)

        if action == "approve":
            return {"action": "approve", "draft": draft}
        elif action == "edit":
            new_draft = self._apply_edit(draft, feedback)
            return {"action": "edit", "draft": new_draft}
        elif action == "regenerate":
            new_draft = self._regenerate(feedback)
            return {"action": "regenerate", "draft": new_draft}
        elif action == "reject":
            return {"action": "reject", "draft": None}
        else:
            return {"action": "unknown", "draft": draft}
