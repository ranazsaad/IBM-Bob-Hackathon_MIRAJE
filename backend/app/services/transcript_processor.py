"""Meeting transcript processor service using IBM watsonx.ai"""

import re
import uuid
from typing import Dict, Any, List
from datetime import datetime
from sqlalchemy.orm import Session

from app.config import settings
from app.database.models import Workspace
from app.api.schemas.responses import TranscriptAnalyzeResponse
from app.api.schemas.workspace import UserStory, EngineeringTicket
from app.services.ibm_watsonx_client import create_async_watsonx_client


class TranscriptProcessor:
    """Service for processing meeting transcripts using IBM Granite models"""
    
    def __init__(self, db: Session):
        """Initialize transcript processor with IBM watsonx.ai"""
        self.db = db
        # Use IBM watsonx.ai client with Granite models
        self.client = create_async_watsonx_client()
    
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
            
            # Clean transcript first (like live meeting does)
            cleaned_transcript = await self._clean_transcript(transcript)
            
            # Extract requirements using AI
            requirements = await self._extract_requirements(cleaned_transcript, context)
            
            # Generate user stories
            user_stories = await self._generate_user_stories(cleaned_transcript, requirements, context)
            
            # Generate engineering tickets
            tickets = await self._generate_tickets(cleaned_transcript, requirements, user_stories, context)
            
            # Generate summary
            summary = await self._generate_summary(cleaned_transcript, context)
            
            # Generate implementation plan (like live meeting)
            implementation_plan = await self._generate_implementation_plan(requirements, context)
            
            # Create metadata
            metadata = {
                "transcript_length": len(transcript),
                "context": context,
                "requirements_count": len(requirements),
                "user_stories_count": len(user_stories),
                "tickets_count": len(tickets),
                "processed_at": datetime.utcnow().isoformat(),
                "source": "transcript_analysis"
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
            
            # Format extracted data (matching live meeting format)
            extracted_data = {
                "cleaned_transcript": cleaned_transcript,
                "requirements": requirements,
                "user_stories": [story.dict() for story in user_stories],
                "tickets": [ticket.dict() for ticket in tickets],
                "summary": summary,
                "implementation_plan": implementation_plan
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
                model=settings.WATSONX_MODEL_ID,
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
                model=settings.WATSONX_MODEL_ID,
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
                model=settings.WATSONX_MODEL_ID,
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
                model=settings.WATSONX_MODEL_ID,
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
    
    async def _clean_transcript(self, raw: str) -> str:
        """Clean and format the transcript"""
        try:
            response = await self.client.chat.completions.create(
                model=settings.WATSONX_MODEL_ID,
                messages=[
                    {"role": "system", "content": "You are an expert transcription editor. Clean the following transcript: fix repetitions, filler words ('um', 'uh'), and obvious errors. Keep all content but make it readable. Do NOT summarize."},
                    {"role": "user", "content": raw[:6000]},
                ],
                temperature=0.2,
                max_tokens=2000,
            )
            return response.choices[0].message.content or raw
        except Exception:
            return raw
    
    async def _generate_implementation_plan(
        self,
        requirements: List[str],
        context: str = None
    ) -> Dict[str, Any]:
        """Generate technical implementation plan"""
        try:
            req_text = "\n".join([f"- {req}" for req in requirements])
            
            prompt = f"""Create a technical implementation plan for these requirements:

{req_text}

Context: {context or 'Software project'}

Generate a JSON object with:
- "architecture": recommended architecture approach
- "tech_stack": suggested technologies and frameworks
- "phases": list of implementation phases with timeline
- "risks": potential technical risks and mitigation strategies
- "team_structure": recommended team composition

Respond ONLY with valid JSON."""

            response = await self.client.chat.completions.create(
                model=settings.WATSONX_MODEL_ID,
                messages=[
                    {"role": "system", "content": "You are a technical architect. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=1500
            )
            
            content = response.choices[0].message.content or "{}"
            # Remove markdown code blocks if present
            content = re.sub(r"^```(?:json)?\s*", "", content, flags=re.MULTILINE)
            content = re.sub(r"\s*```$", "", content, flags=re.MULTILINE)
            
            import json
            try:
                return json.loads(content)
            except:
                # Fallback structure
                return {
                    "architecture": "Microservices architecture recommended",
                    "tech_stack": ["React", "Node.js", "PostgreSQL"],
                    "phases": [
                        {"phase": "Phase 1", "duration": "2-3 weeks", "tasks": ["Setup", "Core features"]},
                        {"phase": "Phase 2", "duration": "3-4 weeks", "tasks": ["Advanced features", "Testing"]}
                    ],
                    "risks": ["Timeline constraints", "Resource availability"],
                    "team_structure": "2-3 developers, 1 designer, 1 QA"
                }
                
        except Exception as e:
            print(f"Error generating implementation plan: {e}")
            return {
                "architecture": "Implementation plan generation failed",
                "tech_stack": [],
                "phases": [],
                "risks": [],
                "team_structure": ""
            }

# Made with IBM watsonx.ai
