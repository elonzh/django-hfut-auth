# -*- coding:utf-8 -*-
from __future__ import unicode_literals


class AppSettings(object):
    def __init__(self, prefix):
        self.prefix = prefix

    def _setting(self, name, dflt):
        # 确保每次调用会自动更新动态修改的配置
        from django.conf import settings
        getter = getattr(settings,
                         'HFUT_AUTH_GETTER',
                         lambda name, dflt: getattr(settings, name, dflt))
        return getter(self.prefix + name, dflt)

    @property
    def CAMPUS(self):
        return self._setting('CAMPUS', 'ALL')


# Ugly? Guido recommends this himself ...
# http://mail.python.org/pipermail/python-ideas/2012-May/014969.html
import sys

settings = AppSettings('HFUT_AUTH_')
settings.__name__ = __name__
sys.modules[__name__] = settings
