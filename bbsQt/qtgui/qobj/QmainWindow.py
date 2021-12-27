#import sys
#import ntpath
import numpy as np
import os
import cv2
import pandas as pd
import shutil


#from PIL import Image
#import random
from PyQt5.QtWidgets import *
from PyQt5.QtCore import * 
from PyQt5.QtGui import *
from PyQt5.QtPrintSupport import *

from ..config import Config as setConfig

from .QButtons import qButtons
from .QImgViewer import PhotoViewer
from .QScenario import qScenario
#from qobj.QShortcuts import createActions
from .QThreadObj import qThreadRecord
#from qobj.QSkeleton import qSkeleton
from datetime import datetime

#import qobj.QSkeleton
import time
#import matplotlib.pyplot as plt
#import src.image as imgutil

#import subprocess

#plt.rcParams['toolbar'] = 'None'

ENABLE_PYK4A = True
from ..pykinect_azure import pykinect
from . import image as imgutil

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
    #VBlayoutMain.addWidget(QLabelImgView)
    VBlayoutMain.addWidget(mylabel)
    #VBlayoutMain.addLayout(HBlayout)
    return VBlayoutMain


def load_image():
    fn_img = "/home/hoseung/Work/Kinect_BBS_demo/G1/000/RGB/a_0001.jpg"
    img = cv2.imread(fn_img)
    #img = imgutil.rgb2gray(img)
    img = cv2.resize(img, (480, 270))
    img = img[:,:,::-1]
    img = np.array(img).astype(np.uint8)
    height, width, channel = img.shape
    bytesPerLine = 3 * width
    pixmap   = QPixmap(QImage(img, width, height, bytesPerLine, QImage.Format_RGB888))
    return pixmap



class QMyMainWindow(QWidget):
    startRecord = pyqtSignal()
    def __init__(self, q1, e_sk, q_text, e_ans): #### 여기가 아닌가?
        """
        q1 = mp.queue to put skeleton 
        e_sk = mp.event to signal skeleton is ready
        """
        super(QMyMainWindow, self).__init__()
        self.q1 = q1
        self.e_sk = e_sk
        self.onPlay = False
        self.ScenarioNo = 1
        self.ScenarioPathOn = False
        self.n_alpha = 20
        self.increasing_alpha = True
        self.Locale = 'en_us' ## ?? G1은 무슨 의미일까? 

        self.recordReady = False

        # add 2021/12/23 
        #self.cameraindex = 0

        self.PWD = os.getcwd()
        self.imgviwerRGB = PhotoViewer(self,"RGB", ENABLE_PYK4A)
        
        #self.imgviwerIRtest = PhotoViewer(self,"IR", ENABLE_PYK4A)
        self.imgviwerSkeleton = PhotoViewer(self, "Skeleton", ENABLE_PYK4A)
        self.qScenario = qScenario(self, self.PWD)
        self.config = setConfig() # to be added
        #self.qSkeleton = qSkeleton()

        #self.class_name = QComboBox()

        # self.acc = [0,0,0] # [x,y,x]

        self.curScenario = self.config.scenario[self.ScenarioNo]

        self.alpha = np.arange(self.n_alpha) / (self.n_alpha-1) * 0.8
        self.tgtsize = (np.arange(self.n_alpha) / (self.n_alpha-1) * 500).astype(np.int)

        self.setGeometry(100, 100, 1200, 850)
        self.setMinimumSize(1000, 600)
        self.setMaximumSize(2048, 1600)
        self.setWindowTitle('Operating Module for NIA 21 Data Capture')

        self.btn = qButtons(self, self.PWD)
        self.coord = np.arange(10)*0.1 + 0.05


        if ENABLE_PYK4A:
            # Modify camera configuration
            self.device_config = pykinect.default_configuration
            self.device_config.color_resolution = pykinect.K4A_COLOR_RESOLUTION_1080P
            self.device_config.depth_mode = pykinect.K4A_DEPTH_MODE_WFOV_2X2BINNED

                # Start cameras using modified configuration
            self.device = pykinect.start_device(device_index=self.btn.cameranum.currentIndex(), config=self.device_config)

            # Initialize the body tracker
            self.bodyTracker = pykinect.start_body_tracker()
        else:
            self.pyK4A = None

        self.qthreadrec = qThreadRecord(self.device, self.bodyTracker, self.btn.LbFPS, self.qScenario, self.PWD, self.btn.cameranum.currentIndex())

        self.setLayout()
        self.initplot()
        self.initset()

        self.stackColor = []
        self.stackIR = []
        self.stackDepth = []
        self.stackSkeleton = []
        self.stackPoints = []

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.showTime)
        self.timer.timeout.connect(self.checkRecordability)
        self.timer.start(1000)


        self.imgviwerRGB.emitDispImgSize.connect(self.qScenario.setRgbDispSize)
        self.imgviwerSkeleton.emitDispImgSize.connect(self.qScenario.setDepthDispSize)

        # self.startRecord.connect(self.moveCheckerCoord)
        self.startRecord.connect(self.recordImages)
    
    def st(self):
        self.btn.endtime.setText("F")

    def end(self):
        self.btn.endtime.setText("T")

    # fixed
    def pnt(self):
        print(self.qthreadrec.pic_Count)
        self.stackPoints.append(self.qthreadrec.pic_Count)
    # fixed
    def overwrite(self):
        if os.path.isdir(f"{self.PWD}/{self.Locale}/{str(self.qScenario.SubjectID).zfill(3)}/{str(self.btn.option.currentText())}/BT/{self.config.Angle}/{self.ScenarioNo}/{self.qScenario.currentRecSeq}") :
            t1 = time.time()
            shutil.rmtree(f"{self.PWD}/{self.Locale}/{str(self.qScenario.SubjectID).zfill(3)}/{str(self.btn.option.currentText())}/BT/{self.config.Angle}/{self.ScenarioNo}/{self.qScenario.currentRecSeq}")
            shutil.rmtree(f"{self.PWD}/{self.Locale}/{str(self.qScenario.SubjectID).zfill(3)}/{str(self.btn.option.currentText())}/RGB/{self.config.Angle}/{self.ScenarioNo}/{self.qScenario.currentRecSeq}")
            shutil.rmtree(f"{self.PWD}/{self.Locale}/{str(self.qScenario.SubjectID).zfill(3)}/{str(self.btn.option.currentText())}/IR/{self.config.Angle}/{self.ScenarioNo}/{self.qScenario.currentRecSeq}")
            shutil.rmtree(f"{self.PWD}/{self.Locale}/{str(self.qScenario.SubjectID).zfill(3)}/{str(self.btn.option.currentText())}/DEPTH/{self.config.Angle}/{self.ScenarioNo}/{self.qScenario.currentRecSeq}")
            self.stackPoints = pd.DataFrame(self.stackPoints)
        

            self.qthreadrec.setRun(False)

            self.qthreadrec.mkd(self.Locale,
                                 self.config.Angle, 
                                 self.qScenario.currentRecSeq,
                                 self.ScenarioNo,
                                 str(self.btn.option.currentText()), 
                                 self.qScenario.SubjectID,
                                 self.qScenario.Correction)
            
            self.stackPoints.to_csv(f"{self.PWD}/{self.Locale}/{str(self.qScenario.SubjectID).zfill(3)}/{str(self.btn.option.currentText())}/BT/{self.config.Angle}/{self.ScenarioNo}/{self.qScenario.currentRecSeq}/points_data.csv")
            self.qthreadrec.save_multiproc(self.q1, self.e_sk)

            while self.qthreadrec.is_recoding():
                time.sleep(2)

            t2 = time.time()

            self.qthreadrec.resetstate()

            print("time during saving images: {} sec.".format(t2 - t1))

            self.resetRecordInterface()

            self.btn.endtime.setText("F")

            print("Saving images done.")
        else:
            msgBox1 = QMessageBox()
            msgBox1.setText("No overwrite")
            msgBox1.exec()    

    def save(self):
        checkfile = f"{self.PWD}/bodytracking_data.csv"
        #print(checkfile)
        if not(os.path.isfile(checkfile)) :
            t1 = time.time()

            self.device.close()
            self.bodyTracker.destroy()

            self.stackPoints = pd.DataFrame(self.stackPoints)

            self.qthreadrec.setRun(False)

            self.qthreadrec.mkd(self.Locale, self.qScenario.SubjectID, self.ScenarioNo)

            print("Main Windows: is q1 empty?", self.q1.empty())
            print("Main Windows: is e_sk set?", self.e_sk.is_set())
            self.qthreadrec.save_multiproc(self.q1, self.e_sk)

            while self.qthreadrec.is_recoding():
                time.sleep(2)

            t2 = time.time()

            self.qthreadrec.resetstate()

            print("time during saving images: {} sec.".format(t2 - t1))

            self.resetRecordInterface()

            self.btn.endtime.setText("F")

            print("Saving images done.")    

            self.device = pykinect.start_device(device_index=self.btn.cameranum.currentIndex(), config=self.device_config)
            self.bodyTracker = pykinect.start_body_tracker()
            self.qthreadrec.reset(self.device, self.bodyTracker)
        else:
            msgBox1 = QMessageBox()
            msgBox1.setText("Check Score!")
            msgBox1.exec()    

    def setLayout(self):
        LayoutMain = QVBoxLayout(self) # with "self", it becomes MAIN layout
        LayoutMain.setAlignment(Qt.AlignTop)        
        LayoutMain.setAlignment(Qt.AlignLeft)    
        
        LayoutViewers = QHBoxLayout()
        # LayoutViewers.setAlignment(Qt.AlignTop)
        LayoutViewers.setAlignment(Qt.AlignLeft)
        
        LayoutViewers.addLayout(self.imgviwerRGB.getLayout(),1)
        LayoutViewers.addLayout(self.imgviwerSkeleton.getLayout(),1)
        #LayoutViewers.addLayout(self.imgviwerIRtest.getLayout(),1)
        #
        qlabel_confirm = QLabel()
        
        qlabel_confirm.setPixmap(load_image())
        
        #qlabel_confirm.set_layout()

        LayoutViewers.addLayout(get_layout(qlabel_confirm))
        LayoutViewers.addLayout(QVBoxLayout(),7)


        LayoutFunctions = QHBoxLayout()

        LayoutMain.addLayout(self.btn.getLayout(),1)
        LayoutMain.addLayout(LayoutViewers,39)
        LayoutMain.addLayout(LayoutFunctions,1)
        LayoutMain.addLayout(self.qScenario.getLayout(),49)

        self.qScenario.end.clicked.connect(self.end)
        self.qScenario.save.clicked.connect(self.save)
    # def update_panel(self,x,y):
    #     self.scatter1.set_offsets([[x,y]])
    #     self.scatter2.set_offsets([[x,y]])            
    #     # plt.draw()



    def resetRecordInterface(self):
        if self.qScenario.Ready.isChecked():
            self.qScenario.Ready.click()


    @pyqtSlot()
    def recordImages(self):
        self.year = str(datetime.today().year % 100).zfill(2)
        self.month = str(datetime.today().month).zfill(2)
        self.day = str(datetime.today().day).zfill(2)

        self.yymmdd = self.year + self.month + self.day

        self.Locale = "G1"#self.qScenario.locale_option.currentText()
        self.stackPoints = []
        if True:
            
            t0 = time.time()

            self.qthreadrec.init(self.PWD, 
                                 self.Locale,
                                 self.qScenario.SubjectID,
                                 self.btn
                                 )
            print("!!!!!!!!!! Qthread initialized")

            self.qthreadrec.start()

            self.qthreadrec.setRun(True)

            while self.qthreadrec.is_recoding():
                # print("recording")
                QApplication.processEvents()
            
            t1 = time.time()

            print("recording done. start to save images")
            print("time during recording: {} sec.".format(t1 - t0))

        else:
            msgBox1 = QMessageBox()
            msgBox1.setText("Check ID!")
            if self.qScenario.Ready.isChecked():
                self.qScenario.Ready.click()
            msgBox1.exec()    

    def checkRecordability(self):
        #timesync = self.qScenario.RECstartTime == self.btn.curtimeLabel.text()
        if self.qScenario.RECstartTime.split(':')[1] == self.btn.curtimeLabel.text().split(':')[1]:
            if (self.qScenario.RECstartTime.split(':')[2] == self.btn.curtimeLabel.text().split(':')[2]) or (int(self.qScenario.RECstartTime.split(':')[2]) + 1 == int(self.btn.curtimeLabel.text().split(':')[2])) or (int(self.qScenario.RECstartTime.split(':')[2]) + 2 == int(self.btn.curtimeLabel.text().split(':')[2])) :
                timesync = True
            else:
                timesync = False
        else:
            timesync = False

        ready = self.qScenario.Ready.isChecked()
        if timesync and ready:
            self.startRecord.emit()

    def showTime(self):
        currentTime = QTime.currentTime()
        displayTxt = currentTime.toString('hh:mm:ss')
        self.btn.curtimeLabel.setText(displayTxt)

    def initset(self):
        pass

    def optionChanged(self):
        print(self.btn.option.currentIndex())
        if self.btn.option.currentIndex() == 0:
            self.imgviwerIR.minval = self.config.cfg_30cm["ir_minval"]
            self.imgviwerIR.MinRangeInput.setText(str(self.imgviwerIR.minval))
            self.imgviwerIR.maxval = self.config.cfg_30cm["ir_maxval"]
            self.imgviwerIR.MaxRangeInput.setText(str(self.imgviwerIR.maxval))            

            self.imgviwerDepth.minval = self.config.cfg_30cm["depth_minval"]
            self.imgviwerDepth.MinRangeInput.setText(str(self.imgviwerDepth.minval))
            self.imgviwerDepth.maxval = self.config.cfg_30cm["depth_maxval"]
            self.imgviwerDepth.MaxRangeInput.setText(str(self.imgviwerDepth.maxval))
            
        elif self.btn.option.currentIndex() == 1:
            self.imgviwerIR.minval = self.config.cfg_50cm["ir_minval"]
            self.imgviwerIR.MinRangeInput.setText(str(self.imgviwerIR.minval))
            self.imgviwerIR.maxval = self.config.cfg_50cm["ir_maxval"]
            self.imgviwerIR.MaxRangeInput.setText(str(self.imgviwerIR.maxval))            

            self.imgviwerDepth.minval = self.config.cfg_50cm["depth_minval"]
            self.imgviwerDepth.MinRangeInput.setText(str(self.imgviwerDepth.minval))
            self.imgviwerDepth.maxval = self.config.cfg_50cm["depth_maxval"]
            self.imgviwerDepth.MaxRangeInput.setText(str(self.imgviwerDepth.maxval))        
        else:
            pass
            
    # add 
    def cameraChanged(self):
        self.device.close()
        self.bodyTracker.destroy()
        #self.qthreadrec.quit()
        print(self.btn.cameranum.currentIndex())
        #self.cameraindex = self.btn.cameranum.currentIndex()
        if ENABLE_PYK4A:
            # Modify camera configuration
            self.device_config = pykinect.default_configuration
            self.device_config.color_resolution = pykinect.K4A_COLOR_RESOLUTION_1080P
            self.device_config.depth_mode = pykinect.K4A_DEPTH_MODE_WFOV_2X2BINNED

                # Start cameras using modified configuration
            self.device = pykinect.start_device(device_index=self.btn.cameranum.currentIndex(), config=self.device_config)

            # Initialize the body tracker
            self.bodyTracker = pykinect.start_body_tracker()
        else:
            self.pyK4A = None
        self.qthreadrec = qThreadRecord(self.device, self.bodyTracker, self.btn.LbFPS, self.qScenario, self.PWD, self.btn.cameranum.currentIndex())
    # todo class and score
    @pyqtSlot()
    def updateScenarioNo(self):
        # self.ScenarioNo = self.qScenario.cBoxSSelect.currentIndex()
        # self.curScenario = self.config.scenario[self.ScenarioNo]
        # self.ScenarioNo = self.ScenarioNo + 1
        # self.qScenario.updaterecseq(self.curScenario)
        pass

    @pyqtSlot()        
    def updateOnPlay(self):    
        self.onPlay = not(self.onPlay)

    @pyqtSlot()    
    def calibration2(self):
        t0 = time.time()
        cnt = 0
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

            self.qScenario.updateSize()            
            QApplication.processEvents()

        i = 0
        while self.onPlay and not(ENABLE_PYK4A):
            print("displaying img")
        
            self.imgviwerRGB.setImgPath(f"{self.PWD}/images/transformed_color0-{i}.jpg")

            self.imgviwerRGB.start()
            i+=1
            if i>4: i=0
            t1 = time.time()
            self.btn.LbFPS.setText("{:.2f}FPS".format(1./(t1-t0)))
            t0 = t1            

            self.qScenario.updateSize()        
            QApplication.processEvents()

    def initplot(self):
        pass

    @pyqtSlot()        
    def displayKinect(self):    
        t0 = time.time()
        while self.onPlay and ENABLE_PYK4A:
            print("displaying ak")
            # Get capture
            capture = self.device.update()

            rat, c_image = capture.get_color_image()
            rat, i_image = capture.get_ir_image()
            rat, d_image = capture.get_depth_image()

            self.imgviwerRGB.setImg(c_image)

            self.imgviwerRGB.start()

            t1 = time.time()
            self.btn.LbFPS.setText("{:.2f}FPS".format(1./(t1-t0)))
            t0 = t1
        
            self.qScenario.updateSize()
            QApplication.processEvents()            

        i = 0
        while self.onPlay and not(ENABLE_PYK4A):
            # print("displaying img")
        
            self.imgviwerRGB.setImgPath(f"{self.PWD}/images/transformed_color0-{i}.jpg")

            self.imgviwerRGB.start()
            i+=1
            if i>4: i=0
            t1 = time.time()
            self.btn.LbFPS.setText("{:.2f}FPS".format(1./(t1-t0)))
            t0 = t1            

            self.qScenario.updateSize()        
            QApplication.processEvents()

    def closeEvent(self, event):
        msgbox     = QMessageBox()
        msgbox.setIcon(QMessageBox.Question)
        reply     = msgbox.question(self, "",
                                    "Are you sure to close window ?", 
                                    QMessageBox.No | QMessageBox.Yes , QMessageBox.Yes)
        if reply == QMessageBox.Yes:
            self.device.close()
            self.bodyTracker.destroy()
            #self.qthreadrec.quit()

            event.accept()
        else:
            event.ignore()
