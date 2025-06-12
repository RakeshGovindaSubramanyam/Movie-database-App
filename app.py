from flask import Flask, request, jsonify, render_template, redirect, url_for
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models import Base, Movie
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# DB setup
engine = create_engine('sqlite:///db.sqlite3')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

# OMDb API key
OMDB_API_KEY = os.getenv("OMDB_API_KEY")

@app.route("/")
def home():
    return jsonify({"message": "Welcome to the Movie Database API"})

@app.route("/ui")
def ui():
    query = request.args.get('q')
    session = Session()
    if query:
        movies = session.query(Movie).filter(Movie.title.ilike(f"%{query}%")).all()
    else:
        movies = session.query(Movie).all()
    return render_template("index.html", movies=movies, query=query)

@app.route("/ui/add_movie", methods=["POST"])
def ui_add_movie():
    title = request.form.get("title")
    if not title:
        return redirect(url_for("ui"))

    url = f"http://www.omdbapi.com/?t={title}&apikey={OMDB_API_KEY}"
    res = requests.get(url)
    data = res.json()

    if data.get("Response") == "True":
        session = Session()
        movie = Movie(
            title=data.get("Title"),
            year=int(data.get("Year")) if data.get("Year") and data.get("Year").isdigit() else None,
            genre=data.get("Genre"),
            director=data.get("Director"),
            actors=data.get("Actors"),
            plot=data.get("Plot"),
            poster=data.get("Poster"),
            rating=0.0
        )
        session.add(movie)
        session.commit()
    return redirect(url_for("ui"))

@app.route("/ui/rate_movie/<int:id>", methods=["POST"])
def ui_rate_movie(id):
    rating = request.form.get("rating")
    if rating:
        session = Session()
        movie = session.query(Movie).get(id)
        if movie:
            movie.rating = float(rating)
            session.commit()
    return redirect(url_for("ui"))

@app.route("/ui/delete_movie/<int:id>", methods=["POST"])
def ui_delete_movie(id):
    session = Session()
    movie = session.query(Movie).get(id)
    if movie:
        session.delete(movie)
        session.commit()
    return redirect(url_for("ui"))

if __name__ == "__main__":
    app.run(debug=True)
