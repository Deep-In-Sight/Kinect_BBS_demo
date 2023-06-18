import sys
import os
import multiprocessing as mplti
from multiprocessing import Queue
import argparse
from glob import glob
from flask import Flask 
from flask import request
from werkzeug.utils import secure_filename
from flask import send_file

from bbsQt.constants import TEST_CLIENT, DEBUG
from server_utils import (
    fn_pred, 
    request_summary, 
    ready_for_connection_test, 
    check_for_keys, 
    predictions_ready)
import fase


app = Flask(__name__)
# Allow large file uploads (~70MB)
app.config['MAX_CONTENT_LENGTH'] = 128 * 1024 * 1024 
#q_text = None
#e_enc = None



@app.route('/upload',methods=['POST'])
def upload_file2():
    if DEBUG: request_summary(request)
    if request.method=='POST':
        f=request.files['file']
        
        if request.headers['dtype']=="ctxt":
            f.save(secure_filename(f.filename))
            print("[Comm] Received ciphertext")
            # The name of ciphertext file to be evaluated
            q_text.put(f.filename)
            # Inform evaluator that a new task is ready
            e_enc.set()

            if DEBUG: print("q_text", q_text)
            msg = "Ciphertext received"

        elif request.headers['dtype']=="test":
            print("[Comm] Received test")
            
            ready_for_connection_test(f.filename)
            msg = "Connection Check"

        return msg

@app.route('/keys',methods=['POST'])
def upload_keys():
    if request.method=='POST':
        if DEBUG: request_summary(request)

        f=request.files['file']
        f.save(secure_filename(f.filename)) # 
        if request.headers['dtype']=="enc_key":
            msg = "stored ENCKEY"
        elif request.headers['dtype']=="mul_key":
            msg = "stored MULKEY"
        elif request.headers['dtype']=="conj_key":
            msg = "stored CONJKEY"
        elif request.headers['dtype']=="rot_key":
            msg = "stored ROTKEY"

        # Flask/Werkzeug's default behavior is that
        # the "route" function is called only after the file transfer is done.
        # So, if the file exists, it means that the file is ready to be used.
        if check_for_keys():
            q_key.put("ready")
            print("[Comm] Keys are ready!")
        
        return msg#"good"

@app.route('/ready', methods=['GET'])
def check_result():
    if predictions_ready():
        return "ready"
    else:
        return "not ready"

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
        fn = fn_pred(request.headers['cnt'])
        print("SENDING", fn)
        return send_file(fn, as_attachment=True)

def run_server(host_ip):
    app.run(ssl_context=('cert.pem', 'key.pem'), host=host_ip, port=4443)
    

def run_evaluator(q_text, evaluator_ready, e_enc):
    server_path = os.getcwd()+'/'
    henc = HEAAN_Evaluator(server_path, evaluator_ready)
    if not TEST_CLIENT:
        print("[SERVER] Running evaluation loop")
        henc.start_evaluate_loop(q_text, e_enc)

    
def main(server_ip):
    #HOST = extract_ip()
    #HOST = '127.0.0.1'

    print("[SERVER] This server's IP:", server_ip)
    
    # Clean up keys
    for fn in glob("*.dat"):
        if os.path.exists(fn):
            os.remove(fn)
    
    for fn in glob("*.txt"):
        if os.path.exists(fn):
            os.remove(fn)

    # Key existence
    evaluator_ready = mplti.Event()
    evaluator_ready.clear()

    keys_ready = mplti.Event()
    keys_ready.clear()

    # Quit the application
    e_quit = mplti.Event()
    e_quit.clear()

    p_flask = mplti.Process(target=run_server, 
                            kwargs={"host_ip":server_ip})
    p_flask.start()

    p_enc = mplti.Process(target=run_evaluator, 
                          args=(q_text, evaluator_ready, e_enc), 
                          daemon=False)
    
    print("[SERVER] Waiting for keys...")
    
    if q_key.get() == "ready":
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

    q_key = Queue(maxsize=8)
    q_text = Queue(maxsize=8)
    # Ciphertext saved
    e_enc = mplti.Event()
    e_enc.clear()

    main(server_ip)