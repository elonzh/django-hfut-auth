# -*- coding:utf-8 -*-
from __future__ import unicode_literals
from logging import Logger, WARNING, StreamHandler, Formatter

__all__ = ['logger', 'unstable', 'log_result_not_found']

logger = Logger('django_hfut', level=WARNING)

sh = StreamHandler()
# https://docs.python.org/3/library/logging.html#logrecord-attributes
fmt = Formatter('[%(levelname)s:%(thread)d]: %(message)s')
sh.setFormatter(fmt)
logger.addHandler(sh)
