from flask import Flask, render_template, request
import pickle
import pandas as pd
import requests

app = Flask(__name__)

# ---------------- YOUR TMDB API KEY ----------------
API_KEY = "8265bd1679663a7ea12ac168da84d2e8"   # <- Put real key here


# ---------------- Load PKL Files ----------------
movies = pickle.load(open('movies.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))


# ---------------- Safe TMDB Poster Fetch ----------------
def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{int(movie_id)}?api_key={API_KEY}&language=en-US"
        data = requests.get(url).json()

        poster_path = data.get("poster_path")
        if poster_path:
            return "https://image.tmdb.org/t/p/w500" + poster_path
        else:
            return "https://via.placeholder.com/500x750?text=No+Image"
    except:
        return "https://via.placeholder.com/500x750?text=No+Image"
    

# ---------------- Recommendation Function ----------------
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_titles = []
    recommended_posters = []

    for i in movie_list:
        # ---- Auto-detect TMDB column ----
        if "tmdbId" in movies.columns:
            movie_id = movies.iloc[i[0]].tmdbId
        elif "tmdb_id" in movies.columns:
            movie_id = movies.iloc[i[0]].tmdb_id
        elif "id" in movies.columns:
            movie_id = movies.iloc[i[0]].id
        else:
            # Backup fallback
            movie_id = 0

        recommended_titles.append(movies.iloc[i[0]].title)
        recommended_posters.append(fetch_poster(movie_id))

    return recommended_titles, recommended_posters


# ---------------- Home Route ----------------
@app.route('/', methods=['GET', 'POST'])
def home():
    movie_list = movies['title'].values
    recommended_movies = []
    posters = []
    selected_movie = ""

    if request.method == 'POST':
        selected_movie = request.form['movie_name']
        recommended_movies, posters = recommend(selected_movie)
                                                                                                      
    return render_template(
        "index.html",
        movie_list=movie_list,
        selected_movie=selected_movie,
        recommended_movies=recommended_movies,
        posters=posters
    )


if __name__ == '__main__':
    app.run(debug=True)
