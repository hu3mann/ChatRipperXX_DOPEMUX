# CONTRIBUTING

See `docs/` for architecture, ADRs, and process. Follow TDD and Conventional Commits.

## AI Commits
- Install: `npm i -g aicommits` (requires OPENAI_API_KEY or compatible provider).
- Run once: `scripts/install-git-hooks.sh` to enable automatic AI commit messages.
- You can still edit the message; ensure it remains **Conventional**.

## Documentation Policy
- **All relevant documents must be updated** in every PR when code changes (docs/ and/or README/CLAUDE.md). CI will fail otherwise.
- Keep docs in `/docs` only; MkDocs builds the site from this folder.
