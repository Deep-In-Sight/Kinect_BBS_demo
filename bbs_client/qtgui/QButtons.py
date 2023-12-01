from PyQt5.QtWidgets import (QPushButton, QHBoxLayout, QLabel, QComboBox, QFileDialog)
from PyQt5.QtCore import Qt, QObject
from PyQt5.QtGui import QIcon, QFont
import os


BTN_MIN_WIDTH         = 100
BTN_MAX_WIDTH         = 200
ICON_MIN_WIDTH         = 30
ICON_MIN_HEIGHT     = 32

class qButtons(QObject):
    def __init__(self, qmain, pwd):
        super(qButtons).__init__()    
        self.obj = ""
        self.PWD = pwd
        self.qmain = qmain
        self.init()

    def init(self):

        self.curtimeLabel = QLabel()
        self.curtimeLabel.setMinimumWidth(70)
        self.curtimeLabel.setText("")
        self.curtimeLabel.setFont(QFont("Arial", 12, QFont.Bold))

        self.BtnCalib = QPushButton()
        self.BtnCalib.setCheckable(True)
        self.BtnCalib.setIcon(QIcon(os.path.join(self.PWD,'res','play.png')))
        self.BtnCalib.setText('[R]ecord')
        self.BtnCalib.setMinimumWidth(ICON_MIN_WIDTH)
        self.BtnCalib.setMinimumHeight(ICON_MIN_HEIGHT)
        self.BtnCalib.setToolTip('Record New Video')
        
        self.fileopenButton = QPushButton()
        self.fileopenButton.setText("Load video")
        self.fileopenButton.clicked.connect(self.openFileNameDialog)
        
        self.empty_space = QLabel()
        self.empty_space.setText('    ')

        self.capturetimeal = QLabel()
        self.capturetimeal.setText('capture time : ')
        self.capturetimeal.setFont(QFont("Arial", 10, QFont.Bold))

        self.capturetime = QLabel()
        self.capturetime.setText('0')
        self.capturetime.setFont(QFont("Arial", 10, QFont.Bold))

        self.endtimeal = QLabel()
        self.endtimeal.setText('end check(T/F) : ')
        self.endtimeal.setFont(QFont("Arial", 12, QFont.Bold))

        self.endtime = QLabel()
        self.endtime.setText('F')
        self.endtime.setFont(QFont("Arial", 12, QFont.Bold))

        self.LbFPS = QLabel()
        self.LbFPS.setMinimumWidth(70)

        self.action_name = QLabel()
        self.action_name.setText('Scenario : ')
        self.action_name.setFont(QFont("Arial", 12, QFont.Bold))
        
        self.action_num = QComboBox()
        [self.action_num.addItem(f"{i}") for i in range(1, 15)]
        self.action_num.currentIndexChanged.connect(self.qmain.actionChanged)

        # self.score_name = QLabel()
        # self.score_name.setText('Select Scenario Score : ')
        # self.score_name.setFont(QFont("Arial", 12, QFont.Bold))
        
        # self.score_num = QComboBox()
        # [self.score_num.addItem(f"{i}") for i in range(5)]
        # self.score_num.activated[str].connect(self.qmain.scoreChanged)

        self.BtnCalib.clicked.connect(self.qmain.updateOnPlay)
        self.BtnCalib.clicked.connect(self.qmain.calibration2)
        
    
    def openFileNameDialog(self):
        # Open file dialog and get the selected file path
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*);;Text Files (*.txt)", options=options)
        if fileName:
            # Read the file and set its content to the text edit
            with open(fileName, 'r') as file:
                self.textEdit.setText(file.read())


    def getLayout(self):
        HBlayoutEdits = QHBoxLayout() 
        HBlayoutEdits.setAlignment(Qt.AlignLeft)

        HBlayoutEdits.addWidget(self.curtimeLabel)
        HBlayoutEdits.addWidget(self.fileopenButton)
        HBlayoutEdits.addWidget(self.BtnCalib)
        HBlayoutEdits.addWidget(self.LbFPS)
        # fix 2021/12/23
        HBlayoutEdits.addWidget(self.action_name)
        HBlayoutEdits.addWidget(self.action_num)
        # HBlayoutEdits.addWidget(self.score_name)
        # HBlayoutEdits.addWidget(self.score_num)
        HBlayoutEdits.addWidget(self.empty_space)
        HBlayoutEdits.addWidget(self.empty_space)
        HBlayoutEdits.addWidget(self.capturetimeal)
        HBlayoutEdits.addWidget(self.capturetime)
        HBlayoutEdits.addWidget(self.empty_space)

        return HBlayoutEdits