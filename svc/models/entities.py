from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import types, text

db = SQLAlchemy()


class Images(db.Model):
    __tablename__ = 'images'
    id = db.Column(types.Integer, primary_key=True, autoincrement=True)
    path = db.Column(types.String(128), nullable=False)
    result = db.Column(types.JSON, nullable=True)
    uploaded_at = db.Column(types.DateTime, nullable=False, default=datetime.utcnow)

    @classmethod
    def save_results(cls, path, result):
        obj = cls(path=path, result=result)
        db.session.add(obj)
        db.session.commit()

    @classmethod
    def get_history(cls, page, per_page):
        query = cls.query.order_by(cls.uploaded_at.desc())
        pagination_result = query.paginate(page, per_page, error_out=False)
        return pagination_result.items

    def serialize(self, base_url):
        return {
            "image_name": self.path,
            "image_url": "{}/{}".format(base_url, self.path),
            "results": self.result,
            "uploaded_at": self.uploaded_at.isoformat()
        }
