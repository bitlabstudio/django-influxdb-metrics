"""Tests for the models of the influxdb_metrics app."""
from django.test import TestCase

from mock import patch

from .. import models


class UserLoggedInHandlerTestCase(TestCase):
    """Tests for the ``user_logged_in_handler`` signal handler."""
    longMessage = False

    def setUp(self):
        self.patch_write_points = patch('influxdb_metrics.models.write_points')
        self.mock_write_points = self.patch_write_points.start()

    def tearDown(self):
        self.patch_write_points.stop()

    def test_handler(self):
        models.user_logged_in_handler(None)

        self.assertEqual(
            self.mock_write_points.call_args[0][0][0]['measurement'],
            'django_auth_user_login',
            msg=('Should send one metric to the login series'))


class UserPostDeleteHandlerTestCase(TestCase):
    """Tests for the ``user_post_delete_handler`` signal handler."""
    longMessage = False

    def setUp(self):
        self.patch_write_points = patch('influxdb_metrics.models.write_points')
        self.mock_write_points = self.patch_write_points.start()

    def tearDown(self):
        self.patch_write_points.stop()

    def test_handler(self):
        models.user_post_save_handler(created=False)
        self.assertFalse(self.mock_write_points.called, msg=(
            'Should not do anything when `created` is `False`'))

        models.user_post_delete_handler(None, created=True)
        self.assertEqual(
            self.mock_write_points.call_args_list[0][0][0][0]['measurement'],
            'django_auth_user_delete',
            msg=('Should send one metric to the delete series'))
        self.assertEqual(
            self.mock_write_points.call_args_list[1][0][0][0]['measurement'],
            'django_auth_user_count',
            msg=('Should send a second metric to the count series'))


class UserPostSaveHandlerTestCase(TestCase):
    """Tests for the ``user_post_save_handler`` signal handler."""
    longMessage = False

    def setUp(self):
        self.patch_write_points = patch('influxdb_metrics.models.write_points')
        self.mock_write_points = self.patch_write_points.start()

    def tearDown(self):
        self.patch_write_points.stop()

    def test_handler(self):
        models.user_post_save_handler(created=False)
        self.assertFalse(self.mock_write_points.called, msg=(
            'Should not do anything when `created` is `False`'))

        models.user_post_save_handler(created=True)

        self.assertEqual(
            self.mock_write_points.call_args_list[0][0][0][0]['measurement'],
            'django_auth_user_create',
            msg=('Should send one metric to the create series'))
        self.assertEqual(
            self.mock_write_points.call_args_list[1][0][0][0]['measurement'],
            'django_auth_user_count',
            msg=('Should send a second metric to the count series'))
