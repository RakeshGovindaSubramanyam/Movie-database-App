from flask import Flask, request, jsonify
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models import Base, Movie
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Flask App and DB Setup
app = Flask(__name__)
engine = create_engine('sqlite:///db.sqlite3')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

# OMDb API key
OMDB_API_KEY = os.getenv("OMDB_API_KEY")


@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Welcome to the Movie Database API"})


@app.route('/movies', methods=['POST'])
def add_movie():
    data = request.get_json()
    title = data.get("title")

    if not title:
        return jsonify({"error": "Title is required"}), 400

    # Call OMDb API to fetch details
    url = f"http://www.omdbapi.com/?t={title}&apikey={OMDB_API_KEY}"
    res = requests.get(url)
    movie_data = res.json()

    if movie_data.get('Response') != 'True':
        return jsonify({"error": "Movie not found in OMDb"}), 404

    session = Session()
    movie = Movie(
        title=movie_data.get('Title'),
        year=int(movie_data.get('Year')) if movie_data.get('Year') and movie_data.get('Year').isdigit() else None,
        genre=movie_data.get('Genre'),
        rating=0.0  # default rating
    )
    session.add(movie)
    session.commit()
    return jsonify({"message": "Movie added", "movie_id": movie.id})


@app.route('/movies/<int:id>/rate', methods=['POST'])
def rate_movie(id):
    data = request.get_json()
    rating = data.get('rating')

    if rating is None:
        return jsonify({"error": "Rating is required"}), 400

    session = Session()
    movie = session.query(Movie).get(id)
    if not movie:
        return jsonify({"error": "Movie not found"}), 404

    movie.rating = float(rating)
    session.commit()
    return jsonify({"message": f"Rating updated to {rating}"})


@app.route('/movies', methods=['GET'])
def list_movies():
    session = Session()
    movies = session.query(Movie).all()
    return jsonify([
        {
            "id": m.id,
            "title": m.title,
            "year": m.year,
            "genre": m.genre,
            "rating": m.rating
        } for m in movies
    ])


@app.route('/movies/search', methods=['GET'])
def search_movie():
    title = request.args.get('title')
    if not title:
        return jsonify({"error": "Please provide a title"}), 400

    session = Session()
    movie = session.query(Movie).filter(Movie.title.ilike(f"%{title}%")).first()

    if movie:
        return jsonify({
            "source": "database",
            "title": movie.title,
            "year": movie.year,
            "genre": movie.genre,
            "rating": movie.rating
        })

    # If not found in DB, check OMDb
    url = f"http://www.omdbapi.com/?t={title}&apikey={OMDB_API_KEY}"
    res = requests.get(url)
    movie_data = res.json()

    if movie_data.get('Response') == 'True':
        return jsonify({
            "source": "omdb",
            "title": movie_data.get('Title'),
            "year": movie_data.get('Year'),
            "genre": movie_data.get('Genre'),
            "plot": movie_data.get('Plot'),
            "imdb_rating": movie_data.get('imdbRating')
        })
    else:
        return jsonify({"error": "Movie not found"}), 404


if __name__ == '__main__':
    app.run(debug=True)
