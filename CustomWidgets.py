import sys
import threading
import time
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import pyqtgraph as pg
import serial
import serial.tools.list_ports
import operator
from enum import Enum

from PyQt5.QtCore import pyqtSlot, QPointF, Qt, QRectF
from PyQt5.QtGui import (QPalette, QConicalGradient, QGradient, QRadialGradient,
                         QFontMetricsF, QFont, QPainter, QPen, QPainterPath, QImage,
                         QPaintEvent)

from QSwitchControl import SwitchControl
class QGraphWidget(pg.PlotWidget):
    
    def __init__(self,parent = None,antialisaing=False,title="",title_size = "15pt",
    has_grid = True,y_ablel ="",x_label="",has_legend=True,pen_color='w',pen_width=2):
        super().__init__(parent)
        self.pen_Color = pen_color
        self.GRAPH_PEN_WIDTH = pen_width
        self.setAntialiasing(antialisaing)
        self.setTitle(title,size = title_size)
        self.showGrid(x=has_grid, y=has_grid)
        self.setLabel('left', y_ablel)
        self.setLabel('bottom', x_label)
        if has_legend:
            self.addLegend()
        self.graphpen = pg.mkPen(color = self.pen_Color,width=self.GRAPH_PEN_WIDTH)
    def setPenColor(self,color):
        self.pen_Color = color
        self.graphpen = pg.mkPen(color = color,width=self.GRAPH_PEN_WIDTH)
    
class QLabeledSlider(QWidget):
    
    def __init__(self,parent=None,orientation = Qt.Horizontal,max_range =100,min_range=0,
    label="Slider",layout='Horizontal',tick_step= 1,onchange_callback = None):
        super().__init__( parent)
        self.OnChangedCallback = onchange_callback

        self.sliderText = QLabel(label)
        self.valueText = QLabel(str(min_range))
        self.slider = QSlider(orientation= orientation)

        self.slider.setRange(min_range,max_range)
        self.slider.setTickInterval(tick_step)
        self.orientation = orientation
        if layout == 'Horizontal':
            self.container = QHBoxLayout(self)
        else :
            self.container = QVBoxLayout(self)

        self.container.addWidget(self.sliderText)
        self.container.addWidget(self.slider)
        self.container.addWidget(self.valueText)
        self.slider.valueChanged.connect(self.OnValueChange)
        self.layout = layout

    def OnValueChange(self):
        self.valueText.setText(str(self.slider.value()))
        if self.OnChangedCallback is not None:
            self.OnChangedCallback(self.slider.value())

class QCheckBoxDialog(QDialog):
    def __init__(self,title = "Dialog",description = "",callback = None, options = [],parent = None ) :
        super().__init__(parent)
        self.description = description
        self.setWindowTitle(title)
        self.description = QLabel(self)
        self.description.setText(description)
        self.description.move(self.rect().center())
        self.optionsList = options
        self.combobox = QComboBox(self)
        self.combobox.addItems(self.optionsList)
        self.description.move(self.rect().center())
        self.okButton = QPushButton(self)
        self.okButton.setText("Select")
        self.okButton.move(110,100)
        self.okButton.clicked.connect(callback)
        self.setFixedSize(300,150)
        self.show()
        
class QToggleButton(QWidget):
    def __init__(self,text="", parent=None, bg_color="#777777", circle_color="#DDD", active_color="#aa00ff", animation_curve=QEasingCurve.OutBounce, animation_duration=500, checked: bool = False, change_cursor=True):
        super().__init__(parent)
        self.toggle = SwitchControl(self, bg_color, circle_color, active_color, animation_curve, animation_duration, checked, change_cursor)
        self.toggle.show()
        self.label = QLabel(text=text,parent=self)
        self.label.show()
        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.toggle)
        self.layout.addWidget(self.label)



class CustomSerial():
    def __init__(self,baudrate = 9600, recieved_callback = None):
        self.baudrate= baudrate
        self.portList = []
        self.OnRecievedCallback = recieved_callback
        self.UpdatePortsList()
        self.PortDialog = QCheckBoxDialog(title="Serial Port",description = "Choose the Port",options = self.portList,callback=self.Connect)

    def UpdatePortsList(self): 
        for port in serial.tools.list_ports.comports():
            self.portList.append(str(port.description))
        print("Found devices",self.portList)
    
    def Connect(self):
        try:
            self.port = serial.tools.list_ports.comports()[self.PortDialog.combobox.currentIndex()].name
            self.port = '/dev/' + self.port if sys.platform.startswith('lin')  else self.port
            self.serialConnection = serial.Serial(baudrate=self.baudrate,port=self.port,timeout=0.1,write_timeout=0)
            print("Connecting to ",self.port)    
            if self.serialConnection.is_open and self.serialConnection.writable():
                print("Port Opened")
            self.PortDialog.hide()
            thread = threading.Thread(target=self.OnRecievedCallback)  
            thread.start()  
        except ConnectionError:
            print("errorn in connection")
        except serial.SerialTimeoutException:
            print("time out Excpetion")
        
        
    def WriteData(self,data):
        print("Sending",data)
        self.serialConnection.flushInput()
        try:
            if self.serialConnection.writable() :
                self.serialConnection.flushInput()
                self.serialConnection.write(str(data).encode())
                print("Sent")
                time.sleep(0.1)
            else:
                self.serialConnection.close()
        except serial.SerialTimeoutException :
            print("write timeout")
            
    def ReadData(self):
        if self.serialConnection.readable() and self.serialConnection.inWaiting() > 0:
            return self.serialConnection.readline().decode()
        else:
            return -1
