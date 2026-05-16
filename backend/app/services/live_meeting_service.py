"""Live Meeting Service — processes real-time speech-to-text notes from meetings"""

import uuid
import re
import json
from typing import List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from openai import AsyncOpenAI

from app.config import settings
from app.database.models import Workspace


class LiveMeetingService:
    """
    Handles live meeting transcription processing.

    The browser sends accumulated speech-recognition text to this service
    which then uses GPT to:
      1. Clean / structure the raw transcript
      2. Extract requirements
      3. Generate user stories
      4. Offer implementation suggestions
    """

    def __init__(self, db: Session):
        self.db = db
        # Bob/Cline: OpenAI-compatible API
        client_kwargs: Dict[str, Any] = {"api_key": settings.OPENAI_API_KEY}
        if settings.effective_api_base:
            client_kwargs["base_url"] = settings.effective_api_base
        self.client = AsyncOpenAI(**client_kwargs)

    # ------------------------------------------------------------------ #
    #  Public API                                                          #
    # ------------------------------------------------------------------ #

    async def process_live_notes(
        self,
        raw_notes: str,
        meeting_title: str = "Meeting",
        context: str = "",
    ) -> Dict[str, Any]:
        """
        Process raw live-transcribed notes and return structured meeting data.

        Args:
            raw_notes:      Raw transcript text from the browser SpeechRecognition API
            meeting_title:  Optional name of the meeting
            context:        Optional additional context (project name, sprint goal…)

        Returns:
            Structured dict with requirements, user stories, tickets, summary
            and implementation suggestions.
        """
        if not raw_notes or not raw_notes.strip():
            return self._empty_result(meeting_title)

        # Run all AI tasks concurrently (sequential is fine for MVP)
        cleaned      = await self._clean_transcript(raw_notes)
        requirements = await self._extract_requirements(cleaned, context)
        user_stories = await self._generate_user_stories(requirements, context)
        tickets      = await self._generate_tickets(user_stories, context)
        summary      = await self._generate_summary(cleaned, context)
        impl_plan    = await self._generate_implementation_plan(requirements, context)

        # Persist workspace so the user can query it with AI modes later
        workspace_id = str(uuid.uuid4())
        metadata = {
            "meeting_title": meeting_title,
            "context": context,
            "requirements_count": len(requirements),
            "processed_at": datetime.utcnow().isoformat(),
            "source": "live_meeting",
        }
        workspace = Workspace(
            id=workspace_id,
            type="transcript",
            workspace_metadata=metadata,
            created_at=datetime.utcnow(),
            last_accessed=datetime.utcnow(),
        )
        self.db.add(workspace)
        self.db.commit()

        return {
            "workspace_id": workspace_id,
            "meeting_title": meeting_title,
            "cleaned_transcript": cleaned,
            "requirements": requirements,
            "user_stories": user_stories,
            "tickets": tickets,
            "summary": summary,
            "implementation_plan": impl_plan,
            "processed_at": metadata["processed_at"],
        }

    async def get_quick_insights(self, partial_notes: str) -> Dict[str, Any]:
        """
        Fast, lightweight analysis for real-time feedback while the meeting
        is still in progress (called periodically by the frontend).
        """
        if len(partial_notes.strip()) < 50:
            return {"insights": [], "key_topics": [], "action_items": []}

        prompt = f"""Analyze this partial meeting transcript and return JSON with:
- "key_topics": list of 3-5 main topics discussed so far
- "action_items": list of concrete actions mentioned
- "insights": list of 2-3 brief AI observations

Transcript so far:
{partial_notes[-3000:]}

Respond ONLY with valid JSON, no extra text."""

        try:
            response = await self.client.chat.completions.create(
                model=settings.WATSONX_MODEL_ID,
                messages=[
                    {"role": "system", "content": "You are a meeting analysis assistant. Always respond with valid JSON only."},
                    {"role": "user",   "content": prompt},
                ],
                temperature=0.3,
                max_tokens=600,
            )
            content = response.choices[0].message.content or "{}"
            # Strip markdown code fences if present
            content = re.sub(r"^```(?:json)?\s*", "", content, flags=re.MULTILINE)
            content = re.sub(r"\s*```$", "", content, flags=re.MULTILINE)
            return json.loads(content)
        except Exception as e:
            print(f"[LiveMeeting] quick_insights error: {e}")
            return {"insights": [], "key_topics": [], "action_items": []}

    # ------------------------------------------------------------------ #
    #  Private helpers                                                     #
    # ------------------------------------------------------------------ #

    async def _clean_transcript(self, raw: str) -> str:
        """Remove repetitions / filler words from raw STT output."""
        try:
            response = await self.client.chat.completions.create(
                model=settings.WATSONX_MODEL_ID,
                messages=[
                    {"role": "system", "content": "You are an expert transcription editor. Clean the following raw speech-to-text output: fix repetitions, filler words ('um', 'uh'), and obvious errors. Keep all content but make it readable. Do NOT summarise."},
                    {"role": "user",   "content": raw[:6000]},
                ],
                temperature=0.2,
                max_tokens=2000,
            )
            return response.choices[0].message.content or raw
        except Exception:
            return raw

    async def _extract_requirements(self, transcript: str, context: str) -> List[str]:
        """Extract clear, actionable requirements from transcript."""
        try:
            prompt = f"""Extract ALL software requirements and features discussed in this meeting transcript.

Context: {context or 'Software project meeting'}

Transcript:
{transcript[:5000]}

Return a numbered list of clear, concrete requirements. Focus on:
- Features to build
- Changes to existing functionality
- Technical constraints
- User needs and pain points
Format each as a single, actionable sentence."""

            response = await self.client.chat.completions.create(
                model=settings.WATSONX_MODEL_ID,
                messages=[
                    {"role": "system", "content": "You are a senior product manager extracting requirements from meeting notes."},
                    {"role": "user",   "content": prompt},
                ],
                temperature=0.3,
                max_tokens=1200,
            )
            content = response.choices[0].message.content or ""
            reqs = []
            for line in content.split("\n"):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith(("-", "•", "*"))):
                    req = re.sub(r"^[\d\.\-•\*\s]+", "", line).strip()
                    if req:
                        reqs.append(req)
            return reqs[:15]
        except Exception as e:
            print(f"[LiveMeeting] extract_requirements error: {e}")
            return []

    async def _generate_user_stories(self, requirements: List[str], context: str) -> List[Dict[str, Any]]:
        """Convert requirements to user stories."""
        if not requirements:
            return []
        try:
            req_text = "\n".join(f"- {r}" for r in requirements)
            prompt = f"""Convert these requirements into user stories.

Requirements:
{req_text}

Context: {context or 'Software project'}

Generate 4-6 user stories as a JSON array where each object has:
- "title": "As a [user], I want [goal] so that [benefit]"
- "description": detailed explanation
- "acceptance_criteria": list of 3-4 testable criteria
- "priority": "high" | "medium" | "low"
- "estimate": story points as string

Respond ONLY with the JSON array."""

            response = await self.client.chat.completions.create(
                model=settings.WATSONX_MODEL_ID,
                messages=[
                    {"role": "system", "content": "You are a product manager. Always respond with valid JSON only."},
                    {"role": "user",   "content": prompt},
                ],
                temperature=0.5,
                max_tokens=1800,
            )
            content = response.choices[0].message.content or "[]"
            content = re.sub(r"^```(?:json)?\s*", "", content, flags=re.MULTILINE)
            content = re.sub(r"\s*```$", "", content, flags=re.MULTILINE)
            stories = json.loads(content)
            return stories[:6] if isinstance(stories, list) else []
        except Exception as e:
            print(f"[LiveMeeting] generate_user_stories error: {e}")
            return []

    async def _generate_tickets(self, user_stories: List[Dict], context: str) -> List[Dict[str, Any]]:
        """Generate engineering tickets from user stories."""
        if not user_stories:
            return []
        try:
            stories_text = "\n".join(f"- {s.get('title', '')}" for s in user_stories)
            prompt = f"""Create engineering tickets for these user stories:

{stories_text}

Context: {context or 'Software project'}

Generate 5-8 technical implementation tickets as a JSON array where each object has:
- "type": "feature" | "bug" | "task" | "chore"
- "title": clear, actionable title
- "description": technical implementation details
- "priority": "critical" | "high" | "medium" | "low"
- "estimate": e.g. "2-3 days"
- "labels": list of tags
- "suggested_files": list of files/modules likely to be changed

Respond ONLY with the JSON array."""

            response = await self.client.chat.completions.create(
                model=settings.WATSONX_MODEL_ID,
                messages=[
                    {"role": "system", "content": "You are a tech lead. Always respond with valid JSON only."},
                    {"role": "user",   "content": prompt},
                ],
                temperature=0.4,
                max_tokens=2000,
            )
            content = response.choices[0].message.content or "[]"
            content = re.sub(r"^```(?:json)?\s*", "", content, flags=re.MULTILINE)
            content = re.sub(r"\s*```$", "", content, flags=re.MULTILINE)
            tickets = json.loads(content)
            return tickets[:8] if isinstance(tickets, list) else []
        except Exception as e:
            print(f"[LiveMeeting] generate_tickets error: {e}")
            return []

    async def _generate_summary(self, transcript: str, context: str) -> str:
        """Generate a concise meeting summary."""
        try:
            response = await self.client.chat.completions.create(
                model=settings.WATSONX_MODEL_ID,
                messages=[
                    {"role": "system", "content": "You are an executive assistant writing concise meeting summaries."},
                    {"role": "user",   "content": f"""Summarise this meeting in under 200 words.
Include: key decisions, action items, next steps, and any blockers mentioned.

Context: {context or 'Software project meeting'}

Transcript:
{transcript[:4000]}"""},
                ],
                temperature=0.3,
                max_tokens=400,
            )
            return response.choices[0].message.content or "Summary unavailable."
        except Exception as e:
            print(f"[LiveMeeting] generate_summary error: {e}")
            return "Summary generation failed."

    async def _generate_implementation_plan(
        self, requirements: List[str], context: str
    ) -> Dict[str, Any]:
        """Generate a high-level implementation plan and ask if user wants to implement."""
        if not requirements:
            return {}
        try:
            req_text = "\n".join(f"- {r}" for r in requirements[:8])
            prompt = f"""Based on these requirements, create a concise implementation plan as JSON with:
- "phases": list of objects with "name", "duration", "tasks" (list)
- "tech_stack": recommended technologies list
- "complexity": "low" | "medium" | "high"
- "estimated_total": total time estimate string
- "quick_wins": list of 2-3 things that can be implemented quickly (1-2 days)

Requirements:
{req_text}

Context: {context or 'Software project'}

Respond ONLY with valid JSON."""

            response = await self.client.chat.completions.create(
                model=settings.WATSONX_MODEL_ID,
                messages=[
                    {"role": "system", "content": "You are a software architect. Always respond with valid JSON only."},
                    {"role": "user",   "content": prompt},
                ],
                temperature=0.4,
                max_tokens=1200,
            )
            content = response.choices[0].message.content or "{}"
            content = re.sub(r"^```(?:json)?\s*", "", content, flags=re.MULTILINE)
            content = re.sub(r"\s*```$", "", content, flags=re.MULTILINE)
            return json.loads(content)
        except Exception as e:
            print(f"[LiveMeeting] generate_implementation_plan error: {e}")
            return {}

    def _empty_result(self, meeting_title: str) -> Dict[str, Any]:
        return {
            "workspace_id": None,
            "meeting_title": meeting_title,
            "cleaned_transcript": "",
            "requirements": [],
            "user_stories": [],
            "tickets": [],
            "summary": "No content captured yet.",
            "implementation_plan": {},
            "processed_at": datetime.utcnow().isoformat(),
        }
