"""Curriculum Designer Agent - creates learning path structure."""
import json
from slugify import slugify
from app.agents.base import BaseAgent
from app.agents.tools import get_search_client
from app.workflow.state import WorkflowState
from app.core.logging import logger


class CurriculumAgent(BaseAgent):
    """
    Curriculum Designer Agent creates the actual learning path
    with phases, tasks, requirements, and resources.
    """
    
    SYSTEM_PROMPT = """You are an expert curriculum designer for programming education.
You follow the "Learn by Doing" philosophy STRICTLY.

RESEARCH FINDINGS:
{research_findings}

STRICT RULES - VIOLATIONS WILL CAUSE REJECTION:

1. REQUIREMENTS ONLY:
   - List WHAT to build, never HOW to build it
   - No "First do X, then do Y" instructions
   - No example code
   - No "try this" or "experiment with"
   - Must be pure requirements

2. HANDS-ON ONLY:
   - EVERY concept must have a practical project
   - No theory-only sections
   - No "read about X" tasks
   - Each task must produce working code

3. BOTTOM-UP LEARNING:
   - Fundamentals before advanced
   - Concepts build on previous concepts
   - No introducing advanced topics early
   - Prerequisites properly ordered

4. NO REPETITION:
   - Each concept taught exactly ONCE
   - No "review" or "practice" sections
   - No "let's reinforce X"
   - Fast-paced progression

5. FAST-PACED:
   - Move quickly to implementation
   - No lengthy explanations
   - Brief descriptions (1-2 sentences max)
   - Focus on doing, not reading

6. RESOURCES:
   - Only official documentation
   - API references
   - Language specifications
   - NO tutorials, guides, or examples

TASK STRUCTURE:
- id: unique identifier (kebab-case)
- title: clear, action-oriented
- description: 1-2 sentences max
- difficulty: 1-5
- estimated_hours: realistic estimate
- requirements: bullet list of WHAT to build
- acceptance_criteria: how to verify completion
- prerequisites: list of task ids that must be done first
- resources: documentation links only

Based on the research findings, create a complete learning path.

Output MUST be valid JSON matching this structure:
{{
    "id": "unique-slug",
    "title": "Path Title",
    "description": "Brief description",
    "version": "1.0",
    "language": "Language Name",
    "area": "Area of Focus",
    "prerequisites": [],
    "total_tasks": 15,
    "estimated_hours": 80,
    "phases": [
        {{
            "id": "phase-id",
            "title": "Phase Title",
            "description": "Brief description",
            "order": 1,
            "tasks": [
                {{
                    "id": "task-id",
                    "phaseId": "phase-id",
                    "title": "Task Title",
                    "description": "Brief description",
                    "difficulty": 3,
                    "estimatedHours": 4,
                    "requirements": ["req1", "req2"],
                    "acceptanceCriteria": ["criteria1", "criteria2"],
                    "prerequisites": [],
                    "resources": [
                        {{
                            "title": "Resource Name",
                            "url": "https://docs.example.com/page",
                            "type": "documentation",
                            "description": "Brief description"
                        }}
                    ]
                }}
            ]
        }}
    ]
}}"""
    
    def __init__(self):
        super().__init__("CurriculumAgent")
        self.search_client = get_search_client()
    
    async def run(self, state: WorkflowState) -> WorkflowState:
        """Execute curriculum design phase."""
        self.log_action(state, "Starting curriculum design")
        
        # Increment iteration counter
        state["iteration"] = state.get("iteration", 0) + 1
        
        try:
            # Get iteration number for prompt context
            iteration = state["iteration"]
            
            # If this is a retry, include expert feedback
            expert_feedback = ""
            if iteration > 1 and state.get("expert_feedback"):
                feedback = state["expert_feedback"]
                if feedback.get("issues"):
                    expert_feedback = f"""
\n\nEXPERT FEEDBACK (ITERATION {iteration}):
The previous draft had these issues that must be fixed:
"""
                    for issue in feedback["issues"]:
                        expert_feedback += f"\n- {issue['severity'].upper()}: {issue['issue']}"
                        if issue.get("suggestion"):
                            expert_feedback += f" Suggestion: {issue['suggestion']}"
            
            # Prepare messages
            messages = [
                {
                    "role": "system",
                    "content": self.SYSTEM_PROMPT.format(
                        research_findings=json.dumps(state["research_findings"], indent=2)
                    ) + expert_feedback
                },
                {
                    "role": "user",
                    "content": f"Create learning path for: {state['topic']} (Attempt {iteration})"
                }
            ]
            
            # Generate curriculum
            logger.info(f"[{self.name}] Sending request to LLM...")
            response = await self.llm.generate_json(
                messages=messages,
                temperature=0.75,
                max_tokens=4000  # Reduced for faster response on free tier
            )
            logger.info(f"[{self.name}] Received response from LLM")
            
            # Validate basic structure
            required_keys = ["id", "title", "phases", "total_tasks", "estimated_hours"]
            for key in required_keys:
                if key not in response:
                    raise ValueError(f"Missing required key in curriculum: {key}")
            
            # Ensure slug format for ID
            response["id"] = slugify(response["id"])
            
            # Validate phases have tasks
            total_tasks = 0
            for phase in response["phases"]:
                if "tasks" not in phase or not phase["tasks"]:
                    raise ValueError(f"Phase {phase.get('id')} has no tasks")
                total_tasks += len(phase["tasks"])
            
            # Update counts
            response["total_tasks"] = total_tasks
            
            # Search for documentation URLs to enrich resources
            logger.info("Searching for documentation URLs...")
            await self._enrich_resources_with_search(response, state["topic"])
            
            # Store in state
            state["draft_curriculum"] = response
            
            self.log_action(
                state,
                "Curriculum design completed",
                {
                    "iteration": iteration,
                    "phases": len(response["phases"]),
                    "total_tasks": total_tasks,
                    "estimated_hours": response["estimated_hours"]
                }
            )
            
            logger.info(f"Curriculum created: {total_tasks} tasks in {len(response['phases'])} phases")
            
        except Exception as e:
            self.add_error(state, f"Curriculum design failed: {str(e)}")
            logger.error(f"Curriculum error: {str(e)}")
        
        return state
    
    async def _enrich_resources_with_search(self, curriculum: dict, topic: str):
        """
        Search for documentation URLs to enrich task resources.
        
        Args:
            curriculum: The curriculum dict to modify
            topic: Main topic
        """
        try:
            # Get unique concepts from all tasks
            concepts_to_search = set()
            for phase in curriculum.get("phases", []):
                for task in phase.get("tasks", []):
                    task_title = task.get("title", "")
                    # Extract key terms from title
                    concepts_to_search.add(task_title)
            
            # Search for documentation for each concept (limit to save time)
            searched_concepts = 0
            for phase in curriculum.get("phases", []):
                for task in phase.get("tasks", []):
                    if searched_concepts >= 5:  # Limit searches
                        break
                    
                    task_title = task.get("title", "")
                    
                    # Search for docs
                    try:
                        search_query = f"{topic} {task_title} documentation official"
                        results = await self.search_client.search_documentation(
                            search_query, 
                            max_results=2
                        )
                        
                        if results:
                            # Add or replace resources
                            current_resources = task.get("resources", [])
                            
                            for result in results[:2]:  # Top 2 results
                                # Check if not already present
                                url = result.get("url", "")
                                if not any(r.get("url") == url for r in current_resources):
                                    current_resources.append({
                                        "title": result.get("title", "Documentation"),
                                        "url": url,
                                        "type": "documentation",
                                        "description": result.get("snippet", "")[:100]
                                    })
                            
                            task["resources"] = current_resources[:5]  # Max 5 resources
                            searched_concepts += 1
                            
                    except Exception as e:
                        logger.warning(f"Failed to search docs for {task_title}: {str(e)}")
                        continue
            
            logger.info(f"Enriched {searched_concepts} tasks with documentation URLs")
            
        except Exception as e:
            logger.error(f"Resource enrichment failed: {str(e)}")
            # Don't fail the whole curriculum if enrichment fails
