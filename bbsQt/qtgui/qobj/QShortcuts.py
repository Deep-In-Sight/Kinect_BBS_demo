from PyQt5.QtWidgets import *
from PyQt5.QtCore import * 
from PyQt5.QtGui import *

def createActions(self):



	playShortcut 		= QShortcut(QKeySequence("p"), self)
	playShortcut.activated.connect(self.btn.BtnPlay.click)
	

	calibShortcut 		= QShortcut(QKeySequence("c"), self)
	calibShortcut.activated.connect(self.btn.BtnCalib.click)	

	# openShortcut 		= QShortcut(QKeySequence("Ctrl+o"), self)
	# openShortcut.activated.connect(self._loadImage) 
	
	# saveShortcut 		= QShortcut(QKeySequence("Ctrl+s"), self)
	# saveShortcut.activated.connect(self._saveData) 

	# zoominShortcut  	= QShortcut(QKeySequence("Ctrl+="), self)
	# zoominShortcut.activated.connect(self.imgviewer.zoomIn) 

	# zoomoutShortcut  	= QShortcut(QKeySequence("Ctrl+-"), self)
	# zoomoutShortcut.activated.connect(self.imgviewer.zoomOut) 

	# fitinShortcut  		= QShortcut(QKeySequence("Ctrl+0"), self)
	# fitinShortcut.activated.connect(self.imgviewer.fitInView) 		

	# cursorShortcut  	= QShortcut(QKeySequence("i"), self)
	# cursorShortcut.activated.connect(self.switchInspectionMode) 	

	# DragShortcut  	= QShortcut(QKeySequence("d"), self)
	# DragShortcut.activated.connect(self.switchDragLabelMode) 		

	# fillLabelOnePixelShortcut  	= QShortcut(QKeySequence("p"), self)
	# fillLabelOnePixelShortcut.activated.connect(self.switchLabelPosMode) 

	# resetShorcut 		= QShortcut(QKeySequence("Ctrl+r"), self)
	# resetShorcut.activated.connect(self.resetImage)

	# closeShortcut  		= QShortcut(QKeySequence("Ctrl+w"), self)
	# closeShortcut.activated.connect(self.Cancel)
