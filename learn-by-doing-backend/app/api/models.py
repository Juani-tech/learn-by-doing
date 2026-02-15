"""API models and schemas."""
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


# ============== Request Models ==============

class PathGenerationRequest(BaseModel):
    """Request to generate a learning path."""
    topic: str = Field(..., description="Topic to learn (e.g., 'Rust CLI tools')")
    context: Optional[str] = Field(
        None, 
        description="Additional context about goals (e.g., 'Want to build system utilities')"
    )
    experience_level: str = Field(
        "intermediate",
        description="Experience level: beginner, intermediate, or advanced"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "topic": "Rust CLI tools",
                "context": "Want to build system utilities like file organizers",
                "experience_level": "intermediate"
            }
        }


# ============== Response Models ==============

class Resource(BaseModel):
    """Resource reference."""
    title: str
    url: str
    type: str = Field(..., description="documentation, reference, article, or book")
    description: str


class Task(BaseModel):
    """Task in a learning path."""
    id: str
    phaseId: str
    title: str
    description: str
    difficulty: int = Field(..., ge=1, le=5)
    estimatedHours: int
    requirements: List[str]
    acceptanceCriteria: List[str]
    prerequisites: List[str]
    resources: List[Resource]


class Phase(BaseModel):
    """Phase in a learning path."""
    id: str
    title: str
    description: str
    order: int
    tasks: List[Task]


class LearningPathData(BaseModel):
    """Complete learning path data."""
    id: str
    title: str
    description: str
    version: str
    language: str
    area: str
    prerequisites: List[str]
    totalTasks: int
    estimatedHours: int
    phases: List[Phase]


class GenerationMetadata(BaseModel):
    """Metadata about path generation."""
    iterationCount: int
    qualityScore: float
    generationTimeSeconds: float
    approved: bool
    maxIterationsReached: bool


class PathGenerationResponse(BaseModel):
    """Response from path generation."""
    pathId: UUID
    path: LearningPathData
    metadata: GenerationMetadata
    
    class Config:
        from_attributes = True


class PathListItem(BaseModel):
    """Summary of a learning path for listing."""
    id: UUID
    slug: str
    title: str
    description: str
    language: Optional[str]
    area: Optional[str]
    totalTasks: int
    estimatedHours: int
    qualityScore: Optional[int]
    createdAt: datetime
    
    class Config:
        from_attributes = True


class PathDetail(BaseModel):
    """Detailed view of a learning path."""
    id: UUID
    slug: str
    title: str
    description: str
    language: Optional[str]
    area: Optional[str]
    version: Optional[str]
    totalTasks: int
    estimatedHours: int
    difficultyLevel: Optional[str]
    rawData: Dict[str, Any]
    metadata: Dict[str, Any]
    qualityScore: Optional[int]
    generationAttempts: int
    createdAt: datetime
    updatedAt: Optional[datetime]
    
    class Config:
        from_attributes = True


# ============== Health Check ==============

class HealthStatus(BaseModel):
    """Health check response."""
    status: str
    version: str
    database: str
    llm: str
