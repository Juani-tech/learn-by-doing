"""Quality Review Agent - final approval based on philosophy."""
import json
from app.agents.base import BaseAgent
from app.workflow.state import WorkflowState
from app.core.logging import logger
from app.config import get_settings


class QualityAgent(BaseAgent):
    """
    Quality Review Agent - THE GATEKEEPER.
    Ensures strict adherence to "Learn by Doing" philosophy.
    """
    
    SYSTEM_PROMPT = """You are the Quality Gatekeeper for LearnByDoing.
Your job is STRICT final approval based on our core philosophy.

DRAFT CURRICULUM TO REVIEW:
{draft_curriculum}

EXPERT FEEDBACK:
{expert_feedback}

STRICT QUALITY CHECKS - EACH MUST SCORE ≥ 0.8:

1. NO HAND-HOLDING (0-1 score):
   ✗ FAIL if: "how to", "example code", "try this", "step-by-step", "guide"
   ✗ FAIL if: Requirements explain implementation details
   ✗ FAIL if: Contains tutorial language
   ✓ PASS if: Pure requirements (WHAT, not HOW)
   
2. NO REPETITION (0-1 score):
   ✗ FAIL if: "Review X concept"
   ✗ FAIL if: "Practice exercise for Y"
   ✗ FAIL if: Same concept taught twice
   ✓ PASS if: Each concept taught exactly ONCE
   
3. BOTTOM-UP ORDER (0-1 score):
   ✗ FAIL if: Advanced concept before fundamentals
   ✗ FAIL if: Prerequisites not respected
   ✗ FAIL if: Topics out of logical order
   ✓ PASS if: Clear progression from basic to advanced
   
4. HANDS-ON ONLY (0-1 score):
   ✗ FAIL if: Any task without practical requirements
   ✗ FAIL if: "Read about X" or "Study Y"
   ✗ FAIL if: Theory-only sections
   ✓ PASS if: EVERY task has code to write
   
5. FAST-PACED (0-1 score):
   ✗ FAIL if: Lengthy descriptions (>2 sentences)
   ✗ FAIL if: Unnecessary explanations
   ✗ FAIL if: Slow progression
   ✓ PASS if: Brief, action-oriented tasks
   
6. RESOURCE QUALITY (0-1 score):
   ✗ FAIL if: Tutorial links present
   ✗ FAIL if: GitHub repos with solutions
   ✗ FAIL if: "How-to" guides
   ✓ PASS if: Only docs, references, specs

APPROVAL CRITERIA:
- ALL scores must be ≥ 0.8
- Average score must be ≥ 0.85
- NO high-severity violations

If ANY check fails significantly, REJECT and specify exactly what needs fixing.

Output MUST be valid JSON:
{{
    "approved": true | false,
    "score": 0.87,
    "scores": {{
        "no_hand_holding": 0.9,
        "no_repetition": 0.85,
        "bottom_up_order": 0.9,
        "hands_on_only": 0.8,
        "fast_paced": 0.85,
        "resource_quality": 0.9
    }},
    "violations": [
        {{
            "principle": "NO HAND-HOLDING",
            "task_id": "task-5",
            "issue": "Contains 'how to implement' language",
            "fix": "Remove implementation details, keep only requirements"
        }}
    ],
    "summary": "Brief summary of quality assessment"
}}"""
    
    def __init__(self):
        super().__init__("QualityAgent")
        self.quality_threshold = get_settings().QUALITY_THRESHOLD
    
    async def run(self, state: WorkflowState) -> WorkflowState:
        """Execute quality review phase."""
        self.log_action(state, "Starting quality review")
        
        try:
            # Prepare messages
            messages = [
                {
                    "role": "system",
                    "content": self.SYSTEM_PROMPT.format(
                        draft_curriculum=json.dumps(state["draft_curriculum"], indent=2),
                        expert_feedback=json.dumps(state.get("expert_feedback", {}), indent=2)
                    )
                },
                {
                    "role": "user",
                    "content": f"Final quality review - Iteration {state['iteration']}/5"
                }
            ]
            
            # Generate quality review
            response = await self.llm.generate_json(
                messages=messages,
                temperature=0.4,  # Very low for strict consistency
                max_tokens=4000
            )
            
            # Validate structure
            required_keys = ["approved", "score", "scores", "violations"]
            for key in required_keys:
                if key not in response:
                    raise ValueError(f"Missing required key in quality review: {key}")
            
            # Calculate average if not provided
            scores = response["scores"]
            if isinstance(scores, dict):
                avg_score = sum(scores.values()) / len(scores)
                response["score"] = round(avg_score, 2)
            
            # Determine approval
            approved = (
                response["approved"] and
                response["score"] >= self.quality_threshold and
                all(score >= 0.8 for score in scores.values())
            )
            
            response["approved"] = approved
            
            # Store in state
            state["quality_review"] = response
            state["approved"] = approved
            
            # Log results
            violation_count = len(response.get("violations", []))
            
            self.log_action(
                state,
                "Quality review completed",
                {
                    "approved": approved,
                    "score": response["score"],
                    "violations": violation_count,
                    "iteration": state["iteration"]
                }
            )
            
            logger.info(f"Quality review: {'APPROVED' if approved else 'REJECTED'} (score: {response['score']:.2f})")
            
            if not approved and state["iteration"] >= 5:
                logger.warning("Max iterations reached, forcing approval with best effort")
                state["approved"] = True
            
        except Exception as e:
            self.add_error(state, f"Quality review failed: {str(e)}")
            logger.error(f"Quality agent error: {str(e)}")
        
        return state
