import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtCore import * 
from PyQt5.QtGui import *
from PyQt5.QtPrintSupport import *
#from PIL import ImageQt, Image
from . import image as imgutil
import cv2


def getNewEllpItem(x,y):
	ellp 	= QGraphicsEllipseItem()
	pen 	= QPen(Qt.cyan, 0.1)
	ellp.setPen(pen)
	ellp.setRect(x-2, y-2, 4, 4)
	return ellp
	

def getNewTextItem(x,y, txt = "Hi"):
	text 	= QGraphicsTextItem(txt)
	text.setDefaultTextColor(Qt.cyan)
	text.setPos(x, y-6)
	f = QFont()
	f.setPointSize(10)
	text.setFont(f)
	return text



class PhotoViewer(QGraphicsView, QThread):
	# emitMouseOnPhoto 	= pyqtSignal(QPoint)
	# emitClassLabelPos  	= pyqtSignal(list)
	emitDispImgSize	= pyqtSignal(int)

	def __init__(self, parent, name):
		super(PhotoViewer, self).__init__(parent)
		self.parent = parent
		self.name = name
		self.ENABLE_PYK4A = False
		if "RGB" in self.name:
			self.WIDTH = 320
			self.HEIGHT = 240
		else:
			self.WIDTH = 240
			self.HEIGHT = 240			
		self._zoom = 0
		self._empty = True
		self.depth_at_center = 0
		self._scene = QGraphicsScene(self)
		self._photo = QGraphicsPixmapItem()
		self._scene.addItem(self._photo)
		self.setScene(self._scene)
		self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
		self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
		self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.setBackgroundBrush(QBrush(QColor(30, 30, 30)))
		self.setFrameShape(QFrame.NoFrame)
		self.setFixedSize(self.WIDTH, self.HEIGHT)

		if "Depth" in self.name:
			ellp = getNewEllpItem(self.WIDTH//2, self.HEIGHT//2)
			self.depthtext = getNewTextItem(self.WIDTH//2, self.HEIGHT//2)
			self._scene.addItem(ellp)
			self._scene.addItem(self.depthtext)



		if "IR" in self.name:
			self.minval = 0
			self.maxval = 4095
		elif "Depth" in self.name:
			self.minval = 0
			self.maxval = 2048
		else:
			self.minval = 0
			self.maxval = 256		

		self.onPlay = False	

	def hasPhoto(self):
		return not self._empty

	def setPhoto(self, pixmap=None):
		self._zoom = 0
		if pixmap and not pixmap.isNull():
			self._empty 	= False
			self._photo.setPixmap(pixmap)
		else:
			self.painter 	= None
			self._empty 	= True
			self._photo.setPixmap(QPixmap())
		self.fitInView()	

	def fitInView(self, scale=True):
		rect = QRectF(self._photo.pixmap().rect())
		if not rect.isNull():
			self.setSceneRect(rect)
			if self.hasPhoto():
				unity = self.transform().mapRect(QRectF(0, 0, 1, 1))
				self.scale(1 / unity.width(), 1 / unity.height())
				viewrect = self.viewport().rect()
				scenerect = self.transform().mapRect(rect)
				factor = min(viewrect.width() / scenerect.width(), 
							 viewrect.height() / scenerect.height())
				self.scale(factor, factor)
			self._zoom = 0		

	def setImgPath(self, path):
		self.imgPath = path

	def setImg(self, img):
		self.img = img

	def start(self):
		# if not(self.onPlay): return
		#if self.ENABLE_PYK4A:
		if True:
			
			img = cv2.resize(self.img, (self.WIDTH,self.HEIGHT))
			if img.ndim == 2: img = np.expand_dims(img, axis=-1)
			if "RGB" in self.name:
				img = img.astype(np.uint8)[...,2::-1]
			self.update(img)

		else:
			print("SELF.name", self.name)
			if "RGB" == self.name:
				img = cv2.resize(cv2.imread(self.imgPath), (self.WIDTH,self.HEIGHT))
				img = img[:,:,::-1]
			else:
				img = cv2.imread(self.imgPath)
				img = imgutil.rgb2gray(img)
				if "Depth" in self.name: 
					h, w, _ = img.shape
					self._scene.removeItem(self.depthtext)
					self.depth_at_center = img[h//2, w//2, 0]
					self.depthtext = getNewTextItem(self.WIDTH//2, self.HEIGHT//2, f"{self.depth_at_center}mm")
					self._scene.addItem(self.depthtext)
				img = cv2.resize(img, (self.WIDTH,self.HEIGHT))					
				img = imgutil.gray_rescale(img,self.minval, self.maxval)				
			self.update(img)
			# self.flush_events()
		self.emitDispImgSize.emit(img.nbytes // 1024**2)

	def update(self, img):
		img = np.array(img).astype(np.uint8)
		height, width, channel = img.shape
		bytesPerLine = 3 * width
		pixmap   = QPixmap(QImage(img, width, height, bytesPerLine, QImage.Format_RGB888))
		self.setPhoto(pixmap)
	
	def loadimg(self, path):
		pixmap = QPixmap(path)
		self.setPhoto(pixmap)


	def minRangeChanged(self):
		try: self.minval = int(self.MinRangeInput.text())
		except: self.MinRangeInput.setText(str(self.minval))

	def maxRangeChanged(self):
		try: self.maxval = int(self.MaxRangeInput.text())
		except: self.MaxRangeInput.setText(str(self.maxval))


	def getLayout(self):
		QLabelImgView 		= QLabel()
		QLabelImgView.setAlignment(Qt.AlignBottom)
		QLabelImgView.setAlignment(Qt.AlignCenter)
		QLabelImgView.setText(self.name)

		HBlayout = QHBoxLayout()
		if not "RGB" in self.name:
			self.MinRangeInput = QLineEdit()
			self.MinRangeInput.setText(str(self.minval))
			self.MinRangeInput.setFixedSize(50,20)

			self.MaxRangeInput = QLineEdit()
			self.MaxRangeInput.setText(str(self.maxval))
			self.MaxRangeInput.setFixedSize(50,20)
			self.MinRangeInput.returnPressed.connect(self.minRangeChanged)
			self.MaxRangeInput.returnPressed.connect(self.maxRangeChanged)

			HBlayout.addWidget(self.MinRangeInput)
			HBlayout.addWidget(self.MaxRangeInput)
		else:
			qlabel = QLabel()
			qlabel.setFixedSize(50, 20)
			HBlayout.addWidget(qlabel)
			
		VBlayoutMain = QVBoxLayout()
		VBlayoutMain.setAlignment(Qt.AlignTop)
		VBlayoutMain.setAlignment(Qt.AlignLeft)
		VBlayoutMain.addWidget(QLabelImgView)
		VBlayoutMain.addWidget(self)
		VBlayoutMain.addLayout(HBlayout)
		return VBlayoutMain		


