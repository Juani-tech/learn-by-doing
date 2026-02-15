"""Domain Expert Agent - validates technical accuracy."""
import json
from app.agents.base import BaseAgent
from app.workflow.state import WorkflowState
from app.core.logging import logger


class ExpertAgent(BaseAgent):
    """
    Domain Expert Agent validates technical accuracy,
    appropriate difficulty progression, and best practices.
    """
    
    SYSTEM_PROMPT = """You are a senior engineer and domain expert.
Your job is to validate the technical accuracy and pedagogy of a learning path.

RESEARCH FINDINGS:
{research_findings}

DRAFT CURRICULUM:
{draft_curriculum}

Review the curriculum thoroughly and assess:

1. TECHNICAL ACCURACY (30%):
   - Are concepts explained correctly?
   - Are tools/frameworks current and appropriate?
   - Are best practices followed?
   - Any outdated or incorrect information?

2. DIFFICULTY PROGRESSION (25%):
   - Does difficulty increase appropriately?
   - Are fundamentals taught before advanced topics?
   - Is the pacing reasonable?
   - No huge jumps in complexity?

3. PRACTICAL VALUE (25%):
   - Are projects realistic and useful?
   - Will learners build employable skills?
   - Are industry standards followed?
   - Capstone project appropriate?

4. COMPLETENESS (20%):
   - Are all essential concepts covered?
   - No critical gaps in knowledge?
   - Prerequisites properly handled?
   - Resources appropriate?

SCORING:
- Calculate overall confidence score (0.0 - 1.0)
- Must be ≥ 0.75 to pass
- Score each category separately

Output MUST be valid JSON:
{{
    "validation": "pass" | "needs_improvement",
    "confidence": 0.85,
    "scores": {{
        "technical_accuracy": 0.9,
        "difficulty_progression": 0.8,
        "practical_value": 0.85,
        "completeness": 0.8
    }},
    "issues": [
        {{
            "severity": "high|medium|low",
            "location": "Phase X, Task Y or general",
            "issue": "description of the problem",
            "suggestion": "how to fix it"
        }}
    ],
    "improvements": [
        "suggestion 1",
        "suggestion 2"
    ],
    "strengths": [
        "what's done well 1",
        "what's done well 2"
    ]
}}"""
    
    def __init__(self):
        super().__init__("ExpertAgent")
    
    async def run(self, state: WorkflowState) -> WorkflowState:
        """Execute expert validation phase."""
        self.log_action(state, "Starting expert validation")
        
        try:
            # Prepare messages
            messages = [
                {
                    "role": "system",
                    "content": self.SYSTEM_PROMPT.format(
                        research_findings=json.dumps(state["research_findings"], indent=2),
                        draft_curriculum=json.dumps(state["draft_curriculum"], indent=2)
                    )
                },
                {
                    "role": "user",
                    "content": "Validate this curriculum for technical accuracy and pedagogy."
                }
            ]
            
            # Generate expert review
            response = await self.llm.generate_json(
                messages=messages,
                temperature=0.6,  # Lower for consistency
                max_tokens=4000
            )
            
            # Validate structure
            required_keys = ["validation", "confidence", "scores", "issues"]
            for key in required_keys:
                if key not in response:
                    raise ValueError(f"Missing required key in expert review: {key}")
            
            # Store in state
            state["expert_feedback"] = response
            
            # Log results
            issue_count = len(response.get("issues", []))
            high_severity = sum(1 for i in response.get("issues", []) if i.get("severity") == "high")
            
            self.log_action(
                state,
                "Expert validation completed",
                {
                    "validation": response["validation"],
                    "confidence": response["confidence"],
                    "issues_found": issue_count,
                    "high_severity_issues": high_severity
                }
            )
            
            logger.info(f"Expert validation: {response['validation']} (confidence: {response['confidence']:.2f})")
            
            if high_severity > 0:
                logger.warning(f"Found {high_severity} high severity issues")
            
        except Exception as e:
            self.add_error(state, f"Expert validation failed: {str(e)}")
            logger.error(f"Expert agent error: {str(e)}")
        
        return state
