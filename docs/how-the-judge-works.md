# How the LLM Judge Works

This document explains the evaluation mechanism at the core of this framework: 
using a second LLM call to grade the accuracy and groundedness of the first.

## The core idea

Testing an LLM-powered application is fundamentally different from testing 
traditional software. A traditional test checks `assert output == expected_value`. 
But LLM outputs are natural language — the same correct answer can be phrased 
a dozen different ways. String matching or regex-based checks are too brittle 
to be useful here.

Instead, this framework uses a second, independent Claude call — the "judge" — 
whose only job is to evaluate whether the first call's answer is correct and 
appropriately grounded in the source material.

There are two Claude calls involved in every test:

1. **The bot being tested** (`app/bot.py` → `ask()`) — answers the user's 
   question using retrieval-augmented generation (RAG).
2. **The judge** (`eval/judge.py` → `judge_answer()`) — grades that answer 
   against a rubric, the same way a human reviewer would.

## What the judge receives

For each test case, the judge is given:
- The original **question** asked
- The bot's actual **answer**
- A list of **expected facts** that should appear if the bot answered correctly
- A **should_answer** flag — whether the bot should have answered at all, 
  or should have declined (this is how the framework catches hallucinations 
  on out-of-scope questions)

For trick questions (things outside the knowledge base), `expected_facts` is 
empty and `should_answer` is `False`. The judge is told explicitly there's 
nothing this answer should match — which is what lets it correctly reward 
refusals and penalize fabricated answers.

## The grading prompt

The judge is given plain-English grading instructions rather than code logic:

1. If `should_answer` is `True`: does the answer correctly include the 
   expected facts, with no contradictions or fabrications?
2. If `should_answer` is `False`: did the bot correctly decline or say it 
   doesn't have the information, rather than making something up?

The judge responds with structured JSON:
```json
{"score": 1-5, "passed": true/false, "reasoning": "one sentence explanation"}
```

## Why Haiku for the judge

The judge uses Claude Haiku rather than a larger model. Judging a well-scoped, 
rubric-based question ("does this answer contain fact X, yes or no") is a 
simpler task than generating a good original answer, so a smaller, cheaper 
model is sufficient — and this keeps the cost of running the full test suite 
low, which matters if it's wired into CI and running on every commit.

## Handling malformed output

LLMs occasionally wrap JSON in markdown code fences even when told not to, 
or return text that doesn't parse as valid JSON at all. The judge defensively 
strips markdown fences before parsing, and if parsing still fails, it fails 
**safe** — treating the result as a failed test rather than crashing the 
suite. This matters for unattended CI runs, where a single malformed response 
shouldn't take down the entire pipeline.

## How this connects to pytest

```python
answer = ask(case["question"])                    # bot answers
result = judge_answer(question, answer, ...)       # judge grades it
assert result["passed"]                            # pytest uses that grade
```

`pytest` itself has no built-in notion of "correctness" for natural language — 
it simply trusts the judge's `passed` boolean. All the actual grading logic 
lives inside the judge's prompt, not in Python code.

## Known limitation: judging the judge

This pattern is how most production LLM evaluation systems work today, 
because deterministic checks can't capture whether a natural-language answer 
is semantically correct. But it comes with a real tradeoff: **the judge 
itself can be wrong or inconsistent**, since it's also an LLM call subject 
to the same non-determinism as the system under test.

This is part of why `test_consistency.py` exists — running the same question 
multiple times and checking variance in outcomes helps surface cases where 
either the bot *or* the judge is unstable, rather than assuming a single 
run is representative.