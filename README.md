# LLM Evaluation Framework

An automated testing framework for RAG-based LLM applications — built to catch
hallucinations, measure output consistency, verify robustness against
adversarial prompts, and prevent quality regressions over time.

## Why this exists

Traditional software testing assumes deterministic output: `assert result ==
expected`. LLM-powered applications break that assumption — the same input
can produce differently worded (and sometimes differently *wrong*) answers
across runs. This project applies QA engineering discipline to that problem:
building the equivalent of unit tests, regression tests, and security tests
for an LLM application, using an LLM-as-judge pattern where deterministic
checks aren't possible.

The system under test is a small RAG (Retrieval-Augmented Generation) support
bot for a fictional product, CloudSync Pro. The actual subject isn't the
point — the evaluation framework built around it is.

## What it tests

| Test suite | Question it answers |
|---|---|
| `test_accuracy.py` | Does the bot answer correctly, and does it hallucinate on out-of-scope questions? |
| `test_consistency.py` | Does the bot give factually stable answers across repeated runs of the same question? |
| `test_adversarial.py` | Does the bot resist prompt injection, system prompt extraction, and out-of-scope requests bundled with legitimate ones? |
| `test_regression.py` | Has a code/prompt change made quality worse compared to a saved baseline? |

## Architecture

User question
│
▼
Retrieve relevant docs (ChromaDB vector search, with relevance threshold)
│
▼
Claude generates answer, grounded ONLY in retrieved context
│
▼
LLM-as-judge (separate Claude call) grades the answer against a rubric
│
▼
pytest asserts pass/fail based on judge's verdict

Two independent LLM calls are involved in every test: the bot being
evaluated, and a judge grading its output against an explicit rubric. This
mirrors how evaluation actually works in production LLM systems, since
deterministic string-matching can't capture whether a natural-language
answer is semantically correct.

## Key findings

This project surfaced several real, non-trivial bugs — documented in full in
[`DEVLOG.md`](DEVLOG.md):

- **Retrieval relevance gap** ([#1](../../issues/1)) — the bot fabricated
  plausible-sounding answers to out-of-scope questions because vector search
  always returned "closest available" documents regardless of actual
  relevance. Fixed with a distance threshold.
- **Judge calibration on paraphrasing** ([#2](../../issues/2)) — the judge
  flagged benign wording differences as factual contradictions. Fixed by
  tightening the grading rubric to focus on real-world fact equivalence.
- **Judge non-determinism** — the same judge call produced different verdicts
  on identical input because temperature wasn't explicitly set. Fixed by
  setting `temperature=0` on all judge calls.
- **Judge rubric drift** — the judge overrode the test's explicit
  `expected_behavior` field with its own opinion about "reasonable" bot
  behavior. Fixed by making the rubric explicitly authoritative in the judge
  prompt.
- **Regression test non-determinism** — an early regression test run flagged
  a false regression because the bot was still running at
  `temperature=1.0`. Fixed by enforcing `temperature=0` for regression and
  adversarial tests specifically, while keeping `temperature=1.0` for
  consistency tests where variance is the thing being measured.

The throughline: **LLM-as-judge is a genuinely useful evaluation pattern, but
it is not automatically reliable ground truth** — it requires the same
rigor, calibration, and skepticism as the system it's evaluating.

## Documentation

- [`DEVLOG.md`](DEVLOG.md) — chronological log of what was built, what broke,
  and why, written as the project progressed
- [`docs/how-the-judge-works.md`](docs/how-the-judge-works.md) — deep dive
  into the LLM-as-judge mechanism

## Running it locally

```bash
git clone https://github.com/juanpaluna1234/llm-eval-framework.git
cd llm-eval-framework
python -m venv venv
source venv/Scripts/activate   # Windows Git Bash; use venv\Scripts\Activate.ps1 for PowerShell
pip install -r requirements.txt
```

Add your Anthropic API key to a `.env` file:

ANTHROPIC_API_KEY=your_key_here


Run the full suite:
```bash
pytest tests/ -v -s
```

Or an individual suite:
```bash
pytest tests/test_accuracy.py -v -s
```

To update the regression baseline after confirming a change is a genuine
improvement (not automatic — this is a deliberate action):
```bash
python -m eval.update_baseline
```

## CI

All four test suites run automatically on every push and pull request via
GitHub Actions ([`.github/workflows/eval.yml`](.github/workflows/eval.yml)).

## Project structure

llm-eval-framework/
├── app/
│ ├── bot.py # RAG pipeline: retrieval + generation
│ └── documents.py # Sample knowledge base
├── eval/
│ ├── judge.py # LLM-as-judge scoring logic
│ ├── regression.py # Baseline comparison logic
│ └── update_baseline.py
├── tests/
│ ├── test_accuracy.py
│ ├── test_consistency.py
│ ├── test_adversarial.py
│ ├── test_regression.py
│ ├── golden_set.json
│ ├── adversarial_set.json
│ └── regression_baseline.json
├── docs/
│ └── how-the-judge-works.md
├── .github/workflows/eval.yml
└── DEVLOG.md


## Known limitations

- The consistency test is only as rigorous as the knowledge base is
  ambiguous — with short, unambiguous source documents, there's limited
  room for genuine variance to surface even at high temperature.
- LLM-as-judge remains an imperfect evaluator in principle, even with
  temperature and prompt fixes applied — a production system might use
  multiple judge calls with majority voting for higher-stakes decisions.
- The knowledge base and adversarial test set are intentionally small,
  built to demonstrate the evaluation methodology rather than provide
  exhaustive coverage.

## Stack

Python, pytest, Claude API (Haiku for judging, cost-efficient for
high-volume grading calls), ChromaDB, GitHub Actions.