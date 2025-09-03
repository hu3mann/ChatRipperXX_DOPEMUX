"""Hierarchical context bridge for privacy-preserving cloud processing with maximum context."""

import json
import logging
import hashlib
import secrets
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import numpy as np
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class AbstractionLevel(Enum):
    """Levels of abstraction for hierarchical context processing."""
    LEVEL_1_FULL = "full_detail"        # Local only - complete fine-grained analysis
    LEVEL_2_MEDIUM = "medium_abstract"   # Edge processing - selective abstraction  
    LEVEL_3_HIGH = "high_abstract"      # Cloud safe - pattern abstractions
    LEVEL_4_PATTERN = "pattern_only"    # Cloud patterns - pure relationship dynamics


class PrivacyTier(Enum):
    """Privacy tiers for context processing."""
    LOCAL_ONLY = "local_only"
    EDGE_SAFE = "edge_safe"  
    CLOUD_SAFE = "cloud_safe"
    PATTERN_ONLY = "pattern_only"


@dataclass
class ContextSummary:
    """Privacy-safe context summary for cloud processing."""
    temporal_pattern: str
    emotional_trajectory: str
    relationship_dynamic: str
    communication_style: str
    conflict_pattern: str
    
    # Boolean flags for sensitive topics (no details)
    substance_context_present: bool = False
    intimate_context_present: bool = False
    boundary_discussion_present: bool = False
    trauma_indicators_present: bool = False
    
    # Numerical abstractions (differential privacy applied)
    emotional_intensity_score: float = 0.0  # 0-1 scale
    conflict_escalation_score: float = 0.0  # 0-1 scale
    intimacy_progression_score: float = 0.0  # 0-1 scale
    trust_stability_score: float = 0.0  # 0-1 scale
    
    # Privacy-safe tokens for fine details
    privacy_tokens: List[str] = field(default_factory=list)
    
    # Metadata
    abstraction_level: AbstractionLevel = AbstractionLevel.LEVEL_3_HIGH
    privacy_tier: PrivacyTier = PrivacyTier.CLOUD_SAFE
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class EncryptedContextVector:
    """Encrypted representation of fine-grained context for cloud processing."""
    encrypted_semantic_vector: bytes
    encrypted_emotional_vector: bytes  
    encrypted_relationship_vector: bytes
    
    # Metadata that's safe to share
    conversation_phase: str  # "opening|development|climax|resolution"
    temporal_position: int   # Hour of day (0-23)
    message_count_range: str # "1-5|6-20|21-50|50+"
    
    # Encryption metadata
    encryption_key_id: str
    vector_dimension: int
    privacy_tier: PrivacyTier = PrivacyTier.CLOUD_SAFE


@dataclass
class HierarchicalEnrichment:
    """Multi-level enrichment with hierarchical context."""
    local_analysis: Dict[str, Any]  # Full local analysis with fine labels
    context_summary: ContextSummary  # Privacy-safe abstraction
    encrypted_context: EncryptedContextVector  # Encrypted vectors for cloud
    cloud_insights: Optional[Dict[str, Any]] = None  # Enhanced cloud analysis
    
    # Integration metadata
    final_enrichment: Optional[Dict[str, Any]] = None
    privacy_validation: Dict[str, Any] = field(default_factory=dict)
    abstraction_chain: List[str] = field(default_factory=list)


class AbstractionEngine:
    """Core engine for creating privacy-safe abstractions."""
    
    def __init__(self, differential_privacy_epsilon: float = 1.0):
        """Initialize abstraction engine with differential privacy."""
        self.dp_epsilon = differential_privacy_epsilon
        self.abstraction_rules = self._load_abstraction_rules()
        self.privacy_tokenizer = PrivacyTokenizer()
        
    def _load_abstraction_rules(self) -> Dict[str, Any]:
        """Load rules for converting fine labels to abstractions."""
        return {
            # Substance abstractions
            "substance_specific": {
                "abstraction": "substance_context_present",
                "pattern_mapping": {
                    "alcohol_consumption": "social_substance_pattern",
                    "cocaine_use": "stimulant_substance_pattern", 
                    "marijuana_use": "depressant_substance_pattern",
                    "prescription_misuse": "pharmaceutical_substance_pattern"
                }
            },
            
            # Intimacy abstractions  
            "intimacy_specific": {
                "abstraction": "intimate_context_present",
                "pattern_mapping": {
                    "sexual_desire": "intimacy_physical_dimension",
                    "emotional_vulnerability": "intimacy_emotional_dimension",
                    "relationship_commitment": "intimacy_commitment_dimension",
                    "boundary_negotiation": "intimacy_boundary_dimension"
                }
            },
            
            # Conflict abstractions
            "conflict_specific": {
                "pattern_mapping": {
                    "conflict_personal_attack": "destructive_conflict_pattern",
                    "conflict_issue_focused": "constructive_conflict_pattern",
                    "conflict_avoidance": "avoidant_conflict_pattern",
                    "conflict_escalation": "escalating_conflict_pattern"
                }
            },
            
            # Trauma abstractions
            "trauma_specific": {
                "abstraction": "trauma_indicators_present",
                "pattern_mapping": {
                    "trauma_childhood": "historical_trauma_pattern",
                    "trauma_relationship": "relational_trauma_pattern",
                    "trauma_recent": "acute_trauma_pattern"
                }
            }
        }
    
    def create_context_summary(
        self, 
        local_enrichment: Dict[str, Any],
        conversation_window: List[Dict[str, Any]]
    ) -> ContextSummary:
        """Create privacy-safe context summary from local enrichment."""
        
        # Extract fine labels and metadata
        fine_labels = local_enrichment.get("fine_labels_local", [])
        coarse_labels = local_enrichment.get("labels_coarse", [])
        meta = local_enrichment.get("meta", {})
        
        # Create temporal pattern abstraction
        temporal_pattern = self._abstract_temporal_patterns(conversation_window)
        
        # Create emotional trajectory abstraction
        emotional_trajectory = self._abstract_emotional_trajectory(conversation_window)
        
        # Create relationship dynamic abstraction
        relationship_dynamic = self._abstract_relationship_dynamics(coarse_labels, fine_labels)
        
        # Create communication style abstraction
        communication_style = self._abstract_communication_style(local_enrichment)
        
        # Create conflict pattern abstraction
        conflict_pattern = self._abstract_conflict_patterns(coarse_labels, fine_labels)
        
        # Detect sensitive topic presence (boolean flags only)
        substance_present = any("substance" in label for label in fine_labels)
        intimate_present = any("intimacy" in label or "sexual" in label for label in fine_labels)
        boundary_present = any("boundary" in label for label in fine_labels)
        trauma_present = any("trauma" in label for label in fine_labels)
        
        # Calculate differential private scores
        emotional_intensity = self._calculate_dp_emotional_intensity(conversation_window)
        conflict_escalation = self._calculate_dp_conflict_escalation(conversation_window)
        intimacy_progression = self._calculate_dp_intimacy_progression(conversation_window)
        trust_stability = self._calculate_dp_trust_stability(conversation_window)
        
        # Generate privacy tokens for fine details
        privacy_tokens = self._generate_privacy_tokens(fine_labels)
        
        return ContextSummary(
            temporal_pattern=temporal_pattern,
            emotional_trajectory=emotional_trajectory,
            relationship_dynamic=relationship_dynamic,
            communication_style=communication_style,
            conflict_pattern=conflict_pattern,
            substance_context_present=substance_present,
            intimate_context_present=intimate_present,
            boundary_discussion_present=boundary_present,
            trauma_indicators_present=trauma_present,
            emotional_intensity_score=emotional_intensity,
            conflict_escalation_score=conflict_escalation,
            intimacy_progression_score=intimacy_progression,
            trust_stability_score=trust_stability,
            privacy_tokens=privacy_tokens,
            abstraction_level=AbstractionLevel.LEVEL_3_HIGH,
            privacy_tier=PrivacyTier.CLOUD_SAFE
        )
    
    def _abstract_temporal_patterns(self, conversation_window: List[Dict[str, Any]]) -> str:
        """Abstract temporal patterns from conversation window."""
        if not conversation_window:
            return "single_message_pattern"
            
        # Analyze message frequency and timing
        message_count = len(conversation_window)
        
        if message_count == 1:
            return "single_message_pattern"
        elif message_count <= 5:
            return "brief_exchange_pattern"
        elif message_count <= 20:
            return "moderate_conversation_pattern"
        elif message_count <= 50:
            return "extended_conversation_pattern"
        else:
            return "lengthy_discussion_pattern"
    
    def _abstract_emotional_trajectory(self, conversation_window: List[Dict[str, Any]]) -> str:
        """Abstract emotional trajectory across conversation."""
        if not conversation_window:
            return "neutral_stable_trajectory"
            
        # Analyze emotional patterns in conversation
        emotions = []
        for msg_data in conversation_window:
            enrichment = msg_data.get("enrichment", {})
            emotion = enrichment.get("emotion_primary", "neutral")
            emotions.append(emotion)
        
        # Create trajectory abstraction
        if len(set(emotions)) == 1:
            return f"{emotions[0]}_stable_trajectory"
        elif "anger" in emotions and "sadness" in emotions:
            return "conflict_to_sadness_trajectory"
        elif "neutral" in emotions and any(e in ["joy", "love"] for e in emotions):
            return "neutral_to_positive_trajectory"  
        elif any(e in ["anger", "fear"] for e in emotions) and "neutral" in emotions:
            return "negative_to_neutral_trajectory"
        else:
            return "mixed_emotional_trajectory"
    
    def _abstract_relationship_dynamics(self, coarse_labels: List[str], fine_labels: List[str]) -> str:
        """Abstract relationship dynamics from labels."""
        # Focus on relationship-relevant coarse labels for safety
        relationship_indicators = [
            label for label in coarse_labels 
            if any(keyword in label for keyword in ["trust", "intimacy", "conflict", "support"])
        ]
        
        if "trust_building" in coarse_labels:
            return "trust_development_dynamic"
        elif "conflict_resolution" in coarse_labels:
            return "conflict_resolution_dynamic"
        elif "intimacy_deepening" in coarse_labels:
            return "intimacy_progression_dynamic"
        elif "support_seeking" in coarse_labels:
            return "support_exchange_dynamic"
        elif len(relationship_indicators) > 2:
            return "complex_relationship_dynamic"
        else:
            return "neutral_relationship_dynamic"
    
    def _abstract_communication_style(self, enrichment: Dict[str, Any]) -> str:
        """Abstract communication style from enrichment data."""
        # Use coarse-level communication indicators
        tone = enrichment.get("tone", "neutral")
        directness = enrichment.get("directness", {}).get("val", 0.5)
        
        if directness > 0.7:
            return f"direct_{tone}_communication"
        elif directness < 0.3:
            return f"indirect_{tone}_communication"
        else:
            return f"moderate_{tone}_communication"
    
    def _abstract_conflict_patterns(self, coarse_labels: List[str], fine_labels: List[str]) -> str:
        """Abstract conflict patterns from labels."""
        conflict_labels = [label for label in coarse_labels if "conflict" in label]
        
        if not conflict_labels:
            return "no_conflict_pattern"
        elif "conflict_constructive" in conflict_labels:
            return "constructive_conflict_pattern"
        elif "conflict_destructive" in conflict_labels:
            return "destructive_conflict_pattern"
        elif "conflict_avoidance" in conflict_labels:
            return "conflict_avoidance_pattern"
        else:
            return "mixed_conflict_pattern"
    
    def _calculate_dp_emotional_intensity(self, conversation_window: List[Dict[str, Any]]) -> float:
        """Calculate emotional intensity with differential privacy."""
        if not conversation_window:
            return 0.0
            
        # Calculate base intensity
        intensities = []
        for msg_data in conversation_window:
            enrichment = msg_data.get("enrichment", {})
            emotion = enrichment.get("emotion_primary", "neutral")
            
            # Map emotions to intensity scores
            emotion_intensity = {
                "joy": 0.7, "love": 0.8, "excitement": 0.9,
                "anger": 0.9, "rage": 1.0, "frustration": 0.7,
                "sadness": 0.6, "grief": 0.8, "disappointment": 0.5,
                "fear": 0.8, "anxiety": 0.7, "worry": 0.6,
                "surprise": 0.6, "curiosity": 0.4,
                "disgust": 0.7, "contempt": 0.8,
                "neutral": 0.0, "calm": 0.2
            }.get(emotion, 0.3)
            
            intensities.append(emotion_intensity)
        
        # Calculate mean intensity
        mean_intensity = np.mean(intensities) if intensities else 0.0
        
        # Add differential privacy noise
        sensitivity = 1.0 / len(intensities) if intensities else 1.0
        noise_scale = sensitivity / self.dp_epsilon
        dp_noise = np.random.laplace(0, noise_scale)
        
        # Apply noise and clamp to [0, 1]
        noisy_intensity = mean_intensity + dp_noise
        return max(0.0, min(1.0, noisy_intensity))
    
    def _calculate_dp_conflict_escalation(self, conversation_window: List[Dict[str, Any]]) -> float:
        """Calculate conflict escalation score with differential privacy."""
        if not conversation_window:
            return 0.0
            
        # Look for escalation indicators
        escalation_indicators = 0
        total_messages = len(conversation_window)
        
        for msg_data in conversation_window:
            enrichment = msg_data.get("enrichment", {})
            labels = enrichment.get("labels_coarse", [])
            
            # Count escalation signals
            if any(indicator in str(labels) for indicator in 
                   ["conflict", "anger", "frustration", "argument"]):
                escalation_indicators += 1
        
        # Calculate base escalation score
        base_score = escalation_indicators / total_messages if total_messages > 0 else 0.0
        
        # Add differential privacy noise
        sensitivity = 1.0 / total_messages if total_messages > 0 else 1.0
        noise_scale = sensitivity / self.dp_epsilon
        dp_noise = np.random.laplace(0, noise_scale)
        
        # Apply noise and clamp
        noisy_score = base_score + dp_noise
        return max(0.0, min(1.0, noisy_score))
    
    def _calculate_dp_intimacy_progression(self, conversation_window: List[Dict[str, Any]]) -> float:
        """Calculate intimacy progression score with differential privacy."""
        if not conversation_window:
            return 0.0
            
        # Look for intimacy indicators
        intimacy_indicators = 0
        total_messages = len(conversation_window)
        
        for msg_data in conversation_window:
            enrichment = msg_data.get("enrichment", {})
            labels = enrichment.get("labels_coarse", [])
            
            # Count intimacy signals (using only coarse labels)
            if any(indicator in str(labels) for indicator in 
                   ["intimacy", "trust", "vulnerability", "closeness"]):
                intimacy_indicators += 1
        
        # Calculate base score
        base_score = intimacy_indicators / total_messages if total_messages > 0 else 0.0
        
        # Add differential privacy
        sensitivity = 1.0 / total_messages if total_messages > 0 else 1.0
        noise_scale = sensitivity / self.dp_epsilon  
        dp_noise = np.random.laplace(0, noise_scale)
        
        noisy_score = base_score + dp_noise
        return max(0.0, min(1.0, noisy_score))
    
    def _calculate_dp_trust_stability(self, conversation_window: List[Dict[str, Any]]) -> float:
        """Calculate trust stability score with differential privacy."""
        if not conversation_window:
            return 0.5  # Neutral baseline
            
        trust_positive = 0
        trust_negative = 0
        total_messages = len(conversation_window)
        
        for msg_data in conversation_window:
            enrichment = msg_data.get("enrichment", {})
            labels = enrichment.get("labels_coarse", [])
            
            # Count trust indicators
            if any(indicator in str(labels) for indicator in 
                   ["trust_building", "reliability", "consistency"]):
                trust_positive += 1
            elif any(indicator in str(labels) for indicator in 
                     ["trust_erosion", "unreliability", "betrayal"]):
                trust_negative += 1
        
        # Calculate stability (positive trust minus negative trust, normalized)
        trust_balance = (trust_positive - trust_negative) / total_messages if total_messages > 0 else 0.0
        base_score = 0.5 + (trust_balance * 0.5)  # Map to [0, 1] with 0.5 as neutral
        
        # Add differential privacy
        sensitivity = 2.0 / total_messages if total_messages > 0 else 1.0
        noise_scale = sensitivity / self.dp_epsilon
        dp_noise = np.random.laplace(0, noise_scale)
        
        noisy_score = base_score + dp_noise
        return max(0.0, min(1.0, noisy_score))
    
    def _generate_privacy_tokens(self, fine_labels: List[str]) -> List[str]:
        """Generate privacy tokens for fine-grained labels."""
        tokens = []
        
        for label in fine_labels:
            # Create consistent hash-based tokens
            token_hash = hashlib.sha256(f"{label}:{secrets.token_hex(8)}".encode()).hexdigest()[:8]
            
            # Categorize by sensitivity
            if any(sensitive in label for sensitive in ["sexual", "substance", "trauma"]):
                token = f"⟦TKN:SENSITIVE:{token_hash}⟧"
            elif any(personal in label for personal in ["family", "relationship", "boundary"]):
                token = f"⟦TKN:PERSONAL:{token_hash}⟧"
            else:
                token = f"⟦TKN:CONTEXT:{token_hash}⟧"
            
            tokens.append(token)
        
        return tokens


class PrivacyTokenizer:
    """Consistent tokenization for privacy-preserving referencing."""
    
    def __init__(self, salt: Optional[str] = None):
        """Initialize with consistent salt for session."""
        self.salt = salt or secrets.token_hex(16)
        self.token_mapping: Dict[str, str] = {}
    
    def tokenize(self, sensitive_text: str, category: str = "GENERAL") -> str:
        """Create consistent privacy token for sensitive text."""
        cache_key = f"{category}:{sensitive_text}"
        
        if cache_key not in self.token_mapping:
            hash_input = f"{sensitive_text}:{category}:{self.salt}"
            token_hash = hashlib.sha256(hash_input.encode()).hexdigest()[:8]
            self.token_mapping[cache_key] = f"⟦TKN:{category}:{token_hash}⟧"
        
        return self.token_mapping[cache_key]


class EncryptionManager:
    """Manages encryption of context vectors for cloud processing."""
    
    def __init__(self):
        """Initialize with session encryption keys."""
        self.session_key = secrets.token_bytes(32)  # 256-bit key
        self.key_id = secrets.token_hex(8)
        
    def encrypt_context_vector(
        self, 
        context_vector: np.ndarray, 
        vector_type: str = "semantic"
    ) -> bytes:
        """Encrypt context vector for cloud processing."""
        # In production, use proper encryption library (cryptography, etc.)
        # This is a placeholder implementation
        vector_bytes = context_vector.astype(np.float32).tobytes()
        
        # Simple XOR encryption for demonstration (use proper AES in production)
        key_repeated = (self.session_key * ((len(vector_bytes) // 32) + 1))[:len(vector_bytes)]
        encrypted = bytes(a ^ b for a, b in zip(vector_bytes, key_repeated))
        
        return encrypted
    
    def decrypt_context_vector(
        self, 
        encrypted_data: bytes, 
        original_shape: Tuple[int, ...],
        dtype: np.dtype = np.float32
    ) -> np.ndarray:
        """Decrypt context vector from cloud processing."""
        # Decrypt using same XOR approach
        key_repeated = (self.session_key * ((len(encrypted_data) // 32) + 1))[:len(encrypted_data)]
        decrypted = bytes(a ^ b for a, b in zip(encrypted_data, key_repeated))
        
        # Convert back to numpy array
        vector = np.frombuffer(decrypted, dtype=dtype).reshape(original_shape)
        return vector


class HierarchicalContextBridge:
    """Main interface for hierarchical context processing."""
    
    def __init__(
        self, 
        dp_epsilon: float = 1.0,
        enable_encryption: bool = True
    ):
        """Initialize hierarchical context bridge."""
        self.abstraction_engine = AbstractionEngine(dp_epsilon)
        self.encryption_manager = EncryptionManager() if enable_encryption else None
        self.privacy_validator = MultiLayerPrivacyValidator()
        
        logger.info("Initialized Hierarchical Context Bridge")
    
    def create_hierarchical_context(
        self,
        local_enrichment: Dict[str, Any],
        conversation_window: List[Dict[str, Any]],
        enable_cloud_processing: bool = False
    ) -> HierarchicalEnrichment:
        """Create hierarchical context for privacy-preserving cloud processing."""
        
        # Level 1: Full local analysis (already provided)
        local_analysis = local_enrichment
        
        # Level 2-3: Create privacy-safe context summary
        context_summary = self.abstraction_engine.create_context_summary(
            local_enrichment, conversation_window
        )
        
        # Level 4: Create encrypted context vectors (if cloud processing enabled)
        encrypted_context = None
        if enable_cloud_processing and self.encryption_manager:
            encrypted_context = self._create_encrypted_context(
                local_enrichment, conversation_window
            )
        
        # Validate privacy boundaries
        privacy_validation = self.privacy_validator.validate_hierarchical_context(
            local_analysis=local_analysis,
            context_summary=context_summary,
            encrypted_context=encrypted_context
        )
        
        return HierarchicalEnrichment(
            local_analysis=local_analysis,
            context_summary=context_summary,
            encrypted_context=encrypted_context,
            privacy_validation=privacy_validation,
            abstraction_chain=[
                AbstractionLevel.LEVEL_1_FULL.value,
                AbstractionLevel.LEVEL_3_HIGH.value,
                AbstractionLevel.LEVEL_4_PATTERN.value if encrypted_context else None
            ]
        )
    
    def _create_encrypted_context(
        self,
        local_enrichment: Dict[str, Any],
        conversation_window: List[Dict[str, Any]]
    ) -> EncryptedContextVector:
        """Create encrypted context vectors for cloud processing."""
        if not self.encryption_manager:
            raise RuntimeError("Encryption manager not initialized")
        
        # Create context vectors from local enrichment
        semantic_vector = self._extract_semantic_vector(local_enrichment)
        emotional_vector = self._extract_emotional_vector(local_enrichment)  
        relationship_vector = self._extract_relationship_vector(local_enrichment)
        
        # Encrypt vectors
        encrypted_semantic = self.encryption_manager.encrypt_context_vector(
            semantic_vector, "semantic"
        )
        encrypted_emotional = self.encryption_manager.encrypt_context_vector(
            emotional_vector, "emotional"
        )
        encrypted_relationship = self.encryption_manager.encrypt_context_vector(
            relationship_vector, "relationship"
        )
        
        # Determine conversation phase
        conversation_phase = self._determine_conversation_phase(conversation_window)
        
        # Determine message count range
        message_count = len(conversation_window)
        if message_count <= 5:
            count_range = "1-5"
        elif message_count <= 20:
            count_range = "6-20"
        elif message_count <= 50:
            count_range = "21-50"
        else:
            count_range = "50+"
        
        return EncryptedContextVector(
            encrypted_semantic_vector=encrypted_semantic,
            encrypted_emotional_vector=encrypted_emotional,
            encrypted_relationship_vector=encrypted_relationship,
            conversation_phase=conversation_phase,
            temporal_position=datetime.now().hour,
            message_count_range=count_range,
            encryption_key_id=self.encryption_manager.key_id,
            vector_dimension=len(semantic_vector),
            privacy_tier=PrivacyTier.PATTERN_ONLY
        )
    
    def _extract_semantic_vector(self, enrichment: Dict[str, Any]) -> np.ndarray:
        """Extract semantic vector representation from enrichment."""
        # Create semantic vector from coarse labels and metadata
        # This is a placeholder - in production would use proper embeddings
        features = []
        
        # Coarse label features (safe for encryption)
        coarse_labels = enrichment.get("labels_coarse", [])
        label_features = [1.0 if label in coarse_labels else 0.0 
                         for label in ["stress", "intimacy", "conflict", "support"]]
        features.extend(label_features)
        
        # Pad to consistent dimension
        while len(features) < 128:
            features.append(0.0)
        
        return np.array(features[:128], dtype=np.float32)
    
    def _extract_emotional_vector(self, enrichment: Dict[str, Any]) -> np.ndarray:
        """Extract emotional vector representation."""
        features = []
        
        # Primary emotion encoding
        emotion = enrichment.get("emotion_primary", "neutral")
        emotion_map = {
            "joy": [1, 0, 0, 0], "sadness": [0, 1, 0, 0],
            "anger": [0, 0, 1, 0], "fear": [0, 0, 0, 1],
            "neutral": [0, 0, 0, 0]
        }
        features.extend(emotion_map.get(emotion, [0, 0, 0, 0]))
        
        # Emotional intensity and directness
        directness = enrichment.get("directness", {}).get("val", 0.5)
        certainty = enrichment.get("certainty", {}).get("val", 0.5)
        features.extend([directness, certainty])
        
        # Pad to consistent dimension
        while len(features) < 64:
            features.append(0.0)
        
        return np.array(features[:64], dtype=np.float32)
    
    def _extract_relationship_vector(self, enrichment: Dict[str, Any]) -> np.ndarray:
        """Extract relationship dynamics vector."""
        features = []
        
        # Boundary signals
        boundary_signal = enrichment.get("boundary_signal", "none")
        boundary_map = {
            "set": [1, 0, 0], "test": [0, 1, 0], "violate": [0, 0, 1], "none": [0, 0, 0]
        }
        features.extend(boundary_map.get(boundary_signal, [0, 0, 0]))
        
        # Repair attempt indicator
        repair_attempt = enrichment.get("repair_attempt", False)
        features.append(1.0 if repair_attempt else 0.0)
        
        # Stance encoding
        stance = enrichment.get("stance", "neutral")
        stance_map = {
            "supportive": [1, 0, 0], "challenging": [0, 1, 0], "neutral": [0, 0, 1]
        }
        features.extend(stance_map.get(stance, [0, 0, 1]))
        
        # Pad to consistent dimension
        while len(features) < 32:
            features.append(0.0)
        
        return np.array(features[:32], dtype=np.float32)
    
    def _determine_conversation_phase(self, conversation_window: List[Dict[str, Any]]) -> str:
        """Determine conversation phase from window."""
        if not conversation_window:
            return "single"
            
        message_count = len(conversation_window)
        
        # Analyze emotional progression to determine phase
        emotions = []
        for msg_data in conversation_window:
            enrichment = msg_data.get("enrichment", {})
            emotion = enrichment.get("emotion_primary", "neutral")
            emotions.append(emotion)
        
        # Simple heuristic for conversation phase
        if message_count <= 2:
            return "opening"
        elif message_count <= 10:
            if any(e in ["anger", "frustration"] for e in emotions):
                return "climax"
            else:
                return "development"
        else:
            if emotions[-2:] == ["neutral", "neutral"] or all(e == "neutral" for e in emotions[-3:]):
                return "resolution"
            else:
                return "development"


class MultiLayerPrivacyValidator:
    """Multi-layer privacy validation for hierarchical context."""
    
    def validate_hierarchical_context(
        self,
        local_analysis: Dict[str, Any],
        context_summary: ContextSummary,
        encrypted_context: Optional[EncryptedContextVector]
    ) -> Dict[str, Any]:
        """Validate privacy boundaries across hierarchical context."""
        
        validation_results = {
            "passed": True,
            "violations": [],
            "risk_score": 0.0,
            "validation_timestamp": datetime.now().isoformat()
        }
        
        # Layer 1: Context summary validation
        summary_violations = self._validate_context_summary(context_summary)
        validation_results["violations"].extend(summary_violations)
        
        # Layer 2: Encrypted context validation
        if encrypted_context:
            encryption_violations = self._validate_encrypted_context(encrypted_context)
            validation_results["violations"].extend(encryption_violations)
        
        # Layer 3: Cross-layer consistency validation
        consistency_violations = self._validate_cross_layer_consistency(
            local_analysis, context_summary, encrypted_context
        )
        validation_results["violations"].extend(consistency_violations)
        
        # Calculate overall risk score
        validation_results["risk_score"] = len(validation_results["violations"]) * 0.1
        validation_results["passed"] = len(validation_results["violations"]) == 0
        
        return validation_results
    
    def _validate_context_summary(self, context_summary: ContextSummary) -> List[str]:
        """Validate context summary for privacy compliance."""
        violations = []
        
        # Check for overly specific patterns
        if len(context_summary.privacy_tokens) > 10:
            violations.append("Excessive privacy tokens may enable reconstruction")
        
        # Check boolean flags consistency
        sensitive_flags = [
            context_summary.substance_context_present,
            context_summary.intimate_context_present,
            context_summary.boundary_discussion_present,
            context_summary.trauma_indicators_present
        ]
        
        if sum(sensitive_flags) > 3:
            violations.append("Too many sensitive context flags active")
        
        # Validate score ranges
        scores = [
            context_summary.emotional_intensity_score,
            context_summary.conflict_escalation_score,
            context_summary.intimacy_progression_score,
            context_summary.trust_stability_score
        ]
        
        if any(score < 0.0 or score > 1.0 for score in scores):
            violations.append("Privacy scores outside valid range [0,1]")
        
        return violations
    
    def _validate_encrypted_context(self, encrypted_context: EncryptedContextVector) -> List[str]:
        """Validate encrypted context for privacy compliance."""
        violations = []
        
        # Check encryption integrity
        if not encrypted_context.encrypted_semantic_vector:
            violations.append("Missing encrypted semantic vector")
        
        if not encrypted_context.encryption_key_id:
            violations.append("Missing encryption key ID")
        
        # Validate metadata safety
        if encrypted_context.temporal_position < 0 or encrypted_context.temporal_position > 23:
            violations.append("Invalid temporal position")
        
        return violations
    
    def _validate_cross_layer_consistency(
        self,
        local_analysis: Dict[str, Any],
        context_summary: ContextSummary,
        encrypted_context: Optional[EncryptedContextVector]
    ) -> List[str]:
        """Validate consistency across abstraction layers."""
        violations = []
        
        # Check fine vs coarse label consistency
        fine_labels = local_analysis.get("fine_labels_local", [])
        
        # If fine labels indicate substance use, context summary should reflect it
        substance_in_fine = any("substance" in label for label in fine_labels)
        if substance_in_fine and not context_summary.substance_context_present:
            violations.append("Substance context inconsistency between layers")
        
        # Check for information leakage through abstraction
        if len(context_summary.privacy_tokens) > len(fine_labels):
            violations.append("Privacy tokens exceed fine labels - potential over-abstraction")
        
        return violations