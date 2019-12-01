import sys
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import *
from PyQt5.uic.properties import QtWidgets
from PyQt5.QtGui import QImage, QPalette, QBrush
from PyQt5.QtCore import QSize

from Main import TakeClass

class Log(QWidget):
    def __init__(self):
        super().__init__()
        self.title="speech_rec"
        self.top =100
        self.left=100
        self.width=400
        self.height=400

        self.app1()

    def app1(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.top,self.left,self.height,self.width)

        username = QLineEdit(self)
        username.setPlaceholderText("username")
        username.move(100,100)

        password = QLineEdit(self)
        password.setPlaceholderText("password")
        password.move(100, 150)

        btn = QPushButton("login",self)
        btn.move(100,200)

        btn.clicked.connect(self.paa)

        oImage = QImage("1.jpg")
        sImage = oImage.scaled(QSize(400, 400))  # resize Image to widgets size

        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(sImage))
        self.setPalette(palette)

        self.show()



    def paa(self):
        self.hide()
        self.tr = TakeClass()

if __name__ == "__main__":
    app= QApplication(sys.argv)
    ex = Log()
    sys.exit(app.exec_())

