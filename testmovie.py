import streamlit as st
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import requests

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="Cini Plaza 🎬", page_icon="🎞️", layout="wide")
OMDB_API_KEY = "53a8cabd"  # Replace with your OMDb API key

# -----------------------------
# STYLE
# -----------------------------
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background: radial-gradient(circle at 20% 20%, #030b24, #000000);
        color: white;
        font-family: 'Poppins', sans-serif;
    }
    .main-title {
    text-align: center;
    font-size: 70px;
    font-weight: 900;
    color: #00eaff;
    text-shadow: 0 0 30px #00eaff, 0 0 60px #0072ff;
    margin-top: 40px;
    margin-bottom: 5px;
    }

    }
    .subtitle {
        text-align: center;
        color: #b0c7ff;
        font-size: 20px;
        margin-bottom: 40px;
    }
    .movie-card {
        background: rgba(255, 255, 255, 0.07);
        border-radius: 18px;
        padding: 12px;
        text-align: center;
        transition: all 0.25s ease-in-out;
        box-shadow: 0 0 10px rgba(0,0,0,0.5);
        cursor: pointer;
        height: 430px;
    }
    .movie-card:hover {
        transform: scale(1.05);
        box-shadow: 0 0 30px rgba(0,255,255,0.4);
    }
    img {
        border-radius: 12px;
        width: 100%;
        height: 330px;
        object-fit: cover;
    }
    .movie-title {
        margin-top: 8px;
        font-size: 16px;
        color: #fff;
        font-weight: bold;
    }
    footer {
        text-align: center;
        color: #8f9ed1;
        margin-top: 30px;
        font-size: 14px;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------
# DATA
# -----------------------------
@st.cache_data
def load_movie_data():
    return pd.DataFrame({
        "title": [
            "Avatar", "Avengers", "Titanic", "The Dark Knight", "Inception",
            "Interstellar", "The Matrix", "Jurassic Park", "Iron Man", "Spider-Man",
            "Doctor Strange", "Black Panther", "The Lion King", "Frozen", "Toy Story",
            "Finding Nemo", "Shutter Island", "Gladiator", "Up", "Coco"
        ],
        "genre": [
            "Action Sci-Fi", "Action Adventure", "Romance Drama", "Action Crime", "Sci-Fi Mystery",
            "Sci-Fi Adventure", "Action Sci-Fi", "Adventure Sci-Fi", "Action Sci-Fi", "Action Fantasy",
            "Fantasy Action", "Action Adventure", "Animation Family", "Animation Musical",
            "Animation Comedy", "Animation Adventure", "Thriller Mystery", "Action History",
            "Animation Family", "Animation Family"
        ]
    })

movies_df = load_movie_data()
features = np.random.rand(len(movies_df), 5)
similarity_matrix = cosine_similarity(features)

# -----------------------------
# API: Poster + Details
# -----------------------------
@st.cache_data(show_spinner=False)
def fetch_movie_details(title):
    try:
        url = f"http://www.omdbapi.com/?t={title}&apikey={OMDB_API_KEY}"
        data = requests.get(url, timeout=4).json()
        if data.get("Response") == "True":
            return {
                "poster": data.get("Poster", "https://via.placeholder.com/300x450/111b3b/FFFFFF?text=No+Poster"),
                "year": data.get("Year", "N/A"),
                "rating": data.get("imdbRating", "N/A"),
                "genre": data.get("Genre", "N/A"),
                "plot": data.get("Plot", "N/A")
            }
    except:
        pass
    return {"poster": "https://via.placeholder.com/300x450/111b3b/FFFFFF?text=No+Poster", "year": "N/A", "rating": "N/A", "genre": "N/A", "plot": "N/A"}

# -----------------------------
# RECOMMENDER
# -----------------------------
def recommend(movie_name):
    idx = movies_df[movies_df['title'].str.lower() == movie_name.lower()].index
    if len(idx) == 0:
        return []
    idx = idx[0]
    sim_scores = list(enumerate(similarity_matrix[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:6]
    return movies_df.iloc[[i[0] for i in sim_scores]]['title'].values

# -----------------------------
# FRONTEND
# -----------------------------
st.markdown("<h1 class='main-title'>Cini Plaza 🎬</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Your AI-powered Movie Recommender — Explore, Discover, Enjoy!</p>", unsafe_allow_html=True)

col1, col2 = st.columns([3, 1])
with col1:
    search = st.text_input("🔍 Search Movie", placeholder="Type a movie name...")
with col2:
    genre_filter = st.selectbox("🎭 Filter by Genre", ["All"] + sorted(movies_df['genre'].unique()))

def display_movies(movie_list):
    cols = st.columns(5)
    for i, title in enumerate(movie_list):
        details = fetch_movie_details(title)
        with cols[i % 5]:
            st.markdown(f"""
                <div class='movie-card'>
                    <img src='{details['poster']}' alt='{title} poster'>
                    <div class='movie-title'>{title}</div>
                </div>
            """, unsafe_allow_html=True)
            # Expander to show details
            with st.expander(f"View Details - {title}"):
                st.markdown(f"**⭐ IMDb:** {details['rating']}")
                st.markdown(f"**🎭 Genre:** {details['genre']}")
                st.markdown(f"**🧾 Plot:** {details['plot']}")
                st.markdown(f"**📅 Year:** {details['year']}")

if "selected_movie" not in st.session_state:
    st.session_state["selected_movie"] = None

if search:
    recs = recommend(search)
    if len(recs) == 0:
        st.warning("No recommendations found. Try another movie name!")
    else:
        st.subheader(f"🎬 Recommendations for **{search.title()}**")
        display_movies(recs)
elif genre_filter != "All":
    st.subheader(f"🎭 {genre_filter} Movies")
    display_movies(movies_df[movies_df['genre'] == genre_filter]['title'].values)
else:
    st.subheader("🔥 Trending Movies")
    display_movies(movies_df['title'].sample(10))

# -----------------------------
# MOVIE DETAILS VIEW
# -----------------------------
if st.session_state["selected_movie"]:
    title = st.session_state["selected_movie"]
    data = fetch_movie_details(title)
    st.markdown("---")
    st.markdown(f"## 🎞️ {title} ({data['year']})")
    colA, colB = st.columns([1, 2])
    with colA:
        st.image(data['poster'], use_container_width=True)
    with colB:
        st.markdown(f"**⭐ IMDb Rating:** {data['rating']}")
        st.markdown(f"**🎭 Genre:** {data['genre']}")
        st.markdown(f"**🧾 Plot:** {data['plot']}")

st.markdown("<footer>Made with ❤️ by Kishore | Powered by Streamlit</footer>", unsafe_allow_html=True)
