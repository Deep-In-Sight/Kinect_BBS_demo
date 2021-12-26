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


def run_qt_app(q1, q_text, lock, e_sk,):
    """
    QT 프로그램이 q1과 e_sk (이벤트 오브젝트)를 받아서 skeleton 데이터를 q1에 넣고, e_sk를 .set()해서 
    HEAAN_Encryptor에 Skeleton이 준비되었다고 신호를 주고싶은데, 어디로 q1과 e_sk를 넣어줘야할지 모르겠음. 
    """
    app = QApplication(sys.argv)
    app.setWindowIcon(getIcon(os.path.join(os.getcwd(),'res','icon')))
    imageEditor = QMyMainWindow(q1, e_sk) ### 여기가 아닌가? 
    imageEditor.show()
    print("!@#@!@$")
    quit = app.exec_()
    #sys.exit(app.exec_())
    #e_quit.wait()
    #quit


# def run_temp_qt(q1, lock, e_sk):
#     fn = "/home/hoseung/Work/Kinect_BBS_demo/G1/000/BT/bodytracking_data.pickle"
#     skeleton = pickle.load(open(fn, "rb"))
#     skeleton = skeleton_to_arr_direct(skeleton)
#     time.sleep(5)
#     q1.put({"skeleton":skeleton})
#     print("Loaded and put skeleton")
#     e_sk.set()


def run_encryptor(q1, q_text, lock, e_key, e_sk, e_enc, key_path="./"):
    key_path = '/home/hoseung/Work/Kinect_BBS_demo/'
    henc = HEAAN_Encryptor(q_text, e_key, lock, key_path)
    #print(henc.prams.n)
    henc.start_encrypt_loop(q1, e_sk, e_enc)



def run_communicator(e_key, q1, q_text, e_enc, e_quit, lock):
    # 1. send keys to server and do quick check
    e_key.wait()
    app_client.run_share_key(q_text, e_key, lock)
    e_enc.wait()
    app_client.query(q1, lock, e_enc, e_quit)


    
def main():
    KEYPATH = "./"  
    lock = mplti.Lock()### 
    ctx = mplti.get_context('spawn') ###

    q1 = ctx.Queue(maxsize=8)
    q_text = ctx.Queue(maxsize=8)

    # Key existence
    e_key = multiprocessing.Event()
    e_key.clear()
    
    # Skeleton exists
    e_sk = multiprocessing.Event()
    e_sk.clear()

    # Ciphertext saved
    e_enc = multiprocessing.Event()
    e_enc.clear()

    # Quit the application
    e_quit = multiprocessing.Event()
    e_quit.clear()

    p_socket = mplti.Process(target=run_communicator, args=(e_key, q1, q_text, e_enc, e_quit, lock), daemon=False)
    p_socket.start()

    
    p_enc = mplti.Process(target=run_encryptor, args=(q1, q_text, lock, e_key, e_sk, e_enc), daemon=False)
    p_enc.start()

    #p_qt = mplti.Process(target=run_temp_qt, args=(q1, lock, e_sk), daemon=True) # 임시
    p_qt = mplti.Process(target=run_qt_app, args=(q1, q_text, lock, e_sk), daemon=False) # 진짜
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
    

    
    