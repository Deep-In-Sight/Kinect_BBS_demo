import sys
import os
import multiprocessing as mplti
import argparse
from PyQt5.QtWidgets import QApplication

from bbsQt.qtgui.qobj.QmainWindow import *
from client.encryptor import HEAAN_Encryptor
from bbsQt import constants
import requests

parser = argparse.ArgumentParser()
parser.add_argument("--host", dest='HOST')
args = parser.parse_args()

constants.HOST = args.HOST
cert = False

def run_qt_app(q1, q_answer, e_sk , e_ans):
    """Run the Qt application."""
    app = QApplication(sys.argv)
    app.setWindowIcon(getIcon(os.path.join(os.getcwd(),'res','icon')))
    imageEditor = QMyMainWindow(q1, q_answer, e_sk, e_ans) ### 여기가 아닌가? 
    imageEditor.show()
    quit = app.exec_()

def check_connection(upload_url):
    """Check if the server is up and running."""
    fn = "test.txt"
    # 연결 테스트용
    with open(fn, "w") as f:
        f.write("Connecting from: " + constants.HOST + "\n")

    try:
        r = requests.post('https://'+upload_url+'/upload', 
                    files={'file':open(fn, 'rb')}, 
                    headers={'dtype':"test"},
                    verify=cert)
    except (requests.exceptions.ConnectionError, requests.exceptions.InvalidURL, requests.exceptions.Timeout) as e:
        print(e)
        print("Connection Error")
        sys.exit()
    except requests.exceptions.HTTPError:
        print("Connection Established")    

    ret = requests.get('https://'+upload_url+'/result',
                        files={"file": open(fn, "rb")},
                        headers={"dtype":"test"},
                        verify=cert)
    print(ret.text)
    

def run_encryptor(q1, q_answer, e_sk, e_ans, e_enc_ans, work_dir="./"):
    """Run the FHE encryptor."""
    henc = HEAAN_Encryptor(args.HOST, work_dir)
    henc.start_encrypt_loop(q1, q_answer, e_sk, e_ans, e_enc_ans)

    
def main():
    KEYPATH = "./"  

    check_connection(constants.HOST)
    
    # lock = mplti.Lock()### 
    ctx = mplti.get_context('spawn') ###

    q1 = ctx.Queue(maxsize=8)
    q_answer = ctx.Queue(maxsize=8)

    # Skeleton exists
    e_sk = mplti.Event()
    e_sk.clear()

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
                    args=(q1, q_answer, e_sk, e_ans, e_enc_ans), daemon=False)
    p_enc.start()

    p_qt = mplti.Process(target=run_qt_app, 
                        args=(q1, q_answer, e_sk, e_ans), daemon=False) # 진짜
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
	main()
