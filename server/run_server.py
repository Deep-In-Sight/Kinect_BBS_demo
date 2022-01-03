import multiprocessing
import sys
import multiprocessing as mplti
#from time import time

from bbsQt.qtgui.qobj.QmainWindow import *
from bbsQt.comm import app_server
from bbsQt.core.evaluator import HEAAN_Evaluator

from PyQt5.QtWidgets import QApplication#, QMainWindow

import fase
#fase.USE_FPGA = True 
from fase.core.heaan import he
from bbsQt.comm.libserver import TEST_CLIENT

def run_evaluator(q_text, lock, e_key, e_enc, e_ans, key_path="./"):
    e_key.wait()
    henc = HEAAN_Evaluator(lock, key_path, e_ans)
    e_key.clear()
    #print(henc.prams.n)
    if not TEST_CLIENT:
        print("[MAIN] Running evaluation loop")
        henc.start_evaluate_loop(q_text, e_enc, e_ans)

def run_communicator(e_key, q_text, e_enc, e_ans, lock):
    # 1. send keys to server and do quick check
    app_server.run_server(q_text, e_key, e_enc, e_ans, lock)
    #e_enc.wait()
    #app_server.query(q1, lock, e_enc, e_quit)

    
def main():
    KEYPATH = "./"  
    lock = mplti.Lock()### 
    ctx = mplti.get_context('spawn') ###

    q1 = ctx.Queue(maxsize=8)
    q_text = ctx.Queue(maxsize=8)

    # Key existence
    e_key = multiprocessing.Event()
    e_key.clear()

    # Ciphertext saved
    e_enc = multiprocessing.Event()
    e_enc.clear()

    e_ans = multiprocessing.Event()
    e_ans.clear()

    # Quit the application
    e_quit = multiprocessing.Event()
    e_quit.clear()

    p_socket = mplti.Process(target=run_communicator, 
                            args=(e_key, q_text, e_enc, e_ans, lock), 
                            daemon=False)
    p_socket.start()

    p_enc = mplti.Process(target=run_evaluator, 
                          args=(q_text, lock, e_key, e_enc, e_ans), 
                          daemon=False)
    p_enc.start()

    #e_key.set()

    e_quit.wait()
    p_socket.join()
    p_socket.close()
    p_enc.join()
    p_enc.close()

    
    sys.exit()
    #e_quit.wait()
    

if __name__ == '__main__':

    # if len(sys.argv) != 2:
    #     print("usage:", sys.argv[0], "choose one: [DI, ETRI, local]")
    #     sys.exit(1)
    # location = sys.argv[1]
    main()

    # while True:
    #     qq = q1.get()
    #     print(qq.keys())
    #     if q1.empty(): break

    # p.close()
    # p2.close()
    

    
    