"""Workflow state definitions."""
from typing import TypedDict, Optional, Any
from datetime import datetime


class WorkflowState(TypedDict, total=False):
    """State managed by LangGraph workflow."""
    
    # Input fields
    topic: str
    context: Optional[str]
    experience_level: str
    
    # Agent outputs
    research_findings: dict[str, Any]
    draft_curriculum: dict[str, Any]
    expert_feedback: dict[str, Any]
    quality_review: dict[str, Any]
    
    # Control fields
    iteration: int
    approved: bool
    final_output: Optional[dict[str, Any]]
    
    # Metadata
    started_at: datetime
    completed_at: Optional[datetime]
    errors: list[str]
    agent_logs: list[dict[str, Any]]


def create_initial_state(
    topic: str,
    context: Optional[str] = None,
    experience_level: str = "intermediate"
) -> WorkflowState:
    """Create initial workflow state."""
    return {
        "topic": topic,
        "context": context,
        "experience_level": experience_level,
        "research_findings": {},
        "draft_curriculum": {},
        "expert_feedback": {},
        "quality_review": {},
        "iteration": 0,
        "approved": False,
        "final_output": None,
        "started_at": datetime.utcnow(),
        "completed_at": None,
        "errors": [],
        "agent_logs": []
    }
