import pandas as pd

# Load dataset
movies = pd.read_csv("data/movies.csv")
ratings = pd.read_csv("data/ratings.csv")

# Quick checks
print("Movies data:\n", movies.head())
print("Ratings data:\n", ratings.head())

# Stats
print("\nTotal number of movies:", len(movies))
print("Total number of ratings:", len(ratings))

# Top 5 popular movies
top_movies = ratings.groupby("movieId").size().sort_values(ascending=False).head(5)
top_movies = top_movies.reset_index(name='rating_count')
top_movies = top_movies.merge(movies, on='movieId')
print("\nTop 5 Most Popular Movies:")
print(top_movies[['title', 'rating_count']])


#

import matplotlib.pyplot as plt

plt.figure(figsize=(10,6))
plt.barh(top_movies['title'], top_movies['rating_count'], color='skyblue')
plt.xlabel('Number of Ratings')
plt.ylabel('Movie Title')
plt.title('Top 5 Most Popular Movies')
plt.gca().invert_yaxis()
plt.tight_layout()
plt.show()
