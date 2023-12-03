import sys
import os
import multiprocessing as mplti
import argparse
from PyQt5.QtWidgets import QApplication

from bbs_client.qtgui.QmainWindow import *

    
def main():
    KEYPATH = "./"  
    
    ctx = mplti.get_context('spawn') ###

    q_sk = ctx.Queue(maxsize=4)

    # Skeleton exists
    e_sk = mplti.Event()
    e_sk.clear()
    
    app = QApplication(sys.argv)
    app.setWindowIcon(getIcon(os.path.join(os.getcwd(),'res','icon')))
    imageEditor = QMyMainWindow(q_sk, e_sk)
    imageEditor.show()
    quit = app.exec_()
    
    sys.exit()
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    args = parser.parse_args()

    main()
