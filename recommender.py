import os
import pandas as pd
import numpy as np
from typing import Tuple, List
from functools import lru_cache

# Optional: use sklearn if available for TF-IDF; otherwise fall back to simple Jaccard
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except Exception:
    SKLEARN_AVAILABLE = False

DATA_DIR = os.environ.get("MOVIELENS_DATA_DIR", os.path.join(os.path.dirname(__file__), "data"))
MOVIES_CSV = os.path.join(DATA_DIR, "movies.csv")
RATINGS_CSV = os.path.join(DATA_DIR, "ratings.csv")

FALLBACK_MOVIES = os.path.join(DATA_DIR, "movies_fallback.csv")
FALLBACK_RATINGS = os.path.join(DATA_DIR, "ratings_fallback.csv")

def _read_csv_safely(path: str, fallback: str) -> pd.DataFrame:
    if os.path.exists(path):
        return pd.read_csv(path)
    elif os.path.exists(fallback):
        return pd.read_csv(fallback)
    else:
        raise FileNotFoundError(f"Could not find {path} or {fallback}. Place MovieLens CSVs in {DATA_DIR}.")

@lru_cache(maxsize=1)
def load_data() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Load movies and ratings. Uses real CSVs if present, else fallback sample."""
    movies = _read_csv_safely(MOVIES_CSV, FALLBACK_MOVIES)
    ratings = _read_csv_safely(RATINGS_CSV, FALLBACK_RATINGS)
    # Ensure required columns exist
    assert {"movieId","title","genres"}.issubset(movies.columns), "movies.csv must have movieId,title,genres"
    assert {"userId","movieId","rating"}.issubset(ratings.columns), "ratings.csv must have userId,movieId,rating"
    return movies, ratings

def basic_insights() -> dict:
    movies, ratings = load_data()
    total_movies = len(movies)
    total_ratings = len(ratings)
    pop = ratings.groupby("movieId").size().sort_values(ascending=False)
    top_ids = pop.head(5).index.tolist()
    id_to_title = movies.set_index("movieId")["title"].to_dict()
    top5 = [{"movieId": mid, "title": id_to_title.get(mid, str(mid)), "num_ratings": int(pop.loc[mid])} for mid in top_ids]
    return {
        "total_movies": int(total_movies),
        "total_ratings": int(total_ratings),
        "top5_popular": top5
    }

def _prep_genre_corpus(movies: pd.DataFrame) -> List[str]:
    # Genres are pipe-separated like "Action|Adventure|Sci-Fi". Transform to space-separated tokens.
    return movies["genres"].fillna("").str.replace("|", " ", regex=False).tolist()

@lru_cache(maxsize=1)
def build_content_model():
    movies, _ = load_data()
    corpus = _prep_genre_corpus(movies)
    if SKLEARN_AVAILABLE:
        vec = TfidfVectorizer(token_pattern=r"[^ ]+")
        X = vec.fit_transform(corpus)
        return {"method": "tfidf", "X": X, "vec": vec, "movies": movies}
    else:
        # Fallback: precompute sets for Jaccard
        genre_sets = [set(g.split("|")) if isinstance(g, str) else set() for g in movies["genres"]]
        return {"method": "jaccard", "genre_sets": genre_sets, "movies": movies}

def _content_similarities(idx: int, model, top_k: int = 10) -> List[Tuple[int, float]]:
    movies = model["movies"]
    if model["method"] == "tfidf":
        X = model["X"]
        sims = (X[idx] @ X.T).toarray().ravel()
    else:
        g0 = model["genre_sets"][idx]
        sims = np.zeros(len(model["genre_sets"]), dtype=float)
        for j, gj in enumerate(model["genre_sets"]):
            if not g0 and not gj:
                sims[j] = 0.0
            else:
                intersect = len(g0 & gj)
                union = len(g0 | gj) if (g0 or gj) else 1
                sims[j] = intersect / union if union else 0.0
    # Exclude the same movie
    sims[idx] = -1.0
    top_idx = np.argpartition(sims, -top_k)[-top_k:]
    sorted_idx = top_idx[np.argsort(sims[top_idx])[::-1]]
    return [(int(i), float(sims[i])) for i in sorted_idx]

def recommend_by_content(title_query: str, k: int = 5, min_avg_rating: float = None):
    """Recommend k movies similar in genres to the given title.
       Optional filter by average rating (computed from ratings.csv).
    """
    movies, ratings = load_data()
    # Find best matching movie by simple case-insensitive containment / similarity
    title_series = movies["title"].astype(str)
    # exact first
    exact = movies[title_series.str.lower() == title_query.lower()]
    if exact.empty:
        contains = movies[title_series.str.lower().str.contains(title_query.lower(), na=False)]
        cand = contains if not contains.empty else movies
        # choose the shortest edit distance-ish via string length diff and common prefix heuristic
        def score(t):
            t_low = t.lower()
            q_low = title_query.lower()
            common = os.path.commonprefix([t_low, q_low])
            return (int(q_low in t_low) * 1000) + len(common) - abs(len(t_low)-len(q_low))
        best_idx = cand["title"].apply(score).astype(int).idxmax()
    else:
        best_idx = exact.index[0]
    model = build_content_model()
    # Map DataFrame index to positional index
    pos = movies.index.get_loc(best_idx)
    sims = _content_similarities(pos, model, top_k=max(k*3, 10))
    rec_rows = []
    # Precompute avg ratings if filter
    avg = None
    if min_avg_rating is not None:
        avg = ratings.groupby("movieId")["rating"].mean()
    for i, s in sims:
        row = model["movies"].iloc[i]
        mid = int(row["movieId"])
        if min_avg_rating is not None:
            if mid not in avg.index or float(avg.loc[mid]) < float(min_avg_rating):
                continue
        rec_rows.append({"movieId": mid, "title": str(row["title"]), "genres": str(row["genres"]), "similarity": round(float(s), 4)})
        if len(rec_rows) >= k:
            break
    target_title = str(movies.loc[best_idx, "title"])
    return target_title, rec_rows

# --- Optional: very simple item-based collaborative filtering by rating correlations ---
def build_item_cf():
    movies, ratings = load_data()
    # Create user-item matrix with mean-centered ratings per user to reduce bias
    pivot = ratings.pivot_table(index="userId", columns="movieId", values="rating")
    centered = pivot.sub(pivot.mean(axis=1), axis=0)
    item_sim = centered.T.corr(min_periods=2)  # Pearson correlation between items
    return {"movies": movies, "item_sim": item_sim}

def recommend_by_item_cf(title_query: str, k: int = 5, min_avg_rating: float = None):
    movies, ratings = load_data()
    # Find movieId by best match
    title_series = movies["title"].astype(str)
    exact = movies[title_series.str.lower() == title_query.lower()]
    if exact.empty:
        contains = movies[title_series.str.lower().str.contains(title_query.lower(), na=False)]
        cand = contains if not contains.empty else movies
        def score(t):
            t_low = t.lower(); q_low = title_query.lower()
            common = os.path.commonprefix([t_low, q_low])
            return (int(q_low in t_low) * 1000) + len(common) - abs(len(t_low)-len(q_low))
        best_idx = cand["title"].apply(score).astype(int).idxmax()
    else:
        best_idx = exact.index[0]
    target_mid = int(movies.loc[best_idx, "movieId"])
    cf = build_item_cf()
    sim_series = cf["item_sim"].get(target_mid)
    if sim_series is None:
        return str(movies.loc[best_idx, "title"]), []
    sim_series = sim_series.drop(labels=[target_mid]).dropna().sort_values(ascending=False)
    avg = None
    if min_avg_rating is not None:
        avg = ratings.groupby("movieId")["rating"].mean()
    recs = []
    for mid, sim in sim_series.items():
        if min_avg_rating is not None:
            if mid not in avg.index or float(avg.loc[mid]) < float(min_avg_rating):
                continue
        mrow = movies[movies["movieId"] == mid]
        if not mrow.empty:
            recs.append({
                "movieId": int(mid),
                "title": str(mrow.iloc[0]["title"]),
                "genres": str(mrow.iloc[0]["genres"]),
                "similarity": round(float(sim), 4)
            })
        if len(recs) >= k:
            break
    return str(movies.loc[best_idx, "title"]), recs
