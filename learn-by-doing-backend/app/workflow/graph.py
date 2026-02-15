"""LangGraph workflow definition."""
from langgraph.graph import StateGraph, END
from app.workflow.state import WorkflowState
from app.agents.research import ResearchAgent
from app.agents.curriculum import CurriculumAgent
from app.agents.expert import ExpertAgent
from app.agents.quality import QualityAgent
from app.core.logging import logger
from app.config import get_settings


def should_continue(state: WorkflowState) -> str:
    """
    Determine if workflow should continue or finalize.
    
    Returns:
        'finalize' if approved or max iterations reached
        'continue' to loop back to curriculum
    """
    settings = get_settings()
    iteration = state.get("iteration", 0)
    approved = state.get("approved", False)
    
    # If approved, we're done
    if approved:
        logger.info(f"Workflow approved on iteration {iteration}")
        return "finalize"
    
    # If max iterations reached, force completion
    if iteration >= settings.MAX_ITERATIONS:
        logger.warning(f"Max iterations ({settings.MAX_ITERATIONS}) reached, finalizing")
        return "finalize"
    
    # Otherwise, continue to next iteration
    logger.info(f"Continuing to iteration {iteration + 1}")
    return "continue"


def finalize_node(state: WorkflowState) -> WorkflowState:
    """
    Finalize the workflow - prepare final output.
    """
    from datetime import datetime
    
    logger.info("Finalizing workflow")
    
    # Mark completion
    state["completed_at"] = datetime.utcnow()
    
    # Set final output
    if state.get("approved") and state.get("draft_curriculum"):
        state["final_output"] = state["draft_curriculum"]
        logger.info("Final output prepared successfully")
    else:
        # Even if not approved, provide best effort
        state["final_output"] = state.get("draft_curriculum")
        logger.warning("Finalizing without full approval - best effort")
    
    return state


def create_workflow():
    """
    Create and compile the LangGraph workflow.
    
    Workflow:
    Research → Curriculum → Expert → Quality → [loop or end]
    
    Returns:
        Compiled workflow graph
    """
    # Initialize agents
    research_agent = ResearchAgent()
    curriculum_agent = CurriculumAgent()
    expert_agent = ExpertAgent()
    quality_agent = QualityAgent()
    
    # Create graph
    workflow = StateGraph(WorkflowState)
    
    # Add nodes
    workflow.add_node("research", research_agent.run)
    workflow.add_node("curriculum", curriculum_agent.run)
    workflow.add_node("expert", expert_agent.run)
    workflow.add_node("quality", quality_agent.run)
    workflow.add_node("finalize", finalize_node)
    
    # Define edges
    workflow.set_entry_point("research")
    workflow.add_edge("research", "curriculum")
    workflow.add_edge("curriculum", "expert")
    workflow.add_edge("expert", "quality")
    
    # Conditional routing from quality
    workflow.add_conditional_edges(
        "quality",
        should_continue,
        {
            "continue": "curriculum",  # Loop back for improvements
            "finalize": "finalize"     # Complete the workflow
        }
    )
    
    # End after finalize
    workflow.add_edge("finalize", END)
    
    # Compile
    compiled = workflow.compile()
    
    logger.info("Workflow compiled successfully")
    return compiled


# Singleton workflow instance
_workflow = None


def get_workflow():
    """Get or create workflow instance."""
    global _workflow
    if _workflow is None:
        _workflow = create_workflow()
    return _workflow
