# -*- coding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth import get_user_model, _clean_credentials
from hfut import StudentSession, ValidationError, SystemLoginFailed, IPBanned

from . import settings
from .signals import hfut_auth_succeeded, hfut_auth_failed

__all__ = ['HFUTBackend']


# https://docs.djangoproject.com/en/stable/topics/auth/customizing/#authentication-backends
# django.contrib.auth.backends.ModelBackend
class HFUTBackend(object):
    def authenticate(self, password, **kwargs):
        UserModel = get_user_model()
        username = kwargs[UserModel.USERNAME_FIELD]
        if settings.CAMPUS == 'ALL':
            campus = kwargs.get('campus')
            if campus is None:
                raise ValueError('配置中设置了多个校区代码但是却没有在认证时提供 campus 参数')
        else:
            campus = settings.CAMPUS

        try:
            session = StudentSession(username, password, campus)
            session.login()
        except (ValidationError, SystemLoginFailed, IPBanned) as e:
            kwargs.update(password=password)
            hfut_auth_failed.send(self.__class__, reason=e, credentials=_clean_credentials(kwargs))
            return None

        try:
            user = UserModel._default_manager.get_by_natural_key(username)
            user.set_password(password)
            user.save()
        except UserModel.DoesNotExist:
            user = None

        responses = hfut_auth_succeeded.send(self.__class__, user=user, session=session)

        for receiver, response in responses:
            if isinstance(response, UserModel):
                return response
            elif response is not None:
                raise TypeError('%s 返回了一个错误的响应类型: %s' % (receiver, response))
        return user

    def get_user(self, user_id):
        UserModel = get_user_model()
        try:
            return UserModel._default_manager.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None
