===============================
django-hfut
===============================

.. image:: https://img.shields.io/github/license/er1iang/django-hfut.svg
    :target: https://github.com/er1iang/django-hfut/blob/master/LICENSE

.. image:: https://img.shields.io/pypi/v/django-hfut.svg
    :target: https://pypi.python.org/pypi/django-hfut

.. image:: https://img.shields.io/travis/er1iang/django-hfut.svg
    :target: https://travis-ci.org/er1iang/django-hfut

.. image:: https://img.shields.io/coveralls/er1iang/django-hfut.svg?maxAge=2592000
    :target: https://coveralls.io/github/er1iang/django-hfut


使用合工大教务接口进行用户身份认证, 支持合肥校区和宣城校区

django-hfut 是一个合肥工业大学学生用户的统一身份认证的工具, 目的是简化使用 Django 开发合工大学生相关网站的用户认证过程.

功能特性
--------------------

- 多版本支持, 同时支持Python2和Python3
- 使用简单, 只需配置好两个配置项就可以工作, 同时自带了登录表单
- 灵活性高, 你可以自定义可用的校区, 认证成功或失败时所进行的操作
- 侵入性小, 你几乎不需要怎么修改你的代码逻辑就能集成基于合工大教务信息的学生身份认证
- 可用性强, 只有在其他认证方式失败同时提供的认证信息格式正确时才会向教务系统发送请求, 避免了错误的用户输入和高频操作导致的IP锁定问题

依赖
____________________

django-hfut 依赖如下::

    django>=1.9
    hfut-stu-lib>=1.4.1

其中由于 `django 1.9 版本支持 Python 2.7, 3.4, 3.5 版本 <https://docs.djangoproject.com/en/stable/faq/install/#what-python-version-can-i-use-with-django>`_ ,
相应的, django-hfut 也支持上述几个版本

安装
--------------------

你只需要在命令行下输入一下代码便能安装好 django-hfut::

    $ pip install django-hfut

如果你没有安装 `pip <https://pip.pypa.io>`_ ，
`Python 安装包指南 <http://docs.python-guide.org/en/latest/starting/installation/>`_
能够指导你安装 PIP .

配置
-----------
settings.py::

    INSTALLED_APPS = (
        ...
        # 必要的 APP
        'django.contrib.auth',
        'django.contrib.contenttypes',
        # 添加 APP
        'django_hfut',
        ...
    )
    AUTHENTICATION_BACKENDS = (
        ...
        # 必要的认证后端
        'django.contrib.auth.backends.ModelBackend',
        # 将 HFUTBackend 放在 ModelBackend 后面, 确保先从本地数据库认证
        'django_hfut.backends.HFUTBackend',
        ...
    )

    # 其他配置, 右侧为默认值
    # 支持认证的校区, 宣城校区为'XC', 合肥校区为'HF', 所有校区为'ALL'
    DJANGO_HFUT_CAMPUS = 'ALL'


使用
--------------------

配置完成后, 按照一般的认证方式认证即可. 注意当 DJANGO_HFUT_CAMPUS = 'ALL' 时, 调用 ``django.contrib.auth.authenticate`` 需要提供 ``campus`` 参数指明是哪个校区.

相应的, 它提供了 ``django_hfut.forms.AuthenticationForm`` , 它集成自 ``django.contrib.auth.forms.AuthenticationForm`` ,
能够自动的根据配置添加 ``campus`` 表单字段, 其他的与父类没有任何区别.

信号
___________________

``django_hfut.signals.hfut_auth_succeeded``:

当通过 ``django_hfut.backends.HFUTBackend`` 认证成功时发送的信号, 提供了 ``user`` , ``session`` 两个参数.

``user`` 是认证得到的用户,注意当数据库里没有对应认证资料的用户时, ``user`` 为 ``None`` ,
你可以接收此信号并提供用户创建逻辑, 返回一个创建完成的用户, 这样就能省去用户的创建视图等等麻烦.

``session`` 是一个 ``hfut_stu_lib.model.StudentSession`` 实例, 你可以使用它调用教务接口获取想要的数据.

``django_hfut.signals.hfut_auth_failed``:

当通过 ``django_hfut.backends.HFUTBackend`` 认证失败时发送的信号, 提供了 ``reason`` , ``credentials`` 两个参数

``reason`` 是一个错误实例, 它告诉你认证失败的原因.

``credentials`` 是调用 ``django.contrib.auth.authenticate`` 时提供的参数, 注意为了安全考虑, 诸如密码,Token等敏感信息都被替换了

授权协议
___________________

* Free software: MIT license
