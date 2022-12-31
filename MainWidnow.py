from random import randint
import sys
import time

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from qt_material import apply_stylesheet
from CustomWidgets import CustomSerial, QGraphWidget, QToggleButton, QLabeledSlider

from qroundprogressbar import QRoundProgressBar

THEME = 'Dark'


def SendUartValue(value):
    messgae = '@'
    messgae += 'A' if modeCheckbox.toggle.isChecked() else 'M'
    messgae += str(mintempSlider.slider.value())
    messgae += str(maxtempSlider.slider.value())
    messgae += 'Y' if fanCheckbox.toggle.isChecked() else 'N'
    messgae += 'Y' if lampCheckbox.toggle.isChecked() else 'N'
    messgae += str(fanSlider.slider.value())
    print(messgae)
    serialClass.WriteData(messgae)


def UpdateReading(message):
    try:
        value = int( message.split('_')[-1] )
        print("---------------")
        print(value);
        gauge.setValue(value)
        gauge.setFormat("Current temp \n %v C \n {}".format(message.split('_')[0]))
    except:
        print("message received error")



    gauge.setFormat("Current temp \n %v C \n {}".format(message.split('_')[0]))


def ReadDataThread():
    try:
        readingline = graphGrid.plot([], [], pen=graphGrid.graphpen, name='Lm readings')
        x = [0]
        y = [0]
        while True:
            serialvalue = serialClass.ReadData()
            if serialvalue == -1 or len(str(serialvalue)) != 4:
                time.sleep(0.1)
                continue
            UpdateReading(serialvalue)
            print(serialvalue)
            x.append(x[-1] + 1)
            y.append(int(serialvalue.split('_')[-1]) )

            readingline.setData(x, y)
            time.sleep(0.1)
    except:
        print("error in thread ")


def ModeCheckBoxFunction():
    auto = modeCheckbox.toggle.isChecked()
    fanCheckbox.setDisabled(auto)
    lampCheckbox.setDisabled(auto)
    fanSlider.setDisabled(auto)

    if auto:
        fanSlider.slider.setValue(0)
        fanCheckbox.toggle.setChecked(False)
        lampCheckbox.toggle.setChecked(False)


if __name__ == "__main__":
    app = QApplication(sys.argv)  # Later on you should add parameters to customize the GUI
    window = QWidget()

    window.setMinimumSize(1000, 600)
    gauge = QRoundProgressBar()
    gauge.setBarStyle(QRoundProgressBar.BarStyle.LINE)
    gauge.setOutlinePenWidth(20)
    gauge.setDataPenWidth(10)
    gauge.setMaximum(150)

    gauge.setFormat("Current temp \n %v C \n {}".format("state"))
    UpdateReading("0")
    gauge.move(window.rect().center())

    graphGrid = QGraphWidget(title="temperature Reading", y_ablel="C")

    SlidersGrid = QWidget()
    SlidersContainer = QVBoxLayout(SlidersGrid)
    fanSlider = QLabeledSlider(label="Fan Speed", min_range=10, max_range=255)
    maxtempSlider = QLabeledSlider(label="max Allowed temp", min_range=30, max_range=150)
    mintempSlider = QLabeledSlider(label="min Allowed temp", min_range=10, max_range=100)
    sendButton = QPushButton("Send")
    sendButton.clicked.connect(SendUartValue)
    SlidersContainer.addWidget(fanSlider)
    SlidersContainer.addWidget(maxtempSlider)
    SlidersContainer.addWidget(mintempSlider)
    SlidersContainer.addWidget(sendButton)
    CheckboxGrid = QWidget()
    CheckboxContainer = QVBoxLayout(CheckboxGrid)
    modeCheckbox = QToggleButton(text="Autmoatic")
    fanCheckbox = QToggleButton("fan Control")
    lampCheckbox = QToggleButton("Lamp Control")

    modeCheckbox.toggle.stateChanged.connect(ModeCheckBoxFunction)

    CheckboxContainer.addWidget(modeCheckbox)
    CheckboxContainer.addWidget(fanCheckbox)
    CheckboxContainer.addWidget(lampCheckbox)

    grid = QGridLayout(window)
    grid.setOriginCorner(0)
    grid.setRowStretch(0, 5)
    grid.setRowStretch(1, 5)
    grid.setRowStretch(2, 1)
    grid.addWidget(gauge, 0, 0, 2, 3)
    grid.addWidget(graphGrid, 0, 3, 2, 2)
    grid.addWidget(SlidersGrid, 2, 0, 1, 3)
    grid.addWidget(CheckboxGrid, 2, 3, 1, 2)

    window.show()

    if THEME == 'Dark':
        apply_stylesheet(app, theme='dark_red.xml')
        graphGrid.setBackground('#232629')
        graphGrid.setPenColor('#F44336')
        modeCheckbox.toggle.set_active_color("#F44336")
        fanCheckbox.toggle.set_active_color("#F44336")
        lampCheckbox.toggle.set_active_color("#F44336")


    else:
        apply_stylesheet(app, theme='light_blue.xml')
        graphGrid.setBackground('#f5f5f5')
        graphGrid.setPenColor('#2196F3')
        modeCheckbox.toggle.set_active_color("#2196F3")
        fanCheckbox.toggle.set_active_color("#2196F3")
        lampCheckbox.toggle.set_active_color("#2196F3")

    serialClass = CustomSerial(recieved_callback=ReadDataThread)

    sys.exit(app.exec_())
