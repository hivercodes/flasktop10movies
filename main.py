from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movie-collection.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
Bootstrap(app)

#create table
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.String(250), nullable=False)
    description = db.Column(db.String(2500), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    ranking = db.Column(db.Integer, nullable=False)
    review = db.Column(db.String(2500), nullable=False)
    img_url = db.Column(db.String(1000), nullable=False)

db.create_all()


class AddMovie(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    submit = SubmitField('Submit')


class EditRating(FlaskForm):
    rating = StringField('Rating', validators=[DataRequired()])
    review = StringField('Review', validators=[DataRequired()])
    submit = SubmitField('Submit')


#list all movies
@app.route("/")
def home():
    all_movies = db.session.query(Movie).all()
    to_sort_movies = []

    for mov in all_movies:
        mov_dict = {"rating": mov.rating, "film": mov}
        to_sort_movies.append(mov_dict)
    sorted_movies = sorted(to_sort_movies, key = lambda i: i['rating'])
    reverse_sorting = sorted_movies[::1]
    ranked_movies = []
    sorted_movies.reverse()
    for film in reverse_sorting:
        index = sorted_movies.index(film) + 1
        film_dict = {"index": index, "film": film["film"]}
        ranked_movies.append(film_dict)

    for d in ranked_movies[::-1]:

        print(d["film"].img_url)
    return render_template("index.html", all_movies=ranked_movies)

#edit database
@app.route("/edit", methods=["POST", "GET"])
def edit():
    form = EditRating()

    if request.method == "POST" and form.validate_on_submit():
        movie_id = request.form["id"]
        movie_to_update = Movie.query.get(movie_id)
        movie_to_update.rating = float(request.form["rating"])
        movie_to_update.review = request.form["review"]
        db.session.commit()
        return redirect(url_for("home"))
    movie_id = request.args.get("id")
    movie_selected = Movie.query.get(movie_id)
    return  render_template(("edit.html"), movie=movie_selected, form=form)

#delete move from database
@app.route("/delete", methods=["POST", "GET"])
def delete():
    movie_id = request.args.get("id")
    movie_to_delete = Movie.query.get(movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for("home"))

#add movie to database
@app.route("/add", methods=["POST", "GET"])
def add():
    form = AddMovie()
    if request.method == "POST" and form.validate_on_submit():
        movie_title = request.form["title"]
        encoded_title = requests.utils.quote(movie_title)
        auth = []
        with open("../api/moviedb") as apifile:
            d = apifile.readlines()
            for dat in d:
                auth.append(str(dat.strip("\n")))

        api = f"https://api.themoviedb.org/3/search/movie?api_key={auth[0]}&language=en-US&&query={encoded_title}&page=1&include_adult=false"
        api_data = requests.get(api).json()
        try:
            title=api_data["results"][0]["original_title"]
            year=api_data["results"][0]["release_date"]
            description=api_data["results"][0]["overview"]
            rating=api_data["results"][0]["vote_average"]
            ranking="Unranked"
            review="Unreviewd"
            img_url=f'https://image.tmdb.org/t/p/w500/{api_data["results"][0]["poster_path"]}'
        except IndexError:
            return redirect(url_for("home"))


        new_movie = Movie(
            title=title,
            year=year,
            description=description,
            rating=rating,
            ranking=ranking,
            review=review,
            img_url=img_url
         )
        db.session.add(new_movie)
        db.session.commit()
        movie = Movie.query.filter_by(title=title).first()
        return redirect(url_for("edit", id=movie.id))
    return render_template("add.html", form=form)


if __name__ == '__main__':
    app.run(debug=True)
