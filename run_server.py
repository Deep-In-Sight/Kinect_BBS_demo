import multiprocessing
import pickle
import sys
import os
import multiprocessing as mplti
from time import time
import bbsQt

from bbsQt.qtgui.qobj.QmainWindow import *
from bbsQt.comm import app_server
from bbsQt.core.evaluator import HEAAN_Evaluator

from PyQt5.QtWidgets import QApplication#, QMainWindow

def run_evaluator(q1, q_text, lock, e_key, e_enc, e_ans, key_path="./"):
    e_key.wait()
    henc = HEAAN_Evaluator(e_key, lock, key_path, e_ans)
    #print(henc.prams.n)
    henc.start_encrypt_loop(q1, e_enc, e_ans)


def run_communicator(e_key, q_text, e_enc, e_ans, lock):
    # 1. send keys to server and do quick check
    app_server.run_server(e_key, e_enc, e_ans, lock)
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
                          args=(q1, q_text, lock, e_key, e_enc, e_ans), 
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
	main()

    # while True:
    #     qq = q1.get()
    #     print(qq.keys())
    #     if q1.empty(): break

    # p.close()
    # p2.close()
    

    
    