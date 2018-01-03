#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/1/3 14:56
# @Author  : yc
# @Site    : 
# @File    : 01_layout.py
# @Software: PyCharm

from flexx import ui,app,event


class Ex(ui.Widget):
    def init(self):
        self.layout = ui.PlotLayout()
        self.slider1 = ui.Slider(min = 999,max = 100,value = 1009)
        self.slider2 = ui.Slider(min=3, max=10, value=3)
        self.progress = ui.ProgressBar(max = 99,value = 9)
        self.layout.add_tools('Edit plot',
                              ui.Label(text='exponent'), self.slider1,
                              ui.Label(text='numel'), self.slider2,
                              )
        self.layout.add_tools('Plot info', ui.Label(text='Maximum'), self.progress)

    class JS:

        @event.connect('slider1.value', 'slider2.value')
        def __update_plot(self, *events):
            e, n = self.slider1.value, self.slider2.value
            xx = range(n+1)
            self.layout._plot.xdata = xx
            self.layout._plot.ydata = [x**e for x in xx]

        @event.connect('layout._plot.ydata')
        def __update_max(self, *events):
            yy = events[-1].new_value
            if yy:
                self.progress.value = max(yy)

app.launch(Ex)
app.run()