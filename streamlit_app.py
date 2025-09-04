import os
import pandas as pd
import streamlit as st
from recommender import basic_insights, load_data, recommend_by_content, recommend_by_item_cf

st.set_page_config(page_title="GDG Movie Recommender", page_icon="🍿", layout="centered")

st.title("🍿 GDG Movie Recommender")
st.caption("MovieLens Small — Content-based & Item-based CF (basic)")

ins = basic_insights()
st.subheader("Dataset Insights")
c1, c2 = st.columns(2)
c1.metric("Total Movies", ins["total_movies"])
c2.metric("Total Ratings", ins["total_ratings"])
top5_df = pd.DataFrame(ins["top5_popular"])
st.table(top5_df)

movies_df, _ = load_data()
titles = sorted(movies_df["title"].astype(str).tolist())

st.subheader("Get Recommendations")
method = st.radio("Method", ["Content-based (genres)", "Item-based CF (ratings)"], index=0, horizontal=True)
movie = st.selectbox("Pick a movie", titles, index=titles.index("The Dark Knight (2008)") if "The Dark Knight (2008)" in titles else 0)
k = st.slider("# of recommendations", 5, 20, 5, 1)
min_avg = st.slider("Min avg rating (optional)", 0.0, 5.0, 0.0, 0.5)

if st.button("Recommend"):
    if method.startswith("Content"):
        matched, recs = recommend_by_content(movie, k=k, min_avg_rating=min_avg if min_avg>0 else None)
    else:
        matched, recs = recommend_by_item_cf(movie, k=k, min_avg_rating=min_avg if min_avg>0 else None)
    st.write(f"**Matched:** {matched}")
    if recs:
        st.dataframe(pd.DataFrame(recs))
    else:
        st.info("No recommendations found. Try reducing filters or switching method.")
