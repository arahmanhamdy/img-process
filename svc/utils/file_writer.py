import boto3
import os
from flask import current_app

UPLOAD_TYPE_KEY = "UPLOAD_TYPE"
S3_BUCKET_KEY = "S3_BUCKET_NAME"
LOCAL_UPLOAD = "lcl"
S3_UPLOAD = "s3"


def get_file_writer(config):
    upload_type = config.get(UPLOAD_TYPE_KEY)
    if upload_type == LOCAL_UPLOAD:
        return LocalFileWriter(config)
    elif upload_type == S3_UPLOAD:
        return S3FileWriter(config)
    current_app.logger.warning("lcl and s3 only supported for UPLOAD_TYPE configuration")


class BaseFileWriter:
    def __init__(self, config):
        self._config = config

    def save(self, file_obj, file_name):
        raise NotImplementedError("`save` method should be implemented in derived classes")


class LocalFileWriter(BaseFileWriter):
    def save(self, file_obj, file_name):
        upload_path = self._config.get("UPLOAD_PATH")
        destination = os.path.join(upload_path, file_name)
        file_obj.save(destination)


class S3FileWriter(BaseFileWriter):
    def __init__(self, config):
        super().__init__(config)
        self._bucket_name = config.get(S3_BUCKET_KEY)
        self._s3_client = boto3.client('s3')

    def save(self, file_obj, file_name):
        self._s3_client.put_object(
            Body=file_obj,
            Bucket=self._bucket_name,
            Key=file_name,
            ContentType=file_obj.content_type
        )
