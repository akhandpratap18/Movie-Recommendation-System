# Movie Recommendation System

This project implements a **Movie Recommendation System** using Firebase and The Movie Database (TMDb) API. The system allows users to search for movies, view details, get genre-based recommendations, and exclude certain movies from future recommendations. It integrates Firebase Firestore to track the user's movie search history and excluded movies.

---

## Features
- **Movie Search:** Search for movies by name and view detailed information.
- **Genre-Based Recommendations:** Get movie suggestions based on selected genres.
- **Exclusion List:** Exclude certain movies from future recommendations.
- **User History Tracking:** Firebase Firestore integration to track search history and exclusions.

---

## Project Description

This Movie Recommendation System uses TMDb's API to retrieve movie details and generate recommendations. It allows users to search for movies, view details like ratings, release year, and genres, and receive genre-based recommendations. The system also gives users control over their recommendations by letting them exclude specific movies.

Key steps:
1. **Firebase Integration:** Firebase Firestore is used to store user search history and exclusions.
2. **Movie Data Retrieval:** TMDb API is used to fetch movie details and recommendations based on genres.
3. **Exclusion Logic:** Users can exclude movies from their recommendations list, and the system will not suggest those movies in the future.
4. **User Interaction:** Users can search for movies, view details, and interact with the system for tailored recommendations.

---

## Requirements

Install the required dependencies using the following command:
```bash
pip install -r requirements.txt
```

### Key Dependencies
- Firebase
- TMDb API
- Streamlit
- requests
- json

---

## How to Use

### Step 1: Clone the Repository
```bash
git clone https://github.com/akhandpratap18/movie-recommendation-system.git
cd movie-recommendation-system
```

### Step 2: Set Up Firebase
1. Create a Firebase project and get the Firebase credentials.
2. Initialize Firebase in your project by following the Firebase documentation.

### Step 3: Set Up TMDb API
1. Create a TMDb account and generate an API key.
2. Add the TMDb API key to your environment variables or a configuration file.

### Step 4: Run the Application
Run the application using the following command:
```bash
streamlit run System.py
```

The application will allow users to search for movies, view details, and get genre-based recommendations.

### Step 5: Interact with the Recommendation System
1. **Search for Movies:** Enter a movie name to get detailed information.
2. **View Recommendations:** Based on the genre you select, get movie suggestions.
3. **Exclude Movies:** Add movies to your exclusion list to prevent them from showing up in future recommendations.

---

