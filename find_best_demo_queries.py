import json
import csv
from pathlib import Path

DATA_PATH = Path("hotpotqa_demo_results.json")
QRELS_PATH = Path("test.tsv")

with open(DATA_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

qrels = {}
with open(QRELS_PATH, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f, delimiter="\t")
    for row in reader:
        qid = row["query-id"]
        did = row["corpus-id"]
        score = int(row["score"])
        if score > 0:
            qrels.setdefault(qid, set()).add(str(did))

def mrr_at_k(results, relevant_doc_ids, k=3):
    for rank, item in enumerate(results[:k], start=1):
        if str(item.get("doc_id")) in relevant_doc_ids:
            return 1.0 / rank
    return 0.0

interesting = []

for query_text, payload in data.items():
    qid = payload.get("query_id")
    relevant = qrels.get(qid, set())
    if not relevant:
        continue

    bm25 = mrr_at_k(payload.get("bm25", []), relevant, k=3)
    colbert = mrr_at_k(payload.get("colbert", []), relevant, k=3)
    rrf = mrr_at_k(payload.get("rrf", []), relevant, k=3)

    # keep only non-ties
    if len({bm25, colbert, rrf}) > 1:
        interesting.append({
            "query": query_text,
            "bm25": bm25,
            "colbert": colbert,
            "rrf": rrf,
        })

# sort to prioritize queries where RRF is strongest
interesting.sort(key=lambda x: (x["rrf"], x["colbert"], x["bm25"]), reverse=True)

print(f"Found {len(interesting)} discriminative queries.\n")
for item in interesting[:20]:
    print("=" * 100)
    print(item["query"])
    print(f"BM25 MRR@3:    {item['bm25']:.3f}")
    print(f"ColBERT MRR@3: {item['colbert']:.3f}")
    print(f"RRF MRR@3:     {item['rrf']:.3f}")