import json
import os

BASELINE_PATH = "tests/regression_baseline.json"


def load_baseline() -> dict:
    """Load the saved baseline scores, or return empty dict if none exist yet."""
    if not os.path.exists(BASELINE_PATH):
        return {}
    with open(BASELINE_PATH) as f:
        return json.load(f)


def save_baseline(scores: dict):
    """Persist the current scores as the new baseline."""
    with open(BASELINE_PATH, "w") as f:
        json.dump(scores, f, indent=2)


def check_regression(case_id: str, current_score: int, baseline: dict, tolerance: int = 0) -> dict:
    """
    Compares a current score against the saved baseline for this case.
    Returns a dict with pass/fail and reasoning.
    tolerance allows for minor fluctuation (e.g., tolerance=1 allows a 1-point drop).
    """
    if case_id not in baseline:
        return {"regressed": False, "reasoning": f"No baseline yet for {case_id} — treating as first run."}

    baseline_score = baseline[case_id]
    if current_score < baseline_score - tolerance:
        return {
            "regressed": True,
            "reasoning": f"Score dropped from {baseline_score} to {current_score} (baseline: {baseline_score})",
        }
    return {
        "regressed": False,
        "reasoning": f"Score {current_score} meets or exceeds baseline {baseline_score}",
    }