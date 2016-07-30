# -*- coding:utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.test import TestCase, mock, override_settings

from hfut_auth.forms import AuthenticationForm


# https://docs.djangoproject.com/en/stable/topics/testing/overview/
# https://docs.python.org/3/library/unittest.mock.html
class TestBackends(TestCase):
    def setUp(self):
        self.username = '2012216146'
        self.password = '123456'
        self.sys_password = '9457a4fb'
        user = User(username=self.username)
        user.set_password(self.password)
        user.save()

    # http://stackoverflow.com/questions/3817213/proper-way-to-test-django-signals
    @mock.patch('hfut_auth.signals.hfut_auth_failed.send')
    @mock.patch('hfut_auth.signals.hfut_auth_succeeded.send')
    # https://docs.djangoproject.com/en/stable/topics/testing/tools/#django.test.SimpleTestCase.modify_settings
    @override_settings(HFUT_AUTH_CAMPUS='XC')
    def test_authenticate(self, mocked_succeeded_signal, mocked_failed_signal):
        user = authenticate(username=self.username, password=self.password)
        self.assertIsNotNone(user)
        user.check_password(self.password)
        self.assertFalse(mocked_failed_signal.called)
        self.assertFalse(mocked_succeeded_signal.called)

        user = authenticate(username=self.username, password='wrong_password')
        self.assertIsNone(user)
        self.assertFalse(mocked_succeeded_signal.called)
        self.assertTrue(mocked_failed_signal.called)
        self.assertEqual(mocked_failed_signal.call_count, 1)

        user = authenticate(username=self.username, password=self.sys_password)
        self.assertIsNotNone(user)
        self.assertTrue(user.check_password(self.sys_password))
        self.assertTrue(mocked_succeeded_signal.called)
        self.assertEqual(mocked_succeeded_signal.call_count, 1)
        # 前面已经调用过了
        self.assertEqual(mocked_failed_signal.call_count, 1)


class TestForm(TestCase):
    def test_form(self):
        with override_settings(HFUT_AUTH_CAMPUS='ALL'):
            form = AuthenticationForm()
            self.assertIn('campus', form.fields)
        with override_settings(HFUT_AUTH_CAMPUS='XC'):
            form = AuthenticationForm()
            self.assertNotIn('campus', form.fields)
