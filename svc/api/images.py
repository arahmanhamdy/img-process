from flask import Blueprint, jsonify, current_app

from svc.controllers.images import ImagesController

bp = Blueprint('images', __name__)


@bp.route('/', methods=['GET'])
def get_images():
    return jsonify("Hello World")


@bp.route('/', methods=['POST'])
def post_image():
    return jsonify("Hello World")


@bp.route('/view/<filename>')
def view_image(filename):
    controller = ImagesController(current_app.config)
    return controller.view_image(filename)


def register_blueprint(app):
    app.register_blueprint(bp, url_prefix='/images')
