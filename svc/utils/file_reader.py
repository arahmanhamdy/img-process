import boto3
from botocore.exceptions import ClientError, BotoCoreError
from flask import send_from_directory, make_response, current_app
from werkzeug.exceptions import NotFound

UPLOAD_TYPE_KEY = "UPLOAD_TYPE"
S3_BUCKET_KEY = "S3_BUCKET_NAME"
LOCAL_UPLOAD = "lcl"
S3_UPLOAD = "s3"


def get_file_reader(config):
    upload_type = config.get(UPLOAD_TYPE_KEY)
    if upload_type == LOCAL_UPLOAD:
        return LocalFileReader(config)
    elif upload_type == S3_UPLOAD:
        return S3FileReader(config)
    current_app.logger.warning("lcl and s3 only supported for UPLOAD_TYPE configuration")


class BaseFileReader:
    def __init__(self, config):
        self._config = config

    def get_response(self, file_name):
        raise NotImplementedError("get_response should be implemented in the derived classes")


class LocalFileReader(BaseFileReader):
    def get_response(self, file_name):
        upload_path = self._config.get("UPLOAD_PATH")
        return send_from_directory(upload_path, file_name)


class S3FileReader(BaseFileReader):
    def __init__(self, config):
        super().__init__(config)
        self._bucket_name = config.get(S3_BUCKET_KEY)
        self._s3_client = boto3.resource('s3')

    def get_response(self, file_name):
        try:
            body, content_type = self._get_file(file_name)
        except (BotoCoreError, ClientError) as e:
            current_app.logger.error(e)
            raise NotFound()

        response = make_response(body.read())
        response.headers['Content-Type'] = content_type
        return response

    def _get_file(self, file_name):
        obj = self._s3_client.Object(self._bucket_name, file_name).get()
        return obj['Body'], obj['ContentType']
