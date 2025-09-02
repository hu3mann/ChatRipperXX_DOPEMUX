# ChatX/ChatRipper Documentation

*A privacy-first, local-first forensic chat analysis tool with optional cloud enrichment*

---

## 📖 Quick Start

| Document | Description |
|----------|-------------|
| **[Architecture](architecture.md)** | System overview, components, and data flows |
| **[Interfaces](interfaces.md)** | CLI contracts, API specifications, and schemas |
| **[Acceptance Criteria](acceptance-criteria.md)** | User stories and test scenarios |

---

## 🏗️ Design & Specifications

### Core Specifications
- **[iMessage Extractor](design/specifications/imessage-extractor.md)** — Full-fidelity iMessage extraction spec
- **[Cloud Enrichment](design/specifications/cloud-enrichment.md)** — Hybrid local/cloud processing

### Planning & Decisions
- **[Roadmap & Open Questions](design/next.md)** — What's next and what needs decisions
- **[Architecture Decision Records](design/adrs/)** — Key technical decisions and rationale

---

## 👩‍💻 Development

| Document | Purpose |
|----------|---------|
| **[Developer Guide](development/developer-guide.md)** | Setup, workflow, and coding standards |
| **[Test Strategy](development/test-strategy.md)** | Testing approach and coverage targets |
| **[Contributing](development/contributing.md)** | How to contribute to the project |

---

## 🚀 Operations

| Document | Purpose |
|----------|---------|
| **[Security Threat Model](operations/security-threat-model.md)** | Security analysis and mitigations |
| **[Non-Functional Requirements](operations/non-functional-requirements.md)** | Performance, scalability, reliability targets |

---

## 📚 Reference

| Document | Purpose |
|----------|---------|
| **[FAQ](reference/faq.md)** | Frequently asked questions |
| **[Changelog](reference/changelog.md)** | Release notes and version history |

---

## 🎯 Core Principles

### Privacy & Security First
- **Local-first processing** — All sensitive data processing happens locally
- **Policy Shield** — 99.5%+ redaction coverage before any cloud operations
- **No attachment uploads** — Media files never leave your device
- **Pseudonymization** — Consistent tokenization of personal identifiers

### Deterministic & Observable
- **Schema-locked outputs** — All data validates against JSON schemas
- **Full provenance** — Every output includes source references
- **Evidence-backed results** — All answers cite specific message chunks
- **Comprehensive logging** — Structured observability throughout

### Performance & Scale
- **≥5k messages/min** extraction throughput
- **<5s query response** times over 100k message corpus
- **<4GB memory** peak for 1M message processing
- **CI-enforced gates** — Performance and privacy validated automatically

---

## 🚀 Quick Command Reference

```bash
# Extract iMessage conversations
chatx imessage pull --contact "friend@example.com" --include-attachments --out ./out

# Extract iMessage from iPhone backup (Finder/iTunes MobileSync)
chatx imessage pull --contact "+15551234567" --from-backup "~/Library/Application Support/MobileSync/Backup/<UDID>" --out ./out

# Extract Instagram DMs for a specific user (required)
chatx instagram pull --zip ./instagram.zip --user "Your Name" --out ./out

# Transform and redact for safety
chatx transform --input ./out/messages.jsonl --chunk turns:40
chatx redact --input ./out/chunks.jsonl --threshold 0.995

# Index for fast retrieval
chatx index --input ./out/redacted/*.json --store chroma

# Query with citations
chatx query "What did we discuss about the project?" --contact "friend@example.com"

# Local-only enrichment
chatx enrich messages --backend local --contact "friend@example.com"

# Hybrid enrichment (requires --allow-cloud after redaction)
chatx enrich messages --backend hybrid --allow-cloud --contact "friend@example.com"
```

---

## 📋 Development Status

### Current Milestone: iMessage Extractor Foundation
- ✅ Architecture and specifications complete
- ✅ Core extraction implementation (PR-1: Foundation)
- ✅ Reactions and replies (PR-2)
- ✅ Attachments and binary copying (PR-3)
- ✅ Missing attachment reporting (PR-4)
- ✅ Local transcription (PR-5)
- 🚧 Validation and performance (PR-6)

### Platform Support
- ✅ **iMessage** (macOS local disk)
- ✅ **iPhone backups (iMessage)** — Initial support (read-only via Manifest.db)
- ✅ **Instagram** — Initial extractor (official data ZIP)
- ⏳ **WhatsApp** — Planned
- ⏳ **iCloud Messages** — Research phase

---

## 🤝 Contributing

1. Read the [Contributing Guide](development/contributing.md)
2. Check the [Developer Guide](development/developer-guide.md) for setup
3. Review [Open Questions](design/next.md) for areas needing decisions
4. Follow the [Test Strategy](development/test-strategy.md) for quality gates

---

## 📄 License & Support

- **License:** See project root for licensing information
- **Issues:** Report bugs and feature requests via GitHub Issues
- **Discussions:** Architecture and design discussions in GitHub Discussions

---

*Last updated: 2025-09-02*
