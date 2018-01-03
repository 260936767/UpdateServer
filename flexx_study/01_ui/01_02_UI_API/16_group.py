#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/1/3 15:59
# @Author  : yc
# @Site    : 
# @File    : 16_group.py
# @Software: PyCharm

from flexx import app, ui, event

class Example(ui.GroupWidget):
    def init(self):
        self.title = 'A silly panel'
        with ui.VBox():
            self.progress = ui.ProgressBar(value=0.001)
            self.but = ui.Button(text='click me')

    class JS:
        @event.connect('but.mouse_down')
        def _change_group_title(self, *events):
            self.progress.value += 0.05

app.init_interactive(Example)
app.create_server(host="127.0.0.1",
                  port=8009,
                  new_loop=False,
                  backend='tornado')
app.start()