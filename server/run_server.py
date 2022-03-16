import sys
import multiprocessing as mplti
import argparse

from bbsQt.qtgui.qobj.QmainWindow import *
from bbsQt.comm import app_server
from bbsQt.constants import TEST_CLIENT
from bbsQt.comm.utils import extract_ip
import fase


def run_evaluator(q_text, evaluator_ready, e_enc, e_ans, server_path="./"):
    #evaluator_ready.wait()
    henc = HEAAN_Evaluator(server_path, evaluator_ready)
    #evaluator_ready.clear()
    if not TEST_CLIENT:
        print("[SERVER] Running evaluation loop")
        henc.start_evaluate_loop(q_text, e_enc, e_ans)

def run_communicator(evaluator_ready, q_text, e_enc, e_ans, HOST):
    # 1. send keys to server and do quick check
    app_server.run_server(q_text, evaluator_ready, e_enc, e_ans, HOST)
    #e_enc.wait()
    #app_server.query(q1, lock, e_enc, e_quit)

    
def main():
    HOST = extract_ip()
    #HOST = '127.0.0.1'

    print("[SERVER] This server's IP:", HOST)
    ctx = mplti.get_context('spawn') ###

    #q1 = ctx.Queue(maxsize=8)
    q_text = ctx.Queue(maxsize=8)

    # Key existence
    evaluator_ready = mplti.Event()
    evaluator_ready.clear()

    # Ciphertext saved
    e_enc = mplti.Event()
    e_enc.clear()

    e_ans = mplti.Event()
    e_ans.clear()

    # Quit the application
    e_quit = mplti.Event()
    e_quit.clear()

    p_socket = mplti.Process(target=run_communicator, 
                            args=(evaluator_ready, q_text, e_enc, e_ans, HOST), 
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
    # Set which version of HEAAN to use
    parser = argparse.ArgumentParser()

    parser.add_argument("--fpga", dest='use_fpga', action='store_true')
    parser.add_argument("--cuda", dest='use_cuda', action='store_true')
    args = parser.parse_args()

    if args.use_fpga:
        fase.USE_FPGA = True
    elif args.use_cuda:
        fase.USE_CUDA = True

    # import HEAAN_Evaluator *after* setting which HEAAN variants to use
    from bbsQt.core.evaluator import HEAAN_Evaluator
    main()