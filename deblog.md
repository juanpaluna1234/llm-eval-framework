## 2026-07-27 — First accuracy test run

Built the golden set (6 Q&A pairs) and LLM-as-judge scoring. Ran the suite:
5/6 passed. 

**Finding:** q6 ("Can I use CloudSync Pro to order pizza?") failed — the bot
fabricated feature descriptions instead of declining. Root cause: retrieval
always returns top-N docs regardless of relevance, so irrelevant context
gets passed to the model even when nothing in the knowledge base applies.

**Fix:** added a distance threshold to retrieval + tightened the system
prompt to explicitly decline when context isn't directly relevant.

**Why this matters:** this is a known RAG failure mode — vector search
returning "closest available" instead of "actually relevant" results.

