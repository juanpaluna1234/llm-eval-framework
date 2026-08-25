import json
import pytest
from app.bot import index_documents, ask
from eval.judge import judge_adversarial

with open("tests/adversarial_set.json") as f:
    ADVERSARIAL_SET = json.load(f)


@pytest.fixture(scope="module", autouse=True)
def setup_index():
    index_documents()


@pytest.mark.parametrize("case", ADVERSARIAL_SET, ids=[c["id"] for c in ADVERSARIAL_SET])
def test_adversarial_robustness(case):
    answer = ask(case["prompt"], temperature=0)  # deterministic for security-relevant checks

    result = judge_adversarial(
        prompt=case["prompt"],
        answer=answer,
        attack_type=case["attack_type"],
        expected_behavior=case["expected_behavior"],
    )

    print(f"\n[{case['id']}] ({case['attack_type']}) Passed: {result['passed']} — {result['reasoning']}")
    print(f"  Prompt: {case['prompt']}")
    print(f"  Answer: {answer[:200]}")

    assert result["passed"], (
        f"Adversarial test failed: {case['prompt']}\n"
        f"Attack type: {case['attack_type']}\n"
        f"Answer: {answer}\n"
        f"Reasoning: {result['reasoning']}"
    )