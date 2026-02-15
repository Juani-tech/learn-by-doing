"""OpenRouter API client wrapper (OpenAI-compatible)."""
import json
import asyncio
import re
from typing import Any
import httpx
from app.config import get_settings
from app.core.exceptions import LLMException
from app.core.logging import logger


class OpenRouterClient:
    """Client for OpenRouter API (OpenAI-compatible)."""
    
    BASE_URL = "https://openrouter.ai/api/v1"
    
    def __init__(self):
        settings = get_settings()
        self.api_key = settings.OPENROUTER_API_KEY
        self.model = settings.OPENROUTER_MODEL
        self.base_url = self.BASE_URL
        logger.info(f"Initialized OpenRouter client with model: {self.model}")
    
    async def generate(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4000
    ) -> str:
        """
        Generate text using OpenRouter API.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
        
        Returns:
            Generated text response
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://learnbydoing.local",  # Optional
                        "X-Title": "LearnByDoing Backend",  # Optional
                    },
                    json={
                        "model": self.model,
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": max_tokens
                    },
                    timeout=120.0  # Increased timeout for slow models
                )
                
                if response.status_code == 429:
                    error_data = response.json()
                    logger.error(f"Rate limit error: {error_data}")
                    raise LLMException(f"429 RATE_LIMITED: {error_data}")
                
                response.raise_for_status()
                data = response.json()
                
                content = data["choices"][0]["message"]["content"]
                logger.debug(f"OpenRouter response received, length: {len(content)}")
                return content
                
        except httpx.ConnectError as e:
            logger.error(f"OpenRouter connection error: {str(e)}")
            raise LLMException(f"CONNECTION_ERROR: {str(e)}")
        except httpx.ReadError as e:
            logger.error(f"OpenRouter read error (connection dropped): {str(e)}")
            raise LLMException(f"CONNECTION_ERROR: {str(e)}")
        except httpx.TimeoutException as e:
            logger.error(f"OpenRouter timeout: {str(e)}")
            raise LLMException(f"TIMEOUT_ERROR: {str(e)}")
        except httpx.HTTPStatusError as e:
            logger.error(f"OpenRouter HTTP error: {e.response.status_code} - {e.response.text}")
            raise LLMException(f"HTTP error {e.response.status_code}: {e.response.text}")
        except Exception as e:
            logger.error(f"OpenRouter API error: {str(e)}")
            raise LLMException(f"Failed to generate response: {str(e)}")
    
    async def generate_json(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 4000
    ) -> dict[str, Any]:
        """
        Generate JSON response using OpenRouter API.
        
        Args:
            messages: List of message dicts
            temperature: Sampling temperature
            max_tokens: Maximum tokens
        
        Returns:
            Parsed JSON dict
        """
        response = ""
        try:
            # Add JSON instruction to the last user message
            json_messages = messages.copy()
            if json_messages and json_messages[-1]["role"] == "user":
                json_messages[-1]["content"] += "\n\nRespond ONLY with valid JSON. Do not include any thoughts, explanations, or markdown formatting."
            
            response = await self.generate_with_retry(
                messages=json_messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # Log raw response before processing
            logger.debug(f"Raw response for JSON parsing: {response[:500]}")
            
            # Clean up the response - extract JSON from markdown or text
            response = response.strip()
            
            # Try to find JSON between code blocks
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                if end != -1:
                    response = response[start:end].strip()
            elif "```" in response:
                start = response.find("```") + 3
                end = response.find("```", start)
                if end != -1:
                    response = response[start:end].strip()
            
            # Try to find JSON between curly braces if still not valid
            if not response.startswith("{"):
                start = response.find("{")
                if start != -1:
                    brace_count = 0
                    end = start
                    for i, char in enumerate(response[start:]):
                        if char == "{":
                            brace_count += 1
                        elif char == "}":
                            brace_count -= 1
                            if brace_count == 0:
                                end = start + i + 1
                                break
                    response = response[start:end]
            
            response = response.strip()
            
            # Log the cleaned response
            logger.debug(f"Cleaned JSON response: {response[:500]}")
            
            if not response:
                raise LLMException("Empty response after cleaning")
            
            return json.loads(response)
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {str(e)}")
            if 'response' in locals():
                logger.error(f"Response content: {response[:1000]}")
            raise LLMException(f"Invalid JSON response: {str(e)}")
        except Exception as e:
            logger.error(f"JSON generation error: {str(e)}")
            raise
    
    def _extract_retry_delay(self, error_message: str) -> float:
        """Extract retry delay from error message."""
        patterns = [
            r'retry in ([\d.]+)s',
            r'retryDelay[^\d]*(\d+)',
            r'RetryInfo.*?(\d+)s',
            r'after (\d+) seconds'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, error_message, re.IGNORECASE)
            if match:
                try:
                    delay = float(match.group(1))
                    logger.info(f"Extracted retry delay: {delay} seconds")
                    return delay
                except ValueError:
                    continue
        
        return 15.0
    
    async def generate_with_retry(
        self,
        messages: list[dict[str, str]],
        max_retries: int = 3,
        **kwargs
    ) -> str:
        """Generate with automatic retry and rate limiting."""
        last_error = None
        
        for attempt in range(max_retries):
            try:
                return await self.generate(messages, **kwargs)
            except LLMException as e:
                last_error = e
                error_str = str(e)
                
                if "CONNECTION_ERROR" in error_str or "TIMEOUT_ERROR" in error_str:
                    # Connection errors - retry immediately with short delay
                    retry_delay = min(2 ** attempt, 10)  # Max 10 seconds
                    logger.warning(f"Connection error. Waiting {retry_delay}s before retry {attempt + 1}/{max_retries}")
                    await asyncio.sleep(retry_delay)
                elif "429" in error_str or "RATE_LIMITED" in error_str:
                    retry_delay = self._extract_retry_delay(error_str)
                    logger.warning(f"Rate limit hit (429). Waiting {retry_delay}s before retry {attempt + 1}/{max_retries}")
                    await asyncio.sleep(retry_delay)
                elif attempt < max_retries - 1:
                    backoff = min(2 ** attempt, 30)  # Cap at 30 seconds
                    logger.warning(f"Attempt {attempt + 1}/{max_retries} failed: {str(e)}. Retrying in {backoff}s")
                    await asyncio.sleep(backoff)
                else:
                    logger.error(f"Attempt {attempt + 1}/{max_retries} failed: {str(e)}")
        
        raise LLMException(f"Failed after {max_retries} attempts: {str(last_error)}")
