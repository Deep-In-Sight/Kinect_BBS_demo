from glob import glob
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QImage, QPixmap, QPalette, QPainter
#from PyQt5.QtPrintSupport import QPrintDialog, QPrinter
from PyQt5.QtWidgets import QLabel, QSizePolicy, QScrollArea, QMessageBox, QMainWindow, QMenu, QAction, qApp, QFileDialog
import os
import qimage2ndarray
import cv2

class QImageViewer(QMainWindow):
    def __init__(self, class_name):
        super().__init__()
        #action = 8
        self.image_dir = f"/home/hoseung/Work/data/BBS/whoismain/e_main_list/{class_name}/" ####
        self.image_list = glob(self.image_dir+"*.jpg")
        self.image_list.sort()
        self.image_list = self.image_list[:1] + self.image_list
        #print(self.image_list)

        #self.printer = QPrinter()
        self.scaleFactor = 1.0

        self.imageLabel = QLabel()
        self.imageLabel.setBackgroundRole(QPalette.Base)
        self.imageLabel.setScaledContents(True)

        self.scrollArea = QScrollArea()
        self.scrollArea.setBackgroundRole(QPalette.Dark)
        self.scrollArea.setWidget(self.imageLabel)
        self.scrollArea.setVisible(False)

        self.setCentralWidget(self.scrollArea)

        self.createActions()
        self.createMenus()

        #Mouse
#         self.setMouseTracking(True)

        self.fout = open(self.image_dir+f"main_list_{class_name}.txt", "w") ##############

        self.setWindowTitle("Image Viewer")
        self.resize(1280, 720)
        
        #self.next_image()
        self.cnt = 0

    def open(self):
        options = QFileDialog.Options()
        dir_root = str(QFileDialog.getExistingDirectory(self, "Select Directory" ))
        #print(dir_root)
        image_list = os.listdir(dir_root)
        image_list.sort()
        #print(image_list)
        #print(dir_root)
        fileName = os.path.join(dir_root, image_list[0])
        if fileName:
            image = QImage(fileName)
            if image.isNull():
                QMessageBox.information(self, "Image Viewer", "Cannot load %s." % fileName)
                return

            self.imageLabel.setPixmap(QPixmap.fromImage(image))
            self.scaleFactor = 1.0

            self.scrollArea.setVisible(True)
            self.fitToWindowAct.setEnabled(True)
            self.updateActions()

            if not self.fitToWindowAct.isChecked():
                self.imageLabel.adjustSize()
    
#     def mousePressEvent(self, e):
#         print(f'image len : {len(self.image_list)}')
#         print(f'cnt {self.cnt}')
#         if self.cnt == len(self.image_list):
#             self.fout.close()
#             self.close()
#         elif e.buttons() & Qt.LeftButton:
#             x = e.x()
#             y = e.y()
#             print(f'x : {x} y : {y}')

#             self.fout.write(f'{self.image_list[self.cnt]} {x} {y} \n')
#             self.fout.flush()
#             self.cnt +=1
#             self.next_image()

    def next_image(self):
        fileName = os.path.join(self.image_dir, self.image_list[self.cnt])

        if fileName:
            image = cv2.imread(fileName)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            #image = cv2.resize(image, dsize=(1300,1300))
            image = QPixmap(self.realsenseFrameToQImage(image))
            if image.isNull():
                QMessageBox.information(self, "Image Viewer", "Cannot load %s." % fileName)
                return

            self.imageLabel.setPixmap(image)

            self.scrollArea.setVisible(True)
            self.fitToWindowAct.setEnabled(True)
            self.updateActions()

            if not self.fitToWindowAct.isChecked():
                self.imageLabel.adjustSize()

    def realsenseFrameToQImage(self, frame):
        result = qimage2ndarray.array2qimage(frame)
        return result
    
    #def eventFilter(self, source, event):
#        if event.type() == QtCore.QEvent.MouseButtonPress:
#        if event.button() == QtCore.Qt.LeftButton:
#            print(event.pos())
    #    if event.key() == QEvent.KeyPress:
    #        print("1")
    
    def keyPressEvent(self,e):
        if e.key() == Qt.Key_1 or e.key() == Qt.Key_2 or e.key() == Qt.Key_3:
            self.fout.write(f'{self.image_list[self.cnt]} {int(e.text()) - 1} \n')
            self.fout.flush()
            self.cnt +=1
            self.next_image()
        elif e.key() == Qt.Key_Backspace: 
            print("Wrong!")
            self.fout.write(f'{self.image_list[self.cnt]} bad \n')
            self.fout.flush()
            self.cnt -=1
            self.next_image()
        elif e.key() == Qt.Key_X:
            self.fout.write(f'{self.image_list[self.cnt]} -1 \n')
            self.fout.flush()
            self.cnt +=1
            self.next_image()
            
                
    def normalSize(self):
        self.imageLabel.adjustSize()
        self.scaleFactor = 1.0

    def fitToWindow(self):
        fitToWindow = self.fitToWindowAct.isChecked()
        self.scrollArea.setWidgetResizable(fitToWindow)
        if not fitToWindow:
            self.normalSize()

        self.updateActions()

    def createActions(self):
        self.openAct = QAction("&Open...", self, shortcut="Ctrl+O", triggered=self.open)
        self.exitAct = QAction("E&xit", self, shortcut="Ctrl+Q", triggered=self.close)
        self.normalSizeAct = QAction("&Normal Size", self, shortcut="Ctrl+S", enabled=False, triggered=self.normalSize)
        self.fitToWindowAct = QAction("&Fit to Window", self, enabled=False, checkable=True, shortcut="Ctrl+F",
                                      triggered=self.fitToWindow)

    def createMenus(self):
        self.fileMenu = QMenu("&File", self)
        self.fileMenu.addAction(self.openAct)
        self.fileMenu.addAction(self.exitAct)

    def updateActions(self):
        self.normalSizeAct.setEnabled(not self.fitToWindowAct.isChecked())


if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    # action 값 넣어야함. 
    imageViewer = QImageViewer(7) ################ ACTION
    imageViewer.show()
    sys.exit(app.exec_())
