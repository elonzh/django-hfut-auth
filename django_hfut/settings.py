# -*- coding:utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals


class AppSettings(object):
    def __init__(self, prefix):
        self.prefix = prefix

    def _setting(self, name, dflt):
        # 确保每次调用会自动更新动态修改的配置
        from django.conf import settings
        getter = getattr(settings,
                         'DJANGO_HFUT_GETTER',
                         lambda name, dflt: getattr(settings, name, dflt))
        return getter(self.prefix + name, dflt)

    @property
    def CAMPUS(self):
        return self._setting('CAMPUS', 'ALL')

    @property
    def SYNC_ACCOUNT(self):
        # fixme: 数据库模型并不能同时支持两个校区
        return self._setting('SYNC_ACCOUNT', None)


# Ugly? Guido recommends this himself ...
# http://mail.python.org/pipermail/python-ideas/2012-May/014969.html
import sys

settings = AppSettings('DJANGO_HFUT_')
settings.__name__ = __name__
sys.modules[__name__] = settings
