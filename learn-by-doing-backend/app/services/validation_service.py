"""Resource validation service."""
import asyncio
from typing import List, Dict, Any
import httpx
from app.config import get_settings
from app.core.logging import logger


class ResourceValidator:
    """Validates resource URLs are accessible."""
    
    def __init__(self):
        settings = get_settings()
        self.timeout = settings.VALIDATION_TIMEOUT
        self.client = httpx.AsyncClient(
            timeout=self.timeout,
            follow_redirects=True,
            headers={
                "User-Agent": "LearnByDoing-Validator/1.0"
            }
        )
    
    async def validate_url(self, url: str) -> Dict[str, Any]:
        """
        Validate a single URL.
        
        Returns:
            Dict with validation results
        """
        try:
            # Try HEAD request first
            response = await self.client.head(url)
            
            # If HEAD fails, try GET
            if response.status_code >= 400:
                response = await self.client.get(url)
            
            return {
                "url": url,
                "accessible": response.status_code < 400,
                "status_code": response.status_code,
                "content_type": response.headers.get("content-type", "unknown"),
                "error": None
            }
            
        except httpx.TimeoutException:
            return {
                "url": url,
                "accessible": False,
                "status_code": None,
                "content_type": None,
                "error": "Timeout"
            }
        except Exception as e:
            return {
                "url": url,
                "accessible": False,
                "status_code": None,
                "content_type": None,
                "error": str(e)
            }
    
    async def validate_batch(
        self,
        resources: List[Dict[str, Any]],
        max_concurrent: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Validate multiple URLs concurrently.
        
        Args:
            resources: List of resource dicts with 'url' key
            max_concurrent: Maximum concurrent validations
        
        Returns:
            List of validation results
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def validate_with_limit(resource: Dict[str, Any]) -> Dict[str, Any]:
            async with semaphore:
                result = await self.validate_url(resource["url"])
                result["resource_title"] = resource.get("title", "Unknown")
                return result
        
        # Create tasks
        tasks = [validate_with_limit(r) for r in resources]
        
        # Run concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "url": resources[i]["url"],
                    "accessible": False,
                    "error": str(result),
                    "resource_title": resources[i].get("title", "Unknown")
                })
            else:
                processed_results.append(result)
        
        # Log summary
        accessible_count = sum(1 for r in processed_results if r["accessible"])
        logger.info(
            f"Resource validation complete: "
            f"{accessible_count}/{len(processed_results)} accessible"
        )
        
        return processed_results
    
    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()
