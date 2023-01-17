import os
import sys
from bbsQt.qtgui.qobj.QmainWindow import *
from PyQt5.QtWidgets import QApplication


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(getIcon(os.path.join(os.getcwd(),'res','icon')))
    imageEditor = QMyMainWindow() 
    imageEditor.show()
    app.exec_()