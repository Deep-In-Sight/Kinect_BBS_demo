from PyQt5.QtWidgets import QApplication, QPushButton, QHBoxLayout, QVBoxLayout, QComboBox, QLabel, QLineEdit
from PyQt5.QtCore import QTime, QObject, Qt, pyqtSlot
from PyQt5.QtGui import QFont, QIcon
import os
from ..config import Config as setConfig
import subprocess
from bbsQt.constants import DIR_VIDEO, BIN_PLAYER
from glob import glob

BTN_MIN_WIDTH         = 100
BTN_MAX_WIDTH         = 200
ICON_MIN_WIDTH         = 30
ICON_MIN_HEIGHT     = 32

recordconfig = setConfig()

def getPushButtonRecord(name, width = 30, height = 40, iconpath = None):
    btn = QPushButton()
    btn.setCheckable(True)
    btn.setText(name)
    btn.setMinimumWidth(width)
    btn.setMinimumHeight(height)
    if iconpath is not None:
        btn.setIcon(QIcon(iconpath))
    return btn

class qScenario(QObject):
    def __init__(self, qmain, pwd, q_answer, btn, startRecord):
        super(qScenario, self).__init__(qmain)
        self.startRecord = startRecord
        self.obj = ""
        self.PWD = pwd
        self.qmain = qmain    
        self.btn = btn    

        self.text_answer = ""
        self.q_answer = q_answer

        self.ScenarioNo = 0
        self.SubjectID = 0
        self.MinRecordTime = recordconfig.minRecordTime # Minimum 2s
        self.MinRecordFrame = recordconfig.minRecordFrame # Minimum 20 frames
        self.info = ""
        self.imgMemoryInfoDisp = ""
        self.imgMemoryInfoToSave = ""
        self.imgMemoryInfoRec = ""
        self.rgbdispsize = 0
        self.irdispsize = 0
        self.depthdispsize = 0
        self.Correction = 0
        
        self.RECstartTime = QTime.currentTime().toString('hh:mm:ss')

        self.recordseq = recordconfig.scenario[0]
        self.currentRecSeq = 0
        self.currentRecCheck = False
        self.imgRecSizes = [0,0,0,0,0] # color, ir, depth, rec time, num frames

    def updateRecImgSizes(self, imgsizes):
        self.imgRecSizes[0] += imgsizes[0]
        self.imgRecSizes[1] += imgsizes[1]        
        self.imgRecSizes[2] += imgsizes[2]
        self.imgRecSizes[3] += imgsizes[3]
        self.imgRecSizes[4] += 1

    def updaterecseq(self, seq):
        self.recordseq = seq


    @pyqtSlot(int)
    def setRgbDispSize(self,val):
        self.rgbdispsize = val

    @pyqtSlot(int)
    def setIrDispSize(self,val):
        self.irdispsize = val

    @pyqtSlot(int)
    def setDepthDispSize(self,val):
        self.depthdispsize = val            


    def setSubjectID(self):
        try:
            self.SubjectID = int(self.SubjectIDInput.text())
        except:
            self.SubjectIDInput.setText(str(self.SubjectID))
        self.update()

    def setMinRecordTime(self):
        try:
            self.MinRecordTime = int(self.RecordTimeInput.text())
        except:
            self.RecordTimeInput.setText(str(self.MinRecordTime))
        self.update()    

    def setMinRecordFrame(self):
        try:
            self.MinRecordFrame = int(self.RecordFrameInput.text())
        except:
            self.RecordFrameInput.setText(str(self.MinRecordFrame))
        self.update()    

    def setRECstartTime(self):
        self.RECstartTime = self.RECstartTimeInput.text()
        self.update()    

    def set_countdown(self, seconds):
        currentTime = QTime.currentTime()
        curtime     = currentTime.toString('hh:mm:ss')
        hh,mm,ss     = map(int,curtime.split(":"))
        if ss > seconds:
            curtime     = currentTime.addSecs(60).toString('hh:mm:ss')
            hh,mm,ss     = map(int,curtime.split(":"))
        
        hh = ("00" + str(hh))[-2:]
        mm = ("00" + str(mm))[-2:]
        ss = ("00" + str(seconds))[-2:]

        self.RECstartTime = f"{hh}:{mm}:{ss}"
        self.qmain.st()
        self.update()
        self.RECstartTimeInput.setText(self.RECstartTime)
        if not self.Ready.isChecked():
            self.Ready.click()

    def endreset(self):
        self.RECEndTimeInput.setText(str(0))

    def update(self):
        #self.viewInfo.setText(self.showinfo())
        #self.sizeInfo.setText(self.showSizeInfo())
        QApplication.processEvents()

    # fix 2021/01/07
    def onchanged(self, text):
        self.scorenum.setText(f'Score : {text}')
        #self.scenarionum.setText(f'Scenario : {text}')

    def videoplay(self):
        # fix 2021/01/07
        video_name = glob(DIR_VIDEO+f"?{self.btn.action_num.currentIndex()+1}_{self.btn.score_num.currentText()}_*.mp4")[0]

        try:
            p = subprocess.Popen([BIN_PLAYER, video_name])
        except:
            print("cannot find video...")

    #def updateSize(self):
    #    # self.sizeInfo.setText(self.showSizeInfo())
    #    pass


    def showinfo(self):
        #{self.text_answer} 
        info      = f" <<< Waiting for prediction... >>>\n"
        return info

    def setRecordTime(self, t):
        self.MinRecordTime = t

    def setRecordFrame(self, f):
        self.MinRecordFrame = f

    def setCorrection(self):
        self.Correction = int(self.CorrectionInput.text())
        self.update()

    def add_timer_button(self, seconds):
        timer = QPushButton()
        timer.setCheckable(False)
        timer.setText(f'{seconds:02d}s')
        timer.setMinimumHeight(40)
        return timer
        
    def start_rec(self):
        self.startRecord.emit()

    def getLayout(self):
        HBlayoutMain = QHBoxLayout() 
        HBlayoutMain.setAlignment(Qt.AlignTop)

        HVlayoutMain = QVBoxLayout() 
        HVlayoutMain.setAlignment(Qt.AlignTop)

        LayoutRecordStart = QLabel()
        LayoutRecordStart.setText("Record START")
        font = QFont()
        font.setBold(True)
        font.setPointSize(15)
        LayoutRecordStart.setFont(font)


        LayoutLocale = QHBoxLayout() 
        qLocaleName = QLabel()
        qLocaleName.setText("Locale:")
        LayoutLocale.addWidget(qLocaleName, alignment=Qt.AlignLeft)
        self.locale_option = QComboBox()
        self.locale_option.addItem("G1")

        LayoutLocale.addWidget(self.locale_option, alignment=Qt.AlignRight)

        LayoutID = QHBoxLayout() 
        LayoutID.setAlignment(Qt.AlignTop)
        LayoutID.setAlignment(Qt.AlignLeft)
        qLabelName = QLabel()
        qLabelName.setText("ID:")
        LayoutID.addWidget(qLabelName)
        self.SubjectIDInput = QLineEdit()
        self.SubjectIDInput.setText(str(self.SubjectID))
        self.SubjectIDInput.setFixedSize(50,20)
        
        LayoutID.addWidget(self.SubjectIDInput)

        # LayoutRT = QHBoxLayout() 
        # LayoutRT.setAlignment(Qt.AlignTop)
        # LayoutRT.setAlignment(Qt.AlignLeft)
        # qLabelName = QLabel()
        # qLabelName.setText("min Record Time [sec.]:")
        # LayoutRT.addWidget(qLabelName)
        self.RecordTimeInput = QLineEdit()
        self.RecordTimeInput.setText(str(self.MinRecordTime))
        self.RecordTimeInput.setFixedSize(50,20)
        
        # LayoutRT.addWidget(self.RecordTimeInput)

        # LayoutRI = QHBoxLayout() 
        # LayoutRI.setAlignment(Qt.AlignTop)
        # LayoutRI.setAlignment(Qt.AlignLeft)
        # qLabelName = QLabel()
        # qLabelName.setText("min Record Frame [imgs]:")
        # LayoutRI.addWidget(qLabelName)
        self.RecordFrameInput = QLineEdit()
        self.RecordFrameInput.setText(str(self.MinRecordFrame))
        self.RecordFrameInput.setFixedSize(50,20)
        # LayoutRI.addWidget(self.RecordFrameInput)

        LayoutRST = QHBoxLayout() 
        LayoutRST.setAlignment(Qt.AlignTop)
        LayoutRST.setAlignment(Qt.AlignLeft)
        qLabelName = QLabel()
        qLabelName.setText("Record Starting Time [HH:MM:SS]:")
        LayoutRST.addWidget(qLabelName)

        self.RECstartTimeInput = QLineEdit()
        self.RECstartTimeInput.setText(str(self.RECstartTime))
        self.RECstartTimeInput.setFixedSize(80,20)        
        LayoutRST.addWidget(self.RECstartTimeInput)

        # LayoutSRST = QHBoxLayout() 
        # LayoutSRST.setAlignment(Qt.AlignTop)
        # LayoutSRST.setAlignment(Qt.AlignRight)

        # self.timers = [self.add_timer_button(tt) for tt in [0,10,20,30,40,50]]
        # for timer in self.timers:
        #     LayoutSRST.addWidget(timer)

        HVlayoutMain.addWidget(LayoutRecordStart, 10)
        HVlayoutMain.addLayout(LayoutLocale, 10)
        HVlayoutMain.addLayout(LayoutID, 10)
        HVlayoutMain.addLayout(LayoutRST, 10)
        #HVlayoutMain.addLayout(LayoutSRST, 10)

        LayoutRecordStartStep = QHBoxLayout() 
        LayoutRecordStartStep.setAlignment(Qt.AlignTop)
        LayoutRecordStartStep.setAlignment(Qt.AlignRight)

        self.videoplaybtn = QPushButton('Video Play')
        self.videoplaybtn.setMinimumHeight(40)
        self.videoplaybtn.setMinimumWidth(140)
        LayoutRecordStartStep.addWidget(self.videoplaybtn)
        self.videoplaybtn.clicked.connect(self.videoplay)

        self.Ready = QPushButton()
        self.Ready.setCheckable(True)
        self.Ready.setText('I\'m Ready')
        self.Ready.setMinimumWidth(100)
        self.Ready.setMinimumHeight(50)
        self.Ready.setIcon(QIcon(os.path.join(self.PWD,'res','icon.png')))
        self.Ready.clicked.connect(self.start_rec)

        LayoutRecordStartStep.addWidget(self.Ready)

        HVlayoutMain.addLayout(LayoutRecordStartStep, 40)


        ###############################
        LayoutRecordEnd = QLabel()
        LayoutRecordEnd.setText("SAVE")
        font = QFont()
        font.setBold(True)
        font.setPointSize(15)
        LayoutRecordEnd.setFont(font)

        LayoutRET = QHBoxLayout() 
        LayoutRET.setAlignment(Qt.AlignTop)
        LayoutRET.setAlignment(Qt.AlignLeft)
        qLabelName = QLabel()
        qLabelName.setText("Record End Time [HH:MM:SS]:")
        LayoutRET.addWidget(qLabelName)

        LayoutSE = QHBoxLayout() 
        LayoutSE.setAlignment(Qt.AlignTop)
        LayoutSE.setAlignment(Qt.AlignRight)

        self.cnt = QPushButton()
        self.cnt.setCheckable(False)
        self.cnt.setText('Print CNT')
        self.cnt.setMinimumHeight(40)
        LayoutSE.addWidget(self.cnt)

        self.end = QPushButton()
        self.end.setCheckable(False)
        self.end.setText('END')
        self.end.setMinimumHeight(40)
        LayoutSE.addWidget(self.end)

        HVlayoutMain.addWidget(LayoutRecordEnd, 10)
        HVlayoutMain.addLayout(LayoutSE, 10)
        ###############################

        LayoutScenarioNum = QHBoxLayout()
        LayoutScenarioNum.setAlignment(Qt.AlignTop)
        LayoutScenarioNum.setAlignment(Qt.AlignRight)

        # scenario update txt label /fix 2021/12/22
        self.scenarionum = QLabel()
        self.scenarionum.setText(f'Scenario : {self.btn.action_num.currentIndex() + 1}')
        LayoutScenarioNum.addWidget(self.scenarionum)

        # score update txt label /fix 2021/12/22
        self.scorenum = QLabel()
        self.scorenum.setText(f'Score : {self.btn.score_num.currentIndex()}')
        LayoutScenarioNum.addWidget(self.scorenum)
        HVlayoutMain.addLayout(LayoutScenarioNum, 2)


        qlabel_dummy = QLabel()
        HVlayoutMain.addWidget(qlabel_dummy, 10)
        HBlayoutMain.addLayout(HVlayoutMain, 30)

        # Todo: add result 
        LayoutInfo = QVBoxLayout()
        self.viewInfo = QLabel()
        self.viewInfo.setAlignment(Qt.AlignCenter)
        self.viewInfo.setScaledContents(True)
        self.viewInfo.setText(self.showinfo())
        self.viewInfo.setMinimumHeight(30)

        # result label
        LayoutInfo.addWidget(self.viewInfo,10)
        # LayoutInfo.addWidget(self.sizeInfo,20)    
        
        # result label
        HBlayoutMain.addLayout(LayoutInfo,20)    

        #self.class_num.currentIndexChanged.connect(self.qmain.updateScenarioNo)
        self.SubjectIDInput.returnPressed.connect(self.setSubjectID)
        self.RecordTimeInput.returnPressed.connect(self.setMinRecordTime)
        self.RecordFrameInput.returnPressed.connect(self.setMinRecordFrame)
        self.RECstartTimeInput.returnPressed.connect(self.setRECstartTime)

        # self.timers[0].clicked.connect(lambda: self.set_countdown(0))
        # self.timers[1].clicked.connect(lambda: self.set_countdown(10))
        # self.timers[2].clicked.connect(lambda: self.set_countdown(20))
        # self.timers[3].clicked.connect(lambda: self.set_countdown(30))
        # self.timers[4].clicked.connect(lambda: self.set_countdown(40))
        # self.timers[5].clicked.connect(lambda: self.set_countdown(50))
        self.cnt.clicked.connect(self.qmain.pnt)
        
        # self.MaxRangeInput.returnPressed.connect(self.maxRangeChanged)

        return HBlayoutMain    


    # def updateImgMemoryInfo(self):
    #     self.imgMemoryInfoDisp = f"[RGB]:{self.rgbdispsize}MB"
    #     self.imgMemoryInfoDisp += f"\n[IR]:{self.irdispsize}MB"
    #     self.imgMemoryInfoDisp += f"\n[Depth]:{self.depthdispsize}MB"

    # def updateImgMemoryInfoRec(self):
    #     self.imgMemoryInfoRec  = "[RGB]:{:.2f}MB".format(self.imgRecSizes[0])
    #     self.imgMemoryInfoRec += "\n[IR]:{:.2f}MB".format(self.imgRecSizes[1])
    #     self.imgMemoryInfoRec += "\n[Depth]:{:.2f}MB".format(self.imgRecSizes[2])
    #     self.imgMemoryInfoRec += "\n[Rec. Time]:{:.2f}sec".format(self.imgRecSizes[3])
    #     self.imgMemoryInfoRec += "\n[Frames]:{:4d}".format(self.imgRecSizes[4])


    # def showSizeInfo(self):
    #     self.updateImgMemoryInfo()
    #     self.updateImgMemoryInfoRec()        
    #     info      = f"<<< Img Info. >>>\n"
    #     info    += self.imgMemoryInfoDisp
    #     info     += f"\n\n<<< REC Info. >>>\n"
    #     info    += self.imgMemoryInfoRec

    #     return info
