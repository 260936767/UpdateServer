#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/1/3 14:26
# @Author  : yc
# @Site    : 
# @File    : 01_01.py
# @Software: PyCharm

from flexx import app,ui

class Example(ui.Widget):
    CSS = '.flx-Example {background:blue; min-width: 20px; min-height:20px}'

    # def init(self):
    #     with ui.HBox():
    #         ui.Button(flex = 3,text = "hello")
    #         ui.Button(flex = 9,text = "world")

    def init(self):
        ui.Label(text = "hello world")

# app.launch(Example)
# app.run()

example = app.launch(Example)
app.export(Example, 'example.html')
