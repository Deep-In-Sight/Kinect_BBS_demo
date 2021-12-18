from PyQt5.QtWidgets import *
from PyQt5.QtCore import * 
from PyQt5.QtGui import *
import os


BTN_MIN_WIDTH 		= 100
BTN_MAX_WIDTH 		= 200
ICON_MIN_WIDTH 		= 30
ICON_MIN_HEIGHT 	= 32

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

		self.BtnFoo = QPushButton()
		self.BtnFoo.setCheckable(True)
		self.BtnFoo.setIcon(QIcon(os.path.join(self.PWD,'res','magnifying_glass.png')))
		self.BtnFoo.setText('[F]oo')
		self.BtnFoo.setMinimumWidth(ICON_MIN_WIDTH)
		self.BtnFoo.setMinimumHeight(ICON_MIN_HEIGHT)
		self.BtnFoo.setToolTip('Foo')

		self.BtnPlay = QPushButton()
		self.BtnPlay.setCheckable(True)
		self.BtnPlay.setIcon(QIcon(os.path.join(self.PWD,'res','play.png')))
		self.BtnPlay.setText('[P]lay')
		self.BtnPlay.setMinimumWidth(ICON_MIN_WIDTH)
		self.BtnPlay.setMinimumHeight(ICON_MIN_HEIGHT)
		self.BtnPlay.setToolTip('Play Azure Kinect')		

		self.BtnCalib = QPushButton()
		self.BtnCalib.setCheckable(True)
		self.BtnCalib.setIcon(QIcon(os.path.join(self.PWD,'res','play.png')))
		self.BtnCalib.setText('[C]alibrate')
		self.BtnCalib.setMinimumWidth(ICON_MIN_WIDTH)
		self.BtnCalib.setMinimumHeight(ICON_MIN_HEIGHT)
		self.BtnCalib.setToolTip('Play Azure Kinect & Run Calibration')

		self.temp = QLabel()
		self.temp.setText('	')

		self.capturetimeal = QLabel()
		self.capturetimeal.setText('capture time : ')

		self.capturetime = QLabel()
		self.capturetime.setText('0')

		self.endtimeal = QLabel()
		self.endtimeal.setText('end check(T/F) : ')

		self.endtime = QLabel()
		self.endtime.setText('F')


		self.BtnPathOnOff = QPushButton()
		self.BtnPathOnOff.setCheckable(True)
		self.BtnPathOnOff.setIcon(QIcon(os.path.join(self.PWD,'res','line.png')))
		self.BtnPathOnOff.setText('Pat[H] On/Off')
		self.BtnPathOnOff.setMinimumWidth(ICON_MIN_WIDTH)
		self.BtnPathOnOff.setMinimumHeight(ICON_MIN_HEIGHT)
		self.BtnPathOnOff.setToolTip('')



		self.LbFPS = QLabel()
		self.LbFPS.setMinimumWidth(70)


		self.option = QComboBox()
		self.option.addItem("BBS")

		self.option.currentIndexChanged.connect(self.qmain.optionChanged)

		self.BtnCalib.clicked.connect(self.qmain.updateOnPlay)
		self.BtnCalib.clicked.connect(self.qmain.calibration2)

		self.BtnPlay.clicked.connect(self.qmain.updateOnPlay)
		self.BtnPlay.clicked.connect(self.qmain.displayKinect)

	# @pyqtSlot()	
	# def updateBtnPlay(self):
	# 	self.BtnPlay.setChecked(not(self.BtnPlay.isChecked()))



	def getLayout(self):
		HBlayoutEdits = QHBoxLayout() 
		HBlayoutEdits.setAlignment(Qt.AlignLeft)

		HBlayoutEdits.addWidget(self.curtimeLabel)
		HBlayoutEdits.addWidget(self.BtnCalib)
		HBlayoutEdits.addWidget(self.LbFPS)
		HBlayoutEdits.addWidget(self.option)
		HBlayoutEdits.addWidget(self.temp)
		HBlayoutEdits.addWidget(self.capturetimeal)
		HBlayoutEdits.addWidget(self.capturetime)
		HBlayoutEdits.addWidget(self.temp)
		HBlayoutEdits.addWidget(self.endtimeal)
		HBlayoutEdits.addWidget(self.endtime)
		
		return HBlayoutEdits