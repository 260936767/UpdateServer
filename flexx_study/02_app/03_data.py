#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/1/6 0:49
# @Author  : 'USER'
# @Site    : 
# @File    : 03_data.py
# @Software: PyCharm

'''
Describe ：

'''

from flexx import app

# Add session-specific data
link = your_model.session.add_data('some_name.png', binary_blob)

# Add shared data
link = app.assets.add_shared_data('some_name.png', binary_blob)

class MyModel(app.Model):

    def some_method(self):
        self.send_data(binary_blob, meta_dict)

    class JS:

        def receive_data(self, array_buffer, meta_dict):
            # This gets called when the data arrives.

            ...  # handle the data