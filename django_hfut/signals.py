# -*- coding:utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from django.dispatch import Signal

__all__ = ['hfut_auth_succeeded', 'hfut_auth_failed']

# https://docs.djangoproject.com/en/1.9/topics/signals/#defining-signals
hfut_auth_succeeded = Signal(providing_args=['session', 'user'])
hfut_auth_failed = Signal(providing_args=['reason', 'credentials'])
