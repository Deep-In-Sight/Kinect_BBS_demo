import sys
import os
import multiprocessing as mplti
import argparse
from PyQt5.QtWidgets import QApplication

from bbsQt.qtgui.qobj.QmainWindow import *
from bbsQt.core.encryptor import HEAAN_Encryptor

from bbsQt import constants


parser = argparse.ArgumentParser()
parser.add_argument("--host", dest='HOST')
args = parser.parse_args()

constants.HOST = args.HOST
from bbsQt.comm import app_client


def run_qt_app(q1, q_answer, e_sk , e_ans):
    app = QApplication(sys.argv)
    app.setWindowIcon(getIcon(os.path.join(os.getcwd(),'res','icon')))
    imageEditor = QMyMainWindow(q1, q_answer, e_sk, e_ans) ### 여기가 아닌가? 
    imageEditor.show()
    quit = app.exec_()
    #sys.exit(app.exec_())
    #e_quit.wait()
    #quit


########################## DEBUGGING ############################
# from bbsQt.core.evaluator import HEAAN_Evaluator
# def run_evaluator(q_text, e_key, e_enc, e_ans, server_path="./server/"):
#     e_key.wait()
#     henc = HEAAN_Evaluator(server_path, e_ans)
#     e_key.clear()
#     print("[MAIN] Running evaluation loop")
#     henc.start_evaluate_loop(q_text, e_enc, e_ans)


def run_encryptor(q1, q_text, q_answer, e_sk, e_enc, e_ans, e_enc_ans, key_path="./serkey/"):
    henc = HEAAN_Encryptor(key_path)
     #print(henc.prams.n)
    henc.start_encrypt_loop(q1, q_text, q_answer, e_sk, e_enc, e_ans, e_enc_ans)


# separate communicator process no more needed.
# def run_communicator(q1, q_text, e_enc, e_enc_ans):
#     # 1. send keys to server and do quick check
#     #e_key.wait()
#     #app_client.run_share_key(q_text, e_key, lock)

#     while True:
#         print("[run comm] waiting for ctxt.....")
#         e_enc.wait()
#         print("[run_comm] e_enc passed. Ctxt is ready")
#         fn_dict = q1.get()
#         print("[run_comm] file name:", fn_dict)
#         answer = app_client.query(fn_dict)
#         e_enc.clear()
        
#         print("[run_comm] got an answer", answer)
#         # ENCRYPTED answer
#         q_text.put(answer['filename']) # put encrypted answer filename
#         print("[run_comm] Prediction file names are ready")
#         e_enc_ans.set()
#         print("[run_comm] e_enc_ans set")

    
def main():
    KEYPATH = "./"  

    lock = mplti.Lock()### 
    ctx = mplti.get_context('spawn') ###

    q1 = ctx.Queue(maxsize=8)
    q_text = ctx.Queue(maxsize=8)
    """
    Ecryptor puts key file information to q_textvas:
    {"root_path":key_path, "keys_to_share":fn_tar}
    """
    q_answer = ctx.Queue(maxsize=8)

    # Key exists
    #e_key = mplti.Event()
    #e_key.clear()
    
    # Skeleton exists
    e_sk = mplti.Event()
    e_sk.clear()

    # Query ciphertext saved
    e_enc = mplti.Event()
    e_enc.clear()

    # Encrypted prediction saved
    e_enc_ans = mplti.Event()
    e_enc_ans.clear()

    # Decrypted prediction saved
    e_ans = mplti.Event()
    e_ans.clear()

    # Quit the application
    e_quit = mplti.Event()
    e_quit.clear()

    p_enc = mplti.Process(target=run_encryptor, 
                    args=(q1, q_text, q_answer, e_sk, e_enc, e_ans, e_enc_ans), daemon=False)
    p_enc.start()

    # p_socket = mplti.Process(target=run_communicator, 
    #         args=(q1, q_text, e_enc, e_enc_ans), daemon=False)
    # p_socket.start()
    
    p_qt = mplti.Process(target=run_qt_app, 
                        args=(q1, q_answer, e_sk, e_ans), daemon=False) # 진짜
    # ## signal quit()  
    p_qt.start()

        
    e_quit.wait()
    # p_socket.join()
    # p_socket.close()
    p_enc.join()
    p_enc.close()
    p_qt.join()
    p_qt.close()
    
    sys.exit()
    #e_quit.wait()


if __name__ == '__main__':
	main()
