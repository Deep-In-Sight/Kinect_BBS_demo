import sys
import os
import multiprocessing as mplti
from multiprocessing import Queue
import argparse

# from bbsQt.qtgui.qobj.QmainWindow import *
# from bbsQt.comm import app_server
from bbsQt.constants import TEST_CLIENT
#from bbsQt.comm.utils import extract_ip

from flask import Flask 
from flask import request
from werkzeug.utils import secure_filename
from flask import send_file

import fase


app = Flask(__name__,static_folder='./static',template_folder = './templates')
app.config['MAX_CONTENT_LENGTH'] = 128 * 1024 * 1024 
q_text = None
e_enc = None

@app.route('/upload',methods=['POST'])
def upload_file2():
    if request.method=='POST':
        print("\nMethod: ", request.method)
        print("Headers: ", request.headers)
        print("Args: ", request.args)
        print("Form data: ", request.form)
        print("FILE: ", request.files)
        # print("JSON data: ", request.get_json())
        
        #print("Received POST request")
        print("request", request)

        f=request.files['file']
        #print(f, ) can I print only a few lines? 
        f.save(secure_filename(f.filename)) # 
        if request.headers['dtype']=="enc_key":
            print("Processing ENCKEY")
            msg = "stored ENCKEY"
        elif request.headers['dtype']=="mul_key":
            msg = "stored MULKEY"
        elif request.headers['dtype']=="ctxt":
            print("Received ciphertext")
            e_enc.set()
            
            q_text.put(f.filename)

            # action = request.headers['action']
            print("Calling HEAAN")
            # result = call_heaan.apply_async(args=[f.filename, action])
            print("Calculation DONE?")
            
        elif request.headers['dtype']=="test":
            print("Received test")
            ready_for_connection_test(f.filename)
            msg = "Connection Check"

        
        

        return msg#"good"

@app.route('/result', methods=['GET'])
def get_result():
    """GET method. 
    계산이 끝나고 파일이 준비되면 클라이언트가 GET을 성공하게 될 것.

    pred_0 ~ pred_4.dat 필요.

    """
    print("\nREQUEST.HEADER", request.headers)
    print("Method: ", request.method)
    print("Args: ", request.args)
    if "dtype" in request.headers:
        if request.headers['dtype']=="test":
            return send_file("test.txt", as_attachment=True)
    else:
        fn = f"result/pred_{request.headers['cnt']}.dat"
        print("SENDING", fn)
        return send_file(fn, as_attachment=True)

def on_raw_message(body):
    pass

def ready_for_connection_test(fn_in):
    with open(fn_in, "a") as fout:
        fout.write(">>>> Connection GOOD\n")

def run_server(host_ip):
    app.run(ssl_context=('cert.pem', 'key.pem'), host=host_ip, port=4443)
    

def run_evaluator(q_text, evaluator_ready, e_enc):
    server_path = os.getcwd()+'/'
    henc = HEAAN_Evaluator(server_path, evaluator_ready)
    if not TEST_CLIENT:
        print("[SERVER] Running evaluation loop")
        henc.start_evaluate_loop(q_text, e_enc)

# def run_communicator(evaluator_ready, q_text, e_enc, e_ans, HOST):
#     # 1. send keys to server and do quick check
#     app_server.run_server(q_text, evaluator_ready, e_enc, e_ans, HOST)
    #e_enc.wait()
    #app_server.query(q1, lock, e_enc, e_quit)

    
def main(server_ip):
    #HOST = extract_ip()
    #HOST = '127.0.0.1'

    print("[SERVER] This server's IP:", server_ip)
    #ctx = mplti.get_context('spawn') ###

    #q1 = ctx.Queue(maxsize=8)
    #q_text = ctx.Queue(maxsize=8)

    # Key existence
    evaluator_ready = mplti.Event()
    evaluator_ready.clear()

    # Ciphertext saved
    e_enc = mplti.Event()
    e_enc.clear()

    # e_ans = mplti.Event()
    # e_ans.clear()

    # Quit the application
    e_quit = mplti.Event()
    e_quit.clear()

    # p_socket = mplti.Process(target=run_communicator, 
    #                         args=(evaluator_ready, q_text, e_enc, e_ans, HOST), 
    #                         daemon=False)
    # p_socket.start()
    p_flask = mplti.Process(target=run_server, kwargs={"host_ip":server_ip})
    p_flask.start()

    p_enc = mplti.Process(target=run_evaluator, 
                          args=(q_text, evaluator_ready, e_enc), 
                          daemon=False)
    p_enc.start()

    #evaluator_ready.set()
    e_quit.wait()
    p_flask.join()
    p_flask.close()
    p_enc.join()
    p_enc.close()
    
    sys.exit()
    #e_quit.wait()
    

if __name__ == '__main__':
    # Set which version of HEAAN to use
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", dest="HOST", default="localhost")
    parser.add_argument("--fpga", dest='use_fpga', action='store_true')
    parser.add_argument("--cuda", dest='use_cuda', action='store_true')
    args = parser.parse_args()
    server_ip = args.HOST
    if args.use_fpga:
        fase.USE_FPGA = True
    elif args.use_cuda:
        fase.USE_CUDA = True

    # import HEAAN_Evaluator *after* setting which HEAAN variants to use
    from bbsQt.core.evaluator import HEAAN_Evaluator

    q_text = Queue(maxsize=8)

    main(server_ip)