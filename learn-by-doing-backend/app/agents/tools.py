"""Web search utilities using DuckDuckGo."""
import asyncio
from typing import List, Dict, Any, Optional
from app.core.logging import logger
from app.config import get_settings


class WebSearchClient:
    """Client for web search using DuckDuckGo (free, no API key)."""
    
    def __init__(self):
        # Lazy import to avoid nest_asyncio patching uvloop at module load
        from ddgs import DDGS
        self.ddgs = DDGS()
        logger.info("Initialized DuckDuckGo search client")
    
    async def search(
        self,
        query: str,
        max_results: int = 10,
        region: str = "us-en",
        safesearch: str = "moderate",
        backend: str = "auto"
    ) -> List[Dict[str, Any]]:
        """
        Search the web using DuckDuckGo.
        
        Args:
            query: Search query
            max_results: Maximum results to return
            region: Region code (e.g., us-en, wt-wt for worldwide)
            safesearch: on, moderate, off
            backend: auto, html, or lite
        
        Returns:
            List of search results with title, url, snippet
        """
        try:
            logger.info(f"Searching DuckDuckGo: {query}")
            
            results = []
            search_results = self.ddgs.text(
                query,
                region=region,
                safesearch=safesearch,
                max_results=max_results,
                backend=backend
            )
            
            for result in search_results:
                results.append({
                    "title": result.get("title", ""),
                    "url": result.get("href", ""),
                    "snippet": result.get("body", ""),
                    "source": "duckduckgo"
                })
            
            logger.info(f"Found {len(results)} search results")
            return results
            
        except Exception as e:
            logger.error(f"DuckDuckGo search error: {str(e)}")
            return []
    
    async def search_documentation(
        self,
        topic: str,
        max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search specifically for documentation.
        
        Args:
            topic: Topic to search
            max_results: Max results
        
        Returns:
            Filtered documentation results
        """
        # Search for documentation
        query = f"{topic} official documentation site:docs. OR site:documentation."
        results = await self.search(query, max_results=max_results * 2)
        
        # Filter for likely documentation
        doc_keywords = ["docs", "documentation", "reference", "api", "guide"]
        filtered = []
        
        for result in results:
            url = result.get("url", "").lower()
            title = result.get("title", "").lower()
            
            # Check if it looks like documentation
            is_doc = any(keyword in url or keyword in title for keyword in doc_keywords)
            
            if is_doc:
                filtered.append(result)
                if len(filtered) >= max_results:
                    break
        
        return filtered[:max_results]
    
    async def search_with_fallback(
        self,
        queries: List[str],
        max_results_per_query: int = 3,
        delay_between_searches: float = 1.0
    ) -> List[Dict[str, Any]]:
        """
        Search multiple queries and combine results.
        
        Args:
            queries: List of search queries
            max_results_per_query: Max results per query
            delay_between_searches: Delay in seconds between searches to avoid rate limiting
        
        Returns:
            Combined unique results
        """
        all_results = []
        seen_urls = set()
        
        for i, query in enumerate(queries):
            try:
                # Add delay between searches (except first one)
                if i > 0 and delay_between_searches > 0:
                    logger.debug(f"Waiting {delay_between_searches}s before next search...")
                    await asyncio.sleep(delay_between_searches)
                
                results = await self.search(query, max_results=max_results_per_query)
                
                for result in results:
                    url = result.get("url", "")
                    if url and url not in seen_urls:
                        seen_urls.add(url)
                        all_results.append(result)
                        
            except Exception as e:
                logger.warning(f"Search failed for query '{query}': {str(e)}")
                continue
        
        return all_results
    
    async def get_latest_info(self, topic: str) -> Dict[str, Any]:
        """
        Get latest information about a topic.
        
        Args:
            topic: Topic to research
        
        Returns:
            Structured information
        """
        queries = [
            f"{topic} what is it used for",
            f"{topic} tutorial getting started",
            f"{topic} official website",
            f"{topic} best practices 2024",
            f"{topic} vs alternatives comparison"
        ]
        
        results = await self.search_with_fallback(
            queries, 
            max_results_per_query=2,
            delay_between_searches=2.0  # 2 second delay to avoid rate limits
        )
        
        return {
            "topic": topic,
            "search_results": results,
            "total_results": len(results)
        }


# Singleton instance
_search_client = None


def get_search_client() -> WebSearchClient:
    """Get or create search client."""
    global _search_client
    if _search_client is None:
        _search_client = WebSearchClient()
    return _search_client
