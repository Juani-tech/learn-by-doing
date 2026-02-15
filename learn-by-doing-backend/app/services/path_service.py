"""Path service - business logic for learning paths."""
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from slugify import slugify

from app.db.models import LearningPath, Phase, Task
from app.workflow.graph import get_workflow
from app.workflow.state import create_initial_state
from app.services.validation_service import ResourceValidator
from app.core.logging import logger
from app.config import get_settings


class PathService:
    """Service for learning path operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.validator = ResourceValidator()
    
    async def generate_path(
        self,
        topic: str,
        context: Optional[str] = None,
        experience_level: str = "intermediate"
    ) -> Dict[str, Any]:
        """
        Generate a learning path using the agentic workflow.
        
        Args:
            topic: Topic to generate path for
            context: Additional context
            experience_level: Experience level
        
        Returns:
            Dictionary with path data and metadata
        """
        logger.info(f"Generating path for: {topic}")
        
        # Create initial state
        initial_state = create_initial_state(
            topic=topic,
            context=context,
            experience_level=experience_level
        )
        
        # Get workflow and run
        workflow = get_workflow()
        
        try:
            # Execute workflow
            final_state = await workflow.ainvoke(initial_state)
            
            # Get results
            path_data = final_state.get("final_output", {})
            
            if not path_data:
                raise ValueError("Workflow completed but no path data generated")
            
            # Validate resources if enabled
            settings = get_settings()
            if settings.VALIDATE_RESOURCES:
                await self._validate_path_resources(path_data)
            
            # Save to database
            path_id = await self._save_path(path_data, final_state)
            
            # Build response
            result = {
                "path_id": path_id,
                "path_data": path_data,
                "iteration_count": final_state.get("iteration", 0),
                "quality_score": final_state.get("quality_review", {}).get("score", 0),
                "approved": final_state.get("approved", False),
                "max_iterations_reached": (
                    final_state.get("iteration", 0) >= get_settings().MAX_ITERATIONS
                )
            }
            
            logger.info(f"Path generation complete: {result['path_id']}")
            return result
            
        except Exception as e:
            logger.error(f"Path generation failed: {str(e)}")
            raise
    
    async def _validate_path_resources(self, path_data: Dict[str, Any]):
        """Validate all resource URLs in the path."""
        resources_to_validate = []
        
        for phase in path_data.get("phases", []):
            for task in phase.get("tasks", []):
                for resource in task.get("resources", []):
                    resources_to_validate.append(resource)
        
        if resources_to_validate:
            logger.info(f"Validating {len(resources_to_validate)} resources")
            await self.validator.validate_batch(resources_to_validate)
    
    async def _save_path(
        self,
        path_data: Dict[str, Any],
        final_state: Dict[str, Any]
    ) -> UUID:
        """Save path to database."""
        # Create slug
        base_slug = slugify(path_data.get("id", "unnamed-path"))
        slug = await self._ensure_unique_slug(base_slug)
        
        # Extract metadata
        quality_review = final_state.get("quality_review", {})
        
        # Create learning path
        path = LearningPath(
            slug=slug,
            title=path_data.get("title", "Untitled Path"),
            description=path_data.get("description", ""),
            language=path_data.get("language"),
            area=path_data.get("area"),
            version=path_data.get("version", "1.0"),
            total_tasks=path_data.get("totalTasks", 0),
            estimated_hours=path_data.get("estimatedHours", 0),
            raw_data=path_data,
            generation_metadata={
                "generation_timestamp": datetime.utcnow().isoformat(),
                "topic": final_state.get("topic"),
                "context": final_state.get("context"),
                "experience_level": final_state.get("experience_level"),
                "iteration_count": final_state.get("iteration"),
                "expert_feedback": final_state.get("expert_feedback"),
                "quality_review": quality_review
            },
            quality_score=int(quality_review.get("score", 0) * 100),
            generation_attempts=final_state.get("iteration", 1)
        )
        
        self.db.add(path)
        await self.db.flush()  # Get the ID
        
        # Create phases and tasks
        for phase_data in path_data.get("phases", []):
            phase = Phase(
                path_id=path.id,
                phase_id=phase_data.get("id", ""),
                order_index=phase_data.get("order", 0),
                title=phase_data.get("title", "Untitled Phase"),
                description=phase_data.get("description", ""),
                raw_data=phase_data
            )
            self.db.add(phase)
            await self.db.flush()
            
            # Create tasks for this phase
            for task_data in phase_data.get("tasks", []):
                task = Task(
                    path_id=path.id,
                    phase_id=phase.id,
                    task_id=task_data.get("id", ""),
                    title=task_data.get("title", "Untitled Task"),
                    description=task_data.get("description", ""),
                    difficulty=task_data.get("difficulty", 3),
                    estimated_hours=task_data.get("estimatedHours", 4),
                    requirements=task_data.get("requirements", []),
                    acceptance_criteria=task_data.get("acceptanceCriteria", []),
                    prerequisites=task_data.get("prerequisites", []),
                    resources=task_data.get("resources", []),
                    raw_data=task_data
                )
                self.db.add(task)
        
        await self.db.commit()
        logger.info(f"Saved path to database: {path.id}")
        
        return path.id
    
    async def _ensure_unique_slug(self, base_slug: str) -> str:
        """Ensure slug is unique by appending number if needed."""
        slug = base_slug
        counter = 1
        
        while True:
            result = await self.db.execute(
                select(LearningPath).where(LearningPath.slug == slug)
            )
            if not result.scalar_one_or_none():
                return slug
            slug = f"{base_slug}-{counter}"
            counter += 1
    
    async def get_path(self, path_id: UUID) -> Optional[LearningPath]:
        """Get a path by ID."""
        result = await self.db.execute(
            select(LearningPath).where(LearningPath.id == path_id)
        )
        return result.scalar_one_or_none()
    
    async def get_path_by_slug(self, slug: str) -> Optional[LearningPath]:
        """Get a path by slug."""
        result = await self.db.execute(
            select(LearningPath).where(LearningPath.slug == slug)
        )
        return result.scalar_one_or_none()
    
    async def list_paths(
        self,
        language: Optional[str] = None,
        area: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[LearningPath]:
        """List paths with optional filtering."""
        query = select(LearningPath).where(LearningPath.status == "active")
        
        if language:
            query = query.where(LearningPath.language == language)
        if area:
            query = query.where(LearningPath.area == area)
        
        query = query.order_by(LearningPath.created_at.desc())
        query = query.offset(offset).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def delete_path(self, path_id: UUID) -> bool:
        """Delete a path."""
        result = await self.db.execute(
            delete(LearningPath).where(LearningPath.id == path_id)
        )
        await self.db.commit()
        return result.rowcount > 0
