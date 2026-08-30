"""
Generates an HTML report summarizing accuracy test results.
Run manually after a test run to get a shareable visual summary.
"""
import json
from datetime import datetime
from app.bot import index_documents, ask
from eval.judge import judge_answer

REPORT_PATH = "eval_report.html"


def generate_report():
    with open("tests/golden_set.json") as f:
        golden_set = json.load(f)

    index_documents()
    results = []

    for case in golden_set:
        answer = ask(case["question"], temperature=0)
        judged = judge_answer(
            question=case["question"],
            answer=answer,
            expected_facts=case["expected_facts"],
            should_answer=case["should_answer"],
        )
        results.append({
            "id": case["id"],
            "question": case["question"],
            "answer": answer,
            "score": judged["score"],
            "passed": judged["passed"],
            "reasoning": judged["reasoning"],
        })
        print(f"[{case['id']}] Score: {judged['score']}/5 — {'PASS' if judged['passed'] else 'FAIL'}")

    _write_html(results)
    print(f"\nReport written to {REPORT_PATH}")


def _write_html(results: list[dict]):
    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    avg_score = sum(r["score"] for r in results) / total if total else 0
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    rows = ""
    for r in results:
        status_color = "#2e7d32" if r["passed"] else "#c62828"
        status_text = "PASS" if r["passed"] else "FAIL"
        rows += f"""
        <tr>
            <td>{r['id']}</td>
            <td>{r['question']}</td>
            <td>{r['answer'][:150]}{'...' if len(r['answer']) > 150 else ''}</td>
            <td style="text-align:center;">{r['score']}/5</td>
            <td style="text-align:center; color:{status_color}; font-weight:bold;">{status_text}</td>
            <td>{r['reasoning']}</td>
        </tr>
        """

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>LLM Eval Report</title>
        <style>
            body {{ font-family: -apple-system, Segoe UI, sans-serif; margin: 40px; background: #fafafa; color: #222; }}
            h1 {{ margin-bottom: 4px; }}
            .meta {{ color: #666; margin-bottom: 24px; }}
            .summary {{ display: flex; gap: 24px; margin-bottom: 32px; }}
            .card {{ background: white; border-radius: 8px; padding: 16px 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
            .card .label {{ font-size: 13px; color: #888; }}
            .card .value {{ font-size: 28px; font-weight: bold; }}
            table {{ width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
            th {{ background: #f0f0f0; text-align: left; padding: 12px; font-size: 13px; text-transform: uppercase; color: #666; }}
            td {{ padding: 12px; border-top: 1px solid #eee; font-size: 14px; vertical-align: top; }}
        </style>
    </head>
    <body>
        <h1>LLM Evaluation Report</h1>
        <div class="meta">Generated {timestamp}</div>
        <div class="summary">
            <div class="card"><div class="label">Total Cases</div><div class="value">{total}</div></div>
            <div class="card"><div class="label">Passed</div><div class="value">{passed}/{total}</div></div>
            <div class="card"><div class="label">Avg Score</div><div class="value">{avg_score:.1f}/5</div></div>
        </div>
        <table>
            <tr><th>ID</th><th>Question</th><th>Answer</th><th>Score</th><th>Status</th><th>Judge Reasoning</th></tr>
            {rows}
        </table>
    </body>
    </html>
    """

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(html)


if __name__ == "__main__":
    generate_report()