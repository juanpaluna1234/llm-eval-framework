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


## 2026-07-28 — First consistency test run

Built `judge_consistency()` and `test_consistency.py` to check whether the
bot gives factually stable answers across repeated runs of the same
question. Ran 5 repetitions each for the 4 answerable golden-set questions
(q1, q2, q4, q5).

**Result:** 4/4 passed — no factual contradictions across any of the 20
bot calls.

**Observation:** wording was nearly identical across runs for several
questions (q1, q4), which is unusual for LLM output. Likely due
to two factors: no `temperature` set explicitly (using the API default,
which trends deterministic), and a narrow, unambiguous knowledge base with
little room for phrasing variation.

**Limitation noted:** this test isn't very rigorous in its current form —
with the bot already behaving near-deterministically, it's not stress-testing
consistency under realistic conditions. A stronger version would:
- Explicitly set `temperature=1.0` (or higher) to force more variation and
  confirm facts still hold even as wording changes
- Introduce deliberately ambiguous or conflicting documents into the
  knowledge base to see if retrieval instability causes fact drift across
  runs, not just wording drift

**Next step:** test with higher temperature and/or ambiguous docs before
considering consistency fully validated. Moving on to adversarial testing
(prompt injection, out-of-scope edge cases) in the meantime.


## 2026-07-29 — Temperature experiment on consistency

Reran `test_consistency.py` with `temperature=1.0` (max allowed by the
Anthropic API) to see if forcing more sampling randomness would surface
wording or factual variation that the default temperature run didn't show.

**Result:** 4/4 still passed, and wording was nearly as consistent as the
previous run — raising temperature had almost no visible effect.

**Conclusion:** the determinism isn't primarily driven by temperature. It's
driven by how narrow and unambiguous the current knowledge base is — each
question maps to one short, clear-cut fact, leaving little room for the
model to vary its output regardless of sampling settings.

**Implication:** this means the consistency test, as currently designed,
doesn't meaningfully stress-test consistency — it's structurally likely to
pass given how simple the knowledge base is. A more rigorous version would
need: multi-part/nuanced answers, ambiguous or conflicting documents (to
test retrieval-driven instability), or more open-ended questions.

**Next step:** leaving this as a documented limitation for now rather than
expanding the knowledge base further, since the goal is a working portfolio
demonstration, not an exhaustive one. Moving on to adversarial testing
(prompt injection, out-of-scope edge cases).