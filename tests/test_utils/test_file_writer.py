import os
import unittest
from unittest.mock import patch, Mock

from botocore.client import BaseClient

from svc.utils.file_writer import LocalFileWriter, S3FileWriter, get_file_writer


class TestGetFileWriter(unittest.TestCase):
    def test_get_local_file_writer_when_config_is_lcl(self):
        config = {
            "UPLOAD_TYPE": "lcl",
        }
        reader = get_file_writer(config)
        self.assertIsInstance(reader, LocalFileWriter)

    def test_get_s3_file_writer_when_config_is_s3(self):
        config = {
            "UPLOAD_TYPE": "s3",
        }
        reader = get_file_writer(config)
        self.assertIsInstance(reader, S3FileWriter)

    @patch("svc.utils.file_writer.current_app")
    def test_returns_none_when_config_is_invalid(self, mock_app):
        config = {
            "UPLOAD_TYPE": "invalid",
        }
        reader = get_file_writer(config)
        self.assertIsNone(reader)


class TestLocalFileWriter(unittest.TestCase):
    def setUp(self):
        self.config = {
            "UPLOAD_PATH": "/upload/path"
        }
        self.writer = LocalFileWriter(self.config)
        self.file_obj = FileObjDouble()

    def test_save_calls_file_save_method_with_correct_parameters(self):
        self.writer.save(self.file_obj, "test.png")
        self.assertEqual(self.file_obj.path, os.path.join("/upload/path", "test.png"))


class TestS3FileWriter(unittest.TestCase):
    def setUp(self):
        self.config = {
            "S3_BUCKET_NAME": "test_bucket"
        }
        self.file_name = "filename"
        self.writer = S3FileWriter(self.config)

    def test_initialized_with_correct_attributes(self):
        self.assertEqual(self.writer._config, self.config)
        self.assertEqual(self.writer._bucket_name, "test_bucket")
        self.assertIsInstance(self.writer._s3_client, BaseClient)

    @patch("svc.utils.file_writer.boto3")
    def test_save_calls_put_object_with_correct_parameters(self, mock_boto3):
        mock_client = Mock(self.writer._s3_client)
        mock_boto3.client.return_value = mock_client
        writer = S3FileWriter(self.config)
        self.file_obj = FileObjDouble(self.file_name, "images/png")
        writer.save(self.file_obj, self.file_name)
        mock_client.put_object.assert_called_once_with(
            Bucket="test_bucket",
            Body=self.file_obj,
            Key=self.file_name,
            ContentType=self.file_obj.content_type
        )


class FileObjDouble:
    def __init__(self, filename="", content_type=""):
        self.filename = filename
        self.path = ""
        self.content_type = content_type

    def save(self, path):
        self.path = path
