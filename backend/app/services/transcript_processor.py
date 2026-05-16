"""Meeting transcript processor service"""

import re
import uuid
from typing import Dict, Any, List
from datetime import datetime
from sqlalchemy.orm import Session
from openai import AsyncOpenAI

from app.config import settings
from app.database.models import Workspace
from app.api.schemas.responses import TranscriptAnalyzeResponse
from app.api.schemas.workspace import UserStory, EngineeringTicket


class TranscriptProcessor:
    """Service for processing meeting transcripts"""
    
    def __init__(self, db: Session):
        """Initialize transcript processor"""
        self.db = db
        # Build OpenAI client — use official API by default
        client_kwargs = {"api_key": settings.OPENAI_API_KEY}
        if settings.effective_api_base:
            client_kwargs["base_url"] = settings.effective_api_base
        self.client = AsyncOpenAI(**client_kwargs)
    
    async def process(
        self,
        transcript: str,
        context: str = None
    ) -> TranscriptAnalyzeResponse:
        """
        Process meeting transcript and extract actionable items
        
        Args:
            transcript: Meeting transcript text
            context: Additional context about the meeting
            
        Returns:
            TranscriptAnalyzeResponse with extracted data
        """
        try:
            # Create workspace
            workspace_id = str(uuid.uuid4())
            
            # Extract requirements using AI
            requirements = await self._extract_requirements(transcript, context)
            
            # Generate user stories
            user_stories = await self._generate_user_stories(transcript, requirements, context)
            
            # Generate engineering tickets
            tickets = await self._generate_tickets(transcript, requirements, user_stories, context)
            
            # Create metadata
            metadata = {
                "transcript_length": len(transcript),
                "context": context,
                "requirements_count": len(requirements),
                "user_stories_count": len(user_stories),
                "tickets_count": len(tickets),
                "processed_at": datetime.utcnow().isoformat()
            }
            
            # Create workspace
            workspace = Workspace(
                id=workspace_id,
                type="transcript",
                workspace_metadata=metadata,
                created_at=datetime.utcnow(),
                last_accessed=datetime.utcnow()
            )
            
            self.db.add(workspace)
            self.db.commit()
            
            # Format extracted data
            extracted_data = {
                "requirements": requirements,
                "user_stories": [story.dict() for story in user_stories],
                "tickets": [ticket.dict() for ticket in tickets],
                "summary": await self._generate_summary(transcript, context)
            }
            
            return TranscriptAnalyzeResponse(
                workspace_id=workspace_id,
                status="completed",
                extracted_data=extracted_data
            )
            
        except Exception as e:
            raise Exception(f"Failed to process transcript: {str(e)}")
    
    async def _extract_requirements(
        self,
        transcript: str,
        context: str = None
    ) -> List[str]:
        """Extract requirements from transcript using AI"""
        try:
            prompt = f"""Extract key requirements and features from this meeting transcript.
            
Context: {context or 'General meeting'}

Transcript:
{transcript}

List each requirement as a clear, concise statement. Focus on:
- New features to build
- Changes to existing functionality
- Technical requirements
- User needs

Format as a numbered list."""

            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a product manager extracting requirements from meeting notes."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            
            # Parse numbered list
            requirements = []
            for line in content.split('\n'):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                    # Remove numbering/bullets
                    req = re.sub(r'^[\d\.\-•\*\s]+', '', line).strip()
                    if req:
                        requirements.append(req)
            
            return requirements[:10]  # Limit to top 10
            
        except Exception as e:
            print(f"Error extracting requirements: {e}")
            return ["Error extracting requirements"]
    
    async def _generate_user_stories(
        self,
        transcript: str,
        requirements: List[str],
        context: str = None
    ) -> List[UserStory]:
        """Generate user stories from requirements"""
        try:
            req_text = "\n".join([f"- {req}" for req in requirements])
            
            prompt = f"""Convert these requirements into user stories following the format:
"As a [user type], I want [goal] so that [benefit]"

Requirements:
{req_text}

Context: {context or 'General application'}

Generate 3-5 user stories with:
- Title (user story statement)
- Description (detailed explanation)
- Acceptance criteria (3-5 bullet points)
- Priority (high/medium/low)

Format as JSON array."""

            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a product manager creating user stories."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=1500
            )
            
            content = response.choices[0].message.content
            
            # Try to parse JSON, fallback to manual parsing
            import json
            try:
                stories_data = json.loads(content)
                user_stories = []
                for story in stories_data[:5]:  # Limit to 5
                    user_stories.append(UserStory(
                        title=story.get("title", "User Story"),
                        description=story.get("description", ""),
                        acceptance_criteria=story.get("acceptance_criteria", []),
                        priority=story.get("priority", "medium"),
                        estimate=story.get("estimate", "TBD")
                    ))
                return user_stories
            except:
                # Fallback: create basic user stories from requirements
                user_stories = []
                for i, req in enumerate(requirements[:5]):
                    user_stories.append(UserStory(
                        title=f"As a user, I want {req}",
                        description=req,
                        acceptance_criteria=[
                            "Feature is implemented",
                            "Tests are passing",
                            "Documentation is updated"
                        ],
                        priority="medium",
                        estimate="TBD"
                    ))
                return user_stories
                
        except Exception as e:
            print(f"Error generating user stories: {e}")
            return []
    
    async def _generate_tickets(
        self,
        transcript: str,
        requirements: List[str],
        user_stories: List[UserStory],
        context: str = None
    ) -> List[EngineeringTicket]:
        """Generate engineering tickets from user stories"""
        try:
            stories_text = "\n".join([f"- {story.title}" for story in user_stories])
            
            prompt = f"""Create engineering tickets for these user stories:

{stories_text}

Context: {context or 'General application'}

Generate 5-8 technical tickets including:
- Feature implementation tickets
- Testing tickets
- Documentation tickets
- Infrastructure/DevOps tickets

For each ticket provide:
- Type (feature/bug/task)
- Title (clear, actionable)
- Description (technical details)
- Priority (low/medium/high/critical)
- Estimate (in days)
- Labels (tags)

Format as JSON array."""

            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a technical lead creating engineering tickets."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            
            # Try to parse JSON
            import json
            try:
                tickets_data = json.loads(content)
                tickets = []
                for ticket in tickets_data[:8]:  # Limit to 8
                    tickets.append(EngineeringTicket(
                        type=ticket.get("type", "task"),
                        title=ticket.get("title", "Engineering Task"),
                        description=ticket.get("description", ""),
                        priority=ticket.get("priority", "medium"),
                        estimate=ticket.get("estimate", "TBD"),
                        labels=ticket.get("labels", []),
                        dependencies=ticket.get("dependencies", [])
                    ))
                return tickets
            except:
                # Fallback: create basic tickets
                tickets = []
                for i, story in enumerate(user_stories[:5]):
                    tickets.append(EngineeringTicket(
                        type="feature",
                        title=f"Implement: {story.title[:50]}",
                        description=story.description,
                        priority="medium",
                        estimate="3-5 days",
                        labels=["feature", "backend"],
                        dependencies=[]
                    ))
                return tickets
                
        except Exception as e:
            print(f"Error generating tickets: {e}")
            return []
    
    async def _generate_summary(
        self,
        transcript: str,
        context: str = None
    ) -> str:
        """Generate executive summary of the meeting"""
        try:
            prompt = f"""Provide a concise executive summary of this meeting.

Context: {context or 'General meeting'}

Transcript:
{transcript[:2000]}  # Limit length

Summary should include:
- Key decisions made
- Action items
- Next steps
- Timeline (if mentioned)

Keep it under 200 words."""

            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are an executive assistant summarizing meetings."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=300
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error generating summary: {e}")
            return "Summary generation failed"

# Made with Bob
