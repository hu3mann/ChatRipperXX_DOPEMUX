# ctx/search-here
Fast semantic search in the **current workspace** using **claude-context**.

**Args**: `$ARGUMENTS` = `<QUERY>`

**Steps**
1) Confirm claude-context is connected; if not, report the missing envs and stop.
2) Run search for `<QUERY>` across the current workspace (assume already indexed; if not, do a quick index first).
3) Show top 10 hits as `file:line — score — short snippet`. Offer to open files inline.
