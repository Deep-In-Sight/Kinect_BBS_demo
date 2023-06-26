from PyQt5.QtWidgets import QApplication, QPushButton, QHBoxLayout, QVBoxLayout, QComboBox, QLabel, QLineEdit
from PyQt5.QtCore import QTime, QObject, Qt, pyqtSlot
from PyQt5.QtGui import QFont, QIcon
import os
import os.path
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
    def __init__(self, qmain, pwd, q_answer, btn, startRecord, stopRecord):
        super(qScenario, self).__init__(qmain)
        self.startRecord = startRecord
        self.stopRecord = stopRecord
        self.obj = ""
        self.PWD = pwd
        self.qmain = qmain    
        self.btn = btn    

        self.text_answer = ""
        self.q_answer = q_answer

        self.ScenarioNo = 0
        #self.SubjectID = 0
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

    def endreset(self):
        self.RECEndTimeInput.setText(str(0))

    def update(self):
        QApplication.processEvents()

    # fix 2021/01/07
    def onchanged(self, text):
        self.scorenum.setText(f'Score : {text}')
        #self.scenarionum.setText(f'Scenario : {text}')

    # def download(self):
        
    
    def videoplay(self):
        # fix 2021/01/07
        video_name = glob(DIR_VIDEO+f"?{self.btn.action_num.currentIndex()+1}_{self.btn.score_num.currentText()}_*.mp4")[0]
        video_abs_path = os.path.join( os.getcwd(), video_name )

        try:
            p = subprocess.Popen([BIN_PLAYER, video_abs_path])
        except:
            print("ERROR: cannot find video...", video_abs_path)

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
        
    @pyqtSlot(bool)
    def start_rec(self, state):
        if state:
            self.Ready.setStyleSheet("background-color: red")
            self.Ready.setText("Stop")
            self.startRecord.emit()
            
        else:
            self.Ready.setStyleSheet("background-color: green")
            self.Ready.setText("Start")
            self.stopRecord.emit()            


    def getLayout(self):
        HBlayoutMain = QHBoxLayout() 
        HBlayoutMain.setAlignment(Qt.AlignTop)

        HVlayoutMain = QVBoxLayout() 
        HVlayoutMain.setAlignment(Qt.AlignTop)

        # LayoutRecordStart = QLabel()
        # LayoutRecordStart.setText("Record START")
        # font = QFont()
        # font.setBold(True)
        # font.setPointSize(15)
        # LayoutRecordStart.setFont(font)

        LayoutRecordStartStep = QHBoxLayout() 
        LayoutRecordStartStep.setAlignment(Qt.AlignTop)
        LayoutRecordStartStep.setAlignment(Qt.AlignRight)

        self.videoplaybtn = QPushButton('Video Play')
        self.videoplaybtn.setMinimumHeight(40)
        self.videoplaybtn.setMinimumWidth(140)
        LayoutRecordStartStep.addWidget(self.videoplaybtn)
        self.videoplaybtn.clicked.connect(self.videoplay)

        # self.downloadbtn = QPushButton('Download')
        # self.downloadbtn.setMinimumHeight(40)
        # self.downloadbtn.setMinimumWidth(140)
        # LayoutRecordStartStep.addWidget(self.downloadbtn)
        # self.downloadbtn.clicked.connect(self.videoplay)

        self.Ready = QPushButton()
        self.Ready.setCheckable(True)
        self.Ready.setText('Start')
        self.Ready.setStyleSheet("background-color: green")
        self.Ready.setMinimumWidth(100)
        self.Ready.setMinimumHeight(50)
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

        HVlayoutMain.addWidget(LayoutRecordEnd, 10)
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
        self.viewInfo.setAlignment(Qt.AlignTop)
        self.viewInfo.setScaledContents(True)
        self.viewInfo.setText(self.showinfo())
        self.viewInfo.setMinimumHeight(30)

        # result label
        LayoutInfo.addWidget(self.viewInfo,10)
        
        # result label
        HBlayoutMain.addLayout(LayoutInfo,20)    

        # self.SubjectIDInput.returnPressed.connect(self.setSubjectID)

        return HBlayoutMain    
