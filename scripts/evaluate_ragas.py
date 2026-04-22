"""
RAGAS evaluation script for the ChatDoctor RAG pipeline.

Runs sample questions through the pipeline and evaluates with RAGAS
metrics using Google Gemini as the judge LLM and sentence-transformers
for embeddings.

Usage:
    python -m scripts.evaluate_ragas
    python -m scripts.evaluate_ragas --samples 5
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from datasets import Dataset

from app.config import settings
from app.services.rag_service import retrieve_context
from app.services.llm_service import generate_answer


SAMPLE_QUESTIONS: list[dict[str, str]] = [
    {
        "question": "What should I do if I have a persistent cough?",
        "ground_truth": (
            "A persistent cough lasting more than 2-3 weeks warrants medical evaluation. "
            "Consider seeing a doctor to rule out infections, asthma, acid reflux, or other causes."
        ),
    },
    {
        "question": "I have a headache and feel dizzy, what could be wrong?",
        "ground_truth": (
            "Headache with dizziness can be due to dehydration, low blood sugar, migraine, "
            "inner-ear issues, or anemia. Persistent or severe symptoms need medical review."
        ),
    },
    {
        "question": "My child has a fever of 39 degrees, should I go to the hospital?",
        "ground_truth": (
            "A fever of 39 C in a child is high. Infants under 3 months need immediate evaluation. "
            "Older children need urgent care if lethargic, dehydrated, or not improving in 24-48 hours."
        ),
    },
    {
        "question": "What are the symptoms of diabetes?",
        "ground_truth": (
            "Common diabetes symptoms include increased thirst, frequent urination, unexplained "
            "weight loss, fatigue, blurred vision, and slow-healing wounds."
        ),
    },
    {
        "question": "How can I treat a sore throat at home?",
        "ground_truth": (
            "Home remedies for sore throat include warm fluids, salt-water gargling, throat "
            "lozenges, rest, and over-the-counter pain relievers. See a doctor if fever or "
            "symptoms persist beyond a few days."
        ),
    },
    {
        "question": "What causes high blood pressure?",
        "ground_truth": (
            "High blood pressure can be caused by genetics, excess salt intake, obesity, lack of "
            "exercise, stress, smoking, alcohol, and underlying kidney or endocrine disease."
        ),
    },
    {
        "question": "I have been feeling very tired lately, what tests should I get?",
        "ground_truth": (
            "Common tests for chronic fatigue include complete blood count, thyroid panel, "
            "vitamin D and B12 levels, iron studies, and blood glucose."
        ),
    },
    {
        "question": "What are the side effects of ibuprofen?",
        "ground_truth": (
            "Ibuprofen side effects include stomach upset, ulcers, kidney issues, and increased "
            "cardiovascular risk with long-term use. Take with food and as directed."
        ),
    },
    {
        "question": "My stomach hurts after eating, what could it be?",
        "ground_truth": (
            "Post-meal stomach pain can be due to gastritis, acid reflux, ulcers, gallbladder "
            "issues, or food intolerances. Persistent symptoms warrant medical evaluation."
        ),
    },
    {
        "question": "How do I lower my cholesterol naturally?",
        "ground_truth": (
            "To lower cholesterol naturally: eat a diet rich in fiber and healthy fats, exercise "
            "regularly, maintain a healthy weight, avoid trans fats, and limit saturated fats."
        ),
    },
]


def run_evaluation(num_samples: int = 5) -> dict:
    samples = SAMPLE_QUESTIONS[:num_samples]

    eval_data: dict[str, list] = {
        "question": [],
        "answer": [],
        "contexts": [],
        "ground_truth": [],
    }

    print(f"Running {len(samples)} samples through the RAG pipeline ...")

    for i, s in enumerate(samples):
        q = s["question"]
        sources = retrieve_context(q, top_k=3)
        answer, confidence = generate_answer(q, sources)
        contexts = [src.snippet for src in sources] or [""]

        eval_data["question"].append(q)
        eval_data["answer"].append(answer)
        eval_data["contexts"].append(contexts)
        eval_data["ground_truth"].append(s["ground_truth"])

        print(f"  [{i+1}/{len(samples)}] confidence={confidence} sources={len(sources)}")

    dataset = Dataset.from_dict(eval_data)

    scores = _evaluate_with_ragas(dataset)
    if scores is None:
        print("Falling back to manual retrieval-only metrics ...")
        scores = _manual_retrieval_metrics(eval_data)

    output_path = Path("evaluation_results.json")
    output_path.write_text(json.dumps(scores, indent=2, ensure_ascii=False))
    print(f"\nResults saved to {output_path}")
    print(json.dumps(scores, indent=2))
    return scores


def _evaluate_with_ragas(dataset: Dataset) -> dict | None:
    if not settings.gemini_api_key:
        print("GEMINI_API_KEY not set; skipping RAGAS full evaluation.")
        return None
    try:
        from langchain_google_genai import (
            ChatGoogleGenerativeAI,
            GoogleGenerativeAIEmbeddings,
        )
        from ragas import evaluate
        from ragas.metrics import (
            answer_relevancy,
            context_precision,
            context_recall,
            faithfulness,
        )
        from ragas.llms import LangchainLLMWrapper
        from ragas.embeddings import LangchainEmbeddingsWrapper

        judge_llm = LangchainLLMWrapper(
            ChatGoogleGenerativeAI(
                model=settings.llm_model,
                google_api_key=settings.gemini_api_key,
                temperature=0.0,
            )
        )
        judge_embeddings = LangchainEmbeddingsWrapper(
            GoogleGenerativeAIEmbeddings(
                model="models/text-embedding-004",
                google_api_key=settings.gemini_api_key,
            )
        )

        result = evaluate(
            dataset,
            metrics=[faithfulness, answer_relevancy, context_precision, context_recall],
            llm=judge_llm,
            embeddings=judge_embeddings,
        )

        scores = {
            k: round(float(v), 4)
            for k, v in result.items()
            if isinstance(v, (int, float))
        }
        return scores
    except Exception as e:  # noqa: BLE001
        print(f"RAGAS evaluation failed: {e}")
        return None


def _manual_retrieval_metrics(eval_data: dict) -> dict:
    """Fallback metrics when RAGAS full eval is unavailable."""
    context_scores = [1.0 if c and c[0] else 0.0 for c in eval_data["contexts"]]
    answer_lengths = [len(a.split()) for a in eval_data["answer"]]

    return {
        "context_hit_rate": round(sum(context_scores) / len(context_scores), 4),
        "avg_answer_length_words": round(sum(answer_lengths) / len(answer_lengths), 1),
        "total_samples": len(eval_data["question"]),
        "note": "Fallback metrics (RAGAS full evaluation unavailable)",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run RAGAS evaluation on ChatDoctor RAG")
    parser.add_argument("--samples", type=int, default=5, help="Number of sample questions")
    args = parser.parse_args()

    run_evaluation(args.samples)


if __name__ == "__main__":
    main()
