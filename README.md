# Hybrid Search Engine (BM25 + ColBERT + RRF)

A hybrid information retrieval system that combines **sparse lexical retrieval (BM25)** and **dense neural retrieval (ColBERT)** to improve document ranking performance across heterogeneous datasets.

This project was developed as part of an MSc **Information Retrieval coursework project** and investigates whether hybrid retrieval systems improve robustness across domains compared with sparse or dense methods alone.

Live demo:  
https://hybridsearchengine.streamlit.app/

---

# Project Overview

The full technical report describing the system design, evaluation methodology, and experiments can be found here:

[Full Technical Report](docs/hybrid_search_engine_report.pdf)

Traditional search engines rely on **lexical retrieval methods** such as BM25 that rank documents using keyword matching and corpus statistics.

However, lexical methods struggle with:

- synonymy
- paraphrasing
- semantic similarity

Dense neural retrieval models address this limitation by encoding queries and documents into **vector embeddings** and measuring semantic similarity. However, dense models may degrade when applied to out of domain corpora.

This project implements a **hybrid retrieval architecture** that produces:

- **BM25 ranking** (sparse retrieval)
- **ColBERT ranking** (dense retrieval)
- **Hybrid ranking using Reciprocal Rank Fusion (RRF)**

The hybrid ranking combines both approaches to produce more robust results.

---

# System Architecture

The search engine operates in two phases.

## Phase 1 — Document Preparation

Documents are processed before user queries.

Steps:

1. Text cleaning (lowercasing)
2. Tokenisation
3. BM25 indexing using Elasticsearch
4. Dense encoding using ColBERT

Outputs:

- inverted index (BM25)
- dense document embeddings (ColBERT)

These representations are stored for efficient query-time retrieval.

---

## Phase 2 — Query Processing

When a user enters a query:

1. Query cleaning
2. BM25 retrieval
3. ColBERT semantic retrieval
4. Reciprocal Rank Fusion merges both rankings
5. Final ranked results returned

Architecture flow:

```
User Query
    ↓
Query Cleaning
    ↓
 ┌───────────────┬───────────────┐
 │               │               │
BM25 Retrieval   ColBERT Retrieval
 │               │
BM25 Ranked List ColBERT Ranked List
        ↓
Reciprocal Rank Fusion (RRF)
        ↓
Final Ranked Results
```

---

# Retrieval Models

## BM25 (Sparse Retrieval)

BM25 ranks documents using:

- term frequency
- inverse document frequency
- document length normalization

It is implemented using **Elasticsearch**, which constructs an inverted index for efficient retrieval.

---

## ColBERT (Dense Retrieval)

ColBERT is a neural retrieval model based on BERT using **late interaction**.

Instead of compressing documents into a single vector, ColBERT compares token-level embeddings between query and documents.

Similarity scoring:

```
score(Q, D) = Σ max(qᵢ · d)
```

This enables fine-grained semantic matching.

---

## Reciprocal Rank Fusion (Hybrid Retrieval)

The final ranking is produced using **Reciprocal Rank Fusion (RRF)**.

RRF merges rankings from BM25 and ColBERT based on their rank positions rather than raw scores.

Advantages:

- no score normalization required
- robust across retrieval models
- strong performance in zero-shot settings

---

# Datasets

The system is evaluated using three datasets from the **BEIR benchmark**:

| Dataset | Domain |
|-------|-------|
| TREC-COVID | Biomedical research retrieval |
| HotpotQA | Multi-hop question answering |
| FiQA-2018 | Financial question answering |

Evaluating across multiple domains allows the system to test cross-domain, zero-shot retrieval robustness.
(not all documents from corpora were included in COLBERT training due to computational restraints).

---

# Evaluation Metrics

Performance is measured using standard Information Retrieval metrics.

### nDCG@10
Measures ranking quality in the top results.

### MRR@10
Measures how early the first relevant document appears.

### Recall@100
Measures how many relevant documents are retrieved.

Together these metrics evaluate:

- ranking quality
- early precision
- retrieval coverage.

---

# Tech Stack

- Python
- Elasticsearch
- PyTorch
- ColBERT
- BEIR Benchmark
- pytrec_eval
- Streamlit (for interactive demo)

---

# Running the Project

Download the repository
```

Install dependencies
```

Run Elasticsearch
```

Run the Streamlit interface
```

streamlit run app.py (on terminal)
```

---

# Example Query

```
covid vaccine transmission
```

The system retrieves documents that:

- contain the query keywords
- discuss related semantic concepts

Hybrid retrieval improves relevance compared with BM25 or ColBERT alone.

---

# Authors

Haadi Muhammad Iftikhar  
Saif Ali Khan Mangan  
Marharyta Dzhafarova  

MSc Data Science & AI  
Queen Mary University of London

---
