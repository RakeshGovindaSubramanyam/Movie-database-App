from flask import Flask, request, jsonify
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models import Base, Movie
import requests, os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
engine = create_engine('sqlite:///db.sqlite3')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

OMDB_API_KEY = os.getenv("OMDB_API_KEY")

# Fetch movie from OMDb API
def fetch_movie(title):
    url = f"https://api.themoviedb.org/3/search/movie"
    params = {"api_key": OMDB_API_KEY, "query": title}
    res = requests.get(url, params=params)
    data = res.json()
    if data['results']:
        movie = data['results'][0]
        return {
            "title": movie['title'],
            "year": int(movie['release_date'][:4]) if movie.get('release_date') else None,
            "genre": "Unknown",  # Genre needs additional request
        }
    return None

@app.route('/movies', methods=['POST'])
def add_movie():
    title = request.json['title']
    data = fetch_movie(title)
    if not data:
        return jsonify({"error": "Movie not found"}), 404

    session = Session()
    movie = Movie(title=data["title"], year=data["year"], genre=data["genre"], rating=0.0)
    session.add(movie)
    session.commit()
    return jsonify({"message": "Movie added", "movie_id": movie.id})

@app.route('/movies/<int:id>/rate', methods=['POST'])
def rate_movie(id):
    rating = request.json['rating']
    session = Session()
    movie = session.query(Movie).get(id)
    if not movie:
        return jsonify({"error": "Movie not found"}), 404
    movie.rating = rating
    session.commit()
    return jsonify({"message": f"Rating updated to {rating}"})

@app.route('/movies', methods=['GET'])
def list_movies():
    session = Session()
    movies = session.query(Movie).all()
    return jsonify([{
        "id": m.id, "title": m.title,
        "year": m.year, "genre": m.genre, "rating": m.rating
    } for m in movies])

if __name__ == '__main__':
    app.run(debug=True)
