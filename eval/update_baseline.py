"""
Run this manually after confirming the golden set results look good,
to intentionally update the regression baseline. This is a deliberate
action, not something that happens automatically on every test run.
"""
import json
from app.bot import index_documents, ask
from eval.judge import judge_answer
from eval.regression import save_baseline

with open("tests/golden_set.json") as f:
    GOLDEN_SET = json.load(f)

index_documents()
scores = {}

for case in GOLDEN_SET:
    answer = ask(case["question"], temperature=0)
    result = judge_answer(
        question=case["question"],
        answer=answer,
        expected_facts=case["expected_facts"],
        should_answer=case["should_answer"],
    )
    scores[case["id"]] = result["score"]
    print(f"[{case['id']}] Score: {result['score']}/5")

save_baseline(scores)
print(f"\nBaseline updated: {scores}")