import sys
import os
import multiprocessing as mplti
import argparse
from PyQt5.QtWidgets import QApplication

from bbsQt.qtgui.qobj.QmainWindow import *
from bbsQt.core.encryptor import HEAAN_Encryptor
from bbsQt import constants
import requests

parser = argparse.ArgumentParser()
parser.add_argument("--host", dest='HOST')
args = parser.parse_args()

constants.HOST = args.HOST
#from bbsQt.comm import app_client

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

def check_connection(upload_url):
    fn = "test.txt"
    # 연결 테스트용
    with open(fn, "w") as f:
        f.write("Connecting from: " + constants.HOST + "\n")

    try:
        r = requests.post('http://'+upload_url+'/upload', 
                    files={'file':open(fn, 'rb')}, 
                    headers={'dtype':"test"})
    except (requests.exceptions.ConnectionError, requests.exceptions.InvalidURL, requests.exceptions.Timeout):
        print("Connection Error")
        sys.exit()
    except requests.exceptions.HTTPError:
        print("Connection Established")    

    ret = requests.get('http://'+upload_url+'/result',
                        files={"file": open(fn, "rb")},
                        headers={"dtype":"test"})
    print(ret.text)
    

def run_encryptor(q1, q_text, q_answer, e_sk, e_enc, e_ans, e_enc_ans, key_path="./serkey/"):
    henc = HEAAN_Encryptor(args.HOST, key_path)
     #print(henc.prams.n)
    henc.start_encrypt_loop(q1, q_text, q_answer, e_sk, e_enc, e_ans, e_enc_ans)

    
def main():
    KEYPATH = "./"  

    check_connection(constants.HOST)
    
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
