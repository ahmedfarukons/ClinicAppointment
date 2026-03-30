"""
RAGAS evaluation script for the ChatDoctor RAG pipeline.

Runs a set of sample questions through the pipeline and evaluates with
RAGAS metrics: faithfulness, answer_relevancy, context_precision.

Usage:
    python -m scripts.evaluate_ragas
    python -m scripts.evaluate_ragas --samples 20
"""

import argparse
import json
from pathlib import Path

from datasets import Dataset

from app.config import settings
from app.services.rag_service import retrieve_context
from app.services.llm_service import generate_answer


SAMPLE_QUESTIONS = [
    "What should I do if I have a persistent cough?",
    "I have a headache and feel dizzy, what could be wrong?",
    "My child has a fever of 39 degrees, should I go to the hospital?",
    "What are the symptoms of diabetes?",
    "I have pain in my chest when I breathe deeply.",
    "How can I treat a sore throat at home?",
    "What causes high blood pressure?",
    "I have been feeling very tired lately, what tests should I get?",
    "What are the side effects of ibuprofen?",
    "My stomach hurts after eating, what could it be?",
]


def run_evaluation(num_samples: int = 10) -> dict:
    questions = SAMPLE_QUESTIONS[:num_samples]

    eval_data = {
        "question": [],
        "answer": [],
        "contexts": [],
        "ground_truth": [],
    }

    print(f"Running {len(questions)} samples through the RAG pipeline …")

    for i, q in enumerate(questions):
        sources = retrieve_context(q, top_k=3)
        answer, confidence = generate_answer(q, sources)

        contexts = [s.snippet for s in sources]

        eval_data["question"].append(q)
        eval_data["answer"].append(answer)
        eval_data["contexts"].append(contexts)
        eval_data["ground_truth"].append("")

        print(f"  [{i+1}/{len(questions)}] confidence={confidence} sources={len(sources)}")

    dataset = Dataset.from_dict(eval_data)

    try:
        from ragas import evaluate
        from ragas.metrics import (
            answer_relevancy,
            context_precision,
            faithfulness,
        )

        result = evaluate(
            dataset,
            metrics=[faithfulness, answer_relevancy, context_precision],
        )

        scores = {k: round(v, 4) for k, v in result.items() if isinstance(v, (int, float))}
    except Exception as e:
        print(f"RAGAS evaluation failed (may need OpenAI key or compatible LLM): {e}")
        print("Falling back to manual retrieval-only metrics …")
        scores = _manual_retrieval_metrics(eval_data)

    output_path = Path("evaluation_results.json")
    output_path.write_text(json.dumps(scores, indent=2, ensure_ascii=False))
    print(f"\nResults saved to {output_path}")
    print(json.dumps(scores, indent=2))
    return scores


def _manual_retrieval_metrics(eval_data: dict) -> dict:
    """Fallback metrics when RAGAS full eval is unavailable."""
    context_scores = []
    for contexts in eval_data["contexts"]:
        if contexts:
            context_scores.append(1.0)
        else:
            context_scores.append(0.0)

    answer_lengths = [len(a.split()) for a in eval_data["answer"]]

    return {
        "context_hit_rate": round(sum(context_scores) / len(context_scores), 4),
        "avg_answer_length_words": round(sum(answer_lengths) / len(answer_lengths), 1),
        "total_samples": len(eval_data["question"]),
        "note": "Fallback metrics (RAGAS full eval unavailable)",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run RAGAS evaluation on ChatDoctor RAG")
    parser.add_argument("--samples", type=int, default=10, help="Number of sample questions")
    args = parser.parse_args()

    run_evaluation(args.samples)


if __name__ == "__main__":
    main()
