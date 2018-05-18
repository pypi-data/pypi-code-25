import unittest
import logging
import requests
import json
import datetime

from unittest import skip
from tests.common import SdkIntegrationTestCase
from dli.client.exceptions import PackageNotFoundException, InvalidPayloadException
from dli.client.builders import PackageBuilder

logger = logging.getLogger(__name__)


class PackageFunctionsTestCase(SdkIntegrationTestCase):

    def test_get_unknown_package_returns_none(self):
        self.assertIsNone(self.client.get_package("unknown"))

    def test_get_package_returns_non_siren_response(self):
        package_id = self.create_package(
            name="test_get_package_returns_non_siren_response"
        )
        package = self.client.get_package(package_id)
        self.assertEqual(package.id, package_id)

    @skip
    def test_get_s3_access_key_for_package_returns_token(self):
        raise Exception("to be implemented")

    def test_get_package_datasets_raises_exception_if_package_does_not_exists(self):
        with self.assertRaises(Exception):
            self.client.get_package_datasets("unknown")

    def test_get_package_datasets_returns_empty_when_no_datasets(self):
        package_id = self.create_package(
            name="test_get_package_datasets_returns_empty_when_no_datasets"
        )
        datasets = self.client.get_package_datasets(package_id)
        self.assertEqual(datasets, [])

    @skip
    def test_get_package_datasets_allow_specifying_maximum_of_rows_to_be_returned(self):
        raise Exception("to be implemented")

    def test_can_delete_package(self):
        package_id = self.create_package_with_no_bucket(
            "test_can_delete_package"
        )
        dataset = self.client.register_dataset_metadata(
            package_id,
            "test",
            ["/path/to/file/A", "/path/to/file/B"]
        )

        self.client.delete_package(package_id)

        self.assertIsNone(self.client.get_package(package_id))
        self.assertIsNone(self.client.get_dataset(dataset.id))

    def test_delete_unknown_package_raises_exception(self):
        with self.assertRaises(PackageNotFoundException):
            self.client.delete_package("unknown")


class RegisterPackageTestCase(SdkIntegrationTestCase):

    def setUp(self):
        super().setUp()
        self.builder = PackageBuilder(
            name="RegisterPackageTestCase" + str(datetime.datetime.now()),
            description="My package description",
            data_source="External",
            content_creator="datalake-mgmt",
            publisher="datalake-mgmt",
            manager="datalake-mgmt"
        )

    def test_can_create_package_with_other_location(self):
        builder = self.builder.with_external_storage(
            location="jdbc://connectionstring:1232/my-db"
        )
        package = self.client.register_package(builder)

        self.assertIsNotNone(package)
        self.assertEqual(package.description, "My package description")
        self.assertEqual(package.dataStorage, "Other")

    def test_can_create_package_with_external_bucket(self):
        with self.assertRaises(InvalidPayloadException) as cm:
            builder = self.builder.with_external_s3_storage(
                bucket_name="my-happy-external-bucket",
                aws_secret_access_key="secret",
                aws_access_key="key"
            )

            self.client.register_package(builder)

        self.assertTrue("access to bucket my-happy-external-bucket" in str(cm.exception))

    def test_can_create_package_with_data_lake_bucket(self):
        builder = self.builder.with_data_lake_storage("my-happy-bucket")
        package = self.client.register_package(builder)

        self.assertIsNotNone(package)
        self.assertEqual(package.dataStorage, "S3")
        self.assertEqual(package.s3Bucket, "local-ihsm-dl-pkg-my-happy-bucket")
