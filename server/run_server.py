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

# def run_evaluator(q1, q_text, lock, e_key, e_enc, e_ans, key_path="./"):
#     e_key.wait()
#     henc = HEAAN_Evaluator(e_key, lock, key_path, e_ans)
#     #print(henc.prams.n)
#     henc.start_evaluate_loop(q1, q_text, e_enc, e_ans)

def run_evaluator(q1, q_text, lock, e_key, e_enc, e_ans, key_path="./"):
    #########################################
    # 심지어 key 이름도 신경 안 씀. 테스트할 때는 파일 안 보내줘도 무방
    e_key.wait() # 여기도 있고 evaluator 안에 또 있음. 하나는 제거할 것.
    # Key 로딩....
    print("Evaluator have loaded keys")
    e_ans.set() # Evaluator는 e_ans를 신호로 씀. 이름 바꿀까? 
    print("Evaluator ready.")

    ########################
    # Evaluator loop
    i = 0
    while True:
        e_enc.wait()
        print("Evaluator received a query", i)
        fn_data = q_text.get()
        print("Evaluator got data file:",fn_data)
        # Ctxt 로딩
        e_enc.clear()
        # run_model()
        # tar.gz 파일 쓰기
        fn_tar = "preds.tar.gz"
        q_text.put({"root_path":'./', 
                "keys_to_share":fn_tar})
        e_ans.set()

        i+=1
    

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
    

    
    