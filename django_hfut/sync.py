# -*- coding:utf-8 -*-
from __future__ import unicode_literals

from hfut import StudentSession
from .models import Major, Term, Course, TeachingPlan, TeachingClass, Student
from .log import logger


class SyncSession(StudentSession):
    # 避免重复读写数据库
    obj_cache = {Term.__name__: {}, Major.__name__: {}, Course.__name__: {}, Student.__name__: {}}
    # 避免重复更新某一学期课程的教学班级和学生信息
    teaching_class_synced_flags = set()

    @staticmethod
    def update_or_create(model, defaults=None, **field_values):
        obj, created = model.objects.update_or_create(defaults=defaults, **field_values)
        if created:
            logger.info('%s 新建成功', obj)
        else:
            logger.info('%s 更新成功', obj)
        return obj

    def sync_obj(self, model, code, defaults=None):
        obj = self.obj_cache[model.__name__].get(code)
        if not obj:
            obj = self.update_or_create(model, defaults=defaults, code=code)
            self.obj_cache[model.__name__][code] = obj
        return obj

    def iter_term_and_major(self):
        """
        同步 Term, Major 表

        :rtype: generator
        :return: Term, Major
        """
        logger.info('开始同步学期和专业数据'.center(72, '='))
        # @structure {'专业': [{'专业代码': str, '专业名称': str}], '学期': [{'学期代码': str, '学期名称': str}]}
        code = self.get_code()
        logger.warning('模拟了数据用于测试：%s', code)
        terms = code['学期']
        majors = code['专业']

        for term in terms:
            term_obj = self.sync_obj(Term, term['学期代码'], dict(name=term['学期名称']))
            yield term_obj, None

        term_objs = self.obj_cache[Term.__name__]
        max_term_number = int(terms[-1]['学期代码'])
        logger.debug('当前最大学期为 %s', max_term_number)
        for major in majors:
            major_obj = self.sync_obj(Major, major['专业代码'], dict(name=major['专业名称']))
            start_year = int(major_obj.name[:4])
            start = (start_year - 2001) * 2 - 1
            end = start + 7
            if max_term_number < end:
                end = max_term_number
            for i in range(start, end + 1):
                term_code = '%03d' % i
                term_obj = term_objs[term_code]
                yield term_obj, major_obj

        logger.info('学期和专业数据同步成功, 共有学期数据%d条, 专业数据%d条'.center(72, '='), len(terms), len(majors))

    def iter_term_and_course(self, term_obj, major_obj=None):
        """
        同步 Course 表, 数据为指定学期, 指定专业(选修计划不用指定)的课程计划

        :param term_obj: django_hfut.models.Term 对象
        :param major_obj: django_hfut.models.Major 对象, 当不提供时同步选修计划, 提供时同时同步 TeachingPlan
        :rtype: generator
        :return: Term, Course
        """
        if major_obj:
            logger.info('开始同步[%s]学期[%s]专业计划课程', term_obj.code, major_obj.code)
            courses = self.get_teaching_plan(xqdm=term_obj.code, zydm=major_obj.code)
            for course in courses:
                course_obj = self.sync_obj(Course, course['课程代码'], dict(name=course['课程名称'],
                                                                        credit=course['学分'],
                                                                        hours=course['学时'], belong_to=course['开课单位']))
                self.update_or_create(TeachingPlan, term=term_obj, course=course_obj, major=major_obj)
                yield term_obj, course_obj

        else:
            logger.info('开始同步[%s]学期选修计划课程', term_obj.code)
            courses = self.get_teaching_plan(xqdm=term_obj.code, kclx='x')
            for course in courses:
                course_obj = self.sync_obj(Course, course['课程代码'], dict(name=course['课程名称'],
                                                                        credit=course['学分'],
                                                                        hours=course['学时'], belong_to=course['开课单位']))
                yield term_obj, course_obj

    def iter_teaching_class(self, term_obj, course_obj):
        """
        同步 TeachingClass 表, 数据为指定学期, 指定课程的教学班信息, 不包括教学班学生

        :param term_obj: django_hfut.models.Term 对象
        :param course_obj: django_hfut.models.Course 对象
        :rtype: generator
        :return: TeachingClass
        """
        xqdm = term_obj.code
        kcdm = course_obj.code
        key = xqdm + kcdm

        if key not in self.teaching_class_synced_flags:
            self.teaching_class_synced_flags.add(key)
            # @structure [{'任课教师': str, '课程名称': str, '教学班号': str, 'c': str, '班级容量': int}]
            teaching_classes = self.search_course(xqdm=xqdm, kcdm=kcdm)
            for teaching_class in teaching_classes:
                jxbh = teaching_class['教学班号']
                # @structure {'校区': str,'开课单位': str,'考核类型': str,'课程类型': str,'课程名称': str,'教学班号': str,
                # '起止周': str, '时间地点': str,'学分': float,'性别限制': str,'优选范围': str,'禁选范围': str,'选中人数': int,'备 注': str}
                class_info = self.get_class_info(xqdm=xqdm, kcdm=kcdm, jxbh=jxbh)
                teaching_class_obj = self.update_or_create(TeachingClass,
                                                           dict(course_type=class_info['课程类型'],
                                                                exam_type=class_info['考核类型'],
                                                                campus=class_info['校区'],
                                                                weeks=class_info['起止周'],
                                                                time_and_place=class_info['时间地点'],
                                                                size=teaching_class['班级容量'],
                                                                sex_limit=class_info['性别限制'],
                                                                preferred_scope=class_info['优选范围'],
                                                                forbidden_scope=class_info['禁选范围'],
                                                                remark=class_info['备注']),
                                                           term=term_obj, course=course_obj, number=jxbh)
                yield teaching_class_obj

    def sync_students(self, teaching_class_obj):
        """
        同步 Student 表, 数据为指定教学班的学生数据

        :param teaching_class_obj: django_hfut.models.TeachingClass 对象
        :return: None
        """
        # @structure {'学期': str, '班级名称': str, '学生': [{'姓名': str, '学号': int}]}
        students = self.get_class_students(xqdm=teaching_class_obj.term.code,
                                           kcdm=teaching_class_obj.course.code,
                                           jxbh=teaching_class_obj.number)['学生']
        # for student in students:
        #     student_obj = self.sync_obj(Student, student['学号'],
        #                                 dict(name=student['姓名'].rstrip('*'),
        #                                      sex='f' if student['姓名'].endswith('*') else 'm'))
        #     yield student_obj
        teaching_class_obj.students = map(lambda s: self.sync_obj(Student, s['学号'],
                                                                  dict(name=s['姓名'].rstrip('*'),
                                                                       sex='f' if s['姓名'].endswith('*') else 'm')),
                                          students)
        teaching_class_obj.save()

    def sync_all(self):
        for term_obj, major_obj in self.iter_term_and_major():
            for term_obj, course_obj in self.iter_term_and_course(term_obj, major_obj):
                # 最耗时的操作 ↓
                for teaching_class in self.iter_teaching_class(term_obj, course_obj):
                    self.sync_students(teaching_class)
