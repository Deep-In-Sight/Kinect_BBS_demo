import sys

from PyQt5.QtWidgets import QApplication
from qobj.QmainWindow import *
import os

def main():
	app = QApplication(sys.argv)
	app.setWindowIcon(getIcon(os.path.join(os.getcwd(),'res','icon')))
	imageEditor = QMainWindow()
	imageEditor.show()

	sys.exit(app.exec_())	

if __name__ == '__main__':
	main()

	