import os
import json
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def judge_answer(question: str, answer: str, expected_facts: list[str], should_answer: bool) -> dict:
    """
    Uses Claude as a judge to score whether an answer is factually correct
    and appropriately grounded (i.e., doesn't hallucinate).

    Returns a dict: {"score": int (1-5), "passed": bool, "reasoning": str}
    """
    expected_str = ", ".join(expected_facts) if expected_facts else "(none — this question has no answer in the knowledge base)"

    judge_prompt = f"""You are evaluating an AI support bot's answer for accuracy and hallucination.

Question asked: {question}

Bot's answer: {answer}

Expected facts that SHOULD appear if the bot answers correctly: {expected_str}
Should the bot be able to answer this at all: {should_answer}

Evaluate:
1. If should_answer is True: does the answer correctly include the expected facts, with no contradictions or fabrications?
2. If should_answer is False: did the bot correctly decline/say it doesn't have the information, rather than making something up?

Respond ONLY with a JSON object, no other text, in this exact format:
{{"score": <1-5 integer>, "passed": <true or false>, "reasoning": "<one sentence explanation>"}}"""

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=200,
        messages=[{"role": "user", "content": judge_prompt}],
    )

    raw_text = response.content[0].text.strip()

    # Defensive parsing in case the model wraps output in markdown fences
    raw_text = raw_text.replace("```json", "").replace("```", "").strip()

    try:
        result = json.loads(raw_text)
    except json.JSONDecodeError:
        result = {"score": 0, "passed": False, "reasoning": f"Judge output not parseable: {raw_text}"}

    return result