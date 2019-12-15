import unittest
from io import StringIO
from unittest.mock import patch

from boto3.resources.base import ServiceResource
from botocore.exceptions import ClientError
from flask import Response
from werkzeug.exceptions import NotFound

from svc.utils.file_reader import LocalFileReader, S3FileReader, get_file_reader


class TestGetFileReader(unittest.TestCase):
    def test_get_local_file_reader_when_config_is_lcl(self):
        config = {
            "UPLOAD_TYPE": "lcl",
        }
        reader = get_file_reader(config)
        self.assertIsInstance(reader, LocalFileReader)

    def test_get_s3_file_reader_when_config_is_s3(self):
        config = {
            "UPLOAD_TYPE": "s3",
        }
        reader = get_file_reader(config)
        self.assertIsInstance(reader, S3FileReader)

    @patch("svc.utils.file_reader.current_app")
    def test_returns_none_when_config_is_invalid(self, mock_app):
        config = {
            "UPLOAD_TYPE": "invalid",
        }
        reader = get_file_reader(config)
        self.assertIsNone(reader)


class TestLocalFileReader(unittest.TestCase):
    def setUp(self):
        self.config = {
            "UPLOAD_PATH": "/upload/path"
        }
        self.reader = LocalFileReader(self.config)
        self.file_name = "filename"

    def test_get_response_raises_not_found_exception_if_file_does_not_exist(self):
        with self.assertRaises(NotFound):
            self.reader.get_response(self.file_name)

    @patch("svc.utils.file_reader.send_from_directory")
    def test_get_response_calls_send_from_directory_with_correct_parameters(self, mock_send):
        self.reader.get_response(self.file_name)
        mock_send.assert_called_once_with("/upload/path", "filename")


class TestS3FileReader(unittest.TestCase):
    def setUp(self):
        self.config = {
            "S3_BUCKET_NAME": "test_bucket"
        }
        self.file_name = "filename"
        self.reader = S3FileReaderSpy(self.config)

    def test_initialized_with_correct_attributes(self):
        reader = S3FileReader(self.config)
        self.assertEqual(reader._config, self.config)
        self.assertEqual(reader._bucket_name, "test_bucket")
        self.assertIsInstance(reader._s3_client, ServiceResource)

    @patch("svc.utils.file_reader.current_app")
    def test_get_response_raises_not_found_exception_if_file_not_found(self, mock_app):
        self.reader.raise_client_error = True
        with self.assertRaises(NotFound):
            self.reader.get_response(self.file_name)

    @patch("svc.utils.file_reader.make_response")
    def test_returns_correct_flask_response_if_file_found(self, make_response_mock):
        make_response_mock.return_value = Response("contents")
        res = self.reader.get_response(self.file_name)
        self.assertEqual(res.response, [b"contents"])
        self.assertEqual(res.headers['Content-Type'], "text/plain")
        self.assertIsInstance(res, Response)
        make_response_mock.assert_called_once_with("contents")


class S3FileReaderSpy(S3FileReader):
    def __init__(self, config):
        super().__init__(config)
        self.raise_client_error = False

    def _get_file(self, file_name):
        if self.raise_client_error:
            raise ClientError({}, "")
        return StringIO("contents"), 'text/plain'
