#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/1/3 15:40
# @Author  : yc
# @Site    : 
# @File    : 09_stack.py
# @Software: PyCharm

from flexx import ui, event,app

class Example(ui.Widget):
    def init(self):
        with ui.HBox():
            with ui.VBox():
                self.buta = ui.Button(text='red')
                self.butb = ui.Button(text='green')
                self.butc = ui.Button(text='blue')
                ui.Widget(flex=1)  # space filler
            with ui.StackedPanel(flex=1) as self.stack:
                self.buta.w = ui.Widget(style='background:#a00;')
                self.butb.w = ui.Widget(style='background:#0a0;')
                self.butc.w = ui.Widget(style='background:#00a;')

    class JS:

        @event.connect('buta.mouse_down', 'butb.mouse_down', 'butc.mouse_down')
        def _stacked_current(self, *events):
            button = events[0].source
            self.stack.current = button.w

app.launch(Example)
app.run()