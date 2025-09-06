"""Neo4j graph database implementation for conversation relationship modeling."""

import logging
from typing import List, Dict, Any, Optional
import asyncio
from datetime import datetime, timezone

try:
    from neo4j import GraphDatabase, Driver, AsyncDriver
    from neo4j.exceptions import ServiceUnavailable, AuthError
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False

from .base import (
    BaseGraphStore, 
    ConversationGraph,
    GraphNode,
    GraphRelationship,
    PatternMatch,
    TemporalEvolution,
    RelationshipTypes,
    PatternTypes
)
from .psychology_relationship_mapper import PsychologyRelationshipMapper, RelationshipContext


logger = logging.getLogger(__name__)


class Neo4jGraphStore(BaseGraphStore):
    """Neo4j implementation of graph storage for conversation relationships."""

    def __init__(self, uri: str, auth: tuple[str, str], database: str = "neo4j"):
        """Initialize Neo4j graph store.
        
        Args:
            uri: Neo4j connection URI (e.g., "bolt://localhost:7687")
            auth: Authentication tuple (username, password)
            database: Database name
            
        Raises:
            ImportError: If neo4j driver not available
        """
        if not NEO4J_AVAILABLE:
            raise ImportError(
                "neo4j driver is required for graph storage. "
                "Install with: pip install neo4j"
            )
        
        self.uri = uri
        self.auth = auth
        self.database = database
        self.driver: Optional[Driver] = None
        self.psychology_mapper = PsychologyRelationshipMapper()
    
    async def connect(self) -> None:
        """Connect to Neo4j database.
        
        Raises:
            ConnectionError: If connection fails
            AuthError: If authentication fails
        """
        try:
            self.driver = GraphDatabase.driver(self.uri, auth=self.auth)
            
            # Test connection
            with self.driver.session(database=self.database) as session:
                session.run("RETURN 1")
            
            logger.info(f"Connected to Neo4j at {self.uri}")
            
        except ServiceUnavailable as e:
            raise ConnectionError(f"Cannot connect to Neo4j at {self.uri}: {e}")
        except AuthError as e:
            raise ConnectionError(f"Authentication failed for Neo4j: {e}")
        except Exception as e:
            raise ConnectionError(f"Neo4j connection error: {e}")
    
    async def disconnect(self) -> None:
        """Disconnect from Neo4j database."""
        if self.driver:
            self.driver.close()
            self.driver = None
            logger.info("Disconnected from Neo4j")
    
    async def create_graph(self, conversation_id: str, 
                          chunks: List[Dict[str, Any]]) -> ConversationGraph:
        """Create conversation graph from message chunks.
        
        Args:
            conversation_id: Unique conversation identifier
            chunks: List of conversation chunks with metadata
            
        Returns:
            ConversationGraph representing the conversation structure
        """
        if not self.driver:
            await self.connect()
        
        nodes = []
        relationships = []
        
        # Create nodes from chunks
        for chunk in chunks:
            node = self._chunk_to_node(chunk)
            nodes.append(node)
        
        # Create relationships between messages
        relationships = await self._create_relationships(chunks)
        
        # Store in Neo4j
        await self._store_graph_in_neo4j(conversation_id, nodes, relationships)
        
        return ConversationGraph(
            conversation_id=conversation_id,
            nodes=nodes,
            relationships=relationships,
            metadata={
                "created_at": datetime.now(timezone.utc).isoformat(),
                "chunk_count": len(chunks),
                "node_count": len(nodes),
                "relationship_count": len(relationships)
            }
        )
    
    async def get_conversation_graph(self, conversation_id: str) -> Optional[ConversationGraph]:
        """Retrieve conversation graph from Neo4j.
        
        Args:
            conversation_id: Conversation to retrieve
            
        Returns:
            ConversationGraph if found, None otherwise
        """
        if not self.driver:
            await self.connect()
        
        try:
            with self.driver.session(database=self.database) as session:
                # Query nodes
                node_query = """
                MATCH (n {conversation_id: $conv_id})
                RETURN n.id as id, n.node_type as type, properties(n) as props
                """
                node_result = session.run(node_query, conv_id=conversation_id)
                
                nodes = []
                for record in node_result:
                    node = GraphNode(
                        id=record["id"],
                        node_type=record["type"],
                        properties=record["props"]
                    )
                    nodes.append(node)
                
                if not nodes:
                    return None
                
                # Query relationships
                rel_query = """
                MATCH (a {conversation_id: $conv_id})-[r]->(b {conversation_id: $conv_id})
                RETURN a.id as from_id, b.id as to_id, type(r) as rel_type, properties(r) as props
                """
                rel_result = session.run(rel_query, conv_id=conversation_id)
                
                relationships = []
                for record in rel_result:
                    rel = GraphRelationship(
                        from_node=record["from_id"],
                        to_node=record["to_id"],
                        relationship_type=record["rel_type"],
                        properties=record["props"]
                    )
                    relationships.append(rel)
                
                return ConversationGraph(
                    conversation_id=conversation_id,
                    nodes=nodes,
                    relationships=relationships,
                    metadata={"retrieved_at": datetime.now(timezone.utc).isoformat()}
                )
                
        except Exception as e:
            logger.error(f"Error retrieving conversation graph {conversation_id}: {e}")
            return None
    
    async def query_relationships(self, conversation_id: str,
                                relationship_types: Optional[List[str]] = None,
                                node_properties: Optional[Dict[str, Any]] = None) -> List[GraphRelationship]:
        """Query relationships based on criteria."""
        if not self.driver:
            await self.connect()
        
        # Build dynamic query
        where_clauses = ["a.conversation_id = $conv_id", "b.conversation_id = $conv_id"]
        params = {"conv_id": conversation_id}
        
        if relationship_types:
            rel_filter = " OR ".join([f"type(r) = '{t}'" for t in relationship_types])
            where_clauses.append(f"({rel_filter})")
        
        if node_properties:
            for key, value in node_properties.items():
                where_clauses.append(f"(a.{key} = ${key}_prop OR b.{key} = ${key}_prop)")
                params[f"{key}_prop"] = value
        
        query = f"""
        MATCH (a)-[r]->(b)
        WHERE {' AND '.join(where_clauses)}
        RETURN a.id as from_id, b.id as to_id, type(r) as rel_type, properties(r) as props
        """
        
        try:
            with self.driver.session(database=self.database) as session:
                result = session.run(query, **params)
                
                relationships = []
                for record in result:
                    rel = GraphRelationship(
                        from_node=record["from_id"],
                        to_node=record["to_id"], 
                        relationship_type=record["rel_type"],
                        properties=record["props"]
                    )
                    relationships.append(rel)
                
                return relationships
                
        except Exception as e:
            logger.error(f"Error querying relationships: {e}")
            return []
    
    async def detect_patterns(self, conversation_id: str,
                            pattern_types: Optional[List[str]] = None) -> List[PatternMatch]:
        """Detect relationship patterns in conversation."""
        if not self.driver:
            await self.connect()
        
        patterns = []
        target_types = pattern_types or PatternTypes.get_all_types()
        
        for pattern_type in target_types:
            pattern_matches = await self._detect_specific_pattern(conversation_id, pattern_type)
            patterns.extend(pattern_matches)
        
        return patterns
    
    async def get_temporal_evolution(self, conversation_id: str,
                                   time_window_days: int = 30) -> TemporalEvolution:
        """Analyze temporal evolution of relationship patterns."""
        if not self.driver:
            await self.connect()
        
        # Query for temporal analysis
        query = """
        MATCH (n {conversation_id: $conv_id})
        WHERE n.timestamp IS NOT NULL
        WITH n ORDER BY n.timestamp
        RETURN 
            n.timestamp as timestamp,
            n.psychology_labels_coarse as psychology_labels,
            n.boundary_signal as boundary_signal,
            n.repair_attempt as repair_attempt
        """
        
        try:
            with self.driver.session(database=self.database) as session:
                result = session.run(query, conv_id=conversation_id)
                
                evolution_data = []
                for record in result:
                    evolution_data.append({
                        "timestamp": record["timestamp"],
                        "psychology_labels": record["psychology_labels"] or [],
                        "boundary_signal": record["boundary_signal"],
                        "repair_attempt": record["repair_attempt"]
                    })
                
                # Analyze trends
                trend_analysis = self._analyze_trends(evolution_data, time_window_days)
                
                return TemporalEvolution(
                    conversation_id=conversation_id,
                    time_window={"days": time_window_days},
                    evolution_metrics=trend_analysis["metrics"],
                    pattern_changes=trend_analysis["changes"],
                    trend_analysis=trend_analysis["analysis"]
                )
                
        except Exception as e:
            logger.error(f"Error analyzing temporal evolution: {e}")
            return TemporalEvolution(
                conversation_id=conversation_id,
                time_window={"days": time_window_days},
                evolution_metrics={},
                pattern_changes=[],
                trend_analysis={"error": str(e)}
            )
    
    def _chunk_to_node(self, chunk: Dict[str, Any]) -> GraphNode:
        """Convert conversation chunk to graph node."""
        chunk_id = chunk.get("chunk_id", "")
        
        # Extract psychology properties
        meta = chunk.get("meta", {})
        properties = {
            "conversation_id": meta.get("contact", ""),
            "text": chunk.get("text", ""),
            "timestamp": meta.get("date_start", ""),
            "message_ids": meta.get("message_ids", []),
            "psychology_labels_coarse": meta.get("labels_coarse", []),
            "platform": meta.get("platform", "")
        }
        
        return GraphNode(
            id=chunk_id,
            node_type="chunk",
            properties=properties
        )
    
    async def _create_relationships(self, chunks: List[Dict[str, Any]]) -> List[GraphRelationship]:
        """Create relationships between conversation chunks."""
        relationships = []
        
        # Sort chunks by timestamp for temporal relationships
        sorted_chunks = sorted(chunks, key=lambda c: c.get("meta", {}).get("date_start", ""))
        
        for i in range(len(sorted_chunks) - 1):
            current_chunk = sorted_chunks[i]
            next_chunk = sorted_chunks[i + 1]
            
            # Create FOLLOWS relationship
            rel = GraphRelationship(
                from_node=current_chunk.get("chunk_id", ""),
                to_node=next_chunk.get("chunk_id", ""),
                relationship_type=RelationshipTypes.FOLLOWS,
                properties={
                    "temporal_sequence": i + 1,
                    "time_gap": self._calculate_time_gap(current_chunk, next_chunk)
                }
            )
            relationships.append(rel)
            
            # Check for psychology-specific relationships
            psych_rels = self._detect_psychology_relationships(current_chunk, next_chunk)
            relationships.extend(psych_rels)
        
        return relationships
    
    def _detect_psychology_relationships(self, chunk1: Dict[str, Any], 
                                       chunk2: Dict[str, Any]) -> List[GraphRelationship]:
        """Detect psychology-specific relationships between chunks using enhanced mapper."""
        relationships = []
        
        # Extract psychology labels
        labels1 = chunk1.get("meta", {}).get("labels_coarse", [])
        labels2 = chunk2.get("meta", {}).get("labels_coarse", [])
        
        # Detect relationship context from combined labels
        combined_labels = list(set(labels1 + labels2))
        relationship_context = self.psychology_mapper.detect_relationship_context(combined_labels)
        
        # Map labels to relationships using enhanced mapper
        detected_relationships = self.psychology_mapper.map_labels_to_relationships(
            chunk1_labels=labels1,
            chunk2_labels=labels2,
            relationship_context=relationship_context,
            temporal_sequence=True
        )
        
        # Create GraphRelationship objects for each detected relationship
        for relationship_type, confidence in detected_relationships:
            # Get explanation for this relationship
            explanation = self.psychology_mapper.get_relationship_explanation(
                relationship_type, labels1 + labels2
            )
            
            rel = GraphRelationship(
                from_node=chunk1.get("chunk_id", ""),
                to_node=chunk2.get("chunk_id", ""),
                relationship_type=relationship_type,
                properties={
                    "confidence": confidence,
                    "context": relationship_context.value,
                    "source_labels_1": labels1,
                    "source_labels_2": labels2,
                    "explanation": explanation,
                    "detection_method": "psychology_mapper_v1"
                }
            )
            relationships.append(rel)
            
            # Log significant relationships for observability
            if confidence > 0.7:
                logger.info(f"High-confidence relationship detected: {relationship_type} "
                           f"(confidence: {confidence:.2f}, context: {relationship_context.value})")
        
        return relationships
    
    def _calculate_time_gap(self, chunk1: Dict[str, Any], chunk2: Dict[str, Any]) -> int:
        """Calculate time gap between chunks in seconds."""
        try:
            time1 = chunk1.get("meta", {}).get("date_start", "")
            time2 = chunk2.get("meta", {}).get("date_start", "")
            
            if time1 and time2:
                dt1 = datetime.fromisoformat(time1.replace('Z', '+00:00'))
                dt2 = datetime.fromisoformat(time2.replace('Z', '+00:00'))
                return int((dt2 - dt1).total_seconds())
        except Exception:
            pass
        
        return 0
    
    async def _store_graph_in_neo4j(self, conversation_id: str, 
                                  nodes: List[GraphNode], 
                                  relationships: List[GraphRelationship]) -> None:
        """Store graph nodes and relationships in Neo4j."""
        if not self.driver:
            return
        
        try:
            with self.driver.session(database=self.database) as session:
                # Clear existing graph for this conversation
                session.run(
                    "MATCH (n {conversation_id: $conv_id}) DETACH DELETE n",
                    conv_id=conversation_id
                )
                
                # Create nodes
                for node in nodes:
                    node_props = node.properties.copy()
                    node_props["id"] = node.id
                    node_props["node_type"] = node.node_type
                    
                    session.run(
                        "CREATE (n:ConversationNode $props)",
                        props=node_props
                    )
                
                # Create relationships
                for rel in relationships:
                    rel_props = rel.properties.copy()
                    
                    session.run(f"""
                        MATCH (a {{id: $from_id}}), (b {{id: $to_id}})
                        CREATE (a)-[r:`{rel.relationship_type}` $props]->(b)
                    """, from_id=rel.from_node, to_id=rel.to_node, props=rel_props)
                
                logger.info(f"Stored graph for {conversation_id}: {len(nodes)} nodes, {len(relationships)} relationships")
                
        except Exception as e:
            logger.error(f"Error storing graph in Neo4j: {e}")
    
    async def _detect_specific_pattern(self, conversation_id: str, 
                                     pattern_type: str) -> List[PatternMatch]:
        """Detect a specific type of pattern."""
        if pattern_type == PatternTypes.ESCALATION_CYCLE:
            return await self._detect_escalation_pattern(conversation_id)
        elif pattern_type == PatternTypes.REPAIR_CYCLE:
            return await self._detect_repair_pattern(conversation_id)
        elif pattern_type == PatternTypes.BOUNDARY_TESTING:
            return await self._detect_boundary_testing_pattern(conversation_id)
        else:
            return []
    
    async def _detect_escalation_pattern(self, conversation_id: str) -> List[PatternMatch]:
        """Detect escalation patterns in conversation."""
        query = """
        MATCH path = (a {conversation_id: $conv_id})-[:ESCALATES_FROM*2..5]->(b {conversation_id: $conv_id})
        RETURN nodes(path) as escalation_nodes, length(path) as escalation_length
        """
        
        try:
            with self.driver.session(database=self.database) as session:
                result = session.run(query, conv_id=conversation_id)
                
                patterns = []
                for record in result:
                    nodes = record["escalation_nodes"]
                    length = record["escalation_length"]
                    
                    pattern = PatternMatch(
                        pattern_type=PatternTypes.ESCALATION_CYCLE,
                        confidence=min(0.7 + (length * 0.1), 1.0),  # Higher confidence for longer chains
                        nodes_involved=[node["id"] for node in nodes],
                        relationships_involved=[],  # Would need more complex query
                        temporal_span={"escalation_length": length},
                        properties={"escalation_chain_length": length}
                    )
                    patterns.append(pattern)
                
                return patterns
                
        except Exception as e:
            logger.error(f"Error detecting escalation pattern: {e}")
            return []
    
    async def _detect_repair_pattern(self, conversation_id: str) -> List[PatternMatch]:
        """Detect repair cycle patterns."""
        query = """
        MATCH (conflict {conversation_id: $conv_id})-[:REPAIRS_AFTER]->(repair {conversation_id: $conv_id})
        RETURN conflict.id as conflict_id, repair.id as repair_id
        """
        
        try:
            with self.driver.session(database=self.database) as session:
                result = session.run(query, conv_id=conversation_id)
                
                patterns = []
                for record in result:
                    pattern = PatternMatch(
                        pattern_type=PatternTypes.REPAIR_CYCLE,
                        confidence=0.8,
                        nodes_involved=[record["conflict_id"], record["repair_id"]],
                        relationships_involved=["REPAIRS_AFTER"],
                        temporal_span={"repair_sequence": 2},
                        properties={"has_repair_attempt": True}
                    )
                    patterns.append(pattern)
                
                return patterns
                
        except Exception as e:
            logger.error(f"Error detecting repair pattern: {e}")
            return []
    
    async def _detect_boundary_testing_pattern(self, conversation_id: str) -> List[PatternMatch]:
        """Detect boundary testing patterns."""
        query = """
        MATCH path = (a {conversation_id: $conv_id})-[:BOUNDARY_TESTS*2..]->(b {conversation_id: $conv_id})
        RETURN nodes(path) as boundary_nodes, length(path) as test_count
        """
        
        try:
            with self.driver.session(database=self.database) as session:
                result = session.run(query, conv_id=conversation_id)
                
                patterns = []
                for record in result:
                    nodes = record["boundary_nodes"]
                    test_count = record["test_count"]
                    
                    pattern = PatternMatch(
                        pattern_type=PatternTypes.BOUNDARY_TESTING,
                        confidence=min(0.6 + (test_count * 0.15), 1.0),
                        nodes_involved=[node["id"] for node in nodes],
                        relationships_involved=["BOUNDARY_TESTS"],
                        temporal_span={"boundary_tests": test_count},
                        properties={"repeated_boundary_violations": test_count >= 3}
                    )
                    patterns.append(pattern)
                
                return patterns
                
        except Exception as e:
            logger.error(f"Error detecting boundary testing pattern: {e}")
            return []
    
    def _analyze_trends(self, evolution_data: List[Dict[str, Any]], 
                       time_window_days: int) -> Dict[str, Any]:
        """Analyze trends in relationship evolution."""
        if not evolution_data:
            return {"metrics": {}, "changes": [], "analysis": {}}
        
        # Basic trend analysis
        total_events = len(evolution_data)
        boundary_events = sum(1 for item in evolution_data if item.get("boundary_signal"))
        repair_attempts = sum(1 for item in evolution_data if item.get("repair_attempt"))
        
        # Calculate frequency patterns
        psychology_label_freq = {}
        for item in evolution_data:
            for label in item.get("psychology_labels", []):
                psychology_label_freq[label] = psychology_label_freq.get(label, 0) + 1
        
        return {
            "metrics": {
                "total_events": total_events,
                "boundary_events": boundary_events,
                "repair_attempts": repair_attempts,
                "boundary_to_repair_ratio": repair_attempts / max(boundary_events, 1)
            },
            "changes": [
                {
                    "type": "boundary_pattern",
                    "frequency": boundary_events / total_events if total_events > 0 else 0
                },
                {
                    "type": "repair_pattern",
                    "frequency": repair_attempts / total_events if total_events > 0 else 0
                }
            ],
            "analysis": {
                "dominant_psychology_labels": psychology_label_freq,
                "relationship_health_indicator": repair_attempts / max(boundary_events, 1),
                "pattern_stability": "stable" if len(set(psychology_label_freq.keys())) < 3 else "variable"
            }
        }