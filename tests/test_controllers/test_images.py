import unittest
from unittest.mock import Mock, patch

from werkzeug.exceptions import BadRequest

from svc.controllers.images import ImagesController
from svc.utils.file_reader import BaseFileReader
from svc.utils.file_writer import BaseFileWriter


class TestImagesController(unittest.TestCase):
    def setUp(self):
        self.config = {
            "UPLOAD_TYPE": "lcl"
        }
        self.controller = ImagesControllerSpy(self.config)
        self.image_name = "image.png"

    def test_view_images_calls_reader_get_response(self):
        self.controller.view_image(self.image_name)
        self.controller.reader.get_response.assert_called_once_with(self.image_name)

    def test_post_images_raises_bad_request_error_if_file_is_empty(self):
        self._assert_raise_bad_request(None)

    def test_post_images_raises_bad_request_error_if_file_name_is_empty(self):
        file_obj = FileObjDouble("")
        self._assert_raise_bad_request(file_obj)

    def test_post_images_raises_bad_request_error_if_file_extension_is_not_allowed(self):
        file_obj = FileObjDouble("image.any", "application/octet-stream")
        self.controller._config.update({"ALLOWED_IMAGES_EXTENSIONS": ["png"]})
        self._assert_raise_bad_request(file_obj)

    def test_post_images_raises_bad_request_error_if_file_mimetype_is_none(self):
        file_obj = FileObjDouble("image.any")
        self.controller._config.update({"ALLOWED_IMAGES_EXTENSIONS": ["png"]})
        self._assert_raise_bad_request(file_obj)

    @patch("svc.controllers.images.request")
    def test_post_images_returns_valid_results(self, mock_request):
        self.controller._config.update({"ALLOWED_IMAGES_EXTENSIONS": ["png"]})
        mock_request.url = "http://localhost"
        file_obj = FileObjDouble("image.png", "images/png")
        with patch("svc.controllers.images.entities") as entities_mock:
            self.controller.post_image(file_obj)
            self.controller.writer.save.assert_called_once()
            entities_mock.Images.save_results.assert_called_once()

    def _assert_raise_bad_request(self, file_obj):
        with self.assertRaises(BadRequest):
            self.controller.post_image(file_obj)


class ImagesControllerSpy(ImagesController):
    def __init__(self, config):
        super().__init__(config)
        self.reader = Mock(BaseFileReader)
        self.writer = Mock(BaseFileWriter)

    def _get_reader(self):
        return self.reader

    def _get_writer(self):
        return self.writer


class FileObjDouble:
    def __init__(self, name, mimetype=None):
        self.filename = name
        self.mimetype = mimetype
