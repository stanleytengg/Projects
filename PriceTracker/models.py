from flask_login import UserMixin
from app import db

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    uid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    symbols = db.relationship('Symbol', backref='user', lazy=True)

    def get_id(self):
        return self.uid

class Symbol(db.Model):
    __tablename__ = 'symbols'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.uid'), nullable=False)