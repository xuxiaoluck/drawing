import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QVBoxLayout, QSizePolicy, QMessageBox, QWidget, QPushButton
from PyQt5.QtGui import QIcon
from PyQt5 import QtCore
from PyQt5.QtCore import QSize

import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import mpl_toolkits.axisartist as axisartist
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from matplotlib.text import Text
import matplotlib.patches as patches
from matplotlib.font_manager import *

from numpy import arange, sin,cos, pi

import numpy as np
import time
import random

from enum import Enum


#设置中文字体
myfont = FontProperties(fname='/usr/share/fonts/truetype/wqy/wqy-microhei.ttc')
#解决负号'-'显示为方块的问题
matplotlib.rcParams['axes.unicode_minus'] = False


class Flags(Enum):
    """一个标志枚举类"""
    MouseLeft = 1
    MouseMiddle = 2
    MouseRight = 3
    SelectedLine = 4
    SelectedRect = 5
    SelectedText = 6


class MainForm(QMainWindow):
    """主窗口界面，设为窗口的主控件，不用再设置大小起点，显示时最大化"""
    def __init__(self):
        super().__init__()
        #self.left = 10
        #self.top = 10
        self.title = 'PyQt MatplotLib 绘图工具'
        #self.width = 640
        #self.height = 400
        #self.resize(QSize(640,480))
        self.initUI()

    def initUI(self):
        """初始化界面，生成绘图窗口"""
        self.setWindowTitle(self.title)
        #self.setGeometry(self.left, self.top, self.width, self.height)

        m = DrawCanvas(self, width=12, height=8)
        self.setCentralWidget(m)
        m.mydraw()
        self.showMaximized()

class DrawCanvas(FigureCanvas):
    """绘制界面"""
    def __init__(self, parent=None, width=8, height=6, dpi=150):

        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = axisartist.Subplot(self.fig, 111)
        self.fig.add_axes(self.axes)
        #使用 ax i s a r t来生成坐标轴及画面
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        self.fig.set_tight_layout(True)
        #调整整体空白

        FigureCanvas.setSizePolicy(self,
                QSizePolicy.Expanding,
                QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

        self.initial_figure(1,0.1,0.5,0.05)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
        #self.fig.canvas.mpl_connect('button_press_event', self.on_button_press)
        self.fig.canvas.mpl_connect('button_release_event', self.on_button_release)
        self.fig.canvas.mpl_connect('pick_event', self.onpick)


        """
        下面为对图像对象的操作用到的变量
        """
        self.selectlineobj = None #当前选中的线型(初期是选中的对象，不限于line)
        self.oldcolor = None  #保存当前对象的OLDCOLOR，以供选择对象换了后恢复COLOR
        self.objselectedxy = (0,0) #对象选中时的mousexy,结合 selectlineobj和mouse松开时的 xydata来决定是否移动对象
        self.ismoveobj = False #是否开始移动OBJ
        """
        上面为对图像对象的操作用到的变量
        """

        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.change_selectobj_color)
        timer.start(500)  #一个时间定时器，用来动态显示选择的对象
        self.counttime = True

    def change_selectobj_color(self):
        """时钟事件，动态改变所选线条颜色"""
        if self.selectlineobj == None:
            return

        self.counttime = not self.counttime
        if isinstance(self.selectlineobj,Rectangle) or \
           isinstance(self.selectlineobj,Line2D) or \
           isinstance(self.selectlineobj,Text):
           self.selectlineobj.set_color('red' if self.counttime else 'blue')

        self.draw()

    def restorecolor(self):
        """恢复原来选中的图像的颜色"""
        if self.selectlineobj != None:  #还原原来的LINE COLOR
            if isinstance(self.selectlineobj,Line2D) or \
               isinstance(self.selectlineobj,Text) or \
               isinstance(self.selectlineobj,Rectangle):
                self.selectlineobj.set_color(self.oldcolor)  #如果选择了新的对象，且不是第一次选择，则恢复以前的COLOR

    def saveselectartistcolor(self):
        """保存选中的图像原来颜色"""
        if isinstance(self.selectlineobj, Line2D) or \
           isinstance(self.selectlineobj, Text):
            self.oldcolor = self.selectlineobj.get_color()
        elif isinstance(self.selectlineobj,Rectangle):
            self.oldcolor = self.selectlineobj.get_ec()

    def onpick(self,event):
        """拾取事件"""
        #判断是哪类对象，再进行处理。
        if self.selectlineobj == None or  (id(self.selectlineobj) != id(event.artist)):
            self.restorecolor()
            self.selectlineobj = event.artist  #保存新选择的对象，以便于进行闪烁显示
            self.saveselectartistcolor()

    def on_mouse_move(self,event):
        """鼠标移动事件,可检测 event.button得到当前是哪个键被按下"""

    def on_button_press(self,event):
        """鼠标点击事件,event.xdata,ydata为在当前坐标轴下的实际坐标，button(1,2,3)分别为鼠标的左中右三键"""
        """点击事件在pick事件之后"""
        #print("press xydata:",event.xdata,event.ydata)

    def on_button_release(self,event):
        """鼠标被放开"""
        #print("release xydata:",event.xdata,event.ydata)

    def initial_figure(self,xmajor,xminjor,ymajor,yminjor):
        """初始化一些设置,传入xy的主次刻度值"""
        #不显示 top、right坐标线 self.axes['top']set_visible(False) 也行
        #通过set_axisline_style方法设置绘图区的底部及左侧坐标轴样式
        #"-|>"代表实心箭头："->"代表空心箭头
        self.axes.axis[:].set_visible(False) #隐藏默认坐标轴，使用 axisartist 重新设置新的坐标轴
        self.axes.axis['x'] = self.axes.new_floating_axis(0,0)
        self.axes.axis['x'].set_axisline_style("-|>", size = 1.0)
        self.axes.axis['y'] = self.axes.new_floating_axis(1,0)
        self.axes.axis['y'].set_axisline_style("-|>", size = 1.0)
        self.axes.axis['y'].set_axis_direction('left')
        self.setaxis(xmajor,xminjor,ymajor,yminjor)

    def setaxis(self,xmajor,xminjor,ymajor,yminjor):
        """设置刻度值"""
        xmajorLocator = MultipleLocator(xmajor) #将x主刻度标签设置为()的倍数
        xmajorFormatter = FormatStrFormatter('%2.1f') #设置x轴标签文本的格式
        ymajorLocator = MultipleLocator(ymajor) #将y轴主刻度标签设置为()的倍数
        ymajorFormatter = FormatStrFormatter('%2.1f') #设置y轴标签文本的格式
        #设置主刻度标签的位置,标签文本的格式
        self.axes.xaxis.set_major_locator(xmajorLocator)
        self.axes.xaxis.set_major_formatter(xmajorFormatter)
        self.axes.yaxis.set_major_locator(ymajorLocator)
        self.axes.yaxis.set_major_formatter(ymajorFormatter)

        xminorLocator = MultipleLocator(xminjor) #将x轴次刻度标签设置为5的倍数
        yminorLocator = MultipleLocator(yminjor) #将此y轴次刻度标签设置为0.1的倍数
        #设置次刻度标签的位置,没有标签文本格式
        self.axes.xaxis.set_minor_locator(xminorLocator)
        self.axes.yaxis.set_minor_locator(yminorLocator)


        #self.axes.grid(which='major',linestyle='--',color='blue',axis='both')
        #self.axes.xaxis.grid(True,which='minor') #x坐标轴的网格使用主刻度
        #self.axes.yaxis.grid(True, which='minor') #y坐标轴的网格使用次刻度


    def mydraw(self):
        t = arange(-3.0, 3.0, 0.005)
        s = sin(2*pi*t)
        cs = cos(2*pi*t)
        self.axes.set_ylim(-3,3)
        sinx = self.axes.plot(t, s,picker=True)
        cosx =self.axes.plot(t,cs,picker=True) #self.line_picker
        self.axes.plot([-1,1],[-1,1],[-1,0],[0,1],color='yellow',picker=2.0)
        self.axes.add_patch(patches.Rectangle((-2.0, -1.0),1.5,2.5,picker=True,fill=False))
        self.axes.text(0.5,2.5,'测试文本test.text',fontproperties=myfont,picker=True)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainForm()
    sys.exit(app.exec_())