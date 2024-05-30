from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'User Data'

    id = db.Column(db.Integer, primary_key = True)
    user_email = db.Column(db.String())
    user_queries = db.Column(db.PickleType)

    def __init__(self, user_email,user_queries):
        self.user_email = user_email
        self.user_queries = user_queries

    def __repr__(self):
        return f"{self.user_email}:{self.user_queries}"