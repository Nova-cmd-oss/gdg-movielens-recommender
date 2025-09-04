import os
import pandas as pd
import gradio as gr
from recommender import load_data, basic_insights, recommend_by_content, recommend_by_item_cf

INSIGHTS = basic_insights()
MOVIES_DF, _ = load_data()
MOVIE_TITLES = sorted(MOVIES_DF["title"].astype(str).tolist())

def recommend_ui(movie_title, method, k, min_avg_rating):
    if method == "Content-based (genres)":
        chosen, recs = recommend_by_content(movie_title, k=k, min_avg_rating=min_avg_rating if min_avg_rating and min_avg_rating>0 else None)
    else:
        chosen, recs = recommend_by_item_cf(movie_title, k=k, min_avg_rating=min_avg_rating if min_avg_rating and min_avg_rating>0 else None)
    df = pd.DataFrame(recs)
    return f"Matched: {chosen}", df

with gr.Blocks(title="GDG Movie Recommender") as demo:
    gr.Markdown("# 🍿 GDG Movie Recommender\nSelect a movie and get similar recommendations.")
    with gr.Row():
        with gr.Column(scale=2):
            method = gr.Radio(choices=["Content-based (genres)", "Item-based CF (ratings)"], value="Content-based (genres)", label="Method")
            movie = gr.Dropdown(choices=MOVIE_TITLES, value="The Dark Knight (2008)" if "The Dark Knight (2008)" in MOVIE_TITLES else MOVIE_TITLES[0], label="Pick a movie (type to search)", allow_custom_value=True)
            k = gr.Slider(5, 20, value=5, step=1, label="# of recommendations")
            min_rating = gr.Slider(0.0, 5.0, value=0.0, step=0.5, label="Min avg rating (optional)")
            run = gr.Button("Recommend")
        with gr.Column(scale=3):
            matched = gr.Textbox(label="Matched Movie", interactive=False)
            table = gr.Dataframe(headers=["movieId","title","genres","similarity"], datatype=["number","str","str","number"], wrap=True)
    gr.Markdown("### Dataset Insights")
    gr.Markdown(f"- **Total Movies**: {INSIGHTS['total_movies']}  \n- **Total Ratings**: {INSIGHTS['total_ratings']}")
    gr.Markdown("**Top 5 Most Popular (by #ratings):**")
    top5_df = pd.DataFrame(INSIGHTS["top5_popular"])
    top5 = gr.Dataframe(top5_df, wrap=True, interactive=False)

    run.click(fn=recommend_ui, inputs=[movie, method, k, min_rating], outputs=[matched, table])

if __name__ == "__main__":
    # To run: python gradio_app.py
    demo.launch(server_name="0.0.0.0", server_port=7860, show_api=False)
