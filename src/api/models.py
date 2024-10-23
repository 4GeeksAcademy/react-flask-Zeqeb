from flask_sqlalchemy import SQLAlchemy
from enum import Enum

db = SQLAlchemy()

class Favorite_Type(Enum):
    Planet=1
    People=2

class User(db.Model):
    __tablename__ ="User"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)

    def __repr__(self):
        return f'Name: {self.name}'

    def serialize(self):
        return {
            "name": self.name,
            "id": self.id,
            "email": self.email,
            # do not serialize the password, its a security breach
        }

class Favorites(db.Model):
    __tablename__="Favorites"
    id = db.Column(db.Integer, primary_key=True)
    favorite_type = db.Column(db.Enum(Favorite_Type), nullable=False)
    favorite_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("User.id")) #ForeignKey se vincula con el nombre de la tabla 
    user = db.relationship("User")#Mientras que relationship con el nombre de la CLASE!

    def __repr__(self):
        favorite=str(self.user) + " - " + str(self.favorite_type)+ ": " + str(self.favorite_id)
        return f'Favorite: {favorite}'