"""Message enrichment pipeline."""


from chatx.enrichment.llm_client import LLMClient
from chatx.schemas.enrichment import EnrichmentMessage
from chatx.schemas.message import CanonicalMessage


class MessageEnricher:
    """Pipeline for enriching messages with LLM metadata."""
    
    def __init__(self, client: LLMClient) -> None:
        """Initialize message enricher.
        
        Args:
            client: LLM client for processing
        """
        self.client = client
    
    def enrich(self, messages: list[CanonicalMessage]) -> list[EnrichmentMessage]:
        """Enrich messages with metadata.
        
        Args:
            messages: List of canonical messages to enrich
            
        Returns:
            List of enrichment results
        """
        return self.client.enrich_messages(messages)
