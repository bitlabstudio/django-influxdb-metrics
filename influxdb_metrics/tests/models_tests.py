"""Tests for the models of the influxdb_metrics app."""
from django.test import TestCase

from mock import patch

from .. import models


class UserLoggedInHandlerTestCase(TestCase):
    """Tests for the ``user_logged_in_handler`` signal handler."""
    longMessage = False

    def setUp(self):
        self.patch_write_point = patch('influxdb_metrics.models.write_point')
        self.mock_write_point = self.patch_write_point.start()

    def tearDown(self):
        self.patch_write_point.stop()

    def test_handler(self):
        models.user_logged_in_handler(None)
        self.assertEqual(
            self.mock_write_point.call_args[0][0],
            'default.django.auth.user.login',
            msg=('Should send one metric to the login series'))


class UserPostDeleteHandlerTestCase(TestCase):
    """Tests for the ``user_post_delete_handler`` signal handler."""
    longMessage = False

    def setUp(self):
        self.patch_write_point = patch('influxdb_metrics.models.write_point')
        self.mock_write_point = self.patch_write_point.start()

    def tearDown(self):
        self.patch_write_point.stop()

    def test_handler(self):
        models.user_post_save_handler(None, created=False)
        self.assertFalse(self.mock_write_point.called, msg=(
            'Should not do anything when `created` is `False`'))

        models.user_post_delete_handler(None, created=True)
        self.assertEqual(
            self.mock_write_point.call_args_list[0][0][0],
            'default.django.auth.user.delete',
            msg=('Should send one metric to the delete series'))
        self.assertEqual(
            self.mock_write_point.call_args_list[1][0][0],
            'default.django.auth.user.count',
            msg=('Should send a second metric to the count series'))


class UserPostSaveHandlerTestCase(TestCase):
    """Tests for the ``user_post_save_handler`` signal handler."""
    longMessage = False

    def setUp(self):
        self.patch_write_point = patch('influxdb_metrics.models.write_point')
        self.mock_write_point = self.patch_write_point.start()

    def tearDown(self):
        self.patch_write_point.stop()

    def test_handler(self):
        models.user_post_save_handler(None, created=False)
        self.assertFalse(self.mock_write_point.called, msg=(
            'Should not do anything when `created` is `False`'))

        models.user_post_save_handler(None, created=True)
        self.assertEqual(
            self.mock_write_point.call_args_list[0][0][0],
            'default.django.auth.user.create',
            msg=('Should send one metric to the create series'))
        self.assertEqual(
            self.mock_write_point.call_args_list[1][0][0],
            'default.django.auth.user.count',
            msg=('Should send a second metric to the count series'))
