import unittest
from io import BytesIO

from PIL import Image

from svc.processors import average_pixel


class TestAveragePixel(unittest.TestCase):
    def test_execute_returns_correct_average_pixel_value(self):
        obj = self._create_image()
        value = average_pixel.execute(obj)
        self.assertEqual(value, 0.6375)

    def _create_image(self):
        obj = BytesIO()
        im = Image.new('RGB', (20, 20))
        im.putdata([(255, 0, 0), (0, 255, 0), (0, 0, 255)])
        im.save(obj, format='png')
        return obj
