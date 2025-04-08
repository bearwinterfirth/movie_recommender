import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import PCA
from sklearn.neighbors import KNeighborsClassifier

def load_data_files():
    '''loading 3 datasets:
    movies.csv with columns   movieId, titles,  genres
    ratings.csv with columns  userId,  movieId, ratings, timestamp
    tags.csv with columns     userId,  movieId, tag,     timestamp
    '''
    movies = pd.read_csv("../moviedata/movies.csv")
    ratings = pd.read_csv("../moviedata/ratings.csv")
    tags = pd.read_csv("../moviedata/tags.csv")
    
    # drop duplicate movies
    movies.drop_duplicates("title", inplace=True)

    # connect movie titles with ratings by merging datasets, also saving movies dataset for future cross-references
    merged = movies.merge(ratings, on="movieId")
    merged.dropna(inplace=True)
    return movies, merged, tags


def narrowing_the_field(movies_with_ratings):
    '''the dataset is too big to handle, som narrowing it down in a few ways
    - cutting the whole dataset roughly in half using timestamps (timestamps will not be
    used for anything else after this)
    - don't want ratings from people who rated only a few movies, and also not ratings from 'professional
    raters', but simply 'everyday users', so keeping users with between 80 and 130 ratings
    - only interested in well-known films, so dropping films with less than 200 ratings
    '''
    # cuting the whole dataset roughly in half by dropping odd timestamps. this still keeps almost all movies and users. 
    movies_with_ratings=movies_with_ratings[movies_with_ratings["timestamp"]%2==0]

    # dropping columns: movieId, genres, timestamp before making pivot table
    movies_with_ratings.drop(columns=["movieId", "genres", "timestamp"], inplace=True)
    
    # keeping only users with between 80 and 130 ratings, referred to as 'everyday users'
    x = movies_with_ratings.groupby("userId").count()
    x = x[(x["rating"]>80) & (x["rating"]<130)]
    everyday_users=x.index
    movies_eu = movies_with_ratings[movies_with_ratings["userId"].isin(everyday_users)]

    # keeping only movies with more than 200 ratings, thereby dropping unknown movies
    x = movies_eu.groupby("title").count()
    x = x[(x["rating"]>200)]
    popular_films=x.index
    movies_eu_pf = movies_eu[movies_eu["title"].isin(popular_films)]

    # eu=everyday users, pf=popular films
    return movies_eu_pf


def create_set_of_genres(movies):
    '''genres are separated by '|' in movie dataset.
    creating a set of all unique genres
    '''
    set_of_genres=set()
    for j in movies.index:
        short_list_of_genres=movies["genres"][j].split("|")
        for word in short_list_of_genres:
            set_of_genres.add(word)
    return set_of_genres, len(set_of_genres)


def genres_one_hot_encoding(movies, set_of_genres):
    '''creating a column for each genre, with a '1' if the film has that genre'''
    for k in set_of_genres:
        movies[k]=np.where(movies["genres"].str.contains(k),1,0)
    movies.drop(columns="genres", inplace=True)
    return movies


def make_pivot_table(movies_with_ratings):
    '''making a pivot table out of movies/ratings, with movie title as index. this will be the design matrix.'''
    movies_pivot = movies_with_ratings.pivot_table(index="title", columns=["userId"], values="rating")
    movies_pivot.fillna(0, inplace=True)
    return movies_pivot


def make_shorter_taglist(tags):
    '''there are over 150 000 different tags in the taglist.
    dropping tags that have been used less than 1000 times.
    '''
    x = tags.groupby("tag").count()
    x = x[x["movieId"]>1000]
    common_tags=x.index
    short_taglist = tags[tags["tag"].isin(common_tags)]

    # drop redundant columns
    short_taglist.drop(columns=["userId", "timestamp"], inplace=True)

    # filling a column with ones for easier adding later
    short_taglist["ones"]=1
    return short_taglist


def merge_movies_pivot_with_tags(taglist, movies, movies_pivot):
    '''making pivot table of taglist, with movieId as index,
    summing the number of times each tag is present for each movie,
    for instance: Titanic: "love":783, "horses":0, "Kate Winslet":486 etc
    '''
    tag_pivot = taglist.pivot_table(index="movieId", columns="tag", values="ones", aggfunc="sum")
    tag_pivot.fillna(0, inplace=True)

    # merging taglist with movies, to pair movieId with title
    movies_with_tags=movies.merge(tag_pivot, on="movieId")

    # merging movies/tags with pivot table (aka design matrix)
    movies_pivot_with_tags=movies_pivot.merge(movies_with_tags, on="title")
    return movies_pivot_with_tags


def merge_movies_pivot_with_genres(movies_pivot_with_tags, movies_with_genres):
    '''adding genres (one-hot-encoded) to the movies pivot (aka design matrix)'''
    movies_pivot_with_tags_and_genres=movies_pivot_with_tags.merge(movies_with_genres, on="title")
    return movies_pivot_with_tags_and_genres
    

def extract_year(df):
    '''almost all movie titles end with year within parentheses. we extract them and make them a separate column.
    after this, the design matrix has columns for user ratings, tags, genres and year, and is indexed by movie title'''
    df.set_index("title", inplace=True)
    df["year"]=df.index.str[-5:-1]
    df=df[df["year"].str.isnumeric()]   # dropping a few exceptions, that didn't follow the common scheme
    df["year"]=df["year"].astype(int)   # formatting the year column as numerics
    return df


def scaling(df):
    '''lots of different ranges among columns, so scaling and normalizing.
    also, ratings tend to be on the higher end of the scale, so scaling definitely needed.'''
    df.columns = df.columns.astype(str)

    scaler = StandardScaler(with_mean=True, with_std=True)
    df_scaled = scaler.fit_transform(df)
    
    # it is important that zero means zero, therefore normalizing with minmaxscaler
    scaler = MinMaxScaler()
    df_scaled_normal = scaler.fit_transform(df_scaled)
    return df_scaled_normal


def principal_component_analysis(df):
    '''reducing the number of columns to 1000'''
    pca = PCA(n_components=1000)
    df=pca.fit_transform(df)
    return df


def similarity(df):
    '''every film gets a similarity score compared to other films'''
    sim_score = cosine_similarity(df)
    return sim_score


def five_films(matrix, movie_title, sim_score, movies):
    '''selecting the five films with the highest similarity score'''
    index=np.where(matrix.index==movie_title)[0][0]
    similar_movies=sorted(list(enumerate(sim_score[index])), key=lambda x: x[1], reverse=True)[1:6]
    
    list_of_films=[]
    for index, j in similar_movies:
        movie=[]
        movie_df = movies[movies["title"]==matrix.index[index]]
        movie.extend(movie_df["title"].values)
        list_of_films.append(movie)
    return list_of_films







movies, movies_with_ratings, tags = load_data_files()
movies_with_ratings = narrowing_the_field(movies_with_ratings)

set_of_genres, number_of_genres = create_set_of_genres(movies)
movies_with_genres=genres_one_hot_encoding(movies, set_of_genres)

movies_pivot=make_pivot_table(movies_with_ratings)
short_taglist=make_shorter_taglist(tags)

movies_pivot_with_tags=merge_movies_pivot_with_tags(short_taglist, movies, movies_pivot)
movies_pivot_with_tags_and_genres=merge_movies_pivot_with_genres(movies_pivot_with_tags, movies_with_genres)

movies_pivot_with_tags_genres_and_year=extract_year(movies_pivot_with_tags_and_genres)
scaled_df=scaling(movies_pivot_with_tags_genres_and_year)
reduced_scaled_df=principal_component_analysis(scaled_df)

sim_score=similarity(scaled_df)
result=five_films(movies_pivot_with_tags_genres_and_year, "Titanic (1997)", sim_score, movies)


print(result)