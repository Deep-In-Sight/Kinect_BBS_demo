import numpy as np
import os
import cv2
import pandas as pd

from bbsQt.constants import CAM_LIST, VERBOSE

from PyQt5.QtWidgets import (QWidget, QMessageBox, QApplication, 
                            QPushButton, QHBoxLayout, QVBoxLayout, QLabel)
from PyQt5.QtCore import QTime, Qt, pyqtSlot, QSize, pyqtSignal, QTimer
from PyQt5.QtGui import QPixmap, QIcon, QImage
from PyQt5.QtPrintSupport import *

from ..config import Config as setConfig

from .QButtons import qButtons
from .QImgViewer import PhotoViewer
from .QScenario import qScenario
from .QThreadObj import qThreadRecord
from datetime import datetime

import time

ENABLE_PYK4A = True
from ..pykinect_azure import pykinect

pykinect.initialize_libraries(track_body=True)

def getIcon(path):
    app_icon = QIcon()
    app_icon.addFile(os.path.join(path, '16x16.png'),   QSize(16,16))
    app_icon.addFile(os.path.join(path, '24x24.png'),   QSize(24,24))
    app_icon.addFile(os.path.join(path, '32x32.png'),   QSize(32,32))
    app_icon.addFile(os.path.join(path, '48x48.png'),   QSize(48,48))
    app_icon.addFile(os.path.join(path, '256x256.png'), QSize(256,256))
    return app_icon


def get_layout(mylabel):
    VBlayoutMain = QVBoxLayout()
    VBlayoutMain.setAlignment(Qt.AlignTop)
    VBlayoutMain.setAlignment(Qt.AlignLeft)
    VBlayoutMain.addWidget(mylabel)
    return VBlayoutMain


def load_image(fn_img = "imgs/instruct_1.png"):
    img = cv2.imread(fn_img)
    img = cv2.resize(img, (480, 270))
    img = img[:,:,::-1]
    img = np.array(img).astype(np.uint8)
    height, width, channel = img.shape
    bytesPerLine = 3 * width
    pixmap   = QPixmap(QImage(img, width, height, bytesPerLine, QImage.Format_RGB888))
    return pixmap


class QMyMainWindow(QWidget):
    startRecord = pyqtSignal()
    stopRecord = pyqtSignal()
    def __init__(self, q1, q_answer, e_sk, e_ans):
        """
        q1 = mp.queue to put skeleton 
        e_sk = mp.event to signal skeleton is ready
        """
        super(QMyMainWindow, self).__init__()
        ### Multiprocessing queue messages
        self.q1 = q1
        self.e_sk = e_sk
        self.q_answer = q_answer
        self.e_ans = e_ans

        self.onPlay = False
        self.ScenarioNo = 1
        #self.Locale = 'en_us' ## ?? G1은 무슨 의미일까? 
        self.Locale = "G1"

        #self.recordReady = False
        
        # add 2021/12/23 
        self.PWD = os.getcwd()
        self.btn = qButtons(self, self.PWD)

        self.imgviwerRGB = PhotoViewer(self,"RGB", ENABLE_PYK4A)
        self.imgviwerSkeleton = PhotoViewer(self, "Skeleton", ENABLE_PYK4A)

        self.startRecord.connect(self.recordImages)
        self.stopRecord.connect(self.end)
        self.qScenario = qScenario(self, self.PWD, q_answer, self.btn, self.startRecord, self.stopRecord)

        self.config = setConfig() # to be added

        self.curScenario = self.config.scenario[self.ScenarioNo]

        self.setGeometry(100, 100, 1200, 850)
        self.setMinimumSize(1000, 600)
        self.setMaximumSize(2048, 1600)
        self.setWindowTitle('Kinect BBS demo')

        # fix 2021/01/07
        self.camera_choice = CAM_LIST    

        self._init_camera(1)
        self.setLayout()

        self.stackColor = []
        self.stackDepth = []
        self.stackSkeleton = []
        # self.stackPoints = []

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.showTime)
        self.timer.start(1000)


        self.imgviwerRGB.emitDispImgSize.connect(self.qScenario.setRgbDispSize)
        self.imgviwerSkeleton.emitDispImgSize.connect(self.qScenario.setDepthDispSize)

        ############################
        LayoutFallPred = QVBoxLayout(self) # with "self", it becomes MAIN layout
        LayoutFallPred.setAlignment(Qt.AlignTop)
        LayoutFallPred.setAlignment(Qt.AlignLeft)

    def end(self):
        self.btn.endtime.setText("T")
        checkfile = f"{self.PWD}/bodytracking_data.csv"
        if not(os.path.isfile(checkfile)) :
            t1 = time.time()

            self.device.close()
            self.bodyTracker.destroy()

            # self.stackPoints = pd.DataFrame(self.stackPoints)
            # print("EEEEEEEEEEEENNNNNNNNNNNNNNNNNNNDDDDDDDDDDDDDDD")
            # print("STACK POINTS")
            # print(self.stackPoints)
            # print("__________________________")

            self.qthreadrec.setRun(False)

            self.qthreadrec.mkd(self.Locale, self.qScenario.SubjectID, self.ScenarioNo)

            # skimage 를 뽑고 이걸 skimage label 넣는다. 
            skimage = self.qthreadrec.save_multiproc()
            if skimage == -1:
                cameraidx = self.btn.cameranum.currentIndex()
                self.startcamera(cameraidx)
            else:    
                self.skimageLabel.setPixmap(skimage)

                # recording 하는 동안 sleep으로 기다리기? 음.. 
                while self.qthreadrec.is_recoding():
                    time.sleep(2)

                t2 = time.time()

                self.qthreadrec.resetstate()

                if not VERBOSE: print("time during saving images: {} sec.".format(t2 - t1))

                self.resetRecordInterface()

                self.btn.endtime.setText("F")

                if not VERBOSE: print("Saving done. device index", self.btn.cameranum.currentIndex())

                ###
                self.device = pykinect.start_device(device_index=self.camera_choice[self.btn.action_num.currentIndex()+1], 
                                                    config=self.device_config)
                self.bodyTracker = pykinect.start_body_tracker()
                self.qthreadrec.reset(self.device, self.bodyTracker)
        
        # Every reached?? 
        #else:
        #    msgBox1 = QMessageBox()
        #    msgBox1.setText("Check Score!")
        #    msgBox1.exec()    

    def setLayout(self):
        LayoutMain = QVBoxLayout(self) # with "self", it becomes MAIN layout
        LayoutMain.setAlignment(Qt.AlignTop)        
        LayoutMain.setAlignment(Qt.AlignLeft)    
        
        LayoutViewers = QHBoxLayout()
        LayoutViewers.setAlignment(Qt.AlignLeft)
        
        LayoutViewers.addLayout(self.imgviwerRGB.getLayout(),1)
        LayoutViewers.addLayout(self.imgviwerSkeleton.getLayout(),1)
        
        self.skimageLabel = QLabel()
        self.skimageLabel.setPixmap(load_image())
        
        # add 2021.12.27 skindexbtn
        self.skindexbtn0 = QPushButton()
        self.skindexbtn0.setCheckable(False)
        self.skindexbtn0.setText('blue')
        self.skindexbtn0.setMinimumHeight(40)

        self.skindexbtn1 = QPushButton()
        self.skindexbtn1.setCheckable(False)
        self.skindexbtn1.setText('orange')
        self.skindexbtn1.setMinimumHeight(40)

        self.skindexbtn2 = QPushButton()
        self.skindexbtn2.setCheckable(False)
        self.skindexbtn2.setText('green')
        self.skindexbtn2.setMinimumHeight(40)
        
        # add 2021.12.27 skbtnlayout
        skBBoxLayout = QVBoxLayout()

        # sk select viewr
        LayoutViewers.addLayout(get_layout(self.skimageLabel))
        
        skBBoxLayout.addWidget(self.skindexbtn0)
        skBBoxLayout.addWidget(self.skindexbtn1)
        skBBoxLayout.addWidget(self.skindexbtn2)
        LayoutViewers.addLayout(skBBoxLayout)

        LayoutViewers.addLayout(QVBoxLayout(),7) # 이건 뭐지? 모양 맞추기용?

        LayoutFunctions = QHBoxLayout()

        LayoutMain.addLayout(self.btn.getLayout(),1)
        LayoutMain.addLayout(LayoutViewers,39)
        LayoutMain.addLayout(LayoutFunctions,1)
        LayoutMain.addLayout(self.qScenario.getLayout(),49)

        # # add 2021.12.27  skindexbox connect 
        self.skindexbtn0.clicked.connect(lambda: self.qthreadrec.select_sk(0))
        self.skindexbtn1.clicked.connect(lambda: self.qthreadrec.select_sk(1))
        self.skindexbtn2.clicked.connect(lambda: self.qthreadrec.select_sk(2))

    def resetRecordInterface(self):
        if self.qScenario.Ready.isChecked():
            self.qScenario.Ready.click()


    @pyqtSlot()
    def recordImages(self):
        # self.year = str(datetime.today().year % 100).zfill(2)
        # self.month = str(datetime.today().month).zfill(2)
        # self.day = str(datetime.today().day).zfill(2)

        # self.yymmdd = self.year + self.month + self.day

        #self.qScenario.locale_option.currentText()
        # self.stackPoints = []
            
        #t0 = time.time()

        self.qthreadrec.init(self.PWD, 
                                self.Locale,
                                self.qScenario.SubjectID,
                                self.btn
                                )
        self.qthreadrec.start()
        self.qthreadrec.setRun(True)

        #self.qScenario.end.setEnabled(True)
        while self.qthreadrec.is_recoding():
            # print("recording")
            QApplication.processEvents()
        
        #t1 = time.time()

    def showTime(self):
        currentTime = QTime.currentTime()
        displayTxt = currentTime.toString('hh:mm:ss')
        self.btn.curtimeLabel.setText(displayTxt)

    # def optionChanged(self):
    #     print(self.btn.option.currentIndex())
    #     if self.btn.option.currentIndex() == 0:
    #         self.imgviwerDepth.minval = self.config.cfg_30cm["depth_minval"]
    #         self.imgviwerDepth.MinRangeInput.setText(str(self.imgviwerDepth.minval))
    #         self.imgviwerDepth.maxval = self.config.cfg_30cm["depth_maxval"]
    #         self.imgviwerDepth.MaxRangeInput.setText(str(self.imgviwerDepth.maxval))
            
    #     elif self.btn.option.currentIndex() == 1:
    #         self.imgviwerDepth.minval = self.config.cfg_50cm["depth_minval"]
    #         self.imgviwerDepth.MinRangeInput.setText(str(self.imgviwerDepth.minval))
    #         self.imgviwerDepth.maxval = self.config.cfg_50cm["depth_maxval"]
    #         self.imgviwerDepth.MaxRangeInput.setText(str(self.imgviwerDepth.maxval))        

    # add 20210107
    def actionChanged(self):
        if not VERBOSE: print("action changed", self.btn.action_num.currentIndex())
        actionidx = self.btn.action_num.currentIndex() + 1
        #a = 1
        #e = 0
        
        self.startcamera(self.camera_choice[actionidx])
        self.qScenario.scenarionum.setText(f'Scenario : {actionidx}')
        self.skimageLabel.setPixmap(load_image(f"imgs/instruct_{actionidx}.png"))

    def scoreChanged(self, text):
        self.qScenario.scorenum.setText(f'Score : {text}')

    # fix 20210107
    def cameraChanged(self):
        if not VERBOSE: print("camera changed", self.btn.cameranum.currentIndex())
        cameraidx = self.btn.cameranum.currentIndex()
        self.startcamera(cameraidx)

    def _init_camera(self, cameraidx):
        #if ENABLE_PYK4A:
        # Modify camera configuration
        self.device_config = pykinect.default_configuration
        self.device_config.color_resolution = pykinect.K4A_COLOR_RESOLUTION_1080P
        self.device_config.depth_mode = pykinect.K4A_DEPTH_MODE_WFOV_2X2BINNED

        # Start cameras using modified configuration
        if not VERBOSE: print("ACTION CHANGED, device index", cameraidx)
        self.device = pykinect.start_device(device_index=cameraidx, config=self.device_config)

        # Initialize the body tracker
        self.bodyTracker = pykinect.start_body_tracker()
        #else:
        #    self.pyK4A = None
        #try:
        self.qthreadrec = qThreadRecord(self.device, self.bodyTracker, self.qScenario, 
                                    self.PWD, cameraidx, 
                                    self.q1, self.e_sk, self.e_ans, self.q_answer)
        #except:
        #    print("Error in camera.... trying again")
        #    self._init_camera(cameraidx)

    # add 20210107
    def startcamera(self, cameraidx):
        try: 
            self.skindexbtn0.clicked.disconnect() 
            self.skindexbtn1.clicked.disconnect() 
            self.skindexbtn2.clicked.disconnect() 
        except Exception: 
            pass
        
        #self.qScenario.onchanged(cameraidx)

        self.device.close()
        self.bodyTracker.destroy()
        
        self._init_camera(cameraidx)

        self.skindexbtn0.clicked.connect(lambda: self.qthreadrec.select_sk(0))
        self.skindexbtn1.clicked.connect(lambda: self.qthreadrec.select_sk(1))
        self.skindexbtn2.clicked.connect(lambda: self.qthreadrec.select_sk(2))
 
    @pyqtSlot()        
    def updateOnPlay(self):    
        self.onPlay = not(self.onPlay)

    @pyqtSlot()    
    def calibration2(self):
        t0 = time.time()
        while self.onPlay and ENABLE_PYK4A:
            # Get capture
            capture = self.device.update()
            
            # Get body tracker frame
            body_frame = self.bodyTracker.update()

            rat, c_image = capture.get_color_image()

            ret, dc_image = capture.get_colored_depth_image()
            ret, b_image = body_frame.get_segmentation_image()  ## <<<<<<<<<<<
            s_image = cv2.addWeighted(dc_image, 0.6, b_image, 0.4, 0)
            s_image = cv2.cvtColor(s_image, cv2.COLOR_BGR2RGB)
            s_image = body_frame.draw_bodies(s_image)

            capture.reset()
            body_frame.reset()

            self.imgviwerRGB.setImg(c_image)
            self.imgviwerSkeleton.setImg(s_image) ## <<<<<<<<<<<

            try:
                self.imgviwerRGB.start()
                self.imgviwerSkeleton.start()
            except:
                pass

            t1 = time.time()
            self.btn.LbFPS.setText("{:.2f}FPS".format(1./(t1-t0)))
            t0 = t1

            #self.qScenario.updateSize()            
            QApplication.processEvents()

        # i = 0
        # while self.onPlay and not(ENABLE_PYK4A):        
        #     self.imgviwerRGB.setImgPath(f"{self.PWD}/images/transformed_color0-{i}.jpg")

        #     self.imgviwerRGB.start()
        #     i+=1
        #     if i>4: i=0
        #     t1 = time.time()
        #     self.btn.LbFPS.setText("{:.2f}FPS".format(1./(t1-t0)))
        #     t0 = t1            

        #     #self.qScenario.updateSize()        
        #     QApplication.processEvents()

    def closeEvent(self, event):
        msgbox     = QMessageBox()
        msgbox.setIcon(QMessageBox.Question)
        reply     = msgbox.question(self, "",
                                    "Are you sure to close window ?", 
                                    QMessageBox.No | QMessageBox.Yes , QMessageBox.Yes)
        if reply == QMessageBox.Yes:
            self.device.close()
            self.bodyTracker.destroy()

            event.accept()
        else:
            event.ignore()
