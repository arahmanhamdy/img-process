import uuid

from werkzeug.exceptions import BadRequest
from werkzeug.utils import secure_filename

from svc.models import entities
from svc.utils.file_reader import get_file_reader
from svc.utils.file_writer import get_file_writer
from svc import processors


class ImagesController:
    def __init__(self, config, base_url):
        self._config = config
        self._base_url = "{}/view".format(base_url)

    def view_image(self, image_name):
        reader = self._get_reader()
        return reader.get_response(image_name)

    def post_image(self, image_obj):
        self._validate_image(image_obj)
        image_name = self._save_image(image_obj)
        result = self._process_image(image_obj)
        entities.Images.save_results(image_name, result)
        response = {
            "image": image_name,
            "image_url": "{}/{}".format(self._base_url, image_name),
            "result": result,
        }
        return response

    def get_history(self, page, count):
        count = count or 20
        page = page or 1
        results = entities.Images.get_history(int(page), int(count))
        return [result.serialize(self._base_url) for result in results]

    def _validate_image(self, image_obj):
        image_validator = _ImageValidator(image_obj, self._config)
        image_validator.validate()

    def _save_image(self, image_obj):
        file_name = secure_filename(image_obj.filename)
        random_key = str(uuid.uuid4())[:5]
        file_name = "{}_{}".format(random_key, file_name)
        writer = self._get_writer()
        writer.save(image_obj, file_name)
        return file_name

    def _process_image(self, image_obj):
        results = {}
        errors = {}
        for task in processors.REGISTERED_TASKS:
            image_obj.stream.seek(0)
            try:
                value = task.execute(image_obj)
                # the execution may be done through a queue, so the results may not be immediate
                if value:
                    results[task.NAME] = value
            except Exception as e:
                errors[task.NAME] = str(e)
        return {**results, "errors": errors}

    def _get_reader(self):
        return get_file_reader(self._config)

    def _get_writer(self):
        return get_file_writer(self._config)


class _ImageValidator:
    def __init__(self, image_obj, config):
        self._image_obj = image_obj
        self._config = config

    def validate(self):
        self._validate_not_none()
        self._validate_allowed_types()

    def _validate_not_none(self):
        if self._image_obj is None or not self._image_obj.filename:
            exc = BadRequest()
            exc.details = "The request doesn't contain uploaded file"
            raise exc

    def _validate_allowed_types(self):
        allowed_extensions = self._config.get("ALLOWED_IMAGES_EXTENSIONS")
        exc = BadRequest()
        exc.details = "The uploaded image extension is not allowed. Only {} extensions are allowed".format(
            ",".join(allowed_extensions)
        )
        if not self._image_obj.mimetype:
            raise exc
        image_extension = self._image_obj.mimetype.split("/")[1]
        if image_extension.lower() not in allowed_extensions:
            raise exc
