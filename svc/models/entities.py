from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import types

db = SQLAlchemy()


class Images(db.Model):
    __tablename__ = 'images'
    id = db.Column(types.Integer, primary_key=True, autoincrement=True)
    path = db.Column(types.String(128), nullable=False)
    result = db.Column(types.JSON, nullable=True)
