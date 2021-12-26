from PyQt5.QtWidgets import *
from PyQt5.QtCore import * 
from PyQt5.QtGui import *
import os
from ..config import Config as setConfig
import subprocess

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
		#self.sizeInfo.setText(self.showSizeInfo())
		QApplication.processEvents()

	# fix 2021/12/22
	def onchanged(self, text):
		self.scorenum.setText(f'Score : {self.score_num.currentText()}')
		self.scenarionum.setText(f'Scenario : {self.class_num.currentText()}')

	def videoplay(self):

		try:
			p = subprocess.Popen(["/usr/bin/mpv", f"/home/etri_ai2/Desktop/video_box/{self.class_num.currentText()}_{self.score_num.currentText()}.mp4"])
		except:
			print("not find video...")

	def updateSize(self):
		# self.sizeInfo.setText(self.showSizeInfo())
		pass


	# def updateImgMemoryInfo(self):
	# 	self.imgMemoryInfoDisp = f"[RGB]:{self.rgbdispsize}MB"
	# 	self.imgMemoryInfoDisp += f"\n[IR]:{self.irdispsize}MB"
	# 	self.imgMemoryInfoDisp += f"\n[Depth]:{self.depthdispsize}MB"
		


	def showinfo(self):
		info 	 = f"                   <<< add result>>>\n"
		# info 	+= f"[ID] {self.SubjectID}\n"
		# #info 	+= f"[ID Correction] {self.Correction}\n"
		# #info 	+= f"[Record Time] {self.MinRecordTime} sec\n"
		# #info 	+= f"[Record Frame] {self.MinRecordFrame} frames\n"
		# info 	+= f"[Record Start Time] {self.RECstartTime}\n"
		return info

	# def updateImgMemoryInfoRec(self):
	# 	self.imgMemoryInfoRec  = "[RGB]:{:.2f}MB".format(self.imgRecSizes[0])
	# 	self.imgMemoryInfoRec += "\n[IR]:{:.2f}MB".format(self.imgRecSizes[1])
	# 	self.imgMemoryInfoRec += "\n[Depth]:{:.2f}MB".format(self.imgRecSizes[2])
	# 	self.imgMemoryInfoRec += "\n[Rec. Time]:{:.2f}sec".format(self.imgRecSizes[3])
	# 	self.imgMemoryInfoRec += "\n[Frames]:{:4d}".format(self.imgRecSizes[4])


	# def showSizeInfo(self):
	# 	self.updateImgMemoryInfo()
	# 	self.updateImgMemoryInfoRec()		
	# 	info 	 = f"<<< Img Info. >>>\n"
	# 	info    += self.imgMemoryInfoDisp
	# 	info 	+= f"\n\n<<< REC Info. >>>\n"
	# 	info    += self.imgMemoryInfoRec

	# 	return info


	def setRecordTime(self, t):
		self.MinRecordTime = t

	def setRecordFrame(self, f):
		self.MinRecordFrame = f

	def setCorrection(self):
		self.Correction = int(self.CorrectionInput.text())
		self.update()

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

		LayoutRT = QHBoxLayout() 
		LayoutRT.setAlignment(Qt.AlignTop)
		LayoutRT.setAlignment(Qt.AlignLeft)
		qLabelName = QLabel()
		qLabelName.setText("min Record Time [sec.]:")
		LayoutRT.addWidget(qLabelName)
		self.RecordTimeInput = QLineEdit()
		self.RecordTimeInput.setText(str(self.MinRecordTime))
		self.RecordTimeInput.setFixedSize(50,20)
		
		LayoutRT.addWidget(self.RecordTimeInput)

		LayoutRI = QHBoxLayout() 
		LayoutRI.setAlignment(Qt.AlignTop)
		LayoutRI.setAlignment(Qt.AlignLeft)
		qLabelName = QLabel()
		qLabelName.setText("min Record Frame [imgs]:")
		LayoutRI.addWidget(qLabelName)
		self.RecordFrameInput = QLineEdit()
		self.RecordFrameInput.setText(str(self.MinRecordFrame))
		self.RecordFrameInput.setFixedSize(50,20)
		LayoutRI.addWidget(self.RecordFrameInput)

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
		#HVlayoutMain.addLayout(LayoutRT, 10)
		#HVlayoutMain.addLayout(LayoutRI, 10)
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

		LayoutSave = QLabel()
		LayoutSave.setText("Save")
		font = QFont()
		font.setBold(True)
		font.setPointSize(15)
		LayoutSave.setFont(font)

		HVlayoutMain.addWidget(LayoutSave)

		# self.cBoxSSelect = QComboBox()
		# for i in range(0,14):
		# 	seq = recordconfig.scenario[i]
		# 	sname = f"[No.{i+1}] "
		# 	for s in seq:
		# 		sname += f"{s}-"
		# 	self.cBoxSSelect.addItem(sname[:-1])

		# fixed combobox
		classlabel = QLabel()
		classlabel.setText("class:")
		#LayoutViewers.addWidget(classlabel, alignment=Qt.AlignTop)

		self.class_num = QComboBox()
		[self.class_num.addItem(f"{i}") for i in range(1, 15)]
		self.class_num.activated[str].connect(self.onchanged)

		#LayoutViewers.addWidget(self.class_num, alignment=Qt.AlignTop)

		scorelabel = QLabel()
		scorelabel.setText("score:")
		#LayoutViewers.addWidget(scorelabel, alignment=Qt.AlignTop)

		self.score_num = QComboBox()
		[self.score_num.addItem(f"{i}") for i in range(5)]
		self.score_num.activated[str].connect(self.onchanged)

		#LayoutViewers.addWidget(self.score_num, alignment=Qt.AlignTop)		


		LayoutScenario = QVBoxLayout()
		LayoutScenario.setAlignment(Qt.AlignTop)
		qLabelName = QLabel()
		qLabelName.setText("Select Scenario")
		LayoutScenario.addWidget(qLabelName,1)
		
		# fix
		LayoutScenario.addWidget(self.class_num,1)
		LayoutScenario.addWidget(self.score_num,1)

		HVlayoutMain.addLayout(LayoutScenario, 2)

		LayoutScenarioNum = QHBoxLayout()
		LayoutScenarioNum.setAlignment(Qt.AlignTop)
		LayoutScenarioNum.setAlignment(Qt.AlignRight)

		# qLabelName = QLabel()
		# qLabelName.setText("Select Scenario Number")
		# LayoutScenario.addWidget(qLabelName,1)

		LayoutSV = QHBoxLayout() 
		LayoutSV.setAlignment(Qt.AlignTop)
		LayoutSV.setAlignment(Qt.AlignRight)

		# scenario update txt label /fix 2021/12/22
		self.scenarionum = QLabel()
		self.scenarionum.setText('Scenario : ')
		LayoutSV.addWidget(self.scenarionum)

		# score update txt label /fix 2021/12/22
		self.scorenum = QLabel()
		self.scorenum.setText(str('Score : '))
		LayoutSV.addWidget(self.scorenum)

		# # socre name label /fix 2021/12/22
		#self.scorenum = QLabel()
		# self.scorenum.setText(f'Score : ')
		# LayoutSV.addWidget(self.scorenum)
		# score update txt
		#self.scorenumv = QLabel()
		# self.scorenumv.setText('Scenario : ')
		# LayoutSV.addWidget(self.scorenumv)


		# self.overw = QPushButton()
		# self.overw.setCheckable(False)
		# self.overw.setText('OVERWRITE')
		# self.overw.setMinimumHeight(40)
		# LayoutSV.addWidget(self.overw)

		self.save = QPushButton()
		self.save.setCheckable(False)
		self.save.setText('SAVE')
		self.save.setMinimumHeight(40)
		LayoutSV.addWidget(self.save)

		HVlayoutMain.addLayout(LayoutScenarioNum,10)
		HVlayoutMain.addLayout(LayoutSV,10)

		# self.recordseqbtn0 = QPushButton(str(0))
		# self.recordseqbtn0.setMinimumHeight(40)
		# self.recordseqbtn1 = QPushButton(str(1))
		# self.recordseqbtn1.setMinimumHeight(40)
		# self.recordseqbtn2 = QPushButton(str(2))
		# self.recordseqbtn2.setMinimumHeight(40)
		# self.recordseqbtn3 = QPushButton(str(3))
		# self.recordseqbtn3.setMinimumHeight(40)

		self.videoplaybtn = QPushButton('Video Play')
		self.videoplaybtn.setMinimumHeight(40)
		
		# LayoutScenarioNum.addWidget(self.recordseqbtn0)
		# self.recordseqbtn0.clicked.connect(self.setcurrentRecordStep0)
		# LayoutScenarioNum.addWidget(self.recordseqbtn1)
		# self.recordseqbtn1.clicked.connect(self.setcurrentRecordStep1)
		# LayoutScenarioNum.addWidget(self.recordseqbtn2)
		# self.recordseqbtn2.clicked.connect(self.setcurrentRecordStep2)
		# LayoutScenarioNum.addWidget(self.recordseqbtn3)
		# self.recordseqbtn3.clicked.connect(self.setcurrentRecordStep3)

		LayoutScenarioNum.addWidget(self.videoplaybtn)
		self.videoplaybtn.clicked.connect(self.videoplay)
		
		qlabel_dummy = QLabel()
		HVlayoutMain.addWidget(qlabel_dummy, 90)
		
		HBlayoutMain.addLayout(HVlayoutMain,30)

		# Todo: add result 
		LayoutInfo = QVBoxLayout()

		self.viewInfo = QLabel()
		self.viewInfo.setAlignment(Qt.AlignLeft)
		self.viewInfo.setScaledContents(True)
		self.viewInfo.setText(self.showinfo())
		self.viewInfo.setMinimumHeight(30)


		# self.sizeInfo = QLabel()
		# self.sizeInfo.setAlignment(Qt.AlignLeft)
		# self.sizeInfo.setScaledContents(True)
		# self.sizeInfo.setText(self.showSizeInfo())
		# self.sizeInfo.setMinimumHeight(50)

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
		self.set10.clicked.connect(self.set10s)
		self.set20.clicked.connect(self.set20s)
		self.set30.clicked.connect(self.set30s)
		self.set40.clicked.connect(self.set40s)
		self.set50.clicked.connect(self.set50s)
		self.set00.clicked.connect(self.set00s)
		self.setN10.clicked.connect(self.setN10s)
		self.setN20.clicked.connect(self.setN20s)
		self.cnt.clicked.connect(self.qmain.pnt)
		
		# self.overw.clicked.connect(self.qmain.overwrite)
		# self.MaxRangeInput.returnPressed.connect(self.maxRangeChanged)

		return HBlayoutMain	
