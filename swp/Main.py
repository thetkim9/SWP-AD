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
import speechRecon

from PyQt5.QtCore import (QCoreApplication, QObject, QRunnable, QThread,
                          QThreadPool, pyqtSignal)
import re

from google.cloud import speech_v1p1beta1 as speech

from Trans import Translation

import os

credential_path = "/home/user/PycharmProjects/swp/TakeClass-16ca2bd11db5.json"
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path

class AThread(QThread):
    trigger = pyqtSignal(object)

    def __init__(self, transcript):
        super().__init__()
        self.transcript = transcript

    def run(self):
        self.trigger.emit(self.transcript)

class TakeClass(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()
        self.record = Recorder(channels=2)
        self.speechLang = ""
        self.transLang = ""
        self.trans = Translation()

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

        self.leftTopWidgets = [QLabel("From: "), QComboBox(), QLabel("To: "), QComboBox(), QLabel("Filename: "), QLineEdit(), QLabel("time here"), QPushButton("Record")]
        #language options should be expanded to all the available languages in BCP-47 language tags
        for widget in self.leftTopWidgets:
            widget.setStyleSheet("background-color: #c6c4c5;");

        self.leftTopWidgets[1].addItems(["English", "Korean"])

        self.leftTopWidgets[3].addItems(["Amharic", "Chinese", "English", "Korean"])
        self.languagetoCode = {"English":"en-US", "Korean":"ko"}
        self.leftMiddleWidgets = [QLabel("Filename: "), QLineEdit(), QPushButton("New File")]
        for widget in self.leftMiddleWidgets:
            widget.setStyleSheet("background-color: #c6c4c5;");

        self.textButtons = [QPushButton("Bold"), QPushButton("Italics"), QPushButton("Underline"), QPushButton("Color"), QPushButton("Highlight")]
        for widget in self.textButtons:
            widget.setStyleSheet("background-color: #c6c4c5;");

        self.textPageLeft = QTextEdit()
        self.textPageLeft.setReadOnly(True)
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
        if sender.text() == "Record":
            self.speechLang = self.leftTopWidgets[1].currentText()
            self.transLang = self.leftTopWidgets[3].currentText()
            if self.leftTopWidgets[5].text() == "":
                self.recfile = self.record.open(str(time.time()) + ".wav", 'wb')
            else:
                self.recfile = self.record.open(self.leftTopWidgets[5].text() + ".wav", 'wb')
            self.recfile.start_recording()
            _thread.start_new_thread(self.start_recognize, ())
            #self.reconStream = speechRecon.start_recognize(self, self.languagetoCode[self.speechLang])
            #self.thread = AThread()
            #thread.finished.connect()
            #self.thread.trigger.connect(lambda: speechRecon.start_recognize(self, self.languagetoCode[self.speechLang]))
            #self.thread.trigger.connect(self.start_recognize)
            #self.thread = AThread()
            #self.thread.trigger.connect(self.start_recognize)
            #self.thread.start()
            sender.setText("Stop")

        elif sender.text() == "Stop":
            self.recfile.stop_recording()
            self.stop_recognize()
            sender.setText("Record")

        elif sender.text() == "New File":
            file1 = open(self.leftMiddleWidgets[1].text() + "-original("+self.speechLang+").txt", "w")
            file1.writelines(self.textPageLeft.toPlainText())
            file1.close()
            file2 = open(self.leftMiddleWidgets[1].text() + "-translated("+self.transLang+").txt", "w")
            file2.writelines(self.textPageRight.toPlainText())
            file2.close()
            pass

        elif sender.text() == "Bold":
            pass

        elif sender.text() == "Italics":
            pass

        elif sender.text() == "Underline":
            pass

        elif sender.text() == "Color":
            pass

        else:
            pass

    def closeEvent(self, event):
        pass

    # write the data into person db
    def writeText(self):
        pass

    def update_values(self):
        self.equalizer.setValues([
            min(100, v+random.randint(0, 50) if random.randint(0, 5) > 2 else v)
            for v in self.equalizer.values()
            ])

    def listen_print_loop(self, responses, stream):

        for response in responses:

            if speechRecon.get_current_time() - stream.start_time > speechRecon.STREAMING_LIMIT:
                stream.start_time = speechRecon.get_current_time()
                break

            if not response.results:
                continue

            result = response.results[0]

            if not result.alternatives:
                continue

            transcript = result.alternatives[0].transcript

            result_seconds = 0
            result_nanos = 0

            if result.result_end_time.seconds:
                result_seconds = result.result_end_time.seconds

            if result.result_end_time.nanos:
                result_nanos = result.result_end_time.nanos

            stream.result_end_time = int((result_seconds * 1000)
                                         + (result_nanos / 1000000))

            corrected_time = (stream.result_end_time - stream.bridging_offset
                              + (speechRecon.STREAMING_LIMIT * stream.restart_counter))
            # Display interim results, but with a carriage return at the end of the
            # line, so subsequent lines will overwrite them.

            if result.is_final:

                sys.stdout.write(speechRecon.GREEN)
                sys.stdout.write('\033[K')
                sys.stdout.write(str(corrected_time) + ': ' + transcript + '\n')
                #self.textPageLeft.setText(self.textPageLeft.toPlainText() + '. ' + transcript)
                thread = AThread(transcript)
                thread.trigger.connect(self.speechToText)
                thread.start()
                stream.is_final_end_time = stream.result_end_time
                stream.last_transcript_was_final = True

                # Exit recognition if any of the transcribed phrases could be
                # one of our keywords.
                if re.search(r'\b(exit|quit)\b', transcript, re.I):
                    # sys.stdout.write(YELLOW)
                    # sys.stdout.write('Exiting...\n')
                    stream.closed = True
                    break

            else:
                sys.stdout.write(speechRecon.RED)
                sys.stdout.write('\033[K')
                sys.stdout.write(str(corrected_time) + ': ' + transcript + '\r')
                #self.textPageLeft.setText(self.textPageLeft.toPlainText() + '. ' +transcript)
                stream.last_transcript_was_final = False

    def speechToText(self, transcript):
        print("???")
        text = self.trans.translate(transcript, self.transLang)
        self.textPageLeft.setText(self.textPageLeft.toPlainText() + '. ' + text)

    def start_recognize(self):
        """start bidirectional streaming from microphone input to speech API"""
        print("test")
        client = speech.SpeechClient()
        config = speech.types.RecognitionConfig(
            encoding=speech.enums.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=speechRecon.SAMPLE_RATE,
            language_code=self.languagetoCode[self.speechLang],
            max_alternatives=1)
        streaming_config = speech.types.StreamingRecognitionConfig(
            config=config,
            interim_results=True)

        self.mic_manager = speechRecon.ResumableMicrophoneStream(speechRecon.SAMPLE_RATE, speechRecon.CHUNK_SIZE)
        print(self.mic_manager.chunk_size)

        sys.stdout.write(speechRecon.YELLOW)
        sys.stdout.write('\nListening, say "Quit" or "Exit" to stop.\n\n')
        sys.stdout.write('End (ms)       Transcript Results/Status\n')
        sys.stdout.write('=====================================================\n')

        with self.mic_manager as stream:

            while not stream.closed:
                '''
                sys.stdout.write(YELLOW)
                sys.stdout.write('\n' + str(
                    STREAMING_LIMIT * stream.restart_counter) + ': NEW REQUEST\n')
                '''

                stream.audio_input = []
                audio_generator = stream.generator()

                requests = (speech.types.StreamingRecognizeRequest(
                    audio_content=content) for content in audio_generator)

                responses = client.streaming_recognize(streaming_config,
                                                       requests)

                # Now, put the transcription responses to use.
                self.listen_print_loop(responses, stream)

                if stream.result_end_time > 0:
                    stream.final_request_end_time = stream.is_final_end_time
                stream.result_end_time = 0
                stream.last_audio_input = []
                stream.last_audio_input = stream.audio_input
                stream.audio_input = []
                stream.restart_counter = stream.restart_counter + 1

                if not stream.last_transcript_was_final:
                    # sys.stdout.write('\n')
                    #self.textPageLeft.setText(self.textPageLeft.toPlainText() + '. ' + '\n')
                    thread = AThread('\n')
                    thread.trigger.connect(self.speechToText)
                    thread.start()

                stream.new_stream = True

    def stop_recognize(self):
        self.mic_manager.__exit__(0, 0, 0)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    #app = QCoreApplication([])
    #app = QGuiApplication()
    ex = TakeClass()
    sys.exit(app.exec_())