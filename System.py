import os
import requests
import random
import streamlit as st
from firebase_admin import credentials, firestore, initialize_app
from dotenv import load_dotenv
import firebase_admin

# Streamlit secrets
API_KEY = st.secrets["IMDB_API"]  # Fetch API key from secrets
FIREBASE_DETAILS = st.secrets["firebase_details"]  # Fetch Firebase details from secrets

# Initialize Firebase app if not already initialized
if not firebase_admin._apps:
    cred = credentials.Certificate(FIREBASE_DETAILS)
    initialize_app(cred)

db = firestore.client()  # Initialize Firestore client

BASE_URL = "https://api.themoviedb.org/3"


# Function to search movies
def search_movie(query, include_adult):
    if not query:
        return []
    url = f"{BASE_URL}/search/movie"
    params = {"api_key": API_KEY, "query": query, "include_adult": include_adult}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json().get("results", [])
    return []


# Function to fetch movie details
def fetch_movie(movie_id):
    url = f"{BASE_URL}/movie/{movie_id}"
    params = {"api_key": API_KEY}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    return None


# Function to get excluded movies from Firestore
def get_excluded_movies(user_id):
    user_ref = db.collection("users").document(user_id)
    doc = user_ref.get()

    if doc.exists:
        user_data = doc.to_dict()
        return user_data.get("Excluded_movies", [])
    return []


# Function to save searched movie to Firestore
def save_search(user_id, movie_id, movie_title, genres, genre_recommendations):
    user_ref = db.collection("users").document(user_id)
    user_data = user_ref.get().to_dict()

    if not user_data:
        user_ref.set({
            "Searched_movies": [],
        })

    user_ref.update({
        "Searched_movies": firestore.ArrayUnion([{
            "id": movie_id,
            "title": movie_title,
            "genres": genres
        }])
    })


# Function to update excluded movies in Firestore
def update_excluded_movies(user_id, movie_id):
    user_ref = db.collection("users").document(user_id)
    user_data = user_ref.get().to_dict()

    if not user_data:
        user_ref.set({
            "Excluded_movies": []
        })

    user_ref.update({
        "Excluded_movies": firestore.ArrayUnion([movie_id])
    })


# Function to get movie recommendations based on genres
def get_movie_recommendations(genre_ids, selected_movie_id, original_language, user_id, include_adult):
    if not genre_ids:
        return []

    excluded_movies = get_excluded_movies(user_id)

    with_genres = ",".join(map(str, genre_ids))
    params = {
        "api_key": API_KEY,
        "with_genres": with_genres,
        "with_original_language": original_language,
        "sort_by": "popularity.desc",
        "include_adult": include_adult
    }

    response = requests.get(f"{BASE_URL}/discover/movie", params=params)

    if response.status_code == 200:
        data = response.json()
        recommendations = [
            movie for movie in data.get("results", [])
            if movie["id"] not in excluded_movies and movie["id"] != selected_movie_id
        ]
        random.shuffle(recommendations)
        recommendations = recommendations[:5]

        return recommendations
    return []


# Function to search movies by starting letter
def search_movies_by_starting_letter(query_start_letter, include_adult):
    movie_results = search_movie(query_start_letter, include_adult)  # Perform the search
    # Filter for movies whose titles start with the same letter
    filtered_results = [
        movie for movie in movie_results
        if movie["title"].lower().startswith(query_start_letter)
    ]
    return filtered_results[:5]  # Return the top 5 matches


# Streamlit UI
st.title("🎬 Movie Recommendation System")

user_id = st.text_input("Enter your User ID:")

movie_input = st.text_input("Search for a movie:", "")
include_adult = st.checkbox("Include Adult Content in Recommendations?", value=False)
if movie_input:
    movie_results = search_movie(movie_input, include_adult)
    if movie_results:
        movie_options = {movie["title"]: movie["id"] for movie in movie_results}
        selected_movie_title = st.selectbox("Select a movie:", list(movie_options.keys()))
        selected_movie_id = movie_options[selected_movie_title]
        movie_data = fetch_movie(selected_movie_id)

        if movie_data:
            save_search(user_id, movie_data["id"], movie_data["title"], [g["name"] for g in movie_data["genres"]], [])

            genre_ids = [g["id"] for g in movie_data["genres"]]
            genre_names = ", ".join([g["name"] for g in movie_data["genres"]])
            st.subheader(movie_data.get("title", "N/A"))
            poster_path = movie_data.get("poster_path")
            if poster_path:
                st.image(f"https://image.tmdb.org/t/p/w500{poster_path}", width=200)
            st.write(f"**Release Date:** {movie_data.get('release_date', 'N/A')}")
            st.write(f"**Genre:** {', '.join([g['name'] for g in movie_data.get('genres', [])])}")
            st.write(f"**Overview:** {movie_data.get('overview', 'N/A')}")
            st.write(f"**Rating:** {movie_data.get('vote_average', 'N/A')}/10")

            original_language = movie_data.get("original_language", "en")
            genre_recommendations = get_movie_recommendations(genre_ids, selected_movie_id, original_language, user_id, include_adult)

            if genre_recommendations:
                st.subheader(f"Top 5 movies in similar genres ({genre_names}):")
                for rec in genre_recommendations:
                    recommended_movie_data = fetch_movie(rec["id"])
                    if recommended_movie_data:
                        st.write(f"**{recommended_movie_data['title']}**")
                        if recommended_movie_data['poster_path']:
                            st.image(f"https://image.tmdb.org/t/p/w500{recommended_movie_data['poster_path']}", width=100)
                        st.write(f"**Release Date:** {recommended_movie_data.get('release_date', 'N/A')}")
                        st.write(f"**Genre:** {', '.join([g['name'] for g in recommended_movie_data.get('genres', [])])}")
                        st.write(f"**Overview:** {recommended_movie_data.get('overview', 'N/A')}")
                        st.write(f"**Rating:** {recommended_movie_data.get('vote_average', 'N/A')}/10")

                        exclude_movie = st.checkbox(f"Remove '{recommended_movie_data['title']}' from future recommendations", key=f"{rec['id']}")
                        if exclude_movie:
                            update_excluded_movies(user_id, rec["id"])

    else:
        # Suggest movies by starting letter
        query_start_letter = movie_input[0].lower()
        movie_results = search_movies_by_starting_letter(query_start_letter, include_adult)

        if not movie_results:
            st.write("No movie suggestions found. Please ensure the movie name is correctly typed.")
        else:
            movie_options = {
                "If the suggestions do not match, please ensure the movie name is correctly typed": None
            }
            movie_options.update({movie["title"]: movie["id"] for movie in movie_results})
            selected_movie_title = st.selectbox("Did you mean:", list(movie_options.keys()))

            if selected_movie_title and selected_movie_title != "If the suggestions do not match, please ensure the movie name is correctly typed":
                selected_movie_id = movie_options[selected_movie_title]
                movie_data = fetch_movie(selected_movie_id)

                if movie_data:
                    save_search(
                        user_id,
                        movie_data["id"],
                        movie_data["title"],
                        [g["name"] for g in movie_data["genres"]],
                        []
                    )

                    genre_ids = [g["id"] for g in movie_data["genres"]]
                    genre_names = ", ".join([g["name"] for g in movie_data["genres"]])
                    st.subheader(movie_data.get("title", "N/A"))
                    poster_path = movie_data.get("poster_path")
                    if poster_path:
                        st.image(f"https://image.tmdb.org/t/p/w500{poster_path}", width=200)
                    st.write(f"**Release Date:** {movie_data.get('release_date', 'N/A')}")
                    st.write(f"**Genre:** {', '.join([g['name'] for g in movie_data.get('genres', [])])}")
                    st.write(f"**Overview:** {movie_data.get('overview', 'N/A')}")
                    st.write(f"**Rating:** {movie_data.get('vote_average', 'N/A')}/10")

                    original_language = movie_data.get("original_language", "en")
                    genre_recommendations = get_movie_recommendations(genre_ids, selected_movie_id, original_language, user_id, include_adult)

                    if genre_recommendations:
                        st.subheader(f"Top 5 movies in similar genres ({genre_names}):")
                        for rec in genre_recommendations:
                            recommended_movie_data = fetch_movie(rec["id"])
                            if recommended_movie_data:
                                st.write(f"**{recommended_movie_data['title']}**")
                                if recommended_movie_data['poster_path']:
                                    st.image(f"https://image.tmdb.org/t/p/w500{recommended_movie_data['poster_path']}", width=100)
                                st.write(f"**Release Date:** {recommended_movie_data.get('release_date', 'N/A')}")
                                st.write(f"**Genre:** {', '.join([g['name'] for g in recommended_movie_data.get('genres', [])])}")
                                st.write(f"**Overview:** {recommended_movie_data.get('overview', 'N/A')}")
                                st.write(f"**Rating:** {recommended_movie_data.get('vote_average', 'N/A')}/10")

                                exclude_movie = st.checkbox(f"Remove '{recommended_movie_data['title']}' from future recommendations", key=f"{rec['id']}")
                                if exclude_movie:
                                    update_excluded_movies(user_id, rec["id"])
