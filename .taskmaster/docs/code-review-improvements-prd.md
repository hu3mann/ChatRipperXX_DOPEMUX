# Code Review Improvements PRD

## Overview
Address critical code quality and architectural issues identified in comprehensive code review of ChatX/ChatRipper codebase. Focus on async integration, performance optimization, and technical debt reduction.

## Priority 1: Critical Async Integration Fix
**Issue**: Neo4j driver uses synchronous operations in async context, blocking event loop
**Impact**: Performance degradation, negates async benefits
**Files**: src/chatx/storage/graph.py lines 65-68, 9-10
**Solution**: Migrate from GraphDatabase.driver to GraphDatabase.async_driver with proper awaited operations

## Priority 2: High-Impact Performance Improvements  
**Neo4j Connection Pooling**: Add explicit connection pool configuration for concurrent access patterns
**Graph Update Optimization**: Replace inefficient DETACH DELETE/CREATE pattern with MERGE-based upsert operations
**Files**: src/chatx/storage/graph.py lines 54-55, 425-429

## Priority 3: Medium Priority Code Quality
**Privacy Budget Optimization**: Consider advanced composition for differential privacy queries to reduce noise
**Dead Code Removal**: Remove unreachable numpy array handling branches in noise generation
**Files**: src/chatx/redaction/policy_shield.py lines 384-386, src/chatx/privacy/differential_privacy.py lines 141-146

## Priority 4: Low Priority Enhancements
**Configuration Externalization**: Move hardcoded model configurations to external YAML/JSON files
**Semantic Content Detection**: Enhance psychology content detection beyond keyword matching
**Files**: src/chatx/embeddings/psychology.py lines 30-48, 51-65

## Success Criteria
- All async operations use AsyncDriver without blocking event loop
- Connection pooling configured with appropriate limits
- Graph updates use efficient MERGE patterns
- Code coverage maintained at 90%+ for modified modules
- Performance benchmarks show improved async throughput