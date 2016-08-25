# -*- coding:utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.contrib.auth.forms import AuthenticationForm as Form

from . import settings

__all__ = ['AuthenticationForm']


class AuthenticationForm(Form):
    def __init__(self, request=None, *args, **kwargs):
        super(AuthenticationForm, self).__init__(request, *args, **kwargs)
        if settings.CAMPUS == 'ALL':
            self.fields['campus'] = forms.ChoiceField(label='校区', choices=(('XC', '宣城校区'), ('HF', '合肥校区')))
