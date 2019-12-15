from svc.utils.file_reader import get_file_reader


class ImagesController:
    def __init__(self, config):
        self._config = config

    def view_image(self, image_name):
        reader = self._get_reader()
        return reader.get_response(image_name)

    def _get_reader(self):
        return get_file_reader(self._config)
