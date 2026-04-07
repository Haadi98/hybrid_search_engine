import json
import re
import difflib
import csv
from pathlib import Path

import streamlit as st

st.set_page_config(
    page_title="Hybrid Search Engine",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
    /* === GLOBAL === */
    .stApp {
        background: linear-gradient(160deg, #1a2332 0%, #0f172a 40%, #020617 100%);
        color: #e2e8f0;
        font-family: 'Inter', -apple-system, sans-serif;
    }
    header[data-testid="stHeader"] { background: transparent; }
    [data-testid="stToolbar"] { display: none; }

    h1, h2, h3, h4, h5, h6, p, div, label, span {
        color: #e2e8f0 !important;
    }

    /* === BADGE === */
    .badge {
        display: inline-block;
        background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%);
        color: #fff !important;
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 2px;
        text-transform: uppercase;
        padding: 6px 16px;
        border-radius: 20px;
        margin-bottom: 8px;
    }

    /* === TITLE === */
    .main-title {
        font-size: 2.8rem;
        font-weight: 800;
        color: #f1f5f9 !important;
        line-height: 1.15;
        margin: 8px 0 12px 0;
    }
    .main-subtitle {
        font-size: 1rem;
        color: #94a3b8 !important;
        margin-bottom: 32px;
    }

    /* === SEARCH INPUT === */
    .stTextInput > div > div > input,
    .stTextInput input {
        background-color: rgba(30,41,59,0.9) !important;
        color: #f1f5f9 !important;
        -webkit-text-fill-color: #f1f5f9 !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 14px !important;
        padding: 14px 18px !important;
        font-size: 1rem !important;
    }
    .stTextInput > div > div > input:focus,
    .stTextInput input:focus {
        border-color: #06b6d4 !important;
        box-shadow: 0 0 0 2px rgba(6,182,212,0.15) !important;
    }
    .stTextInput input::placeholder,
    .stTextInput > div > div > input::placeholder,
    .stTextInput > div > div > input::-webkit-input-placeholder,
    .stTextInput > div > div > input::-moz-placeholder {
        color: #94a3b8 !important;
        -webkit-text-fill-color: #94a3b8 !important;
        opacity: 1 !important;
    }

    /* === SEARCH BUTTON === */
    .stButton > button {
        background: linear-gradient(135deg, #60a5fa, #3b82f6) !important;
        color: white !important;
        -webkit-text-fill-color: white !important;
        border: none !important;
        border-radius: 14px !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        padding: 12px 28px !important;
        transition: all 0.2s !important;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #93c5fd, #60a5fa) !important;
        box-shadow: 0 4px 20px rgba(96,165,250,0.3) !important;
        transform: translateY(-1px) !important;
    }

    /* === EXAMPLE QUERY CHIPS === */
    div.stButton > button[kind="secondary"] {
        background: rgba(255,255,255,0.04) !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        color: #94a3b8 !important;
        -webkit-text-fill-color: #94a3b8 !important;
        border-radius: 10px !important;
        font-size: 0.82rem !important;
        padding: 8px 16px !important;
        font-weight: 400 !important;
        box-shadow: none !important;
        transform: none !important;
    }
    div.stButton > button[kind="secondary"]:hover {
        background: rgba(6,182,212,0.08) !important;
        border-color: rgba(6,182,212,0.25) !important;
        color: #e2e8f0 !important;
        -webkit-text-fill-color: #e2e8f0 !important;
        box-shadow: none !important;
        transform: none !important;
    }

    /* === DATASET CARD === */
    .dataset-card {
        background: rgba(255,255,255,0.02);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 18px;
        padding: 24px 28px;
        margin: 24px 0;
    }
    .dataset-label {
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: #64748b !important;
        margin-bottom: 4px;
    }
    .dataset-name {
        font-size: 1.4rem;
        font-weight: 700;
        color: #f1f5f9 !important;
        margin-bottom: 8px;
    }
    .dataset-query {
        font-size: 0.9rem;
        color: #94a3b8 !important;
    }
    .matched-query {
        font-size: 0.85rem;
        color: #06b6d4 !important;
        margin-top: 4px;
    }

    /* === RESULT COLUMNS === */
    .result-column {
        background: rgba(255,255,255,0.02);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 18px;
        padding: 16px 20px;
        min-height: auto;
        margin-bottom: 12px;
    }
    .result-header {
        font-size: 1.2rem;
        font-weight: 700;
        color: #f1f5f9 !important;
        margin-bottom: 2px;
    }
    .result-subtitle {
        font-size: 0.8rem;
        color: #64748b !important;
        margin-bottom: 8px;
    }

    /* === RESULT ITEM === */
    .result-item {
        background: rgba(255,255,255,0.02);
        border: 1px solid rgba(255,255,255,0.05);
        border-radius: 14px;
        padding: 18px;
        margin-bottom: 12px;
    }
    .result-item-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 6px;
    }
    .rank-badge {
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 1px;
        color: #06b6d4 !important;
        margin-bottom: 4px;
    }
    .score-badge {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.08);
        color: #94a3b8 !important;
        font-size: 0.8rem;
        font-weight: 600;
        padding: 4px 12px;
        border-radius: 20px;
        white-space: nowrap;
    }
    .result-title {
        font-size: 0.95rem;
        font-weight: 600;
        color: #e2e8f0 !important;
        margin-bottom: 8px;
    }
    .result-snippet {
        font-size: 0.83rem;
        color: #94a3b8 !important;
        line-height: 1.5;
        margin-bottom: 8px;
    }
    .result-docid {
        font-size: 0.75rem;
        color: #475569 !important;
    }

    /* === HIDE STREAMLIT DEFAULTS === */
    div[data-testid="stHorizontalBlock"] > div {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
    }
    .stMarkdown { color: #e2e8f0; }
</style>
""", unsafe_allow_html=True)


# ============================================================
# DATA — load all datasets at startup
# ============================================================
DATASETS_CONFIG = {
    "HotpotQA": {
        "data_file": "hotpotqa_demo_results_top10.json",
        "qrels_file": "hotpotqa_test.tsv",
        "examples": [
            "What is the first two words of the fifth studio album of Joseph Edgar Foreman?",
            "What government position was held by the woman who portrayed Corliss Archer in the film Kiss and Tell?",
            'The director of the romantic comedy "Big Stone Gap" is based in what New York city?',
        ],
    },
    "FiQA-2018": {
        "data_file": "fiqa_demo_results.json",
        "qrels_file": "fiqa_test.tsv",
        "examples": [
            "How do you determine “excess cash” for Enterprise Value calculations from a balance sheet?",
            "What are the consequences of IRS “reclassification” on both employer and employee?",
            "Is working on a W2 basis, with benefits paid to me, a good idea?"
        ],
    },
}


@st.cache_data
def load_all_datasets():
    all_data = {}
    all_qrels = {}
    all_queries = {}

    for ds_name, cfg in DATASETS_CONFIG.items():
        base = Path(__file__).parent
        data_path = base / cfg["data_file"]
        qrels_path = base / cfg["qrels_file"]

        if not data_path.exists() or not qrels_path.exists():
            continue

        with open(data_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        sample_query = next(iter(data))
        print("DEBUG FILE:", data_path)
        print("DEBUG BM25 LEN:", len(data[sample_query]["bm25"]))
        all_data[ds_name] = data

        qrels = {}
        with open(qrels_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter="\t")
            for row in reader:
                qid = row["query-id"]
                cid = row["corpus-id"]
                score = int(row["score"])
                if score > 0:
                    qrels.setdefault(qid, set()).add(cid)
        all_qrels[ds_name] = qrels

        for query_text in data.keys():
            all_queries[query_text] = ds_name

    return all_data, all_qrels, all_queries


ALL_DATA, ALL_QRELS, QUERY_TO_DATASET = load_all_datasets()
ALL_QUERY_TEXTS = list(QUERY_TO_DATASET.keys())


# ============================================================
# HELPERS
# ============================================================
def mrr_at_k(results, relevant_doc_ids, k=10):
    top_k_ids = [str(item.get("doc_id")) for item in results[:k]]
    for rank, doc_id in enumerate(top_k_ids, start=1):
        if doc_id in relevant_doc_ids:
            return 1.0 / rank
    return 0.0


def normalize(text):
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text


def search_all_datasets(query):
    query = query.strip()
    if not query:
        return None, None, None

    if query in QUERY_TO_DATASET:
        ds = QUERY_TO_DATASET[query]
        return query, ALL_DATA[ds][query], ds

    query_norm = normalize(query)
    query_tokens = [t for t in query_norm.split() if len(t) >= 3]
    if query_tokens:
        scored = []
        for candidate in ALL_QUERY_TEXTS:
            candidate_norm = normalize(candidate)
            score = sum(1 for token in query_tokens if token in candidate_norm)
            if score > 0:
                scored.append((score, candidate))
        if scored:
            scored.sort(key=lambda x: (-x[0], len(x[1])))
            best = scored[0][1]
            ds = QUERY_TO_DATASET[best]
            return best, ALL_DATA[ds][best], ds

    matches = difflib.get_close_matches(query, ALL_QUERY_TEXTS, n=1, cutoff=0.2)
    if matches:
        best = matches[0]
        ds = QUERY_TO_DATASET[best]
        return best, ALL_DATA[ds][best], ds

    return None, None, None


def render_result_card(item, score_label="Score"):
    title = item.get('title', 'Untitled document')
    score = item.get('score', 0)
    snippet = item.get('snippet', '')
    doc_id = item.get('doc_id', '')
    rank = item.get('rank', '?')

    st.markdown(f"""
    <div class="result-item">
        <div class="result-item-header">
            <div>
                <div class="rank-badge">RANK #{rank}</div>
                <div class="result-title">{title if title else "Untitled"}</div>
            </div>
            <div class="score-badge">{score_label}: {score:.4f}</div>
        </div>
        <div class="result-snippet">{snippet[:250]}{'...' if len(snippet) > 250 else ''}</div>
        <div class="result-docid">Doc ID: {doc_id}</div>
    </div>
    """, unsafe_allow_html=True)


def render_results_column(title, subtitle, results, score_label="Score"):
    st.markdown(f"""
    <div class="result-column">
        <div class="result-header">{title}</div>
        <div class="result-subtitle">{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)

    if not results:
        st.info("No results found.")
        return

    for item in results:
        render_result_card(item, score_label=score_label)


# ============================================================
# HEADER
# ============================================================
st.markdown('<div class="badge">HYBRID SEARCH ENGINE</div>', unsafe_allow_html=True)
st.markdown('<div class="main-title">Hybrid Search Engine: BM25, ColBERT & RRF</div>', unsafe_allow_html=True)
st.markdown('<div class="main-subtitle">Search across HotpotQA, FiQA-2018, and TREC-COVID. Compares sparse retrieval, dense retrieval, and hybrid fusion side by side.</div>', unsafe_allow_html=True)

# ============================================================
# SESSION STATE
# ============================================================
if "selected_query" not in st.session_state:
    st.session_state.selected_query = ""
if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "last_matched_query" not in st.session_state:
    st.session_state.last_matched_query = None
if "last_dataset" not in st.session_state:
    st.session_state.last_dataset = None
if "search_triggered" not in st.session_state:
    st.session_state.search_triggered = False
if "last_metric_scores" not in st.session_state:
    st.session_state.last_metric_scores = None

# ============================================================
# SEARCH BAR
# ============================================================
col_input, col_button = st.columns([6, 1])
with col_input:
    query_input = st.text_input(
        "Enter query",
        key="query_input",
        label_visibility="collapsed",
        placeholder="Enter a query from any dataset..."
    )
with col_button:
    search_clicked = st.button("Search", use_container_width=True)

# ============================================================
# EXAMPLE QUERIES
# ============================================================
st.markdown("**Example queries:**")

for ds_name, cfg in DATASETS_CONFIG.items():
    if ds_name not in ALL_DATA:
        continue
    examples = cfg["examples"]
    cols = st.columns(len(examples))
    for i, eq in enumerate(examples):
        with cols[i]:
            if st.button(eq, key=f"ex_{ds_name}_{i}", type="secondary"):
                st.session_state.selected_query = eq
                query_input = eq
                search_clicked = True

# ============================================================
# PROCESS SEARCH
# ============================================================
if search_clicked and query_input:
    st.session_state.selected_query = query_input
    matched_query, result, dataset_name = search_all_datasets(query_input)
    st.session_state.last_matched_query = matched_query
    st.session_state.last_result = result
    st.session_state.last_dataset = dataset_name
    st.session_state.search_triggered = True

    metric_scores = None
    if result and matched_query and dataset_name:
        query_id = result.get("query_id")
        qrels = ALL_QRELS.get(dataset_name, {})
        relevant_doc_ids = qrels.get(query_id, set())
        metric_scores = {
            "bm25": mrr_at_k(result.get("bm25", []), relevant_doc_ids, k=10),
            "colbert": mrr_at_k(result.get("colbert", []), relevant_doc_ids, k=10),
            "rrf": mrr_at_k(result.get("rrf", []), relevant_doc_ids, k=10),
        }

    st.session_state.last_metric_scores = metric_scores

matched_query = st.session_state.last_matched_query
result = st.session_state.last_result
dataset_name = st.session_state.last_dataset
metric_scores = st.session_state.last_metric_scores

# ============================================================
# DATASET CARD
# ============================================================
matched_text = ""
if matched_query and matched_query != st.session_state.selected_query:
    matched_text = f'<div class="matched-query">Matched to closest stored query: {matched_query}</div>'

st.markdown(f"""
<div class="dataset-card">
    <div class="dataset-label">MATCHED DATASET</div>
    <div class="dataset-name">{dataset_name or "None"}</div>
    <div class="dataset-query">Selected query: {st.session_state.selected_query or 'None'}</div>
    {matched_text}
</div>
""", unsafe_allow_html=True)

# ============================================================
# RESULTS
# ============================================================
if st.session_state.search_triggered:
    if result is None:
        st.error("No matching stored query was found in any dataset.")
    else:
        if metric_scores:
            st.markdown("### Top-10 Ranking Quality (MRR@10)")
            m1, m2, m3 = st.columns(3)
            m1.metric("BM25 MRR@10", f"{metric_scores['bm25']:.3f}")
            m2.metric("ColBERT MRR@10", f"{metric_scores['colbert']:.3f}")
            m3.metric("RRF MRR@10", f"{metric_scores['rrf']:.3f}")

        col1, col2, col3 = st.columns(3)
        with col1:
            render_results_column("BM25", "Sparse lexical retrieval", result.get("bm25", []), score_label="BM25 Score")
        with col2:
            render_results_column("ColBERT", "Dense semantic retrieval", result.get("colbert", []), score_label="ColBERT Score")
        with col3:
            render_results_column("RRF Hybrid", "Fusion of BM25 + ColBERT", result.get("rrf", []), score_label="RRF Score")