import json
import pytest
from app.bot import index_documents, ask
from eval.judge import judge_consistency

with open("tests/golden_set.json") as f:
    GOLDEN_SET = json.load(f)

# Only test consistency on questions the bot SHOULD answer —
# refusals are trivially consistent and not interesting to che ck here.
ANSWERABLE_CASES = [case for case in GOLDEN_SET if case["should_answer"]]

N_RUNS = 5


@pytest.fixture(scope="module", autouse=True)
def setup_index():
    index_documents()


@pytest.mark.parametrize("case", ANSWERABLE_CASES, ids=[c["id"] for c in ANSWERABLE_CASES])
def test_answer_consistency(case):
    answers = [ask(case["question"], temperature=1.0) for _ in range(N_RUNS)]

    result = judge_consistency(case["question"], answers)

    print(f"\n[{case['id']}] Consistent: {result['consistent']} — {result['reasoning']}")
    for i, ans in enumerate(answers):
        print(f"  Run {i+1}: {ans[:100]}...")

    assert result["consistent"], (
        f"Inconsistent answers for: {case['question']}\n"
        f"Reasoning: {result['reasoning']}\n"
        f"Answers: {answers}"
    )