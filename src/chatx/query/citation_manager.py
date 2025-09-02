"""Citation management for query responses."""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class Citation:
    """Represents a citation to source content."""
    chunk_id: str
    message_ids: list[str]
    score: float
    text_snippet: str
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime | None = None
    platform: str | None = None
    contact: str | None = None
    
    def to_dict(self) -> dict[str, Any]:
        """Convert citation to dictionary."""
        return {
            "chunk_id": self.chunk_id,
            "message_ids": self.message_ids,
            "score": self.score,
            "text_snippet": self.text_snippet,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "platform": self.platform,
            "contact": self.contact,
        }


class CitationManager:
    """Manages citations for query responses."""
    
    def __init__(self):
        """Initialize citation manager."""
        self.citations: list[Citation] = []
        
    def add_citation(
        self,
        chunk_id: str,
        message_ids: list[str],
        score: float,
        text: str,
        metadata: dict[str, Any] | None = None,
        max_snippet_length: int = 200
    ) -> Citation:
        """Add a citation from search results.
        
        Args:
            chunk_id: Unique chunk identifier
            message_ids: List of message IDs in this chunk
            score: Relevance score from vector search
            text: Full text content
            metadata: Additional metadata from search
            max_snippet_length: Maximum length for text snippet
            
        Returns:
            Created citation
        """
        # Create text snippet
        snippet = text[:max_snippet_length]
        if len(text) > max_snippet_length:
            snippet += "..."
        
        # Extract useful metadata
        meta = metadata or {}
        timestamp_str = meta.get("date_start")
        timestamp = None
        if timestamp_str:
            try:
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                logger.warning(f"Could not parse timestamp: {timestamp_str}")
        
        citation = Citation(
            chunk_id=chunk_id,
            message_ids=message_ids,
            score=score,
            text_snippet=snippet,
            metadata=meta,
            timestamp=timestamp,
            platform=meta.get("platform"),
            contact=meta.get("contact"),
        )
        
        self.citations.append(citation)
        return citation
    
    def get_citations(self) -> list[Citation]:
        """Get all citations sorted by relevance score."""
        return sorted(self.citations, key=lambda c: c.score, reverse=True)
    
    def get_top_citations(self, n: int = 5) -> list[Citation]:
        """Get top N citations by relevance score."""
        return self.get_citations()[:n]
    
    def get_unique_message_ids(self) -> set[str]:
        """Get all unique message IDs from citations."""
        message_ids = set()
        for citation in self.citations:
            message_ids.update(citation.message_ids)
        return message_ids
    
    def format_citations_for_prompt(self, max_citations: int = 5) -> str:
        """Format citations for inclusion in LLM prompt.
        
        Args:
            max_citations: Maximum number of citations to include
            
        Returns:
            Formatted citation text for prompt
        """
        top_citations = self.get_top_citations(max_citations)
        if not top_citations:
            return "No relevant context found."
        
        formatted_parts = []
        for i, citation in enumerate(top_citations, 1):
            timestamp_str = ""
            if citation.timestamp:
                timestamp_str = f" ({citation.timestamp.strftime('%Y-%m-%d %H:%M')})"
            
            platform_str = f" [{citation.platform}]" if citation.platform else ""
            
            formatted_parts.append(
                f"[Context {i}]{platform_str}{timestamp_str}:\n{citation.text_snippet}\n"
            )
        
        return "\n".join(formatted_parts)
    
    def clear(self) -> None:
        """Clear all citations."""
        self.citations.clear()
    
    def to_dict(self) -> dict[str, Any]:
        """Convert citations to dictionary format."""
        return {
            "citations": [c.to_dict() for c in self.get_citations()],
            "total_citations": len(self.citations),
            "unique_message_count": len(self.get_unique_message_ids()),
        }
