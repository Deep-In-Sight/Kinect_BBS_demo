import multiprocessing
import sys
import os
import multiprocessing as mplti

from bbsQt.qtgui.qobj.QmainWindow import *
from bbsQt.comm import app_client
from bbsQt.core.encryptor import HEAAN_Encryptor

from PyQt5.QtWidgets import QApplication

TEST=True
from bbsQt.constants import DEBUG



def run_qt_app(q1, q_answer, lock, e_sk , e_ans):
    app = QApplication(sys.argv)
    app.setWindowIcon(getIcon(os.path.join(os.getcwd(),'res','icon')))
    imageEditor = QMyMainWindow(q1, e_sk, q_answer, e_ans) ### 여기가 아닌가? 
    imageEditor.show()
    quit = app.exec_()
    #sys.exit(app.exec_())
    #e_quit.wait()
    #quit



########################## DEBUGGING ############################
from bbsQt.core.evaluator import HEAAN_Evaluator
def run_evaluator(q_text, lock, e_key, e_enc, e_ans, server_path="./server/"):
    e_key.wait()
    henc = HEAAN_Evaluator(lock, server_path, e_ans)
    e_key.clear()
    print("[MAIN] Running evaluation loop")
    henc.start_evaluate_loop(q_text, e_enc, e_ans)

def debug_eval(q1, q_text, lock, e_sk, e_key, e_enc, e_ans):
    import pickle
    action=1
    cam='e'
    test_data_dir = "./models/"
    dataset = pickle.load(open(test_data_dir + f"BBS_dataset_{action}_{cam}_unnormed.pickle", "rb"))
    X_valid = dataset["valid_x"][12:13]
    y_valid = dataset["valid_y"][12:13]
    print("ANSWER", y_valid)
    
    q1.put({"action":action,
            "cam":cam, 
            "skeleton": X_valid})
    e_sk.set()

    #run_evaluator(q_text, lock, e_key, e_enc, e_ans, server_path="./server/")


def run_encryptor(q1, q_text, q_answer, e_key, e_sk, e_enc, e_ans, e_enc_ans, lock, key_path="./"):
    henc = HEAAN_Encryptor(q_text, e_key, lock, key_path, test=TEST)
     #print(henc.prams.n)
    henc.start_encrypt_loop(q1, q_text, q_answer, e_sk, e_enc, e_ans, e_enc_ans)


def run_communicator(e_key, q1, q_text, e_enc, e_quit, e_ans, e_enc_ans, lock):
    # 1. send keys to server and do quick check
    e_key.wait()
    app_client.run_share_key(q_text, e_key, lock)

    while True:
        print("[run comm] waiting for ctxt.....")
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
    print("hi")
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
    e_key = multiprocessing.Event()
    e_key.clear()
    
    # Skeleton exists
    e_sk = multiprocessing.Event()
    e_sk.clear()

    # Query ciphertext saved
    e_enc = multiprocessing.Event()
    e_enc.clear()

    # Encrypted prediction saved
    e_enc_ans = multiprocessing.Event()
    e_enc_ans.clear()

    # Decrypted prediction saved
    e_ans = multiprocessing.Event()
    e_ans.clear()

    # Quit the application
    e_quit = multiprocessing.Event()
    e_quit.clear()

    p_enc = mplti.Process(target=run_encryptor, 
                    args=(q1, q_text, q_answer, e_key, e_sk, e_enc, e_ans, e_enc_ans, lock), daemon=False)
    p_enc.start()

    if not DEBUG:
        p_socket = mplti.Process(target=run_communicator, 
                args=(e_key, q1, q_text, e_enc, e_quit, e_ans, e_enc_ans, lock), daemon=False)
        p_socket.start()
        
        p_qt = mplti.Process(target=run_qt_app, 
                            args=(q1, q_answer, lock, e_sk, e_ans), daemon=False) # 진짜
        # ## signal quit()  
        p_qt.start()

    else:
        p_debug = mplti.Process(target=debug_eval, 
                args=(q1, q_text, lock, e_sk, e_key, e_enc, e_ans), daemon=False)
        p_debug.start()

        
    

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
    

    
    
