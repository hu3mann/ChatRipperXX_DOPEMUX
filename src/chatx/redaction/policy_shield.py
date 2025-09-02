"""Privacy redaction system (Policy Shield)."""

import json
import logging
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from chatx.redaction.advanced_detector import AdvancedThreatDetector
from chatx.redaction.patterns import ConsistentTokenizer, HardFailDetector, PIIMatch, PIIPatterns
from chatx.schemas.validator import validate_redaction_report

logger = logging.getLogger(__name__)


@dataclass
class PrivacyPolicy:
    """Privacy policy configuration."""
    threshold: float = 0.995  # Coverage threshold (99.5%)
    strict_mode: bool = False  # Use 99.9% threshold if True
    block_hard_fail: bool = True  # Block processing on hard-fail classes
    pseudonymize: bool = True  # Use consistent pseudonymization
    detect_names: bool = True  # Detect common names as PII
    opaque_tokens: bool = True  # Use opaque tokens instead of categories
    use_advanced_detector: bool = True  # Use ML-enhanced threat detection
    threat_model: str | None = None  # HuggingFace model for threat detection
    
    def get_effective_threshold(self) -> float:
        """Get the effective coverage threshold."""
        return 0.999 if self.strict_mode else self.threshold


@dataclass
class RedactionReport:
    """Report on redaction quality and coverage."""
    coverage: float
    strict: bool
    hardfail_triggered: bool
    messages_total: int
    tokens_redacted: int
    placeholders: dict[str, int]
    coarse_label_counts: dict[str, int]
    visibility_leaks: list[str]
    notes: list[str]
    threat_detections: dict[str, int]  # Threat level counts
    advanced_analysis_used: bool  # Whether ML analysis was used
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


class PolicyShield:
    """Privacy redaction system for protecting sensitive data."""
    
    def __init__(self, policy: PrivacyPolicy | None = None, salt_file: Path | None = None) -> None:
        """Initialize Policy Shield with privacy policy.
        
        Args:
            policy: Privacy policy configuration
            salt_file: Path to salt file for consistent tokenization
        """
        self.policy = policy or PrivacyPolicy()
        self.pii_detector = PIIPatterns()
        self.hard_fail_detector = HardFailDetector()
        
        # Initialize advanced threat detector if enabled
        self.advanced_detector: AdvancedThreatDetector | None = None
        if self.policy.use_advanced_detector:
            try:
                self.advanced_detector = AdvancedThreatDetector(
                    model_name=self.policy.threat_model,
                    cache_dir=Path("./.threat_cache")
                )
                logger.info("Advanced threat detection enabled")
            except Exception as e:
                logger.warning(f"Failed to initialize advanced detector: {e}")
                logger.info("Falling back to pattern-based detection only")
        
        # Initialize tokenizer
        salt = self._load_or_create_salt(salt_file) if salt_file else None
        self.tokenizer = ConsistentTokenizer(salt=salt)
        
        detector_type = "Advanced ML-enhanced" if self.advanced_detector else "Pattern-based"
        logger.info(f"Initialized Policy Shield ({detector_type}) with threshold: {self.policy.get_effective_threshold()}")
    
    def _load_or_create_salt(self, salt_file: Path) -> str:
        """Load salt from file or create new one."""
        if salt_file.exists():
            with open(salt_file) as f:
                return f.read().strip()
        else:
            # Create new salt
            import secrets
            salt = secrets.token_hex(32)
            salt_file.parent.mkdir(parents=True, exist_ok=True)
            with open(salt_file, 'w') as f:
                f.write(salt)
            logger.info(f"Created new salt file: {salt_file}")
            return salt
    
    def _detect_pii_in_text(self, text: str) -> list[PIIMatch]:
        """Detect PII entities in text."""
        return self.pii_detector.detect_pii(text, include_names=self.policy.detect_names)
    
    def _redact_text(self, text: str) -> tuple[str, list[PIIMatch], int]:
        """Redact PII from text.
        
        Args:
            text: Original text
            
        Returns:
            Tuple of (redacted_text, pii_matches, tokens_redacted)
        """
        pii_matches = self._detect_pii_in_text(text)
        if not pii_matches:
            return text, [], 0
        
        # Sort matches by position (reverse order to maintain indices)
        sorted_matches = sorted(pii_matches, key=lambda x: x.start, reverse=True)
        
        redacted_text = text
        tokens_redacted = 0
        
        for match in sorted_matches:
            # Generate replacement token
            if self.policy.pseudonymize:
                replacement = self.tokenizer.tokenize_pii(match.text, match.type)
            else:
                replacement = f"[{match.type.upper()}]"
            
            # Replace in text
            redacted_text = (
                redacted_text[:match.start] +
                replacement +
                redacted_text[match.end:]
            )
            
            # Count tokens redacted (rough estimate)
            tokens_redacted += len(match.text.split())
        
        return redacted_text, pii_matches, tokens_redacted
    
    def _calculate_coverage(self, original_text: str, pii_matches: list[PIIMatch]) -> float:
        """Calculate redaction coverage.
        
        Args:
            original_text: Original text
            pii_matches: Detected PII matches
            
        Returns:
            Coverage ratio (0.0 to 1.0)
        """
        if not original_text.strip():
            return 1.0
        
        total_tokens = len(original_text.split())
        if total_tokens == 0:
            return 1.0
        
        pii_tokens = sum(len(match.text.split()) for match in pii_matches)
        coverage = max(0.0, (total_tokens - pii_tokens) / total_tokens)
        
        return coverage
    
    def _check_hard_fail_classes(self, text: str, context: list[str] | None = None) -> tuple[list[str], dict[str, Any]]:
        """Check for hard-fail content classes using advanced detection.
        
        Args:
            text: Text to check
            context: Optional context messages for ML analysis
            
        Returns:
            Tuple of (detected_classes, detection_metadata)
        """
        detection_metadata = {
            "advanced_analysis_used": False,
            "threat_level": "safe",
            "confidence": 0.0,
            "evidence": [],
        }
        
        # Use advanced detector if available
        if self.advanced_detector:
            try:
                result = self.advanced_detector.analyze_content(text, context)
                detection_metadata.update({
                    "advanced_analysis_used": True,
                    "threat_level": result.threat_level.value,
                    "confidence": result.confidence,
                    "evidence": result.evidence,
                    "reasoning": result.reasoning,
                })
                
                # Return detected classes based on threat level
                if result.should_block_all:
                    return result.detected_classes, detection_metadata
                elif result.should_block_cloud:
                    # Store for later cloud blocking but don't fail completely
                    detection_metadata["block_cloud_only"] = True
                    return [], detection_metadata
                else:
                    return [], detection_metadata
                    
            except Exception as e:
                logger.warning(f"Advanced detection failed, falling back to patterns: {e}")
        
        # Fallback to pattern-based detection
        legacy_classes = self.hard_fail_detector.detect_hard_fail_classes(text)
        return legacy_classes, detection_metadata
    
    def redact_chunk_text(self, text: str) -> tuple[str, dict[str, Any]]:
        """Redact text chunk and return metadata.
        
        Args:
            text: Text to redact
            
        Returns:
            Tuple of (redacted_text, redaction_metadata)
        """
        # Check for hard-fail classes first
        hard_fail_classes, threat_metadata = self._check_hard_fail_classes(text)
        if hard_fail_classes and self.policy.block_hard_fail:
            raise ValueError(f"Hard-fail classes detected: {hard_fail_classes}")
        
        # Redact PII
        redacted_text, pii_matches, tokens_redacted = self._redact_text(text)
        
        # Calculate coverage
        coverage = self._calculate_coverage(text, pii_matches)
        
        # Check coverage threshold
        threshold = self.policy.get_effective_threshold()
        if coverage < threshold:
            logger.warning(f"Coverage {coverage:.3f} below threshold {threshold}")
        
        # Build metadata
        metadata = {
            'coverage': coverage,
            'tokens_redacted': tokens_redacted,
            'pii_types': [match.type for match in pii_matches],
            'hard_fail_classes': hard_fail_classes,
            'threshold_met': coverage >= threshold,
            'threat_analysis': threat_metadata,  # Include advanced threat analysis
        }
        
        return redacted_text, metadata
    
    def redact_chunks(self, chunks: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], RedactionReport]:
        """Redact conversation chunks.
        
        Args:
            chunks: List of chunk dictionaries
            
        Returns:
            Tuple of (redacted_chunks, redaction_report)
        """
        logger.info(f"Starting redaction of {len(chunks)} chunks")
        
        redacted_chunks = []
        total_tokens_redacted = 0
        coverage_scores = []
        placeholder_counts: dict[str, int] = {}
        hard_fail_triggered = False
        visibility_leaks = []
        notes = []
        threat_detections: dict[str, int] = {
            "safe": 0, "suspicious": 0, "probable": 0, "confirmed": 0
        }
        advanced_analysis_used = False
        
        for i, chunk in enumerate(chunks):
            try:
                original_text = chunk.get('text', '')
                if not original_text:
                    redacted_chunks.append(chunk)
                    continue
                
                # Redact the text
                redacted_text, metadata = self.redact_chunk_text(original_text)
                
                # Update chunk
                redacted_chunk = chunk.copy()
                redacted_chunk['text'] = redacted_text
                
                # Add redaction metadata to provenance
                if 'provenance' not in redacted_chunk:
                    redacted_chunk['provenance'] = {}
                redacted_chunk['provenance']['redaction'] = {
                    'coverage': metadata['coverage'],
                    'tokens_redacted': metadata['tokens_redacted'],
                    'pii_types': metadata['pii_types'],
                    'threshold_met': metadata['threshold_met'],
                }
                
                # Track statistics
                coverage_scores.append(metadata['coverage'])
                total_tokens_redacted += metadata['tokens_redacted']
                
                # Count PII types
                for pii_type in metadata['pii_types']:
                    placeholder_counts[pii_type] = placeholder_counts.get(pii_type, 0) + 1
                
                # Check for hard-fail
                if metadata['hard_fail_classes']:
                    hard_fail_triggered = True
                    notes.append(f"Chunk {i}: Hard-fail classes detected: {metadata['hard_fail_classes']}")
                
                # Track threat detection statistics
                threat_analysis = metadata.get('threat_analysis', {})
                if threat_analysis.get('advanced_analysis_used', False):
                    advanced_analysis_used = True
                    threat_level = threat_analysis.get('threat_level', 'safe')
                    threat_detections[threat_level] = threat_detections.get(threat_level, 0) + 1
                    
                    # Log significant threats
                    if threat_level in ['probable', 'confirmed']:
                        confidence = threat_analysis.get('confidence', 0.0)
                        reasoning = threat_analysis.get('reasoning', 'No reasoning provided')
                        notes.append(f"Chunk {i}: {threat_level} threat (confidence: {confidence:.2f}) - {reasoning}")
                else:
                    # Pattern-based detection
                    threat_detections["safe"] += 1
                
                redacted_chunks.append(redacted_chunk)
                
            except Exception as e:
                logger.error(f"Error redacting chunk {i}: {e}")
                notes.append(f"Chunk {i}: Redaction error: {str(e)}")
                # Skip this chunk or add to visibility leaks
                visibility_leaks.append(f"chunk_{i}")
        
        # Calculate overall coverage
        overall_coverage = sum(coverage_scores) / len(coverage_scores) if coverage_scores else 1.0
        
        # Build report
        report = RedactionReport(
            coverage=overall_coverage,
            strict=self.policy.strict_mode,
            hardfail_triggered=hard_fail_triggered,
            messages_total=len(chunks),
            tokens_redacted=total_tokens_redacted,
            placeholders=placeholder_counts,
            coarse_label_counts={},  # Would be populated from label taxonomy
            visibility_leaks=visibility_leaks,
            notes=notes,
            threat_detections=threat_detections,
            advanced_analysis_used=advanced_analysis_used,
        )
        
        logger.info(f"Redaction complete: {overall_coverage:.3f} coverage, {total_tokens_redacted} tokens redacted")
        return redacted_chunks, report
    
    def save_redaction_report(self, report: RedactionReport, output_file: Path) -> None:
        """Save redaction report to file.
        
        Args:
            report: Redaction report
            output_file: Output file path
        """
        # Validate report against schema
        try:
            is_valid, errors = validate_redaction_report(report.to_dict(), strict=False)
            if not is_valid:
                logger.warning(f"Redaction report validation warnings: {errors}")
        except Exception as e:
            logger.warning(f"Could not validate redaction report: {e}")
        
        # Ensure output directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Save report
        with open(output_file, 'w') as f:
            json.dump(report.to_dict(), f, indent=2)
        
        logger.info(f"Redaction report saved to: {output_file}")
    
    def get_tokenizer_stats(self) -> dict[str, Any]:
        """Get tokenizer statistics."""
        return self.tokenizer.get_mapping_stats()
    
    def preflight_cloud_check(
        self,
        redacted_chunks: list[dict[str, Any]],
        report: RedactionReport
    ) -> tuple[bool, list[str]]:
        """Preflight check for cloud processing readiness.
        
        Args:
            redacted_chunks: Redacted chunks
            report: Redaction report
            
        Returns:
            Tuple of (passed, blocking_issues)
        """
        blocking_issues = []
        
        # Check coverage threshold
        threshold = self.policy.get_effective_threshold()
        if report.coverage < threshold:
            blocking_issues.append(f"Coverage {report.coverage:.3f} below required {threshold}")
        
        # Check for hard-fail triggers
        if report.hardfail_triggered:
            blocking_issues.append("Hard-fail classes detected")
        
        # Check for visibility leaks
        if report.visibility_leaks:
            blocking_issues.append(f"Visibility leaks detected: {report.visibility_leaks}")
        
        # Check for fine-grained labels (should not exist in redacted data)
        for chunk in redacted_chunks:
            meta = chunk.get('meta', {})
            if 'labels_fine_local' in meta and meta['labels_fine_local']:
                blocking_issues.append("Fine-grained labels present in redacted data")
                break
        
        passed = len(blocking_issues) == 0
        return passed, blocking_issues
    
    def get_threat_detection_stats(self) -> dict[str, Any]:
        """Get threat detection statistics from advanced detector.
        
        Returns:
            Threat detection statistics
        """
        if not self.advanced_detector:
            return {
                "advanced_detection_enabled": False,
                "fallback_mode": "pattern_based_only"
            }
        
        stats = self.advanced_detector.get_detection_stats()
        return {
            "advanced_detection_enabled": True,
            "detector_stats": stats,
            "pattern_sets_loaded": len(self.advanced_detector.pattern_sets),
            "ml_classifier_available": self.advanced_detector.classifier is not None,
        }
    
    def update_threat_patterns(self, new_patterns: dict[str, list[str]]) -> bool:
        """Update threat detection patterns (for threat intelligence integration).
        
        Args:
            new_patterns: New patterns by category
            
        Returns:
            True if patterns were updated successfully
        """
        if not self.advanced_detector:
            logger.warning("Cannot update patterns - advanced detector not available")
            return False
        
        try:
            self.advanced_detector.update_patterns(new_patterns)
            logger.info(f"Updated threat patterns: {list(new_patterns.keys())}")
            return True
        except Exception as e:
            logger.error(f"Failed to update threat patterns: {e}")
            return False
