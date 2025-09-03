# docs/find
Use **context7** to find authoritative docs/snippets with runnable examples.

**Args**: `$ARGUMENTS` = `<QUERY>`

**Steps**
1) context7.search for `<QUERY>` (aim for SDK docs, RFCs, or official guides).
2) Return top 5 with: title, source, short summary, and a minimal code sample if present.
3) Suggest integration points in this repo (files/functions) where the example applies.

**Tools**: context7 only.
