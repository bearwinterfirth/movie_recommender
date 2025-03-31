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

def create_set_of_genres(movies):
    set_of_genres=set()
    for j in movies.index:
        short_list_of_genres=movies["genres"][j].split("|")
        for word in short_list_of_genres:
            set_of_genres.add(word)
    return set_of_genres, len(set_of_genres)

def genres_one_hot_encoding(movies, set_of_genres):
    for k in set_of_genres:
        movies[k]=np.where(movies["genres"].str.contains(k),1,0)
    return movies

# def extract_year(movies):
#     movies["year"]=movies["title"].str[-5:-1]
#     movies=movies[movies["year"].str.isnumeric()]
#     movies["year"]=movies["year"].astype(int)
#     return movies

def make_pivot_table(movies):
    movies_pivot = movies.pivot_table(index="title", columns=["userId"], values="rating")
    movies_pivot.fillna(0, inplace=True)
    return movies_pivot

def sum_genres(movies, movies_pivot):
    for j in range(6,6+number_of_genres):
        new_df=pd.DataFrame(movies.groupby("title")[movies.columns[j]].sum())
        movies_pivot=new_df.merge(movies_pivot, on="title")
    return movies_pivot

def extract_year(matrix):
    matrix["year"]=matrix.index.str[-5:-1]
    matrix=matrix[matrix["year"].str.isnumeric()]
    matrix["year"]=matrix["year"].astype(int)
    return matrix

def scaling(matrix):
    matrix.columns = matrix.columns.astype(str)
    scaler = StandardScaler(with_mean=True, with_std=True)
    matrix_scaled = scaler.fit_transform(matrix)
    sim_score = cosine_similarity(matrix_scaled)
    return sim_score

def five_films(matrix, movie_title, sim_score, movies):
    index=np.where(matrix.index==movie_title)[0][0]
    similar_movies=sorted(list(enumerate(sim_score[index])), key=lambda x: x[1], reverse=True)[1:6]
    
    list_of_films=[]
    for index, j in similar_movies:
        movie=[]
        movie_df = movies[movies["title"]==matrix.index[index]]
        movie.extend(movie_df["title"].values)
        list_of_films.append(movie)
    return list_of_films





just_movies, movies_with_ratings = load_data_files()
fewer_movies = narrowing_the_field(movies_with_ratings)
set_of_genres, number_of_genres = create_set_of_genres(fewer_movies)
movies_with_genres=genres_one_hot_encoding(fewer_movies, set_of_genres)
# fewer_movies=extract_year(fewer_movies)
movies_pivot=make_pivot_table(fewer_movies)
movies_pivot_with_genres=sum_genres(fewer_movies, movies_pivot)
movies_pivot_with_genres_and_year=extract_year(movies_pivot_with_genres)
sim_score=scaling(movies_pivot_with_genres_and_year)
result=five_films(movies_pivot_with_genres_and_year, "Titanic (1997)", sim_score, just_movies)


print(result)