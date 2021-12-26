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


class qRecord(QObject):
	def __init__(self, qmain, pwd):
		super(qRecord, self).__init__(qmain)
		self.qmain = qmain

	# def 

