"""Advanced ML-based content detection for Policy Shield.

This module provides enhanced detection capabilities for illegal content
using both pattern-based and ML-based approaches with confidence scoring.
"""

import hashlib
import json
import logging
import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

try:
    from transformers import pipeline
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False

logger = logging.getLogger(__name__)


class ThreatLevel(Enum):
    """Threat classification levels."""
    SAFE = "safe"
    SUSPICIOUS = "suspicious"  # Level 1: Log + warn
    PROBABLE = "probable"      # Level 2: Block cloud, allow local
    CONFIRMED = "confirmed"    # Level 3: Block all processing


@dataclass
class DetectionResult:
    """Result from content detection analysis."""
    threat_level: ThreatLevel
    confidence: float  # 0.0 - 1.0
    detected_classes: list[str]
    evidence: list[str]  # Specific patterns/phrases that triggered detection
    reasoning: str  # Human-readable explanation
    should_block_cloud: bool
    should_block_all: bool


@dataclass
class PatternSet:
    """Structured pattern set with metadata."""
    category: str
    patterns: list[str]
    threat_level: ThreatLevel
    confidence_base: float
    context_required: bool = True  # Whether context analysis is needed


class AdvancedThreatDetector:
    """ML-enhanced threat detection with tiered blocking levels."""
    
    def __init__(self, model_name: str | None = None, cache_dir: Path | None = None):
        """Initialize the advanced detector.
        
        Args:
            model_name: HuggingFace model for classification (None for pattern-only)
            cache_dir: Directory to cache models and patterns
        """
        self.cache_dir = cache_dir or Path("./.threat_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # ML classifier (optional)
        self.classifier = None
        self.tokenizer = None
        
        if HF_AVAILABLE and model_name:
            try:
                self._initialize_ml_classifier(model_name)
            except Exception as e:
                logger.warning(f"Failed to initialize ML classifier: {e}")
                logger.info("Falling back to pattern-based detection only")
        
        # Load enhanced pattern database
        self.pattern_sets = self._load_pattern_database()
        
        # Detection statistics
        self.detection_stats = {
            "total_analyzed": 0,
            "threats_detected": 0,
            "by_level": {level.value: 0 for level in ThreatLevel},
            "by_category": {},
        }
    
    def _initialize_ml_classifier(self, model_name: str) -> None:
        """Initialize the ML classifier for contextual analysis."""
        logger.info(f"Initializing ML classifier: {model_name}")
        
        # Use a lightweight, privacy-focused model
        # Note: In production, this would be a custom-trained model
        # For now, we'll use a general text classification model
        try:
            self.classifier = pipeline(
                "text-classification",
                model=model_name,
                tokenizer=model_name,
                device=-1,  # CPU only for privacy
                truncation=True,
                max_length=512,
            )
            logger.info("ML classifier initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize classifier: {e}")
            raise
    
    def _load_pattern_database(self) -> dict[str, PatternSet]:
        """Load enhanced pattern database with expanded coverage."""
        
        # Enhanced CSAM detection patterns (more sophisticated)
        csam_patterns = [
            # Direct indicators
            r'\b(?:child|kid|minor|underage|young|little)\s+(?:porn|explicit|sexual|nude|naked)',
            r'\b(?:cp|cheese pizza|childlove|pedo|loli|shota)\b',
            r'\b(?:preteen|teen|adolescent)\s+(?:model|pic|photo|video|content)',
            
            # Coded language and euphemisms
            r'\b(?:candy|sweet|innocent|fresh|pure)\s+(?:content|material|stuff)',
            r'\b(?:family|home|private)\s+(?:video|photo|collection|album)',
            r'\b(?:young|little)\s+(?:friend|angel|princess|star)',
            
            # Age-related suspicious patterns
            r'\b(?:[5-9]|1[0-7])\s*(?:year|yr|y\.?o\.?|age)',
            r'\b(?:elementary|middle school|high school)\s+(?:girl|boy|student)',
            
            # Trading/sharing indicators
            r'\b(?:trade|swap|share|exchange)\s+(?:pics|photos|videos|content)',
            r'\b(?:collection|archive|folder|set)\s+(?:of|with)\s+(?:young|teen)',
        ]
        
        # Enhanced violence detection
        violence_patterns = [
            # Direct threats
            r'\b(?:kill|murder|hurt|harm|attack|assault)\s+(?:someone|people|person)',
            r'\b(?:shoot|stab|beat|torture)\s+(?:up|them|him|her)',
            
            # Weapon-related
            r'\b(?:bomb|explosive|weapon|gun|knife)\s+(?:making|building|buying|getting)',
            r'\b(?:ammunition|bullets|firearms)\s+(?:purchase|acquire|obtain)',
            
            # Planning violence
            r'\b(?:plan|planning|gonna|going to)\s+(?:kill|hurt|attack)',
            r'\b(?:target|victim|hit list)',
            
            # School/mass violence
            r'\b(?:school|workplace|mass)\s+(?:shooting|attack|violence)',
        ]
        
        # Enhanced drug-related detection
        drugs_patterns = [
            # Direct trafficking
            r'\b(?:sell|buy|deal|traffic|smuggle)\s+(?:drugs|cocaine|heroin|meth|fentanyl)',
            r'\b(?:drug\s+deal|trafficking|smuggling|distribution)',
            
            # Coded language
            r'\b(?:snow|white|ice|crystal|rock|powder)\s+(?:for sale|available|selling)',
            r'\b(?:party favors|candy|product|stuff)\s+(?:available|for sale)',
            
            # Manufacturing
            r'\b(?:cook|cooking|making|producing)\s+(?:meth|drugs|product)',
            r'\b(?:lab|operation|setup)\s+(?:for|cooking|making)',
            
            # Distribution networks
            r'\b(?:supplier|connect|hookup|dealer)\s+(?:available|needed)',
        ]
        
        # Financial crimes
        financial_patterns = [
            # Money laundering
            r'\b(?:money\s+launder|clean\s+money|wash\s+cash)',
            r'\b(?:cryptocurrency|bitcoin|crypto)\s+(?:mixing|tumbling|laundering)',
            
            # Fraud
            r'\b(?:credit\s+card|cc|identity)\s+(?:fraud|theft|stealing)',
            r'\b(?:fake\s+id|forged|counterfeit)\s+(?:documents|papers|cards)',
            
            # Tax evasion
            r'\b(?:tax\s+evasion|offshore\s+account|hide\s+money)',
        ]
        
        return {
            "csam": PatternSet(
                category="csam",
                patterns=csam_patterns,
                threat_level=ThreatLevel.CONFIRMED,
                confidence_base=0.9,
                context_required=True,
            ),
            "violence": PatternSet(
                category="violence",
                patterns=violence_patterns,
                threat_level=ThreatLevel.PROBABLE,
                confidence_base=0.8,
                context_required=True,
            ),
            "drugs": PatternSet(
                category="illegal_drugs",
                patterns=drugs_patterns,
                threat_level=ThreatLevel.PROBABLE,
                confidence_base=0.7,
                context_required=True,
            ),
            "financial_crimes": PatternSet(
                category="financial_crimes",
                patterns=financial_patterns,
                threat_level=ThreatLevel.SUSPICIOUS,
                confidence_base=0.6,
                context_required=True,
            ),
        }
    
    def analyze_content(self, text: str, context: list[str] | None = None) -> DetectionResult:
        """Analyze content for threats using multi-layered approach.
        
        Args:
            text: Text content to analyze
            context: Optional surrounding messages for context analysis
            
        Returns:
            DetectionResult with threat assessment
        """
        self.detection_stats["total_analyzed"] += 1
        
        # Stage 1: Pattern-based detection
        pattern_results = self._pattern_analysis(text)
        
        # Stage 2: ML-based contextual analysis (if available)
        ml_results = None
        if self.classifier and context:
            ml_results = self._ml_contextual_analysis(text, context)
        
        # Stage 3: Combine results and make final decision
        final_result = self._combine_results(text, pattern_results, ml_results)
        
        # Update statistics
        self._update_stats(final_result)
        
        # Log detection for audit trail
        self._log_detection(text, final_result)
        
        return final_result
    
    def _pattern_analysis(self, text: str) -> dict[str, Any]:
        """Perform pattern-based analysis."""
        results = {
            "matches": [],
            "max_threat_level": ThreatLevel.SAFE,
            "max_confidence": 0.0,
            "categories": set(),
        }
        
        text_lower = text.lower()
        
        for category, pattern_set in self.pattern_sets.items():
            category_matches = []
            
            for pattern in pattern_set.patterns:
                matches = list(re.finditer(pattern, text_lower, re.IGNORECASE))
                
                for match in matches:
                    evidence = match.group()
                    confidence = pattern_set.confidence_base
                    
                    # Boost confidence for exact sensitive terms
                    if any(term in evidence for term in ['csam', 'child porn', 'cp']):
                        confidence = min(1.0, confidence + 0.2)
                    
                    category_matches.append({
                        "pattern": pattern,
                        "evidence": evidence,
                        "confidence": confidence,
                        "position": (match.start(), match.end()),
                    })
            
            if category_matches:
                results["categories"].add(category)
                results["matches"].extend(category_matches)
                
                # Update max threat level
                if pattern_set.threat_level.value > results["max_threat_level"].value:
                    results["max_threat_level"] = pattern_set.threat_level
                
                # Update max confidence
                max_cat_confidence = max(m["confidence"] for m in category_matches)
                results["max_confidence"] = max(results["max_confidence"], max_cat_confidence)
        
        return results
    
    def _ml_contextual_analysis(self, text: str, context: list[str]) -> dict[str, Any]:
        """Perform ML-based contextual analysis."""
        try:
            # Combine text with context for analysis
            full_context = " ".join(context[-3:] + [text])  # Last 3 messages + current
            
            # Classify the content
            result = self.classifier(full_context)
            
            # Map classifier output to our threat levels
            # This is a simplified mapping - in production would be more sophisticated
            label = result[0]["label"].lower()
            score = result[0]["score"]
            
            threat_level = ThreatLevel.SAFE
            if "toxic" in label or "hate" in label:
                if score > 0.8:
                    threat_level = ThreatLevel.PROBABLE
                elif score > 0.5:
                    threat_level = ThreatLevel.SUSPICIOUS
            
            return {
                "ml_label": label,
                "ml_score": score,
                "ml_threat_level": threat_level,
                "context_analyzed": True,
            }
        
        except Exception as e:
            logger.warning(f"ML analysis failed: {e}")
            return {"context_analyzed": False, "error": str(e)}
    
    def _combine_results(
        self,
        text: str,
        pattern_results: dict[str, Any],
        ml_results: dict[str, Any] | None
    ) -> DetectionResult:
        """Combine pattern and ML results into final decision."""
        
        # Start with pattern-based results
        threat_level = pattern_results["max_threat_level"]
        confidence = pattern_results["max_confidence"]
        detected_classes = list(pattern_results["categories"])
        evidence = [match["evidence"] for match in pattern_results["matches"]]
        
        # Adjust based on ML results if available
        if ml_results and ml_results.get("context_analyzed"):
            ml_threat = ml_results.get("ml_threat_level", ThreatLevel.SAFE)
            ml_confidence = ml_results.get("ml_score", 0.0)
            
            # If ML disagrees with patterns, take the more conservative approach
            if ml_threat.value > threat_level.value:
                threat_level = ml_threat
                confidence = max(confidence, ml_confidence)
            elif ml_threat.value < threat_level.value and ml_confidence > 0.7:
                # ML strongly suggests it's safe - reduce threat level but not below suspicious
                if threat_level == ThreatLevel.CONFIRMED:
                    threat_level = ThreatLevel.PROBABLE
                    confidence *= 0.8  # Reduce confidence
        
        # Generate reasoning
        reasoning_parts = []
        if evidence:
            reasoning_parts.append(f"Pattern matches: {len(evidence)} suspicious phrases detected")
        if ml_results and ml_results.get("context_analyzed"):
            reasoning_parts.append(f"Context analysis: {ml_results.get('ml_label', 'unknown')}")
        
        reasoning = "; ".join(reasoning_parts) if reasoning_parts else "No threats detected"
        
        # Determine blocking actions
        should_block_cloud = threat_level in [ThreatLevel.PROBABLE, ThreatLevel.CONFIRMED]
        should_block_all = threat_level == ThreatLevel.CONFIRMED
        
        return DetectionResult(
            threat_level=threat_level,
            confidence=confidence,
            detected_classes=detected_classes,
            evidence=evidence[:5],  # Limit evidence for privacy
            reasoning=reasoning,
            should_block_cloud=should_block_cloud,
            should_block_all=should_block_all,
        )
    
    def _update_stats(self, result: DetectionResult) -> None:
        """Update detection statistics."""
        if result.threat_level != ThreatLevel.SAFE:
            self.detection_stats["threats_detected"] += 1
        
        self.detection_stats["by_level"][result.threat_level.value] += 1
        
        for category in result.detected_classes:
            if category not in self.detection_stats["by_category"]:
                self.detection_stats["by_category"][category] = 0
            self.detection_stats["by_category"][category] += 1
    
    def _log_detection(self, text: str, result: DetectionResult) -> None:
        """Log detection for audit trail (privacy-aware)."""
        if result.threat_level == ThreatLevel.SAFE:
            return
        
        # Create privacy-preserving log entry
        text_hash = hashlib.sha256(text.encode()).hexdigest()[:16]
        
        log_entry = {
            "timestamp": logging.Formatter().formatTime(logging.LogRecord(
                name="", level=0, pathname="", lineno=0, msg="", args=(), exc_info=None
            )),
            "text_hash": text_hash,
            "threat_level": result.threat_level.value,
            "confidence": result.confidence,
            "categories": result.detected_classes,
            "evidence_count": len(result.evidence),
        }
        
        # Log at appropriate level
        if result.threat_level == ThreatLevel.CONFIRMED:
            logger.critical(f"THREAT DETECTED: {log_entry}")
        elif result.threat_level == ThreatLevel.PROBABLE:
            logger.error(f"Probable threat: {log_entry}")
        else:
            logger.warning(f"Suspicious content: {log_entry}")
    
    def get_detection_stats(self) -> dict[str, Any]:
        """Get detection statistics for monitoring."""
        total = self.detection_stats["total_analyzed"]
        if total == 0:
            return self.detection_stats
        
        return {
            **self.detection_stats,
            "threat_rate": self.detection_stats["threats_detected"] / total,
            "performance_metrics": {
                "patterns_loaded": sum(len(ps.patterns) for ps in self.pattern_sets.values()),
                "ml_enabled": self.classifier is not None,
                "cache_dir": str(self.cache_dir),
            }
        }
    
    def update_patterns(self, new_patterns: dict[str, list[str]]) -> None:
        """Update pattern database (for threat intelligence integration)."""
        logger.info(f"Updating threat patterns: {list(new_patterns.keys())}")
        
        for category, patterns in new_patterns.items():
            if category in self.pattern_sets:
                # Add to existing patterns
                self.pattern_sets[category].patterns.extend(patterns)
                logger.info(f"Added {len(patterns)} patterns to {category}")
            else:
                logger.warning(f"Unknown category for pattern update: {category}")
        
        # Save updated patterns to cache
        self._save_patterns_to_cache()
    
    def _save_patterns_to_cache(self) -> None:
        """Save current patterns to cache for persistence."""
        cache_file = self.cache_dir / "threat_patterns.json"
        
        patterns_data = {}
        for category, pattern_set in self.pattern_sets.items():
            patterns_data[category] = {
                "patterns": pattern_set.patterns,
                "threat_level": pattern_set.threat_level.value,
                "confidence_base": pattern_set.confidence_base,
            }
        
        with open(cache_file, 'w') as f:
            json.dump(patterns_data, f, indent=2)
        
        logger.debug(f"Saved patterns to cache: {cache_file}")
