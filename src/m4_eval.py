from __future__ import annotations

"""Module 4: RAGAS Evaluation — 4 metrics + failure analysis."""

import os, sys, json, re
from dataclasses import dataclass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import TEST_SET_PATH


@dataclass
class EvalResult:
    question: str
    answer: str
    contexts: list[str]
    ground_truth: str
    faithfulness: float
    answer_relevancy: float
    context_precision: float
    context_recall: float


def load_test_set(path: str = TEST_SET_PATH) -> list[dict]:
    """Load test set from JSON. (Đã implement sẵn)"""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def evaluate_ragas(questions: list[str], answers: list[str],
                   contexts: list[list[str]], ground_truths: list[str]) -> dict:
    """Run RAGAS evaluation."""
    try:
        from ragas import evaluate
        from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall
        from datasets import Dataset

        dataset = Dataset.from_dict({
            "question": questions,
            "answer": answers,
            "contexts": contexts,
            "ground_truth": ground_truths,
        })
        result = evaluate(dataset, metrics=[
            faithfulness,
            answer_relevancy,
            context_precision,
            context_recall,
        ])
        df = result.to_pandas()
        per_question = [
            EvalResult(
                question=row["question"],
                answer=row["answer"],
                contexts=row["contexts"],
                ground_truth=row["ground_truth"],
                faithfulness=float(row.get("faithfulness", 0.0)),
                answer_relevancy=float(row.get("answer_relevancy", 0.0)),
                context_precision=float(row.get("context_precision", 0.0)),
                context_recall=float(row.get("context_recall", 0.0)),
            )
            for _, row in df.iterrows()
        ]
        return {
            "faithfulness": _avg(c.faithfulness for c in per_question),
            "answer_relevancy": _avg(c.answer_relevancy for c in per_question),
            "context_precision": _avg(c.context_precision for c in per_question),
            "context_recall": _avg(c.context_recall for c in per_question),
            "per_question": per_question,
        }
    except Exception as e:
        print(f"  ⚠️  RAGAS evaluation failed: {e}")
        per_question = [
            _heuristic_eval(question, answer, ctxs, ground_truth)
            for question, answer, ctxs, ground_truth
            in zip(questions, answers, contexts, ground_truths)
        ]
        return {
            "faithfulness": _avg(c.faithfulness for c in per_question),
            "answer_relevancy": _avg(c.answer_relevancy for c in per_question),
            "context_precision": _avg(c.context_precision for c in per_question),
            "context_recall": _avg(c.context_recall for c in per_question),
            "per_question": per_question,
        }


def failure_analysis(eval_results: list[EvalResult], bottom_n: int = 10) -> list[dict]:
    """Analyze bottom-N worst questions using Diagnostic Tree."""
    diagnostic_tree = {
        "faithfulness": ("LLM hallucinating", "Tighten prompt, lower temperature"),
        "context_recall": ("Missing relevant chunks", "Improve chunking or add BM25"),
        "context_precision": ("Too many irrelevant chunks", "Add reranking or metadata filter"),
        "answer_relevancy": ("Answer does not match question", "Improve prompt template"),
    }
    scored = []
    for result in eval_results:
        metrics = {
            "faithfulness": result.faithfulness,
            "answer_relevancy": result.answer_relevancy,
            "context_precision": result.context_precision,
            "context_recall": result.context_recall,
        }
        avg_score = _avg(metrics.values())
        worst_metric = min(metrics, key=metrics.get)
        diagnosis, suggested_fix = diagnostic_tree[worst_metric]
        scored.append({
            "question": result.question,
            "worst_metric": worst_metric,
            "score": avg_score,
            "metric_score": metrics[worst_metric],
            "diagnosis": diagnosis,
            "suggested_fix": suggested_fix,
        })

    return sorted(scored, key=lambda item: item["score"])[:bottom_n]


def _avg(values) -> float:
    nums = [float(v) for v in values]
    return sum(nums) / len(nums) if nums else 0.0


def _heuristic_eval(question: str, answer: str, contexts: list[str], ground_truth: str) -> EvalResult:
    joined_context = " ".join(contexts)
    answer_tokens = _tokens(answer)
    question_tokens = _tokens(question)
    context_tokens = _tokens(joined_context)
    ground_truth_tokens = _tokens(ground_truth)

    faithfulness = _overlap(answer_tokens, context_tokens)
    answer_relevancy = _overlap(answer_tokens, question_tokens | ground_truth_tokens)
    context_precision = _overlap(context_tokens, question_tokens | ground_truth_tokens)
    context_recall = _overlap(ground_truth_tokens, context_tokens)

    return EvalResult(
        question=question,
        answer=answer,
        contexts=contexts,
        ground_truth=ground_truth,
        faithfulness=faithfulness,
        answer_relevancy=answer_relevancy,
        context_precision=context_precision,
        context_recall=context_recall,
    )


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"\w+", text.lower(), flags=re.UNICODE))


def _overlap(source: set[str], target: set[str]) -> float:
    if not source:
        return 0.0
    return len(source & target) / len(source)


def save_report(results: dict, failures: list[dict], path: str = "reports/ragas_report.json"):
    """Save evaluation report to JSON. (Đã implement sẵn)"""
    report = {
        "aggregate": {k: v for k, v in results.items() if k != "per_question"},
        "num_questions": len(results.get("per_question", [])),
        "failures": failures,
    }
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"Report saved to {path}")


if __name__ == "__main__":
    test_set = load_test_set()
    print(f"Loaded {len(test_set)} test questions")
    print("Run pipeline.py first to generate answers, then call evaluate_ragas().")
