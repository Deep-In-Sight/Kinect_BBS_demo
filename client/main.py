import sys
import os
import multiprocessing as mplti
import argparse
from PyQt5.QtWidgets import QApplication

from bbsQt.qtgui.qobj.QmainWindow import *
from client.encryptor import HEAANEncryptor
from bbsQt import constants

def run_qt_app(q_sk, q_answer, e_sk , e_ans):
    """Run the Qt application."""
    app = QApplication(sys.argv)
    app.setWindowIcon(getIcon(os.path.join(os.getcwd(),'res','icon')))
    imageEditor = QMyMainWindow(q_sk, q_answer, e_sk, e_ans) ### 여기가 아닌가? 
    imageEditor.show()
    quit = app.exec_()    

def run_encryptor(q_sk, q_answer, e_sk, e_ans, work_dir="./"):
    """Run the FHE encryptor."""
    henc = HEAANEncryptor(args.HOST, constants.CERTIFICATE, work_dir)
    henc.start_encrypt_loop(q_sk, q_answer, e_sk, e_ans)

    
def main():
    KEYPATH = "./"  

    # lock = mplti.Lock()### 
    ctx = mplti.get_context('spawn') ###

    q_sk = ctx.Queue(maxsize=8)
    q_answer = ctx.Queue(maxsize=8)

    # Skeleton exists
    e_sk = mplti.Event()
    e_sk.clear()

    # Decrypted prediction saved
    e_ans = mplti.Event()
    e_ans.clear()

    # Quit the application
    e_quit = mplti.Event()
    e_quit.clear()

    p_enc = mplti.Process(target=run_encryptor, 
                    args=(q_sk, q_answer, e_sk, e_ans), daemon=False)
    p_enc.start()

    p_qt = mplti.Process(target=run_qt_app, 
                        args=(q_sk, q_answer, e_sk, e_ans), daemon=False)
    # ## signal quit()  
    p_qt.start()

        
    e_quit.wait()
    p_enc.join()
    p_enc.close()
    p_qt.join()
    p_qt.close()
    
    sys.exit()
    #e_quit.wait()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", dest='HOST')
    args = parser.parse_args()

    constants.HOST = args.HOST
    main()
