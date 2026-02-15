"""Path API routes."""
import time
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.api.deps import get_db
from app.api.models import (
    PathGenerationRequest,
    PathGenerationResponse,
    PathDetail,
    PathListItem,
    LearningPathData,
    GenerationMetadata
)
from app.services.path_service import PathService
from app.db.models import LearningPath as LearningPathModel
from app.core.logging import logger

router = APIRouter()


@router.post("/generate", response_model=PathGenerationResponse)
async def generate_path(
    request: PathGenerationRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate a new learning path using agentic workflow.
    
    This endpoint initiates the full workflow:
    1. Research Agent discovers the topic
    2. Curriculum Designer creates the structure
    3. Domain Expert validates technical accuracy
    4. Quality Review ensures "learn by doing" philosophy
    
    The workflow loops until approved or max iterations reached.
    
    **Note**: This operation takes 30-120 seconds.
    """
    start_time = time.time()
    
    logger.info(f"Starting path generation for: {request.topic}")
    
    try:
        # Create service and generate
        service = PathService(db)
        result = await service.generate_path(
            topic=request.topic,
            context=request.context,
            experience_level=request.experience_level
        )
        
        # Calculate generation time
        generation_time = time.time() - start_time
        
        # Build response
        response = PathGenerationResponse(
            pathId=result["path_id"],
            path=LearningPathData(**result["path_data"]),
            metadata=GenerationMetadata(
                iterationCount=result["iteration_count"],
                qualityScore=result["quality_score"],
                generationTimeSeconds=round(generation_time, 2),
                approved=result["approved"],
                maxIterationsReached=result["max_iterations_reached"]
            )
        )
        
        logger.info(f"Path generation completed in {generation_time:.2f}s")
        return response
        
    except Exception as e:
        logger.error(f"Path generation failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate path: {str(e)}"
        )


@router.get("/{path_id}", response_model=PathDetail)
async def get_path(
    path_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get a learning path by ID."""
    service = PathService(db)
    path = await service.get_path(path_id)
    
    if not path:
        raise HTTPException(status_code=404, detail="Path not found")
    
    return path


@router.get("/slug/{slug}", response_model=PathDetail)
async def get_path_by_slug(
    slug: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a learning path by slug."""
    service = PathService(db)
    path = await service.get_path_by_slug(slug)
    
    if not path:
        raise HTTPException(status_code=404, detail="Path not found")
    
    return path


@router.get("/", response_model=list[PathListItem])
async def list_paths(
    language: Optional[str] = None,
    area: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """
    List all learning paths with optional filtering.
    
    Args:
        language: Filter by programming language
        area: Filter by area of focus
        limit: Maximum results to return
        offset: Pagination offset
    """
    service = PathService(db)
    paths = await service.list_paths(
        language=language,
        area=area,
        limit=limit,
        offset=offset
    )
    return paths


@router.delete("/{path_id}")
async def delete_path(
    path_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Delete a learning path."""
    service = PathService(db)
    success = await service.delete_path(path_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Path not found")
    
    return {"message": "Path deleted successfully"}
