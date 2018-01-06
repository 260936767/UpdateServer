#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/1/6 16:58
# @Author  : 'USER'
# @Site    : 
# @File    : 04_model_class.py
# @Software: PyCharm

'''
Describe ：

'''

class MyModel(Model):

    @event.connect('foo')
    def handle_changes_to_foo_in_python(self, *events):
        ...

    class Both:

        @event.prop
        def foo(self, v=0):
            return float(v)

    class JS:

        BAR = [1, 2, 3]

        def handle_changes_to_foo_in_js(self, *events):
            ...
