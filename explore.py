import os
import pandas as pd
import matplotlib.pyplot as plt
from recommender import load_data, basic_insights

def main(outdir="artifacts"):
    os.makedirs(outdir, exist_ok=True)
    ins = basic_insights()
    print("Total Movies:", ins["total_movies"])
    print("Total Ratings:", ins["total_ratings"])
    print("Top 5 Popular:")
    for row in ins["top5_popular"]:
        print(f"  - {row['title']} ({row['num_ratings']} ratings)")

    # Save a simple bar chart for top 5 (no custom colors/styles)
    titles = [r["title"] for r in ins["top5_popular"]]
    counts = [r["num_ratings"] for r in ins["top5_popular"]]
    plt.figure()
    plt.bar(titles, counts)
    plt.title("Top 5 Most Popular Movies (#ratings)")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    img_path = os.path.join(outdir, "top5_popular.png")
    plt.savefig(img_path, dpi=150)
    print("Saved chart to:", img_path)

if __name__ == "__main__":
    main()
