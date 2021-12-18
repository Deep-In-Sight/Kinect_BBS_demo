from PyQt5.QtWidgets import *
from PyQt5.QtCore import * 
from PyQt5.QtGui import *
import os
from config import Config as setConfig

BTN_MIN_WIDTH 		= 100
BTN_MAX_WIDTH 		= 200
ICON_MIN_WIDTH 		= 30
ICON_MIN_HEIGHT 	= 32


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
	def __init__(self, qmain, pwd):
		super(qScenario, self).__init__(qmain)
		self.obj = ""
		self.PWD = pwd
		self.qmain = qmain	

		self.ScenarioNo = 0
		self.SubjectID = 0
		self.MinRecordTime = recordconfig.minRecordTime
		self.MinRecordFrame = recordconfig.minRecordFrame
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


	def setcurrentRecordStep0(self):
		self.currentRecSeq = 0
		self.scenarionumv.setText(str(self.cBoxSSelect.currentIndex()+1))
		self.scorenumv.setText(str(0))
	
	def setcurrentRecordStep1(self):
		self.currentRecSeq = 1
		self.scenarionumv.setText(str(self.cBoxSSelect.currentIndex()+1))
		self.scorenumv.setText(str(1))

	def setcurrentRecordStep2(self):
		self.currentRecSeq = 2
		self.scenarionumv.setText(str(self.cBoxSSelect.currentIndex()+1))
		self.scorenumv.setText(str(2))

	def setcurrentRecordStep3(self):
		self.currentRecSeq = 3
		self.scenarionumv.setText(str(self.cBoxSSelect.currentIndex()+1))
		self.scorenumv.setText(str(3))

	def setcurrentRecordStep4(self):
		self.currentRecSeq = 4
		self.scenarionumv.setText(str(self.cBoxSSelect.currentIndex()+1))
		self.scorenumv.setText(str(4))

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

	def setMinRecordFrame(self)	:
		try:
			self.MinRecordFrame = int(self.RecordFrameInput.text())
		except:
			self.RecordFrameInput.setText(str(self.MinRecordFrame))
		self.update()	

	def setRECstartTime(self):
		self.RECstartTime = self.RECstartTimeInput.text()
		self.update()	

	def reserve2min(self):
		currentTime = QTime.currentTime()
		curtime 	= currentTime.toString('hh:mm:ss')
		hh,mm,ss 	= map(int,curtime.split(":"))
		ss = 0
		mm += 2
		if mm == 60:
			mm = 0
			hh += 1
		if mm == 61:
			mm = 1
			hh += 1
		hh = ("00" + str(hh))[-2:]
		mm = ("00" + str(mm))[-2:]
		self.RECstartTime = f"{hh}:{mm}:00"
		self.update()
		self.RECstartTimeInput.setText(self.RECstartTime)
		if not self.Ready.isChecked():
			self.Ready.click()

	def reserve1min(self):
		currentTime = QTime.currentTime()
		curtime 	= currentTime.toString('hh:mm:ss')
		hh,mm,ss 	= map(int,curtime.split(":"))
		ss = 0
		mm += 1
		if mm > 59:
			mm = 0
			hh += 1
		hh = ("00" + str(hh))[-2:]
		mm = ("00" + str(mm))[-2:]
		self.RECstartTime = f"{hh}:{mm}:00"
		self.update()
		self.RECstartTimeInput.setText(self.RECstartTime)
		if not self.Ready.isChecked():
			self.Ready.click()

	def reserve30sec(self):
		currentTime = QTime.currentTime()
		curtime 	= currentTime.toString('hh:mm:ss')
		hh,mm,ss 	= map(int,curtime.split(":"))
		ss += 30
		if ss > 59:
			ss -= 60
			mm += 1
		
		if ss < 10:
			ss = 0
		elif ss < 40:
			ss = 30			
		else:
			ss = 0
			mm += 1

		if mm > 59:
			mm = 0
			hh += 1	
		

		hh = ("00" + str(hh))[-2:]
		mm = ("00" + str(mm))[-2:]
		ss = ("00" + str(ss))[-2:]
		self.RECstartTime = f"{hh}:{mm}:{ss}"
		self.update()
		self.RECstartTimeInput.setText(self.RECstartTime)
		if not self.Ready.isChecked():
			self.Ready.click()

	def set10s(self):
		currentTime = QTime.currentTime()
		curtime 	= currentTime.toString('hh:mm:ss')
		hh,mm,ss 	= map(int,curtime.split(":"))

		hh = ("00" + str(hh))[-2:]
		mm = ("00" + str(mm))[-2:]
		ss = ("00" + str(10))[-2:]

		self.RECstartTime = f"{hh}:{mm}:{ss}"
		self.qmain.st()
		self.update()
		self.RECstartTimeInput.setText(self.RECstartTime)
		if not self.Ready.isChecked():
			self.Ready.click()

	def set20s(self):
		currentTime = QTime.currentTime()
		curtime 	= currentTime.toString('hh:mm:ss')
		hh,mm,ss 	= map(int,curtime.split(":"))

		hh = ("00" + str(hh))[-2:]
		mm = ("00" + str(mm))[-2:]
		ss = ("00" + str(20))[-2:]

		self.RECstartTime = f"{hh}:{mm}:{ss}"
		self.qmain.st()
		self.update()
		self.RECstartTimeInput.setText(self.RECstartTime)
		if not self.Ready.isChecked():
			self.Ready.click()

	def set30s(self):
		currentTime = QTime.currentTime()
		curtime 	= currentTime.toString('hh:mm:ss')
		hh,mm,ss 	= map(int,curtime.split(":"))

		hh = ("00" + str(hh))[-2:]
		mm = ("00" + str(mm))[-2:]
		ss = ("00" + str(30))[-2:]

		self.RECstartTime = f"{hh}:{mm}:{ss}"
		self.qmain.st()
		self.update()
		self.RECstartTimeInput.setText(self.RECstartTime)
		if not self.Ready.isChecked():
			self.Ready.click()

	def set40s(self):
		currentTime = QTime.currentTime()
		curtime 	= currentTime.toString('hh:mm:ss')
		hh,mm,ss 	= map(int,curtime.split(":"))

		hh = ("00" + str(hh))[-2:]
		mm = ("00" + str(mm))[-2:]
		ss = ("00" + str(40))[-2:]

		self.RECstartTime = f"{hh}:{mm}:{ss}"
		self.qmain.st()
		self.update()
		self.RECstartTimeInput.setText(self.RECstartTime)
		if not self.Ready.isChecked():
			self.Ready.click()

	def set50s(self):
		currentTime = QTime.currentTime()
		curtime 	= currentTime.toString('hh:mm:ss')
		hh,mm,ss 	= map(int,curtime.split(":"))

		hh = ("00" + str(hh))[-2:]
		mm = ("00" + str(mm))[-2:]
		ss = ("00" + str(50))[-2:]

		self.RECstartTime = f"{hh}:{mm}:{ss}"
		self.qmain.st()
		self.update()
		self.RECstartTimeInput.setText(self.RECstartTime)
		if not self.Ready.isChecked():
			self.Ready.click()

	def set00s(self):
		currentTime = QTime.currentTime()
		curtime 	= currentTime.toString('hh:mm:ss')
		hh,mm,ss 	= map(int,curtime.split(":"))

		hh = ("00" + str(hh))[-2:]
		mm = ("00" + str(mm+1))[-2:]
		ss = ("00" + str(00))[-2:]

		self.RECstartTime = f"{hh}:{mm}:{ss}"
		self.qmain.st()
		self.update()
		self.RECstartTimeInput.setText(self.RECstartTime)
		if not self.Ready.isChecked():
			self.Ready.click()

	def setN10s(self):
		currentTime = QTime.currentTime()
		curtime 	= currentTime.toString('hh:mm:ss')
		hh,mm,ss 	= map(int,curtime.split(":"))

		hh = ("00" + str(hh))[-2:]
		mm = ("00" + str(mm+1))[-2:]
		ss = ("00" + str(10))[-2:]

		self.RECstartTime = f"{hh}:{mm}:{ss}"
		self.qmain.st()
		self.update()
		self.RECstartTimeInput.setText(self.RECstartTime)
		if not self.Ready.isChecked():
			self.Ready.click()

	def setN20s(self):
		currentTime = QTime.currentTime()
		curtime 	= currentTime.toString('hh:mm:ss')
		hh,mm,ss 	= map(int,curtime.split(":"))

		hh = ("00" + str(hh))[-2:]
		mm = ("00" + str(mm+1))[-2:]
		ss = ("00" + str(20))[-2:]

		self.RECstartTime = f"{hh}:{mm}:{ss}"
		self.qmain.st()
		self.update()
		self.RECstartTimeInput.setText(self.RECstartTime)
		if not self.Ready.isChecked():
			self.Ready.click()

	def endreset(self):
		self.RECEndTimeInput.setText(str(0))

	def fendset10(self):
		settime = self.RECEndTimeInput.text()
		settime = int(settime) + 10
		self.RECEndTimeInput.setText(str(settime))

	def fendset30(self):
		settime = self.RECEndTimeInput.text()
		settime = int(settime) + 30
		self.RECEndTimeInput.setText(str(settime))

	def fendset1m(self):
		settime = self.RECEndTimeInput.text()
		settime = int(settime) + 60
		self.RECEndTimeInput.setText(str(settime))

	def update(self):
		self.viewInfo.setText(self.showinfo())
		self.sizeInfo.setText(self.showSizeInfo())
		QApplication.processEvents()


	def updateSize(self):
		self.sizeInfo.setText(self.showSizeInfo())


	def updateImgMemoryInfo(self):
		self.imgMemoryInfoDisp = f"[RGB]:{self.rgbdispsize}MB"
		self.imgMemoryInfoDisp += f"\n[IR]:{self.irdispsize}MB"
		self.imgMemoryInfoDisp += f"\n[Depth]:{self.depthdispsize}MB"
		


	def showinfo(self):
		info 	 = f"<<< Scenario Setup >>>\n"
		info 	+= f"[ID] {self.SubjectID}\n"
		#info 	+= f"[ID Correction] {self.Correction}\n"
		#info 	+= f"[Record Time] {self.MinRecordTime} sec\n"
		#info 	+= f"[Record Frame] {self.MinRecordFrame} frames\n"
		info 	+= f"[Record Start Time] {self.RECstartTime}\n"
		return info

	def updateImgMemoryInfoRec(self):
		self.imgMemoryInfoRec  = "[RGB]:{:.2f}MB".format(self.imgRecSizes[0])
		self.imgMemoryInfoRec += "\n[IR]:{:.2f}MB".format(self.imgRecSizes[1])
		self.imgMemoryInfoRec += "\n[Depth]:{:.2f}MB".format(self.imgRecSizes[2])
		self.imgMemoryInfoRec += "\n[Rec. Time]:{:.2f}sec".format(self.imgRecSizes[3])
		self.imgMemoryInfoRec += "\n[Frames]:{:4d}".format(self.imgRecSizes[4])


	def showSizeInfo(self):
		self.updateImgMemoryInfo()
		self.updateImgMemoryInfoRec()		
		info 	 = f"<<< Img Info. >>>\n"
		info    += self.imgMemoryInfoDisp
		info 	+= f"\n\n<<< REC Info. >>>\n"
		info    += self.imgMemoryInfoRec

		return info


	def setRecordTime(self, t):
		self.MinRecordTime = t

	def setRecordFrame(self, f):
		self.MinRecordFrame = f

	def setCorrection(self):
		self.Correction = int(self.CorrectionInput.text())
		self.update()

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

		LayoutSRST = QHBoxLayout() 
		LayoutSRST.setAlignment(Qt.AlignTop)
		LayoutSRST.setAlignment(Qt.AlignRight)

		self.set10 = QPushButton()
		self.set10.setCheckable(False)
		self.set10.setText('10s')
		self.set10.setMinimumHeight(40)
		LayoutSRST.addWidget(self.set10)

		self.set20 = QPushButton()
		self.set20.setCheckable(False)
		self.set20.setText('20s')
		self.set20.setMinimumHeight(40)
		LayoutSRST.addWidget(self.set20)

		self.set30 = QPushButton()
		self.set30.setCheckable(False)
		self.set30.setText('30s')
		self.set30.setMinimumHeight(40)
		LayoutSRST.addWidget(self.set30)

		self.set40 = QPushButton()
		self.set40.setCheckable(False)
		self.set40.setText('40s')
		self.set40.setMinimumHeight(40)
		LayoutSRST.addWidget(self.set40)

		self.set50 = QPushButton()
		self.set50.setCheckable(False)
		self.set50.setText('50s')
		self.set50.setMinimumHeight(40)
		LayoutSRST.addWidget(self.set50)

		self.set00 = QPushButton()
		self.set00.setCheckable(False)
		self.set00.setText('1m00s')
		self.set00.setMinimumHeight(40)
		LayoutSRST.addWidget(self.set00)

		self.setN10 = QPushButton()
		self.setN10.setCheckable(False)
		self.setN10.setText('1m10s')
		self.setN10.setMinimumHeight(40)
		LayoutSRST.addWidget(self.setN10)

		self.setN20 = QPushButton()
		self.setN20.setCheckable(False)
		self.setN20.setText('1m20s')
		self.setN20.setMinimumHeight(40)
		LayoutSRST.addWidget(self.setN20)

		HVlayoutMain.addWidget(LayoutRecordStart, 10)
		HVlayoutMain.addLayout(LayoutLocale, 10)
		HVlayoutMain.addLayout(LayoutID, 10)
		HVlayoutMain.addLayout(LayoutRST, 10)
		HVlayoutMain.addLayout(LayoutSRST, 10)

		LayoutRecordStartStep = QHBoxLayout() 
		LayoutRecordStartStep.setAlignment(Qt.AlignTop)
		LayoutRecordStartStep.setAlignment(Qt.AlignRight)

		self.Ready = QPushButton()
		self.Ready.setCheckable(True)
		self.Ready.setText('I\'m Ready')
		self.Ready.setMinimumWidth(100)
		self.Ready.setMinimumHeight(50)
		self.Ready.setIcon(QIcon(os.path.join(self.PWD,'res','icon.png')))

		LayoutRecordStartStep.addWidget(self.Ready)

		HVlayoutMain.addLayout(LayoutRecordStartStep, 40)

		LayoutRecordEnd = QLabel()
		LayoutRecordEnd.setText("Record END")
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


		self.end = QPushButton()
		self.end.setCheckable(False)
		self.end.setText('END')
		self.end.setMinimumHeight(40)
		LayoutSE.addWidget(self.end)

		HVlayoutMain.addWidget(LayoutRecordEnd, 10)
		HVlayoutMain.addLayout(LayoutSE, 10)

		LayoutSave = QLabel()
		LayoutSave.setText("Save")
		font = QFont()
		font.setBold(True)
		font.setPointSize(15)
		LayoutSave.setFont(font)

		HVlayoutMain.addWidget(LayoutSave)

		LayoutSV = QHBoxLayout() 
		LayoutSV.setAlignment(Qt.AlignTop)
		LayoutSV.setAlignment(Qt.AlignRight)

		self.save = QPushButton()
		self.save.setCheckable(False)
		self.save.setText('SAVE')
		self.save.setMinimumHeight(40)
		LayoutSV.addWidget(self.save)

		HVlayoutMain.addLayout(LayoutSV,10)

		qlabel_dummy = QLabel()
		HVlayoutMain.addWidget(qlabel_dummy, 90)
		
		HBlayoutMain.addLayout(HVlayoutMain,30)

		LayoutInfo = QVBoxLayout()

		self.viewInfo = QLabel()
		self.viewInfo.setAlignment(Qt.AlignLeft)
		self.viewInfo.setScaledContents(True)
		self.viewInfo.setText(self.showinfo())
		self.viewInfo.setMinimumHeight(30)


		self.sizeInfo = QLabel()
		self.sizeInfo.setAlignment(Qt.AlignLeft)
		self.sizeInfo.setScaledContents(True)
		self.sizeInfo.setText(self.showSizeInfo())
		self.sizeInfo.setMinimumHeight(50)

		LayoutInfo.addWidget(self.viewInfo,10)
		LayoutInfo.addWidget(self.sizeInfo,20)	
		HBlayoutMain.addLayout(LayoutInfo,20)	

		self.SubjectIDInput.returnPressed.connect(self.setSubjectID)
		self.RECstartTimeInput.returnPressed.connect(self.setRECstartTime)
		self.set10.clicked.connect(self.set10s)
		self.set20.clicked.connect(self.set20s)
		self.set30.clicked.connect(self.set30s)
		self.set40.clicked.connect(self.set40s)
		self.set50.clicked.connect(self.set50s)
		self.set00.clicked.connect(self.set00s)
		self.setN10.clicked.connect(self.setN10s)
		self.setN20.clicked.connect(self.setN20s)

		return HBlayoutMain	
