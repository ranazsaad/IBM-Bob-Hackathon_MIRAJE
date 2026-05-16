"""AI mode endpoints"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.api.schemas.requests import ModeQueryRequest
from app.api.schemas.responses import ModeQueryResponse
from app.services.ai_orchestrator import AIOrchestrator

router = APIRouter()


@router.post("/illustration/query", response_model=ModeQueryResponse)
async def illustration_mode_query(
    request: ModeQueryRequest,
    db: Session = Depends(get_db)
):
    """
    Illustration Mode: Generate visual explanations
    
    - Architecture diagrams
    - Dependency maps
    - Component relationships
    - Onboarding guides
    """
    try:
        orchestrator = AIOrchestrator(db)
        result = await orchestrator.process_query(
            mode="illustration",
            workspace_id=request.workspace_id,
            query=request.query,
            context=request.context
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/development/query", response_model=ModeQueryResponse)
async def development_mode_query(
    request: ModeQueryRequest,
    db: Session = Depends(get_db)
):
    """
    Development Mode: Code analysis and improvements
    
    - Code reviews
    - Refactoring suggestions
    - Security analysis
    - Best practices
    """
    try:
        orchestrator = AIOrchestrator(db)
        result = await orchestrator.process_query(
            mode="development",
            workspace_id=request.workspace_id,
            query=request.query,
            context=request.context
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/testing/query", response_model=ModeQueryResponse)
async def testing_mode_query(
    request: ModeQueryRequest,
    db: Session = Depends(get_db)
):
    """
    Testing Mode: Test generation and analysis
    
    - Unit test generation
    - Integration tests
    - Coverage analysis
    - Edge case identification
    """
    try:
        orchestrator = AIOrchestrator(db)
        result = await orchestrator.process_query(
            mode="testing",
            workspace_id=request.workspace_id,
            query=request.query,
            context=request.context
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/deployment/query", response_model=ModeQueryResponse)
async def deployment_mode_query(
    request: ModeQueryRequest,
    db: Session = Depends(get_db)
):
    """
    Deployment Mode: Infrastructure configuration
    
    - Dockerfile generation
    - docker-compose setup
    - CI/CD pipelines
    - Kubernetes configs
    """
    try:
        orchestrator = AIOrchestrator(db)
        result = await orchestrator.process_query(
            mode="deployment",
            workspace_id=request.workspace_id,
            query=request.query,
            context=request.context
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/documentation/query", response_model=ModeQueryResponse)
async def documentation_mode_query(
    request: ModeQueryRequest,
    db: Session = Depends(get_db)
):
    """
    Documentation Mode: Generate documentation
    
    - README generation
    - API documentation
    - Onboarding guides
    - Technical summaries
    """
    try:
        orchestrator = AIOrchestrator(db)
        result = await orchestrator.process_query(
            mode="documentation",
            workspace_id=request.workspace_id,
            query=request.query,
            context=request.context
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Made with Bob
