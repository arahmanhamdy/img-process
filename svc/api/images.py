from flask import Blueprint, jsonify, current_app, request
from werkzeug.exceptions import BadRequest

from svc.controllers.images import ImagesController

bp = Blueprint('images', __name__)


@bp.route('', methods=['GET'])
def get_history():
    page = request.args.get("page")
    per_page = request.args.get("count")
    controller = ImagesController(current_app.config, request.base_url)
    result = controller.get_history(page, per_page)
    return jsonify(result)


@bp.route('', methods=['POST'])
def post_image():
    controller = ImagesController(current_app.config, request.base_url)
    image_obj = request.files.get("image")
    try:
        result = controller.post_image(image_obj)
        return jsonify(result)
    except BadRequest as e:
        response = jsonify({
            "error": e.description,
            "details": e.details
        })
        return response, 400


@bp.route('/view/<filename>')
def view_image(filename):
    controller = ImagesController(current_app.config, request.base_url)
    return controller.view_image(filename)


def register_blueprint(app):
    app.register_blueprint(bp, url_prefix='/images')
