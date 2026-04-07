import json
import csv
from pathlib import Path

DATASETS = {
    "HotpotQA": {
        "data_path": Path("hotpotqa_demo_results.json"),
        "qrels_path": Path("hotpotqa_test.tsv"),
    },
    "FiQA-2018": {
        "data_path": Path("fiqa_demo_results.json"),
        "qrels_path": Path("fiqa_test.tsv"),
    },
}


def load_qrels(path):
    qrels = {}
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            qid = str(row["query-id"]).strip()
            did = str(row["corpus-id"]).strip()
            score = int(row["score"])
            if score > 0:
                qrels.setdefault(qid, set()).add(did)
    return qrels


def mrr_at_k(results, relevant_doc_ids, k=3):
    for rank, item in enumerate(results[:k], start=1):
        if str(item.get("doc_id")).strip() in relevant_doc_ids:
            return 1.0 / rank
    return 0.0


def print_bucket(title, items, limit=20):
    print("\n" + "=" * 120)
    print(title)
    print("=" * 120)
    print(f"Found {len(items)} queries.\n")

    items = sorted(items, key=lambda x: (x["rrf"], x["colbert"], x["bm25"]), reverse=True)

    for item in items[:limit]:
        print(item["query"])
        print(f"  BM25 MRR@3:    {item['bm25']:.3f}")
        print(f"  ColBERT MRR@3: {item['colbert']:.3f}")
        print(f"  RRF MRR@3:     {item['rrf']:.3f}")
        print("-" * 120)


for dataset_name, paths in DATASETS.items():
    print("\n" + "#" * 140)
    print(f"DATASET: {dataset_name}")
    print("#" * 140)

    with open(paths["data_path"], "r", encoding="utf-8") as f:
        data = json.load(f)

    qrels = load_qrels(paths["qrels_path"])

    colbert_beats_bm25 = []
    rrf_beats_both = []
    bm25_wins = []

    for query_text, payload in data.items():
        qid = str(payload.get("query_id")).strip()
        relevant = qrels.get(qid, set())
        if not relevant:
            continue

        bm25 = mrr_at_k(payload.get("bm25", []), relevant, k=3)
        colbert = mrr_at_k(payload.get("colbert", []), relevant, k=3)
        rrf = mrr_at_k(payload.get("rrf", []), relevant, k=3)

        row = {
            "query": query_text,
            "bm25": bm25,
            "colbert": colbert,
            "rrf": rrf,
        }

        if colbert > bm25:
            colbert_beats_bm25.append(row)

        if rrf > bm25 and rrf > colbert:
            rrf_beats_both.append(row)

        if bm25 > colbert and bm25 > rrf:
            bm25_wins.append(row)

    print_bucket(f"1) {dataset_name} — QUERIES WHERE COLBERT BEATS BM25", colbert_beats_bm25)
    print_bucket(f"2) {dataset_name} — QUERIES WHERE RRF BEATS BOTH", rrf_beats_both)
    print_bucket(f"3) {dataset_name} — QUERIES WHERE BM25 WINS", bm25_wins)