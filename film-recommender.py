import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def load_data_files():
    movies = pd.read_csv("../moviedata/movies.csv")
    ratings = pd.read_csv("../moviedata/ratings.csv")
    movies.drop_duplicates("title", inplace=True)
    merged = ratings.merge(movies, on="movieId")
    merged.dropna(inplace=True)
    return movies, merged

def narrowing_the_field(movies):
    movies=movies[movies["timestamp"]%10==0]
    
    x = movies.groupby("userId").count()
    x = x[(x["rating"]>80) & (x["rating"]<200)]
    everyday_users=x.index
    movies_eu = movies[movies["userId"].isin(everyday_users)]

    x = movies_eu.groupby("title").count()
    x = x[(x["rating"]>200)]
    popular_films=x.index
    movies_eu_pf = movies_eu[movies_eu["title"].isin(popular_films)]

    return movies_eu_pf


just_movies, movies_with_ratings = load_data_files()
fewer_movies = narrowing_the_field(movies_with_ratings)

print(fewer_movies)