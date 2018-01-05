#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/1/6 0:48
# @Author  : 'USER'
# @Site    : 
# @File    : 02_assets.py
# @Software: PyCharm

'''
Describe ：

'''
from flexx import app

app.assets.associate_asset(__name__,"xxx.js")
app.assets.associate_asset(__name__,"xxx.css")
app.assets.associate_asset(__name__,"http://some/lib/xx.css") #远程资源
app.assets.add_shared_asset(__name__,"xxx.js")  #注册资源

class Custom_Model(app.Model):
    pass
