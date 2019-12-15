from flask import Flask

from svc.api import images
from svc.models.entities import db

_blueprints = [
    images
]


class Application(Flask):
    def __init__(self, config, **kwargs):
        super().__init__(__name__, **kwargs)
        self.config.from_mapping(config)


def create_app(config):
    app = Application(config)
    db.init_app(app)
    db.create_all(app=app)
    for bp in _blueprints:
        bp.register_blueprint(app)
    return app
