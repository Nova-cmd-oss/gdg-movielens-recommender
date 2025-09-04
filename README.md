# GDG Movie Recommender (MovieLens Small)

A clean, beginner-friendly recommender system with a **Gradio/Streamlit UI**.  
It supports:
- ✅ Data exploration (basic insights)
- ✅ **Content-based** recommendations (genres via TF-IDF or Jaccard fallback)
- ✅ **Item-based collaborative filtering** (simple Pearson correlation)
- ✅ UI with **Gradio** or **Streamlit**
- ✅ Optional rating filter
- ✅ Test runner with 3 sample queries
- ✅ Graceful fallback to a tiny sample dataset if MovieLens CSVs are not present

> Built to meet the GDG On Campus task requirements with clarity and modularity.

---

## 1) Setup

### Option A: Use the tiny fallback data (quick demo)
This repo already includes small fallback CSVs (`data/movies_fallback.csv`, `data/ratings_fallback.csv`) so everything runs out-of-the-box for demo/testing.

### Option B: Use the real MovieLens Small dataset (recommended for submission)
1. Download **MovieLens Latest Small** from GroupLens (ml-latest-small.zip).
2. Extract and copy the following files into `data/`:
   - `movies.csv`
   - `ratings.csv`
3. (Optional) set an env var if your data lives elsewhere:
   ```bash
   export MOVIELENS_DATA_DIR=/path/to/movielens/data
   ```

> Both **Gradio** and **Streamlit** apps auto-detect the real CSVs if present, and otherwise fallback to the sample.

### Install dependencies
Create a venv (optional) and then:
```bash
pip install -r requirements.txt
```

---

## 2) Run the UI

### Gradio
```bash
python gradio_app.py
```
Open the printed local URL in your browser. Type/select a movie, choose a method, and click **Recommend**.

### Streamlit
```bash
streamlit run streamlit_app.py
```

---

## 3) Data Exploration (Must-have)
Basic stats are displayed in the UI. You can also run:
```bash
python explore.py
```
This prints counts and saves `artifacts/top5_popular.png`.

---

## 4) Recommendation Logic (Must-have)

We provide **two** methods; pick one in the UI (content-based is default).

### A) Content-Based (Genres)
- Parses `genres` text into tokens.
- Uses **TF-IDF + cosine similarity** (if scikit-learn is installed).  
  Falls back to **Jaccard similarity** if scikit-learn is not available.
- Returns the top *k* closest movies by genre similarity.
- Optional **min avg rating** filter (computed from `ratings.csv`).

### B) Item-Based Collaborative Filtering (Basic)
- Builds a **user–item rating matrix**.
- Mean-centers per user to reduce bias.
- Computes **Pearson correlation** between movie columns.
- Recommends the top *k* correlated movies.
- Optional **min avg rating** filter.

---

## 5) Testing (Must-have)

We test 3 inputs as requested:
- "The Dark Knight"
- "Toy Story"
- "Interstellar"

Run:
```bash
python test_runner.py
```
This prints the matched title and 5 recommendations for each method.

> For the UI screenshots: run one of the UIs locally with the real MovieLens CSVs, test with the 3 movies above, and capture screenshots of the results.

---

## 6) Advanced (Optional)

### A) Movie Posters with TMDB
Add posters by setting `TMDB_API_KEY` and querying TMDB by title to fetch `poster_path`.  
(Left as a simple extension point to avoid external calls during review.)

### B) Ratings Filter
Already available in both UIs as a **Min Avg Rating** slider.

---

## 7) Project Structure

```
gdg-movielens-recommender/
├── data/
│   ├── movies.csv              # <-- put real dataset here (optional)
│   ├── ratings.csv             # <-- put real dataset here (optional)
│   ├── movies_fallback.csv     # tiny demo dataset (included)
│   └── ratings_fallback.csv    # tiny demo dataset (included)
├── recommender.py              # core logic (content-based + item CF)
├── gradio_app.py               # Gradio UI
├── streamlit_app.py            # Streamlit UI
├── explore.py                  # basic insights + chart
├── test_runner.py              # prints recs for 3 movies
├── requirements.txt
└── README.md
```

---

## 8) Design Choices & Justification

- **Start simple, scale later**: content-based on `genres` is interpretable and fast; CF adds collaborative signal without complexity.
- **Stateless UI**: recomputations are cached internally (lightweight for small datasets).
- **Reproducibility**: deterministic results given the CSVs; no external API dependency by default.
- **Clarity**: modular functions and readable code; easy to extend (e.g., posters, hybrid scoring).

---

## 9) Screenshots (to submit)

1. UI home page with dataset stats (Gradio or Streamlit).
2. Recommendations for **The Dark Knight**.
3. Recommendations for **Toy Story**.
4. Recommendations for **Interstellar**.
5. (Optional) UI with **Min Avg Rating** filter applied.

---

## 10) Troubleshooting

- **No results?** Try content-based method and reduce Min Avg Rating filter.
- **Movie not found?** Start typing and pick from the dropdown. The app attempts fuzzy match for text inputs.
- **Performance issues?** This is small-scale; results should be instant. If you swap in a larger dataset, consider precomputing similarity matrices and saving via `joblib`.

Enjoy building! 🚀
