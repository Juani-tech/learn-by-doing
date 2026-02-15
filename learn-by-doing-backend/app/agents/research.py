"""Research Agent - discovers topic information using web search."""
import json
from typing import Any
from app.agents.base import BaseAgent
from app.agents.tools import get_search_client
from app.workflow.state import WorkflowState
from app.core.logging import logger


class ResearchAgent(BaseAgent):
    """
    Research Agent discovers what a technology/paradigm is,
    its use cases, prerequisites, and core concepts using web search.
    """
    
    SYSTEM_PROMPT = """You are a computer science research expert.
Your goal is to analyze search results and provide a concise analysis.

CRITICAL: Be concise! Use brief bullet points. Do not write long paragraphs.
Keep descriptions under 100 words. This prevents hitting token limits.

WEB SEARCH RESULTS:
{search_results}

Topic: {topic}
Context: {context}
Experience Level: {experience_level}

Based on the search results above and your knowledge, provide a brief analysis:

1. TOPIC ANALYSIS:
   - What is this technology/paradigm?
   - What are its primary use cases?
   - What is the learning curve (easy/moderate/steep)?
   - Who uses it (industries, companies)?
   - Is it actively maintained/popular?

2. PREREQUISITES:
   - What should someone know before learning this?
   - Required background knowledge
   - Nice-to-have skills
   - Recommended prior experience

3. CORE CONCEPTS (in learning order):
   - List key concepts from fundamental to advanced
   - Estimate difficulty for each (1-5)
   - Group into logical phases (3-4 phases)
   - Include only concepts mentioned in search or well-known

4. ECOSYSTEM:
   - Essential tools/libraries (based on search results)
   - Build tools
   - Testing frameworks
   - Documentation resources (use URLs from search if relevant)
   - Package managers

5. SCOPE ASSESSMENT:
   - Is this a full language, framework, paradigm, or tool?
   - Estimated learning time for intermediate developer
   - Suggested number of tasks (6-25 based on scope)
   - Complexity level

Guidelines:
- BE CONCISE: Short descriptions, bullet points only
- Limit concept descriptions to 20 words max
- Use 3-5 core concepts, not 10+
- Use information from search results primarily

Output MUST be valid JSON with this structure:
{{
    "topic_analysis": {{
        "what_is_it": "description",
        "primary_use_cases": ["use case 1", "use case 2"],
        "learning_curve": "steep",
        "target_audience": "description",
        "popularity": "high|medium|low",
        "actively_maintained": true|false
    }},
    "prerequisites": ["prereq 1", "prereq 2"],
    "core_concepts": [
        {{
            "name": "concept name",
            "category": "fundamental|intermediate|advanced",
            "difficulty": 3,
            "phase": 1,
            "description": "brief description"
        }}
    ],
    "ecosystem": {{
        "essential_tools": ["tool1", "tool2"],
        "build_tools": ["tool1"],
        "testing_frameworks": ["framework1"],
        "package_managers": ["cargo", "npm"],
        "key_resources": ["resource1", "resource2"]
    }},
    "scope_assessment": {{
        "type": "language|framework|paradigm|tool",
        "estimated_hours": 60,
        "suggested_tasks": 15,
        "suggested_phases": 4,
        "complexity": "high|medium|low"
    }},
    "search_metadata": {{
        "sources_found": 5,
        "confidence": "high|medium|low"
    }}
}}"""
    
    def __init__(self):
        super().__init__("ResearchAgent")
        self.search_client = get_search_client()
    
    async def run(self, state: WorkflowState) -> WorkflowState:
        """Execute research phase with web search."""
        self.log_action(state, "Starting research with web search")
        
        try:
            topic = state["topic"]
            context = state.get("context") or "General learning path"
            
            # Search for topic information
            logger.info(f"Searching web for: {topic}")
            
            # Multiple search queries for comprehensive coverage
            search_queries = [
                f"{topic} what is it used for",
                f"{topic} official documentation getting started",
                f"{topic} best practices tutorial",
                f"{topic} core concepts fundamentals",
                f"{topic} ecosystem tools libraries"
            ]
            
            # Perform searches
            search_results = []
            for query in search_queries[:3]:  # Limit to 3 queries to save time
                try:
                    results = await self.search_client.search(query, max_results=3)
                    search_results.extend(results)
                except Exception as e:
                    logger.warning(f"Search query failed: {query} - {str(e)}")
                    continue
            
            # Remove duplicates by URL
            seen_urls = set()
            unique_results = []
            for result in search_results:
                url = result.get("url", "")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    unique_results.append(result)
            
            search_results = unique_results[:10]  # Keep top 10
            
            logger.info(f"Found {len(search_results)} unique search results")
            
            # Format search results for prompt
            search_context = self._format_search_results(search_results)
            
            # Prepare messages with search results
            messages = [
                {
                    "role": "system",
                    "content": self.SYSTEM_PROMPT.format(
                        search_results=search_context,
                        topic=topic,
                        context=context,
                        experience_level=state.get("experience_level", "intermediate")
                    )
                },
                {
                    "role": "user",
                    "content": f"Analyze these search results about: {topic}"
                }
            ]
            
            # Generate research findings
            response = await self.llm.generate_json(
                messages=messages,
                temperature=0.7,
                max_tokens=4000
            )
            
            # Add search metadata
            response["search_metadata"] = {
                "sources_found": len(search_results),
                "confidence": "high" if len(search_results) >= 5 else "medium" if len(search_results) >= 3 else "low",
                "search_queries": search_queries[:3]
            }
            
            # Store raw search results for resource extraction
            response["_raw_search_results"] = search_results
            
            # Validate response structure
            required_keys = ["topic_analysis", "prerequisites", "core_concepts", "ecosystem", "scope_assessment"]
            missing_keys = [key for key in required_keys if key not in response]
            if missing_keys:
                logger.error(f"Response missing keys: {missing_keys}")
                logger.error(f"Response keys found: {list(response.keys())}")
                logger.error(f"Response preview: {str(response)[:500]}")
                raise ValueError(f"Missing required keys: {missing_keys}")
            
            # Store in state
            state["research_findings"] = response
            
            self.log_action(
                state, 
                "Research completed",
                {
                    "concepts_found": len(response["core_concepts"]),
                    "suggested_tasks": response["scope_assessment"]["suggested_tasks"],
                    "suggested_phases": response["scope_assessment"]["suggested_phases"],
                    "search_sources": len(search_results),
                    "confidence": response["search_metadata"]["confidence"]
                }
            )
            
            logger.info(
                f"Research complete: {len(response['core_concepts'])} concepts, "
                f"{len(search_results)} sources, confidence: {response['search_metadata']['confidence']}"
            )
            
        except Exception as e:
            self.add_error(state, f"Research failed: {str(e)}")
            logger.error(f"Research error: {str(e)}")
        
        return state
    
    def _format_search_results(self, results: list) -> str:
        """Format search results for inclusion in prompt."""
        if not results:
            return "No web search results found. Relying on general knowledge."
        
        formatted = []
        for i, result in enumerate(results[:8], 1):  # Top 8 results
            formatted.append(
                f"[{i}] {result.get('title', 'No title')}\n"
                f"URL: {result.get('url', 'No URL')}\n"
                f"Content: {result.get('snippet', 'No snippet')[:300]}\n"
            )
        
        return "\n\n".join(formatted)
