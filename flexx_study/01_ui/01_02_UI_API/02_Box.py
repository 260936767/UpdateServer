#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/1/3 15:21
# @Author  : yc
# @Site    : 
# @File    : 02_Box.py
# @Software: PyCharm

from flexx import ui,app

class Example(ui.Widget):
    def init(self):
        with ui.BoxLayout(orientation='v'):

            ui.Label(text='Flex 0 0 0')
            with ui.HBox(flex=0):
                self.b1 = ui.Button(text='Hola', flex=0)
                self.b2 = ui.Button(text='Hello world', flex=0)
                self.b3 = ui.Button(text='Foo bar', flex=0)

            ui.Label(text='Flex 1 0 3')
            with ui.HBox(flex=0):
                self.b1 = ui.Button(text='Hola', flex=1)
                self.b2 = ui.Button(text='Hello world', flex=0)
                self.b3 = ui.Button(text='Foo bar', flex=3)

            ui.Widget(flex=1)
            ui.Label(text='Note the spacer Widget above')

if __name__ == "__main__":
    app.launch(Example)
    app.run()