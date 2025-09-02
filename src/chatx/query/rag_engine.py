"""RAG (Retrieval-Augmented Generation) engine for query processing."""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from .simple_ollama import SimpleOllamaClient, SimpleLLMConfig
from chatx.indexing.vector_store import ChromaDBVectorStore, IndexingConfig, SearchResult

from .citation_manager import Citation, CitationManager

logger = logging.getLogger(__name__)


@dataclass
class QueryConfig:
    """Configuration for RAG queries."""
    # Retrieval settings
    k: int = 10  # Number of chunks to retrieve
    min_score_threshold: float = 0.1  # Minimum relevance score
    max_context_chunks: int = 5  # Maximum chunks to include in LLM context
    
    # LLM settings
    model_name: str = "gemma2:9b-instruct-q4_K_M"
    temperature: float = 0.3
    max_output_tokens: int = 800
    timeout_seconds: int = 30
    
    # Context settings
    include_timestamps: bool = True
    include_platform_info: bool = True
    snippet_length: int = 300
    
    # Privacy settings
    allow_cloud: bool = False
    backend: str = "local"  # local, cloud, hybrid


@dataclass
class QueryResponse:
    """Response from RAG query."""
    answer: str
    citations: list[Citation] = field(default_factory=list)
    query: str = ""
    contact: str = ""
    filters: dict[str, Any] = field(default_factory=dict)
    
    # Metadata
    retrieval_stats: dict[str, Any] = field(default_factory=dict)
    llm_stats: dict[str, Any] = field(default_factory=dict)
    processing_time_ms: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert response to dictionary."""
        return {
            "answer": self.answer,
            "citations": [c.to_dict() for c in self.citations],
            "query": self.query,
            "contact": self.contact,
            "filters": self.filters,
            "retrieval_stats": self.retrieval_stats,
            "llm_stats": self.llm_stats,
            "processing_time_ms": self.processing_time_ms,
            "timestamp": self.timestamp.isoformat(),
        }


class RAGEngine:
    """RAG engine for answering queries with citations."""
    
    def __init__(
        self,
        vector_store: ChromaDBVectorStore | None = None,
        ollama_client: SimpleOllamaClient | None = None,
        config: QueryConfig | None = None
    ):
        """Initialize RAG engine.
        
        Args:
            vector_store: Vector store for retrieval
            ollama_client: LLM client for generation
            config: Query configuration
        """
        self.config = config or QueryConfig()
        
        # Initialize vector store
        if vector_store is None:
            indexing_config = IndexingConfig(persist_directory="./.chroma_db")
            self.vector_store = ChromaDBVectorStore(indexing_config)
        else:
            self.vector_store = vector_store
        
        # Initialize LLM client
        if ollama_client is None:
            llm_config = SimpleLLMConfig(
                model_name=self.config.model_name,
                temperature=self.config.temperature,
                max_output_tokens=self.config.max_output_tokens,
            )
            self.ollama_client = SimpleOllamaClient(llm_config)
        else:
            self.ollama_client = ollama_client
        
        self.citation_manager = CitationManager()
        logger.info(f"Initialized RAG engine with model: {self.config.model_name}")
    
    def query(
        self,
        question: str,
        contact: str,
        filters: dict[str, Any] | None = None
    ) -> QueryResponse:
        """Process a query with RAG.
        
        Args:
            question: User question
            contact: Contact identifier for scoping search
            filters: Optional search filters (date ranges, labels, etc.)
            
        Returns:
            Query response with answer and citations
        """
        start_time = datetime.now()
        
        try:
            # Step 1: Retrieve relevant context
            search_results = self._retrieve_context(question, contact, filters)
            
            if not search_results:
                return QueryResponse(
                    answer="I couldn't find any relevant information to answer your question.",
                    query=question,
                    contact=contact,
                    filters=filters or {},
                    retrieval_stats={"retrieved_chunks": 0, "search_query": question},
                    processing_time_ms=(datetime.now() - start_time).total_seconds() * 1000,
                )
            
            # Step 2: Create citations
            citations = self._create_citations(search_results)
            
            # Step 3: Generate answer
            answer, llm_stats = self._generate_answer(question, search_results)
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return QueryResponse(
                answer=answer,
                citations=citations,
                query=question,
                contact=contact,
                filters=filters or {},
                retrieval_stats={
                    "retrieved_chunks": len(search_results),
                    "search_query": question,
                    "min_score": min(r.score for r in search_results) if search_results else 0.0,
                    "max_score": max(r.score for r in search_results) if search_results else 0.0,
                },
                llm_stats=llm_stats,
                processing_time_ms=processing_time,
            )
        
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            return QueryResponse(
                answer=f"I encountered an error while processing your question: {str(e)}",
                query=question,
                contact=contact,
                filters=filters or {},
                processing_time_ms=processing_time,
            )
    
    def _retrieve_context(
        self,
        question: str,
        contact: str,
        filters: dict[str, Any] | None = None
    ) -> list[SearchResult]:
        """Retrieve relevant context chunks."""
        try:
            # Connect to vector store if needed
            if self.vector_store.client is None:
                self.vector_store.connect()
            
            # Convert filters to ChromaDB format
            chroma_filters = self._convert_filters_to_chroma(filters)
            
            # Perform search
            results = self.vector_store.search(
                query=question,
                contact=contact,
                k=self.config.k,
                filters=chroma_filters
            )
            
            # Filter by minimum score threshold
            filtered_results = [
                r for r in results
                if r.score >= self.config.min_score_threshold
            ]
            
            logger.info(f"Retrieved {len(filtered_results)} relevant chunks for query")
            return filtered_results[:self.config.max_context_chunks]
        
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return []
    
    def _convert_filters_to_chroma(self, filters: dict[str, Any] | None) -> dict[str, Any]:
        """Convert query filters to ChromaDB where clause format."""
        if not filters:
            return {}
        
        chroma_filters = {}
        
        # Handle date filters
        if "since" in filters:
            try:
                since_date = self._parse_date(filters["since"])
                chroma_filters["date_start"] = {"$gte": since_date.isoformat()}
            except ValueError as e:
                logger.warning(f"Could not parse 'since' date: {e}")
        
        if "until" in filters:
            try:
                until_date = self._parse_date(filters["until"])
                chroma_filters["date_end"] = {"$lte": until_date.isoformat()}
            except ValueError as e:
                logger.warning(f"Could not parse 'until' date: {e}")
        
        # Handle label filters
        if "labels_any" in filters and filters["labels_any"]:
            # Find chunks with any of these labels
            chroma_filters["coarse_labels"] = {"$in": filters["labels_any"]}
        
        if "labels_all" in filters and filters["labels_all"]:
            # This is more complex in ChromaDB - would need multiple queries
            logger.warning("labels_all filter not fully implemented")
        
        if "labels_not" in filters and filters["labels_not"]:
            # Exclude chunks with these labels
            chroma_filters["coarse_labels"] = {"$nin": filters["labels_not"]}
        
        # Handle platform filter
        if "platform" in filters:
            chroma_filters["platform"] = filters["platform"]
        
        return chroma_filters
    
    def _parse_date(self, date_str: str) -> datetime:
        """Parse date string to datetime object."""
        # Try common date formats
        for fmt in ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"]:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        # Try ISO format
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except ValueError:
            pass
        
        raise ValueError(f"Could not parse date: {date_str}")
    
    def _create_citations(self, search_results: list[SearchResult]) -> list[Citation]:
        """Create citations from search results."""
        self.citation_manager.clear()
        
        for result in search_results:
            self.citation_manager.add_citation(
                chunk_id=result.chunk_id,
                message_ids=result.message_ids,
                score=result.score,
                text=result.text,
                metadata=result.metadata,
                max_snippet_length=self.config.snippet_length,
            )
        
        return self.citation_manager.get_citations()
    
    def _generate_answer(
        self,
        question: str,
        search_results: list[SearchResult]
    ) -> tuple[str, dict[str, Any]]:
        """Generate answer using LLM with retrieved context."""
        
        # Format context from search results
        context = self._format_context_for_prompt(search_results)
        
        # Create prompt
        prompt = self._create_qa_prompt(question, context)
        
        try:
            # Generate response
            start_time = datetime.now()
            response_text = self.ollama_client.generate(prompt)
            generation_time = (datetime.now() - start_time).total_seconds() * 1000
            
            # Estimate token counts (rough approximation)
            input_tokens = len(prompt.split()) * 1.3  # Approximate tokens
            output_tokens = len(response_text.split()) * 1.3
            
            llm_stats = {
                "model": self.config.model_name,
                "generation_time_ms": generation_time,
                "input_tokens_approx": int(input_tokens),
                "output_tokens_approx": int(output_tokens),
                "temperature": self.config.temperature,
            }
            
            return response_text.strip(), llm_stats
        
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            return f"I encountered an error generating the answer: {str(e)}", {}
    
    def _format_context_for_prompt(self, search_results: list[SearchResult]) -> str:
        """Format search results into context for LLM prompt."""
        if not search_results:
            return "No relevant context found."
        
        context_parts = []
        for i, result in enumerate(search_results[:self.config.max_context_chunks], 1):
            # Extract timestamp if available
            timestamp_str = ""
            if self.config.include_timestamps and result.metadata.get("date_start"):
                try:
                    date_start = result.metadata["date_start"]
                    timestamp_str = f" ({date_start[:10]})"  # Just the date part
                except (ValueError, KeyError):
                    pass
            
            # Extract platform if available
            platform_str = ""
            if self.config.include_platform_info and result.metadata.get("platform"):
                platform_str = f" [{result.metadata['platform']}]"
            
            context_parts.append(
                f"Context {i}{platform_str}{timestamp_str}:\n{result.text}\n"
            )
        
        return "\n".join(context_parts)
    
    def _create_qa_prompt(self, question: str, context: str) -> str:
        """Create prompt for question answering."""
        return (
            "You are a helpful assistant that answers questions based on conversation history.\n"
            "Use only the provided context to answer the question. "
            "If the context doesn't contain relevant information, say so.\n\n"
            f"CONTEXT:\n{context}\n\n"
            f"QUESTION: {question}\n\n"
            "INSTRUCTIONS:\n"
            "- Answer based only on the provided context\n"
            "- Be concise and specific\n"
            "- If the context doesn't contain enough information, "
            'say "I don\'t have enough information to answer this question"\n'
            "- Reference specific details from the context when possible\n"
            "- Do not make assumptions beyond what's explicitly stated in the context\n\n"
            "ANSWER:"
        )
    
    def close(self) -> None:
        """Close connections."""
        if self.vector_store:
            self.vector_store.close()
        if self.ollama_client and hasattr(self.ollama_client, 'close'):
            self.ollama_client.close()
