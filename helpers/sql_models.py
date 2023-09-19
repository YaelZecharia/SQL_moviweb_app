from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.schema import CheckConstraint

db = SQLAlchemy()

user_movie_association = db.Table('user_movie_association',
                                  db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                                  db.Column('movie_id', db.Integer, db.ForeignKey('movie.id'))
                                  )


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    director = db.Column(db.String)
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    poster = db.Column(db.String)

    # One-to-many relationship with review
    reviews = db.relationship('Review', backref='movie')


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)

    # Many-to-many relationship to movies
    favorite_movies = db.relationship('Movie', secondary=user_movie_association)
    # One-to-many relationship with review
    reviews = db.relationship('Review', backref='user')


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=False)
    review_text = db.Column(db.String)
    rating = db.Column(db.Float, nullable=False)

    __table_args__ = (
        CheckConstraint('rating >= 1 AND rating <= 10', name='rating_check'),
    )



