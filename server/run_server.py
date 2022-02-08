import multiprocessing
import sys
import multiprocessing as mplti
#from time import time

from bbsQt.qtgui.qobj.QmainWindow import *
from bbsQt.comm import app_server
from bbsQt.core.evaluator import HEAAN_Evaluator
#from PyQt5.QtWidgets import QApplication#, QMainWindow
from bbsQt.constants import TEST_CLIENT

def run_evaluator(q_text, evaluator_ready, e_enc, e_ans, server_path="./"):
    #evaluator_ready.wait()
    henc = HEAAN_Evaluator(server_path, evaluator_ready)
    #evaluator_ready.clear()
    if not TEST_CLIENT:
        print("[MAIN] Running evaluation loop")
        henc.start_evaluate_loop(q_text, e_enc, e_ans)

def run_communicator(evaluator_ready, q_text, e_enc, e_ans):
    # 1. send keys to server and do quick check
    app_server.run_server(q_text, evaluator_ready, e_enc, e_ans)
    #e_enc.wait()
    #app_server.query(q1, lock, e_enc, e_quit)

    
def main():
    #KEYPATH = "./"  
    lock = mplti.Lock()### 
    ctx = mplti.get_context('spawn') ###

    #q1 = ctx.Queue(maxsize=8)
    q_text = ctx.Queue(maxsize=8)

    # Key existence
    evaluator_ready = multiprocessing.Event()
    evaluator_ready.clear()

    # Ciphertext saved
    e_enc = multiprocessing.Event()
    e_enc.clear()

    e_ans = multiprocessing.Event()
    e_ans.clear()

    # Quit the application
    e_quit = multiprocessing.Event()
    e_quit.clear()

    p_socket = mplti.Process(target=run_communicator, 
                            args=(evaluator_ready, q_text, e_enc, e_ans), 
                            daemon=False)
    p_socket.start()

    p_enc = mplti.Process(target=run_evaluator, 
                          args=(q_text, evaluator_ready, e_enc, e_ans), 
                          daemon=False)
    p_enc.start()

    #evaluator_ready.set()

    e_quit.wait()
    p_socket.join()
    p_socket.close()
    p_enc.join()
    p_enc.close()

    
    sys.exit()
    #e_quit.wait()
    

if __name__ == '__main__':

    main()