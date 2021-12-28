import multiprocessing
import pickle
import sys
import os
import multiprocessing as mplti
from time import time
import bbsQt

from bbsQt.qtgui.qobj.QmainWindow import *
from bbsQt.comm import app_client
from bbsQt.core.encryptor import HEAAN_Encryptor

from PyQt5.QtWidgets import QApplication#, QMainWindow


# def run_qt_app(q1, q_answer, lock, e_sk , e_ans):
#     app = QApplication(sys.argv)
#     app.setWindowIcon(getIcon(os.path.join(os.getcwd(),'res','icon')))
#     imageEditor = QMyMainWindow(q1, e_sk, q_answer, e_ans) ### 여기가 아닌가? 
#     imageEditor.show()
#     quit = app.exec_()
#     #sys.exit(app.exec_())
#     #e_quit.wait()
#     #quit

def run_qt_app(q1, q_answer, lock, e_sk , e_ans):
    app = QApplication(sys.argv)
    app.setWindowIcon(getIcon(os.path.join(os.getcwd(),'res','icon')))
    imageEditor = QMyMainWindow(q1, e_sk, q_answer, e_ans) ### 여기가 아닌가? 
    imageEditor.show()
    quit = app.exec_()
    #sys.exit(app.exec_())
    #e_quit.wait()
    #quit

# def run_encryptor(q1, q_text, q_answer, e_key, e_sk, e_enc, e_ans, e_enc_ans, lock, key_path="./"):
#     key_path = './'
#     henc = HEAAN_Encryptor(q_text, e_key, lock, key_path)
#     #print(henc.prams.n)
#     #e_key.wait()
#     app_client.run_share_key(q_text, e_key, lock)
#     henc.start_encrypt_loop(q1, q_text, q_answer, e_sk, e_enc, e_ans, e_enc_ans)
def run_encryptor(q1, q_text, q_answer, e_key, e_sk, e_enc, e_ans, e_enc_ans, lock, key_path="./"):
    ############################################# 
    #
    fn_tar = "test.tar.gz"
    q_text.put({"root_path":key_path, 
                "keys_to_share":fn_tar})
    e_key.set()
    print("[Encryptor] HEAAN is ready")
    #############################################
    # encryptor loop
    i = 0
    while True:
        # 대기 1
        e_sk.wait()
        print("[Encryptor] good to go") 
        sk = q1.get()
        e_sk.clear() # reset skeleton event

        # 결과 생성
        fn = f"ctx_a{sk['action']:02d}_{i}.dat"
        q1.put({"fn_enc_skeleton": fn})
        print("[Encryptor] skeleton encrypted and saved. q1 got file name", fn)
        e_enc.set() # Tell encryption is done and file is ready
        
        # 응답 대기 
        print("[Encryptor] Waiting for prediction...")
        # Decrypt
        e_enc_ans.wait()
        fn_preds = q_text.get()
        
        # 복호화 결과 출력
        e_enc_ans.clear()
        ans_str = f"Predicted score: 1234"
        q_answer.put(ans_str)
        e_ans.set()
        
        i+=1

def run_communicator(e_key, q1, q_text, e_enc, e_quit, e_ans, e_enc_ans, lock):
    # 1. send keys to server and do quick check
    e_key.wait()
    app_client.run_share_key(q_text, e_key, lock)

    while True:
        e_enc.wait()
        print("[run_comm] e_enc passed. Ctxt is ready")
        fn_dict = q1.get()
        print("[run_comm] file name:", fn_dict)
        answer = app_client.query(fn_dict, lock)
        e_enc.clear()
        
        print("[run_comm] got an answer", answer)
        # ENCRYPTED answer
        q_text.put(answer['filename']) # put encrypted answer filename
        print("[run_comm] Prediction file names are ready")
        e_enc_ans.set()
        print("[run_comm] e_enc_ans set")

    
def main():
    KEYPATH = "./"  
    lock = mplti.Lock()### 
    ctx = mplti.get_context('spawn') ###

    q1 = ctx.Queue(maxsize=8)
    q_text = ctx.Queue(maxsize=8)
    q_answer = ctx.Queue(maxsize=8)

    # Key existence
    e_key = multiprocessing.Event()
    e_key.clear()
    
    # Skeleton exists
    e_sk = multiprocessing.Event()
    e_sk.clear()

    # Ciphertext saved
    e_enc = multiprocessing.Event()
    e_enc.clear()

    # answer saved
    e_ans = multiprocessing.Event()
    e_ans.clear()

    # answer saved
    e_enc_ans = multiprocessing.Event()
    e_enc_ans.clear()

    # Quit the application
    e_quit = multiprocessing.Event()
    e_quit.clear()

    p_socket = mplti.Process(target=run_communicator, 
    args=(e_key, q1, q_text, e_enc, e_quit, e_ans, e_enc_ans, lock), daemon=False)
    p_socket.start()

    
    p_enc = mplti.Process(target=run_encryptor, 
                    args=(q1, q_text, q_answer, e_key, e_sk, e_enc, e_ans, e_enc_ans, lock), daemon=False)
    p_enc.start()

    #p_qt = mplti.Process(target=run_temp_qt, args=(q1, lock, e_sk), daemon=True) # 임시
    p_qt = mplti.Process(target=run_qt_app, 
                        args=(q1, q_answer, lock, e_sk, e_ans), daemon=False) # 진짜
    # ## signal quit()  
    p_qt.start()

    #e_key.set()

    e_quit.wait()
    p_socket.join()
    p_socket.close()
    p_enc.join()
    p_enc.close()
    p_qt.join()
    p_qt.close()
    
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
    

    
    