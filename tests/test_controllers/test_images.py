import unittest
from unittest.mock import Mock

from svc.controllers.images import ImagesController
from svc.utils.file_reader import BaseFileReader


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


class ImagesControllerSpy(ImagesController):
    def __init__(self, config):
        super().__init__(config)
        self.reader = Mock(BaseFileReader)

    def _get_reader(self):
        return self.reader
