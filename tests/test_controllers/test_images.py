from datetime import datetime
import unittest
from unittest.mock import Mock, patch

from svc.models.entities import Images

from werkzeug.exceptions import BadRequest

from svc.controllers.images import ImagesController
from svc.utils.file_reader import BaseFileReader
from svc.utils.file_writer import BaseFileWriter


class TestImagesController(unittest.TestCase):
    def setUp(self):
        self.config = {
            "UPLOAD_TYPE": "lcl"
        }
        self.controller = ImagesControllerSpy(self.config, "http://localhost")
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

    def test_post_images_returns_valid_results(self):
        self.controller._config.update({"ALLOWED_IMAGES_EXTENSIONS": ["png"]})
        file_obj = FileObjDouble("image.png", "images/png")
        with patch("svc.controllers.images.entities") as entities_mock:
            self.controller.post_image(file_obj)
            self.controller.writer.save.assert_called_once()
            entities_mock.Images.save_results.assert_called_once()

    def test_get_history_returns_empty_list_if_no_results(self):
        with patch("svc.controllers.images.entities") as entities_mock:
            entities_mock.Images.get_history.return_value = []
            result = self.controller.get_history(10, 20)
            self.assertEqual(result, [])

    def test_get_history_returns_serialized_items_if_results(self):
        results = [Images(path="test.png", result={}, uploaded_at=datetime.utcnow()) for i in range(10)]
        with patch("svc.controllers.images.entities") as entities_mock:
            entities_mock.Images.get_history.return_value = results
            result = self.controller.get_history(1, 20)
            self.assertEqual(len(result), 10)

    def test_process_images_returns_valid_results(self):
        task1 = TaskDouble("task1", raises_exception=False)
        task2 = TaskDouble("task2", raises_exception=True)
        with patch("svc.controllers.images.processors") as processors:
            processors.REGISTERED_TASKS = [task1, task2]
            results = self.controller._process_image(None)
            expected = {
                "task1": {"value": 10},
                "errors": {"task2": "Unknown Error"}
            }
            self.assertDictEqual(results, expected)

    def _assert_raise_bad_request(self, file_obj):
        with self.assertRaises(BadRequest):
            self.controller.post_image(file_obj)


class ImagesControllerSpy(ImagesController):
    def __init__(self, config, base_url):
        super().__init__(config, base_url)
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


class TaskDouble:
    def __init__(self, name, raises_exception):
        self.NAME = name
        self.raises_exception = raises_exception

    def execute(self, image_obj):
        if self.raises_exception:
            raise Exception("Unknown Error")
        return {"value": 10}
