"""Analysis endpoints for GitHub and transcripts"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.api.schemas.requests import GitHubAnalyzeRequest, TranscriptAnalyzeRequest
from app.api.schemas.responses import GitHubAnalyzeResponse, TranscriptAnalyzeResponse
from app.services.github_analyzer import GitHubAnalyzer
from app.services.transcript_processor import TranscriptProcessor

router = APIRouter()


@router.post("/github", response_model=GitHubAnalyzeResponse)
async def analyze_github_repo(
    request: GitHubAnalyzeRequest,
    db: Session = Depends(get_db)
):
    """
    Analyze a GitHub repository
    
    - Fetches repository metadata
    - Indexes file structure
    - Extracts key files
    - Stores in vector database
    """
    try:
        analyzer = GitHubAnalyzer(db)
        result = await analyzer.analyze(
            repo_url=str(request.repo_url),
            branch=request.branch,
            depth=request.depth
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/transcript", response_model=TranscriptAnalyzeResponse)
async def analyze_transcript(
    request: TranscriptAnalyzeRequest,
    db: Session = Depends(get_db)
):
    """
    Analyze a meeting transcript
    
    - Extracts requirements
    - Generates user stories
    - Creates engineering tickets
    - Produces implementation plan
    """
    try:
        processor = TranscriptProcessor(db)
        result = await processor.process(
            transcript=request.transcript,
            context=request.context
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Made with Bob
