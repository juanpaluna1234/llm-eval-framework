import json
import pytest
from app.bot import index_documents, ask
from eval.judge import judge_answer

with open("tests/golden_set.json") as f:
    GOLDEN_SET = json.load(f)


@pytest.fixture(scope="module", autouse=True)
def setup_index():
    """Index documents once before running the test module."""
    index_documents()


@pytest.mark.parametrize("case", GOLDEN_SET, ids=[c["id"] for c in GOLDEN_SET])
def test_answer_accuracy(case):
    answer = ask(case["question"])
    result = judge_answer(
        question=case["question"],
        answer=answer,
        expected_facts=case["expected_facts"],
        should_answer=case["should_answer"],
    )

    print(f"\n[{case['id']}] Score: {result['score']}/5 — {result['reasoning']}")

    assert result["passed"], (
        f"Failed: {case['question']}\n"
        f"Answer: {answer}\n"
        f"Reasoning: {result['reasoning']}"
    )