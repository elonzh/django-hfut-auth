# -*- coding:utf-8 -*-
from __future__ import unicode_literals
import logging.config

__all__ = ['logger']

DEFAULT_LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'formatters': {
        'hfut_auth': {
            'format': '[%(asctime)s] %(message)s',
        }
    },
    'handlers': {
        'debug_console': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'hfut_auth'
        },
        'default_console': {
            'level': 'WARNING',
            'class': 'logging.StreamHandler',
            'formatter': 'hfut_auth'
        },
    },
    'loggers': {
        'hfut_auth': {
            'handlers': ['debug_console', 'default_console'],
            'level': 'INFO',

        }
    }
}

logging.config.dictConfig(DEFAULT_LOGGING)

logger = logging.getLogger('hfut_auth')
