#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/1/5 23:45
# @Author  : 'USER'
# @Site    : 
# @File    : 01_custom_model.py
# @Software: PyCharm

'''
Describe ：

'''


from flexx import app,event

class Custom_Model(app.Model):

    def init(self):         #初始化 成员属性
         # TODO
    @event.connect("foo")   #python方式的事件监听
    def on_foo(self,*events):
        #todo
    class Both:
        @event.property     #开始结束都存在的属性
        def foo(self,v):
            return v
    class JS:
        @event.connect("foo")   #javascript方式的事件监听
        def on_foo(self,*events):
            #todo

