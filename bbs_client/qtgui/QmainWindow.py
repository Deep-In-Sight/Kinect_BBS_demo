import numpy as np
import os
import cv2
import time

from bbs_client.constants import CAM_LIST, VERBOSE
from PyQt5.QtWidgets import (QWidget, QMessageBox, QApplication, 
                            QPushButton, QHBoxLayout, QVBoxLayout, QLabel,
                            )
from PyQt5.QtCore import QTime, Qt, pyqtSlot, QSize, pyqtSignal, QTimer
from PyQt5.QtGui import QPixmap, QIcon, QImage
from PyQt5.QtPrintSupport import *

from .config import Config as setConfig
from .QButtons import qButtons
from .QImgViewer import PhotoViewer
from .QScenario import qScenario
from .QThreadObj import qThreadRecord

import mediapipe as mp
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils 
mp_drawing_styles = mp.solutions.drawing_styles

from bbs_client.model import kinect_utils as ku 
from bbs_client.model import rec_utils as ru
from bbs_client.constants import NFRAMES

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
    VBlayoutMain.name = "VBlayoutMain"
    return VBlayoutMain


def load_image(fn_img = "imgs/instruct_1.png"):
    img = cv2.imread(fn_img)
    img = cv2.resize(img, (640, 480))
    img = img[:,:,::-1]
    img = np.array(img).astype(np.uint8)
    height, width, channel = img.shape
    bytesPerLine = 3 * width
    pixmap   = QPixmap(QImage(img, width, height, bytesPerLine, QImage.Format_RGB888))
    return pixmap


def is_valid_skeleton(skeleton):
    return np.all(skeleton['frame'] != 0)


class QMyMainWindow(QWidget):
    startRecord = pyqtSignal()
    stopRecord = pyqtSignal()
    def __init__(self, q_sk, e_sk):
        """
        q_sk = mp.queue to put skeleton 
        e_sk = mp.event to signal skeleton is ready
        """
        super(QMyMainWindow, self).__init__()

        self.onPlay = False
        self.ScenarioNo = 1
        
        self.q_sk = q_sk
        self.e_sk = e_sk

        # add 2021/12/23 
        self.PWD = os.getcwd()
        self.btn = qButtons(self, self.PWD)

        self.imgviwerRGB = PhotoViewer(self,"RGB")

        self.startRecord.connect(self.recordImages)
        self.stopRecord.connect(self.end)
        self.qScenario = qScenario(self, self.PWD, self.btn, self.startRecord, self.stopRecord, q_sk)

        self.config = setConfig() # to be added

        self.curScenario = self.config.scenario[self.ScenarioNo]

        self.setGeometry(100, 100, 1200, 900)
        self.setMinimumSize(900, 600)
        self.setMaximumSize(1920, 1080)
        self.setWindowTitle('Kinect BBS demo')

        # fix 2021/01/07
        self.camera_choice = CAM_LIST    

        self._init_camera()
        self.setLayout()

        self.stackColor = []
        # self.stackPoints = []

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.showTime)
        self.timer.start(1000)

        self.imgviwerRGB.emitDispImgSize.connect(self.qScenario.setRgbDispSize)

        ############################
        LayoutFallPred = QVBoxLayout(self) # with "self", it becomes MAIN layout
        LayoutFallPred.setAlignment(Qt.AlignTop)
        LayoutFallPred.setAlignment(Qt.AlignLeft)

    def end(self):
        """Stop recording and save the video and skeleton"""
        #self.btn.endtime.setText("T")
        checkfile = f"{self.PWD}/bodytracking_data.csv"
        print("[[[END]]]")

        if not(os.path.isfile(checkfile)):
            print("checkfile", checkfile)
            t1 = time.time()

            self.qthreadrec.setRun(False)

            # self.qthreadrec.mkd(self.ScenarioNo)

            # skimage 를 뽑고 이걸 skimage label 넣는다. 
            skimage = self.qthreadrec.save_multiproc()
            print("skimage", skimage)
            if isinstance(skimage, int) and skimage == -1:
                #cameraidx = self.btn.cameranum.currentIndex()
                self.startcamera()
            else:    
                # self.skimageLabel.setPixmap(skimage)

                # recording 하는 동안 sleep으로 기다리기? 음.. 
                while self.qthreadrec.is_recoding():
                    time.sleep(2)

                t2 = time.time()

                self.qthreadrec.resetstate()

                if VERBOSE: 
                    print(f"[QMainWindow.end]time during saving images: {t2 - t1:.2f} sec.")

                self.resetRecordInterface()
                #self.btn.endtime.setText("F")

                if VERBOSE: 
                    print("[QMainWindow.end]Saving done")

                # Reset device
                self.qthreadrec.reset(self.device, self.bodyTracker)
                
                self.qthreadrec.select_sk()
        
    def setLayout(self):
        LayoutMain = QVBoxLayout(self) # with "self", it becomes MAIN layout
        LayoutMain.setAlignment(Qt.AlignTop)        
        LayoutMain.setAlignment(Qt.AlignLeft)    
        
        LayoutViewers = QHBoxLayout()
        LayoutViewers.setAlignment(Qt.AlignLeft)
        
        LayoutViewers.addLayout(self.imgviwerRGB.getLayout(),1)
        #LayoutViewers.addLayout(self.imgviwerSkeleton.getLayout(),1)
        
        # self.skimageLabel = QLabel()
        # self.skimageLabel.setFixedSize(640, 480)
        # self.skimageLabel.setPixmap(load_image())

        # add 2021.12.27 skindexbtn
        self.skindexbtn0 = QPushButton()
        self.skindexbtn0.setCheckable(False)
        self.skindexbtn0.setText('Encrypt')
        self.skindexbtn0.setMinimumHeight(40)
        
        # add 2021.12.27 skbtnlayout
        #skBBoxLayout = QVBoxLayout()
        #testLayout = QVBoxLayout()

        # sk select viewr
        # LayoutViewers.addLayout(get_layout(self.skimageLabel))
        
        # skBBoxLayout.addWidget(self.skindexbtn0)
        # skBBoxLayout.addWidget(self.fileopenButton)
        # skBBoxLayout.addWidget(self.skindexbtn1)
        # skBBoxLayout.addWidget(self.skindexbtn2)
        #LayoutViewers.addLayout(skBBoxLayout)
        #LayoutViewers.addLayout(testLayout)

        LayoutViewers.addLayout(QVBoxLayout(),7) # 이건 뭐지? 모양 맞추기용?

        LayoutFunctions = QHBoxLayout()

        LayoutMain.addLayout(self.btn.getLayout(),1)
        LayoutMain.addLayout(LayoutViewers,39)
        LayoutMain.addLayout(LayoutFunctions,3)
        LayoutMain.addLayout(self.qScenario.getLayout(),49)

        self.Ready = QPushButton()
        self.Ready.setCheckable(True)
        self.Ready.setText('Record')
        self.Ready.setStyleSheet("background-color: green")
        self.Ready.setMinimumWidth(100)
        self.Ready.setMinimumHeight(50)
        # TODO: Record start 대신 Decrypt 기능 
        self.Ready.clicked.connect(self.start_rec)

        #LayoutRecordStartStep.addWidget(self.Ready)

        self.encryptbtn = QPushButton('Encrypt')
        self.encryptbtn.setStyleSheet("background-color: green")
        self.encryptbtn.setMinimumHeight(40)
        self.encryptbtn.setMinimumWidth(140)
        #LayoutRecordStartStep.addWidget(self.encryptbtn)
        self.encryptbtn.clicked.connect(self.qScenario.encrypt)

        self.decryptbtn = QPushButton('Decrypt')
        self.decryptbtn.setStyleSheet("background-color: green")
        self.decryptbtn.setMinimumHeight(40)
        self.decryptbtn.setMinimumWidth(140)
        #LayoutRecordStartStep.addWidget(self.decryptbtn)
        self.decryptbtn.clicked.connect(self.qScenario.decrypt)


        LayoutFunctions.addWidget(self.Ready)
        LayoutFunctions.addWidget(self.encryptbtn)
        LayoutFunctions.addWidget(self.decryptbtn)

        # # add 2021.12.27  skindexbox connect 
        # self.skindexbtn0.clicked.connect(lambda: self.qthreadrec.select_sk(0))

    def resetRecordInterface(self):
        if self.Ready.isChecked():
            self.Ready.click()

    def start_rec(self, state):
        if state:
            self.Ready.setStyleSheet("background-color: red")
            self.Ready.setText("Stop")
            self.startRecord.emit()
            
        else:
            self.Ready.setStyleSheet("background-color: green")
            self.Ready.setText("Record")
            self.stopRecord.emit()  

    @pyqtSlot()
    def recordImages(self):
        self.qthreadrec.init(self.PWD, 
                                self.btn,
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

    # add 20210107
    def actionChanged(self):
        if VERBOSE: print("action changed", self.btn.action_num.currentIndex())
        actionidx = self.btn.action_num.currentIndex() + 1
        
        self.qScenario.scenarionum.setText(f'Scenario : {actionidx}')
        # self.skimageLabel.setPixmap(load_image(f"imgs/instruct_{actionidx}.png"))
        # self.startcamera()

    def scoreChanged(self, text):
        self.qScenario.scorenum.setText(f'Score : {text}')

    def _init_camera(self):
        # Start cameras using modified configuration
        self.device = cv2.VideoCapture(0)

        # Initialize the body tracker
        self.bodyTracker = mp_pose.Pose(
                                min_detection_confidence=0.5,
                                min_tracking_confidence=0.5)

        self.qthreadrec = qThreadRecord(self.device, self.bodyTracker, self.qScenario, 
                                    self.PWD, self.imgviwerRGB, self.q_sk, self.e_sk)

    # add 20210107
    def startcamera(self):
        # try: 
        #     # self.skindexbtn0.clicked.disconnect() 
        
        self._init_camera()
        # self.skindexbtn0.clicked.connect(lambda: self.qthreadrec.select_sk(0))
 
    @pyqtSlot()        
    def updateOnPlay(self):    
        self.onPlay = not(self.onPlay)

    @pyqtSlot()    
    def calibration2(self):
        """connected to calibration button"""
        t0 = time.time()
        while self.onPlay:
            # Get capture
            success, image = self.device.read()
            if not success:
                break
            
            # Get body tracker frame
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            joint = self.bodyTracker.process(image)

            # Draw landmarks
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            mp_drawing.draw_landmarks(
                    image,
                    joint.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS,
                    landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())

            self.imgviwerRGB.setImg(cv2.flip(image, 1))

            self.imgviwerRGB.start()

            t1 = time.time()
            self.btn.LbFPS.setText("{:.2f}FPS".format(1./(t1-t0)))
            t0 = t1

            #self.qScenario.updateSize()            
            QApplication.processEvents()

    def closeEvent(self, event):
        msgbox     = QMessageBox()
        msgbox.setIcon(QMessageBox.Question)
        reply     = msgbox.question(self, "",
                                    "Are you sure to close window ?", 
                                    QMessageBox.No | QMessageBox.Yes , QMessageBox.Yes)
        if reply == QMessageBox.Yes:
            self.device.release()
            #self.bodyTracker.destroy()

            event.accept()
        else:
            event.ignore()

            """No selection needed anymore. MP finds only one skeleton"""
            #pickle.dump(self.stackJoint, open(f"{self.path_bt}/bodytracking_data.pickle", "wb"))
            
            if VERBOSE: print(f'[Qthread obj] skeleton index : {skindex}')
            
            # Safety check
            if not hasattr(self, 'skarr'):
                print("[QThreadObj.select_sk] No skeleton list")
                return 
            if not is_valid_skeleton(self.skarr):
                print("[QThreadObj.select_sk] Invalid skeleton")
                return 
            
            # FIX   20210107
            this_scenario = self.btn.action_num.currentText()
            # this_score = self.btn.score_num.currentText()
            
            sub = ru.smoothed_frame_N(self.skarr, 
                                    nframe=NFRAMES[f'{this_scenario}'],
                                    shift=1)
            skeleton = ru.ravel_rec(sub)[np.newaxis, :]

            camera_num = 'e'

            #tm = time.localtime()
            #time_mark = f"{tm.tm_mon:02d}{tm.tm_mday:02d}{tm.tm_hour:02d}{tm.tm_min:02d}{tm.tm_sec:02d}"
            #sav_dir = f"BT/"
            #if not os.path.isdir(sav_dir): os.mkdir(sav_dir)
            #pickle.dump(self.skarr, open(sav_dir+"f{camera_num}_{time_mark}_{this_scenario}_{this_score}_skeleton.pickle", "wb"))
            
            self.q_sk.put({"action":this_scenario,
                        "cam":camera_num, 
                        "skeleton": skeleton})
            print("[QtThreadObj] Skeleton sent to encryptor")
            self.e_sk.set()
            print("[QtThreadObj] Waiting for Evaluator's response...")