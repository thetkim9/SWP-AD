import pickle
import random
import sys

from PyQt5.QtCore import QSize
from PyQt5.QtGui import QImage, QPalette, QBrush

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import (QWidget, QPushButton,
                             QHBoxLayout, QVBoxLayout, QApplication, QLabel,
                             QComboBox, QTextEdit, QLineEdit, QFrame)
#from RecordNRecognize import Recorder
from RecordNRecognize import Recorder
import _thread
import time
from equalizer_bar import EqualizerBar

class TakeClass(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()
        self.dbfilename = 'assignment6.dat'
        self.record = Recorder(channels=2)
        #self.scoredb = []
        #self.readScoreDB()
        #self.showScoreDB(self.scoredb)



    def initUI(self):
        oImage = QImage("background.jpg")
        entireHBox = QHBoxLayout()

        firstSubVBoxes = [QVBoxLayout(), QVBoxLayout()]



        for vBox in firstSubVBoxes:
            entireHBox.addLayout(vBox)
        secondSubHBoxesLeft = [QHBoxLayout() for i in range(4)]#4
        secondSubHBoxesRight = [QHBoxLayout() for i in range(2)]

        for layout in secondSubHBoxesLeft:
            firstSubVBoxes[0].addLayout(layout)
        for layout in secondSubHBoxesRight:
            firstSubVBoxes[1].addLayout(layout)

        self.equalizer = EqualizerBar(35, ['#0C0786', '#40039C', '#6A00A7', '#8F0DA3', '#B02A8F', '#CA4678', '#E06461',
                                          '#F1824C', '#FCA635', '#FCCC25', '#EFF821'])

        self.leftTopWidgets = [QLabel("From: "), QComboBox(), QLabel("To: "), QComboBox(), QLabel("Filename: "), QLineEdit(), QLabel("time here"), QPushButton("Record"), QPushButton("Save")]
        #language options should be expanded to all the available languages in BCP-47 language tags
        for i in range(9):self.leftTopWidgets[i].setStyleSheet("background-color: #c6c4c5;");

        self.leftTopWidgets[1].addItems(["English", "Korean"])

        self.leftTopWidgets[3].addItems(["Amharic", "Chinese", "English", "Korean"])
        self.languagetoCode = {"English":"en-US", "Korean":"ko"}
        self.leftMiddleWidgets = [QLabel("Filename: "), QLineEdit(), QPushButton("Save"), QPushButton("New File")]
        for i in range(4):self.leftMiddleWidgets[i].setStyleSheet("background-color: #c6c4c5;");

        self.textButtons = [QPushButton("Bold"), QPushButton("Italics"), QPushButton("Underline"), QPushButton("Color"), QPushButton("Highlight")]
        for i in range(5):self.textButtons[i].setStyleSheet("background-color: #c6c4c5;");

        self.textPageLeft = QTextEdit()
        self.textPageRight = QTextEdit()
        self.textPageRight.setStyleSheet("background-color: #c6c4c5;");
       # self.textPageRight.setStyleSheet("QTextEdit {color:red};");
        self.textPageLeft.setStyleSheet("background-color: #c6c4c5;");




        for widget in self.leftTopWidgets:
            secondSubHBoxesLeft[0].addWidget(widget)

        secondSubHBoxesLeft[1].addWidget(self.equalizer)
        self._timer = QtCore.QTimer()
        self._timer.setInterval(100)
        self._timer.timeout.connect(self.update_values)
        self._timer.start()

        #(self.waveDisplay)
        for widget in self.leftMiddleWidgets:
            secondSubHBoxesLeft[2].addWidget(widget)
        secondSubHBoxesLeft[3].addWidget(self.textPageLeft)
        for button in self.textButtons:
            secondSubHBoxesRight[0].addWidget(button)
        secondSubHBoxesRight[1].addWidget(self.textPageRight)


        self.leftTopWidgets[7].clicked.connect(self.buttonClicked)
        self.leftTopWidgets[8].clicked.connect(self.buttonClicked)
        for button in self.textButtons:
            button.clicked.connect(self.buttonClicked)
        #self.setGeometry(100, 100, 1700, 1000)
        #self.setGeometry(100, 100, 17, 500)
        #self.showFullScreen()
        self.setWindowTitle('Take Class')
        self.setLayout(entireHBox)

        oImage = QImage("1.jpg")
        #sImage = oImage.scaled(QSize(300, 200))  # resize Image to widgets size
        sImage = oImage.scaled(QSize(100, 100))  # resize Image to widgets size

        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(sImage))
        self.setPalette(palette)

        self.label = QLabel(self)  # test, if it's really backgroundimage
        #self.label.setGeometry(100, 700, 200, 50)


        self.show()

    def buttonClicked(self):
        sender = self.sender()
        if sender.text()=="Record":
            if self.leftTopWidgets[5].text()=="":
                self.recfile = self.record.open(str(time.time())+".wav", 'wb')
            else:
                self.recfile = self.record.open(self.leftTopWidgets[5].text()+".wav", 'wb')
            self.recfile.start_recording()
            sender.setText("Stop")
        elif sender.text()=="Stop":
            self.recfile.stop_recording()
            sender.setText("Record")

    def closeEvent(self, event):
        self.writeScoreDB()

    def readScoreDB(self):
        try:
            fH = open(self.dbfilename, 'rb')
        except FileNotFoundError as e:
            self.scoredb = []
            return

        try:
            self.scoredb =  pickle.load(fH)
        except:
            pass
        else:
            pass
        fH.close()

    # write the data into person db
    def writeScoreDB(self):
        fH = open(self.dbfilename, 'wb')
        pickle.dump(self.scoredb, fH)
        fH.close()

    def showScoreDB(self, db):
        string = ""
        for p in db:
            for attr in sorted(p):
                string += attr + "=" + str(p[attr]) + ' '
            string += "\n"
        self.resultScreen.setText(string)

    def update_values(self):
        self.equalizer.setValues([
            min(100, v+random.randint(0, 50) if random.randint(0, 5) > 2 else v)
            for v in self.equalizer.values()
            ])

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = TakeClass()
    sys.exit(app.exec_())