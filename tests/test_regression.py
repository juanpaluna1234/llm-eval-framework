import json
import pytest
from app.bot import index_documents, ask
from eval.judge import judge_answer
from eval.regression import load_baseline, check_regression

with open("tests/golden_set.json") as f:
    GOLDEN_SET = json.load(f)


@pytest.fixture(scope="module", autouse=True)
def setup_index():
    index_documents()


@pytest.fixture(scope="module")
def baseline():
    return load_baseline()


@pytest.mark.parametrize("case", GOLDEN_SET, ids=[c["id"] for c in GOLDEN_SET])
def test_no_regression(case, baseline):
    answer = ask(case["question"], temperature=0)
    result = judge_answer(
        question=case["question"],
        answer=answer,
        expected_facts=case["expected_facts"],
        should_answer=case["should_answer"],
    )

    regression_check = check_regression(case["id"], result["score"], baseline)

    print(f"\n[{case['id']}] Score: {result['score']}/5 — {regression_check['reasoning']}")

    assert not regression_check["regressed"], (
        f"Regression detected for: {case['question']}\n"
        f"{regression_check['reasoning']}"
    )