import pickle
import random
import sys
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QImage, QPalette, QBrush
from PyQt5.QtWidgets import (QWidget, QPushButton,
                             QHBoxLayout, QVBoxLayout, QApplication, QLabel,
                             QComboBox, QTextEdit, QLineEdit, QFrame, QColorDialog, QFontComboBox)
import speechRecon
from RecordNRecognize import Recorder
import _thread
import time
from equalizer_bar import EqualizerBar
#import speechRecon

from PyQt5.QtCore import (QCoreApplication, QObject, QRunnable, QThread,
                          QThreadPool, pyqtSignal)
import re
from google.cloud import speech_v1p1beta1 as speech
import os
from google.cloud.bigquery.client import Client
import pyaudio
import numpy as np


os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/home/metti/PycharmProjects/main/TakeClass-16ca2bd11db5.json'

bq_client = Client()


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
        self.CHUNK = 3000
        print(self.CHUNK)
        self.RATE = 44100
        p = pyaudio.PyAudio()
        self.stream = p.open(format=pyaudio.paInt16, channels=1, rate=self.RATE, input=True,
                        frames_per_buffer=self.CHUNK)
        self.fftLen = 2048
        self.shift = 4096
        self.signal_scale = 1. / 2000

        self.capture_setting = {
            "ch": 1,
            "fs": 16000,
            "chunk": self.shift
        }

        self.initUI()
        self.record = Recorder(channels=2)
        self.speechLang = ""
        self.transLang = ""

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

        fontBox =QFontComboBox(self)
        fontBox.currentFontChanged.connect(self.fontFamily)
        fontBox.setStyleSheet("background-color: #c6c4c5;");

        fontSize = QComboBox(self)
        fontSize.setEditable(True)
        fontSize.setStyleSheet("background-color: #c6c4c5;");

        # Minimum number of chars displayed
        fontSize.setMinimumContentsLength(3)

        fontSize.activated.connect(self.fontSize)

        # Typical font sizes
        fontSizes = ['6', '7', '8', '9', '10', '11', '12', '13', '14',
                     '15', '16', '18', '20', '22', '24', '26', '28',
                     '32', '36', '40', '44', '48', '54', '60', '66',
                     '72', '80', '88', '96']

        for i in fontSizes:
            fontSize.addItem(i)



        for widget in self.textButtons:
            widget.setStyleSheet("background-color: #c6c4c5;");

        self.textPageLeft = QTextEdit()
        self.textPageLeft.setReadOnly(True)
        self.textPageRight = QTextEdit()

        self.textPageRight.setTabStopWidth(33)

        self.textPageRight.setStyleSheet("background-color: #c6c4c5;");
        self.textPageLeft.setStyleSheet("background-color: #c6c4c5;");




        for widget in self.leftTopWidgets:
            secondSubHBoxesLeft[0].addWidget(widget)

        secondSubHBoxesLeft[1].addWidget(self.equalizer)
        self._timer = QtCore.QTimer()
        self._timer.setInterval(5)
        self._timer.timeout.connect(self.update_values)

        self._timer.start()

        #(self.waveDisplay)
        for widget in self.leftMiddleWidgets:
            secondSubHBoxesLeft[2].addWidget(widget)
        secondSubHBoxesLeft[3].addWidget(self.textPageLeft)
        for button in self.textButtons:
            secondSubHBoxesRight[0].addWidget(button)

        secondSubHBoxesRight[0].addWidget(fontBox)
        secondSubHBoxesRight[0].addWidget(fontSize)

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
        sImage = oImage.scaled(QSize(100,100))  # resize Image to widgets size

        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(sImage))
        self.setPalette(palette)

        self.label = QLabel(self)  # test, if it's really backgroundimage


        self.show()

    def fontFamily(self, font):
        self.textPageRight.setCurrentFont(font)

    def fontSize(self, fontsize):
        self.textPageRight.setFontPointSize(int(fontsize))

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
            if self.textPageRight.fontWeight() == QtGui.QFont.Bold:

                self.textPageRight.setFontWeight(QtGui.QFont.Normal)

            else:

                self.textPageRight.setFontWeight(QtGui.QFont.Bold)

        elif sender.text() == "Italics":
            state = self.textPageRight.fontItalic()

            self.textPageRight.setFontItalic(not state)
        elif sender.text() == "Underline":
            state = self.textPageRight.fontUnderline()

            self.textPageRight.setFontUnderline(not state)

        elif sender.text() == "Color":
            color = QColorDialog.getColor()
            self.textPageRight.setTextColor(color)

        elif sender.text() == "Highlight":
            color = QColorDialog.getColor()

            self.textPageRight.setTextBackgroundColor(color)

        else:
            pass



    def closeEvent(self, event):
        self.writeScoreDB()

    # write the data into person db
    def writeText(self):
        fH = open(self.dbfilename, 'wb')
        pickle.dump(self.scoredb, fH)
        fH.close()

    def update_values(self):
        data = np.fromstring(self.stream.read(self.CHUNK), dtype=np.int16)
        peak = np.average(np.abs(data)) * 2
        bars = int(50 * peak / 2 ** 16)

        if bars !=0:

            self.equalizer.setValues([
                min(100, v+random.randint(0, 50) if random.randint(0, 5) > 2 else v)
                for v in self.equalizer.values()
                ])
        else:
            self.equalizer.setValues([
                min(0, v + random.randint(0, 50) if random.randint(0, 5) > 2 else v)
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
        self.textPageLeft.setText(self.textPageLeft.toPlainText() + '. ' + transcript)

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
    ex = TakeClass()
    sys.exit(app.exec_())