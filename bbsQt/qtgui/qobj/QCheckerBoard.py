import numpy as np 
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from qobj.QThreadObj import qThreadBlinkv2
from PyQt5.QtWidgets import *
from PyQt5.QtCore import * 
from PyQt5.QtGui import *
from PyQt5.QtPrintSupport import *
from config import Config as setConfig
from PIL import Image

recordconfig = setConfig()


class MplCanvas(FigureCanvas):
	def __init__(self, parent=None, width=5, height=5, dpi=100):
		self.n_alpha = 20
		self.increasing_alpha = True
		self.alpha = np.arange(self.n_alpha) / (self.n_alpha-1) * 0.8
		self.tgtsize = (np.arange(self.n_alpha) / (self.n_alpha-1) * 500).astype(np.int)
		self.init()
		self.qthblink = qThreadBlinkv2(parent = self)
		super(MplCanvas, self).__init__(self.fig)

	# def update(self, x,y):
		# pass

	def update_panel(self,x,y):
		self.scatter1.set_offsets([[x,y]])
		# self.scatter2.set_offsets([[x,y]])			
		# plt.draw()		

	def blink_moving_tgt(self, tgtpos, n_blink = 3, n_move = 30):
		x, y = self.scatter1.get_offsets()[0]

		if self.n_alpha * n_blink < n_move:
			n_move = self.n_alpha * n_blink

		dx = (tgtpos[0] - x) / n_move
		dy = (tgtpos[1] - y) / n_move

		for i in range(self.n_alpha * n_blink):
			n = i % self.n_alpha
			if i < n_move:
				x += dx
				y += dy
				self.update_panel(x,y)
			self.scatter1.set_alpha(self.alpha[n])
			self.scatter1.set_sizes([self.tgtsize[n]])
			self.draw()		
			self.flush_events()

	def init(self):
		self.fig , self.ax = plt.subplots(figsize = (5,5), num="DISPLAY")
		# plt.figure()
		# plt.ion()
		left 	= 0.0
		bottom 	= 0.0
		width 	= 1.
		height 	= 1.

		
		self.plot	= self.fig.add_axes([left, bottom, width, height])
		self.plot.set_xlim(0, 1)
		self.plot.set_ylim(0, 1)

	

		self.scatter1 = self.plot.scatter([0.5],[0.5], s=[500], c="r", alpha=1, marker="o")
		# self.scatter2 = self.plot.scatter([0.5],[0.5], s=[100], c="k", alpha=1, marker="x")

		self.pathplots = [ self.plot.plot(
							[np.random.uniform(),np.random.uniform()], 
							[np.random.uniform(),np.random.uniform()], 
							"r--", alpha = 0) for _ in range(9) ]

		self.startendtxt = [self.plot.text(0.5,0.5,"start", color = "r", fontsize = 13, alpha = 0), 
							self.plot.text(0.5,0.5,"end"  , color = "r", fontsize = 13, alpha = 0)]
		# self.arrowplot = self.plot.add_patch(None)

		



class CheckerBoardWindow(QWidget):
	def __init__(self):
		super().__init__()
		layout = QVBoxLayout()
		layout.setContentsMargins(0,0,0,0)
		self.canvas = MplCanvas(self, width=5, height=5, dpi=100)
		layout.addWidget(self.canvas)
		self.setLayout(layout)

		

