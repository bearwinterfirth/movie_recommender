import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def load_data_files():
    movies = pd.read_csv("ml-latest/movies.csv")
    ratings = pd.read_csv("ml-latest/ratings.csv")
    return movies, ratings

movies, ratings = load_data_files()
movies.head()