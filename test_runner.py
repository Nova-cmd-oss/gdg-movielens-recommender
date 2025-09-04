from recommender import recommend_by_content, recommend_by_item_cf

TEST_TITLES = ["The Dark Knight", "Toy Story", "Interstellar"]

def run_tests():
    for t in TEST_TITLES:
        print("="*60)
        print("Input:", t)
        matched, recs = recommend_by_content(t, k=5)
        print("Matched:", matched)
        for r in recs:
            print("  ->", r["title"], "|", r["genres"], "| sim:", r["similarity"])
    print("\nNow Item-based CF (if ratings available):")
    for t in TEST_TITLES:
        print("="*60)
        print("Input:", t)
        matched, recs = recommend_by_item_cf(t, k=5)
        print("Matched:", matched)
        for r in recs:
            print("  ->", r["title"], "|", r["genres"], "| sim:", r["similarity"])

if __name__ == "__main__":
    run_tests()
