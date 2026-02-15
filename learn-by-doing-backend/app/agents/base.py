"""Base agent class."""
from abc import ABC, abstractmethod
from typing import Any, Optional
from app.core.llm import OpenRouterClient
from app.core.logging import logger
from app.workflow.state import WorkflowState


class BaseAgent(ABC):
    """Base class for all agents."""
    
    def __init__(self, name: str):
        self.name = name
        self.llm = OpenRouterClient()
        logger.info(f"Initialized agent: {name}")
    
    @abstractmethod
    async def run(self, state: WorkflowState) -> WorkflowState:
        """
        Execute the agent's logic.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated workflow state
        """
        pass
    
    def log_action(self, state: WorkflowState, action: str, details: Optional[dict] = None):
        """Log agent action to state."""
        log_entry = {
            "agent": self.name,
            "action": action,
            "iteration": state.get("iteration", 0),
            "details": details or {}
        }
        state["agent_logs"].append(log_entry)
        logger.info(f"[{self.name}] {action}")
    
    def add_error(self, state: WorkflowState, error: str):
        """Add error to state."""
        state["errors"].append(f"[{self.name}] {error}")
        logger.error(f"[{self.name}] Error: {error}")
