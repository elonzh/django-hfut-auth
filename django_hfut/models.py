# -*- coding:utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from datetime import datetime

from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models
from django.utils import six

from hfut import StudentSession, HF_PASSWORD_PATTERN


# https://docs.djangoproject.com/en/stable/ref/models/options/
# https://docs.djangoproject.com/en/stable/ref/models/fields/

@six.python_2_unicode_compatible
class Student(models.Model):
    class Meta:
        verbose_name = '学生'
        verbose_name_plural = verbose_name

    # https://docs.djangoproject.com/en/stable/ref/applications/#troubleshooting
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='student', null=True)
    # 保存教务密码
    code = models.CharField(verbose_name='学号', max_length=10, primary_key=True)
    sys_password = models.CharField(verbose_name='教务系统密码', max_length=16, null=True)

    id_card_number = models.CharField(verbose_name='身份证号', max_length=18, unique=True, null=True,
                                      validators=[RegexValidator(r'\d{17}[xX\d]{1}', '身份证号格式不正确')],
                                      editable=False)

    name = models.CharField(verbose_name='姓名', max_length=32)
    photo = models.URLField(verbose_name='照片', null=True)
    sex = models.CharField(verbose_name='性别', max_length=2, choices=[('m', '男'), ('f', '女')], null=True)
    birthday = models.DateTimeField(verbose_name='出生日期', null=True)
    phone = models.CharField(verbose_name='联系电话', max_length=13, null=True, validators=[
        RegexValidator(r'\d{11}|\d{4}-\d{7}', '电话格式为11位数字或 0000-1234567')])
    # 家庭电话可修改, 故不做正则
    home_phone = models.CharField(verbose_name='家庭电话', max_length=13, null=True)

    campus = models.CharField(verbose_name='校区', choices=(('XC', '宣城校区'), ('HF', '合肥校区')), max_length=4)
    college = models.CharField(verbose_name='学院简称', max_length=32, null=True)
    major = models.CharField(verbose_name='专业简称', max_length=32, null=True)
    klass = models.CharField(verbose_name='班级简称', max_length=32, null=True)

    nation = models.CharField(verbose_name='民族', max_length=32, null=True)
    native_place = models.CharField(verbose_name='籍贯', max_length=16, null=True)
    home_address = models.CharField(verbose_name='家庭地址', max_length=256, null=True)
    # 生源信息
    adimission_type = models.CharField(verbose_name='入学方式', max_length=16, null=True)
    adimission_date = models.CharField(verbose_name='入学时间', max_length=16, null=True)
    examinee_code = models.CharField(verbose_name='考生号', max_length=14, null=True)
    high_school = models.CharField(verbose_name='毕业高中', max_length=64, null=True)
    student_origin = models.CharField(verbose_name='生源地', max_length=16, null=True)
    foreign_language = models.CharField(verbose_name='外语语种', max_length=16, null=True)
    # 状态信息
    can_curricula_variable = models.BooleanField(verbose_name='能否选课', default=True)
    politics_status = models.CharField(verbose_name='政治面貌', max_length=16, null=True)
    marital_status = models.CharField(verbose_name='婚姻状况', max_length=16, null=True)
    school_roll_status = models.CharField(verbose_name='学籍状态', max_length=16, null=True)
    registration_status = models.CharField(verbose_name='注册状态', max_length=16, null=True)

    def update(self, sys_password=None):
        sys_password = sys_password or self.sys_password
        session = StudentSession(self.code, sys_password, self.campus)
        session.login()
        stu_info = session.get_my_info()

        self.sys_password = sys_password
        self.id_card_number = stu_info['身份证号']

        self.name = stu_info['姓名']
        self.photo = stu_info['照片']
        self.sex = 'm' if stu_info['性别'] == '男' else 'f'
        self.birthday = datetime.strptime(stu_info['出生日期'], '%Y-%m-%d') if stu_info['出生日期'] else None
        self.phone = stu_info['联系电话']
        self.home_phone = stu_info['家庭电话']

        self.campus = session.campus
        self.college = stu_info['学院简称']
        self.major = stu_info['专业简称']
        self.klass = stu_info['班级简称']

        self.nation = stu_info['民族']
        self.native_place = stu_info['籍贯']
        self.home_address = stu_info['家庭地址']
        # 生源信息
        self.adimission_type = stu_info['入学方式']
        self.adimission_date = stu_info['入学时间']
        self.examinee_code = stu_info['考生号']
        self.high_school = stu_info['毕业高中']
        self.student_origin = stu_info['生源地']
        self.foreign_language = stu_info['外语语种']
        # 状态信息
        self.can_curricula_variable = True if stu_info['能否选课'] == '能' else False
        self.politics_status = stu_info['政治面貌']
        self.marital_status = stu_info['婚姻状况']
        self.school_roll_status = stu_info['学籍状态']
        self.registration_status = stu_info['注册状态']

        self.save()

    def __str__(self):
        return '<Student [{:s} {:s}]>'.format(six.text_type(self.code), self.name)


@six.python_2_unicode_compatible
class Major(models.Model):
    class Meta:
        verbose_name = '专业'
        verbose_name_plural = verbose_name

    code = models.CharField(verbose_name='专业代码', max_length=10, primary_key=True)
    name = models.CharField(verbose_name='专业名称', max_length=64)

    def __str__(self):
        return '<Major [{:s}]{:s}>'.format(self.code, self.name)


@six.python_2_unicode_compatible
class Term(models.Model):
    class Meta:
        verbose_name = '学期'
        verbose_name_plural = verbose_name

    code = models.CharField(verbose_name='学期代码', max_length=3, primary_key=True)
    name = models.CharField(verbose_name='学期名称', max_length=64)

    def __str__(self):
        return '<Term [{:s}]{:s}>'.format(self.code, self.name)


@six.python_2_unicode_compatible
class Course(models.Model):
    class Meta:
        verbose_name = '学生用户的资料'
        verbose_name_plural = '学生用户的资料表'

    code = models.CharField(verbose_name='课程代码', max_length=32, primary_key=True)
    name = models.CharField(verbose_name='课程名称', max_length=64)
    credit = models.FloatField(verbose_name='学分')
    hours = models.IntegerField(verbose_name='学时')
    belong_to = models.CharField(verbose_name='开课单位', max_length=64)

    def __str__(self):
        return '<Course [{:s}]{:s}>'.format(self.code, self.name)


@six.python_2_unicode_compatible
class TeachingPlan(models.Model):
    class Meta:
        verbose_name = '教学计划'
        verbose_name_plural = verbose_name
        default_related_name = 'teaching_plan'
        unique_together = (('term', 'course', 'major'),)

    term = models.ForeignKey(Term)
    course = models.ForeignKey(Course)
    major = models.ForeignKey(Major)

    def __str__(self):
        return '<TeachingPlan {!s}-{!s}-{!s}>'.format(self.term, self.major, self.course)


@six.python_2_unicode_compatible
class TeachingClass(models.Model):
    class Meta:
        verbose_name = '教学班级'
        verbose_name_plural = verbose_name
        default_related_name = 'teaching_classes'
        unique_together = (('term', 'course', 'number'),)

    term = models.ForeignKey(Term)
    course = models.ForeignKey(Course)
    students = models.ManyToManyField(Student)

    # fixme: 放在哪比较合适？
    course_type = models.CharField(verbose_name='课程类型', max_length=32)
    exam_type = models.CharField(verbose_name='考核类型', max_length=32)

    number = models.CharField(verbose_name='教学班号', max_length=4)
    campus = models.CharField(verbose_name='校区', max_length=32)
    # weeks = ArrayField(base_field=models.PositiveSmallIntegerField())
    weeks = models.CharField(verbose_name='起止周', max_length=32, null=True)
    time_and_place = models.CharField(verbose_name='时间地点', max_length=128, null=True)
    size = models.IntegerField(verbose_name='班级容量', null=True)

    sex_limit = models.CharField(verbose_name='性别限制', max_length=32, null=True)
    preferred_scope = models.CharField(verbose_name='优选范围', max_length=128, null=True)
    forbidden_scope = models.CharField(verbose_name='禁选范围', max_length=128, null=True)
    remark = models.TextField(verbose_name='备注', max_length=256, null=True)

    def __str__(self):
        return '<TeachingClass {!s}-{!s}{:s}班>'.format(self.term, self.course, self.number)


@six.python_2_unicode_compatible
class Grade(models.Model):
    class Meta:
        verbose_name = '学生'
        verbose_name_plural = verbose_name
        unique_together = (('teaching_class', 'student'),)

    teaching_class = models.ForeignKey(TeachingClass)
    student = models.ForeignKey(Student, related_name='grades')
    grade = models.CharField(verbose_name='成绩', max_length=8)
    makeup_grade = models.CharField(verbose_name='补考成绩', max_length=8, null=True)

    def __str__(self):
        return '<Grade {!s}-{!s}-{:s}-{:s}>'.format(self.student, self.teaching_class, self.grade, self.makeup_grade)
