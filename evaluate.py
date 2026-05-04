"""
evaluate.py — Đánh giá RAG pipeline với 10 test questions.
Chạy: python evaluate.py
Kết quả lưu vào evaluation_results.json và in ra bảng tổng hợp.
"""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(__file__))

from config import get_settings
from src.rag import load_data, build_or_load_indexes, build_chain, run_query

# ── 10 test questions (3 types) ────────────────────────────────────────────────
TEST_QUESTIONS = [
    {"id": 1,  "type": "Troubleshooting", "question": "My pod is stuck in CrashLoopBackOff. How do I debug it?"},
    {"id": 2,  "type": "Troubleshooting", "question": "My pod status is OOMKilled. What does that mean and how do I fix it?"},
    {"id": 3,  "type": "Troubleshooting", "question": "My deployment pods are stuck in Pending state. What should I check?"},
    {"id": 4,  "type": "Troubleshooting", "question": "My pod shows ImagePullBackOff error. How do I fix it?"},
    {"id": 5,  "type": "How-to",          "question": "How do I create a ConfigMap in Kubernetes?"},
    {"id": 6,  "type": "How-to",          "question": "How do I expose a deployment as a service in Kubernetes?"},
    {"id": 7,  "type": "How-to",          "question": "How do I get logs from a running pod?"},
    {"id": 8,  "type": "Concept",         "question": "What is a Pod in Kubernetes?"},
    {"id": 9,  "type": "Concept",         "question": "What is the difference between a Deployment and a StatefulSet?"},
    {"id": 10, "type": "Concept",         "question": "What is a Kubernetes namespace and when should I use it?"},
]

JUDGE_PROMPT = """You are evaluating a Kubernetes Q&A system.

Question: {question}

Retrieved Context:
{context}

Answer given:
{answer}

Score the answer on two criteria (integer 1-5 each):

1. Faithfulness: Does the answer rely on the retrieved context rather than making things up?
   1 = completely fabricated, 5 = fully grounded in context

2. Relevance: Does the answer actually address the question asked?
   1 = completely off-topic, 5 = directly and completely answers the question

Respond ONLY with valid JSON, no explanation, no markdown:
{{"faithfulness": <1-5>, "relevance": <1-5>, "comment": "<one short sentence>"}}"""


def call_with_retry(fn, max_retries=5):
    """Gọi fn(), nếu 429 thì đợi rồi thử lại."""
    for attempt in range(max_retries):
        try:
            return fn()
        except Exception as e:
            msg = str(e)
            if "429" in msg or "RESOURCE_EXHAUSTED" in msg:
                # Parse retry delay từ message nếu có
                wait = 65
                import re
                m = re.search(r"retryDelay.*?(\d+)s", msg)
                if m:
                    wait = int(m.group(1)) + 5
                print(f"  ⏳ Rate limit hit, waiting {wait}s before retry {attempt+1}/{max_retries}...")
                time.sleep(wait)
            else:
                raise
    raise Exception(f"Failed after {max_retries} retries")


def judge_answer(question: str, context: str, answer: str) -> dict:
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_core.messages import HumanMessage

    cfg = get_settings()
    judge = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        google_api_key=cfg.gemini_api_key,
        temperature=0.0,
        max_output_tokens=256,
    )
    prompt = JUDGE_PROMPT.format(
        question=question,
        context=context[:2000],
        answer=answer,
    )
    def _call():
        response = judge.invoke([HumanMessage(content=prompt)])
        raw = response.content.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return json.loads(raw.strip())

    try:
        return call_with_retry(_call)
    except Exception as e:
        print(f"  ⚠ Judge failed: {e}")
        return {"faithfulness": 0, "relevance": 0, "comment": "evaluation failed"}


def format_context_for_judge(doc_previews: list) -> str:
    return "\n".join(f"[{i+1}] {d}" for i, d in enumerate(doc_previews))


def print_table(results: list):
    print("\n" + "=" * 90)
    print(f"{'#':<4} {'Type':<16} {'Question':<42} {'Faith':>6} {'Relev':>6}")
    print("=" * 90)
    for r in results:
        q_short = r["question"][:40] + "…" if len(r["question"]) > 40 else r["question"]
        faith = f"{r['faithfulness']}/5" if r['faithfulness'] > 0 else "ERR"
        relev = f"{r['relevance']}/5"    if r['relevance'] > 0    else "ERR"
        print(f"{r['id']:<4} {r['type']:<16} {q_short:<42} {faith:>6} {relev:>6}")
    print("=" * 90)
    valid = [r for r in results if r["faithfulness"] > 0]
    if valid:
        avg_f = sum(r["faithfulness"] for r in valid) / len(valid)
        avg_r = sum(r["relevance"]    for r in valid) / len(valid)
        print(f"{'':4} {'AVERAGE':16} {'':42} {avg_f:>5.1f}/5 {avg_r:>5.1f}/5")
    print("=" * 90)
    print(f"\nTotal: {len(results)} questions | Valid: {len(valid)}")


def main():
    cfg = get_settings()
    if not cfg.gemini_api_key:
        print("❌ GEMINI_API_KEY not found. Check your .env file.")
        return

    print("⎈ K8s RAG — Evaluation")
    print("=" * 50)
    print("Loading data & index...")
    docs      = load_data()
    retriever = build_or_load_indexes(docs)
    chain     = build_chain(retriever, api_key=cfg.gemini_api_key)
    print(f"✅ Index loaded. Running {len(TEST_QUESTIONS)} test questions...\n")

    results = []
    for item in TEST_QUESTIONS:
        print(f"[{item['id']:02d}/10] {item['question'][:65]}…")

        # Run RAG — retry nếu 429
        try:
            result = call_with_retry(lambda q=item["question"]: run_query(chain, q))
        except Exception as e:
            print(f"  ⚠ RAG failed: {e}")
            results.append({
                "id": item["id"], "type": item["type"],
                "question": item["question"], "answer": "",
                "n_docs": 0, "latency_s": 0,
                "faithfulness": 0, "relevance": 0, "comment": "rag failed",
            })
            continue

        answer      = result["answer"]
        context     = format_context_for_judge(result["doc_previews"])

        # Delay giữa RAG call và judge call để tránh hit rate limit
        time.sleep(4)

        # Judge
        scores = judge_answer(item["question"], context, answer)

        row = {
            "id":           item["id"],
            "type":         item["type"],
            "question":     item["question"],
            "answer":       answer,
            "n_docs":       result["n_sources"],
            "latency_s":    result["latency_s"],
            "faithfulness": scores.get("faithfulness", 0),
            "relevance":    scores.get("relevance", 0),
            "comment":      scores.get("comment", ""),
        }
        results.append(row)
        print(f"       Faithfulness: {row['faithfulness']}/5 | Relevance: {row['relevance']}/5")
        print(f"       Comment: {row['comment']}")

        # Delay giữa các câu hỏi
        if item["id"] < len(TEST_QUESTIONS):
            print(f"       Waiting 5s before next question...")
            time.sleep(5)
        print()

    print_table(results)

    out_path = "evaluation_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n💾 Full results saved to {out_path}")


if __name__ == "__main__":
    main()