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

"""
id 
title 
year 
description 
rating 
ranking
review
img_url
"""



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

new_movie = Movie(
    title="Phone Booth",
    year=2002,
    description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
    rating=7.3,
    ranking=10,
    review="My favourite character was the caller.",
    img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
)




class Movieform(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    year = StringField('Release Year', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    rating = StringField('Rating', validators=[DataRequired()])
    ranking = StringField('Ranking', validators=[DataRequired()])
    review = StringField('Review', validators=[DataRequired()])
    img_url = StringField('img_url', validators=[DataRequired()])
    submit = SubmitField('Submit')


class EditRating(FlaskForm):
    rating = StringField('Rating', validators=[DataRequired()])
    review = StringField('Review', validators=[DataRequired()])
    submit = SubmitField('Submit')

@app.route("/")
def home():
    all_movies = db.session.query(Movie).all()
    return render_template("index.html", all_movies=all_movies)


@app.route("/edit", methods=["POST", "GET"])
def edit():
    form = EditRating()

    if request.method == "POST" and form.validate_on_submit():
        movie_id = request.form["id"]
        print(movie_id)
        movie_to_update = Movie.query.get(movie_id)
        movie_to_update.rating = float(request.form["rating"])
        print(request.form["rating"])
        movie_to_update.review = request.form["review"]
        print(request.form["review"])
        db.session.commit()
        return redirect(url_for("home"))
    movie_id = request.args.get("id")
    movie_selected = Movie.query.get(movie_id)
    return  render_template(("edit.html"), movie=movie_selected, form=form)

@app.route("/delete", methods=["POST", "GET"])
def delete():
    movie_id = request.args.get("id")
    movie_to_delete = Movie.query.get(movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for("home"))



if __name__ == '__main__':
    app.run(debug=True)
