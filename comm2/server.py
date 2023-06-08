import json
import argparse
from flask import Flask 
from flask import request
from werkzeug.utils import secure_filename
from flask import send_file
from celery import Celery

from bbsconfig import FN_STATE, REDIS_BROKER_URL, REDIS_RESULT_URL
from utils import gen_empty_state
import fase


flask_app = Flask(__name__,static_folder='./static',template_folder = './templates')

# Configure the redis server
flask_app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
flask_app.config['result_backend'] = 'redis://localhost:6379/0'

flask_app.config['MAX_CONTENT_LENGTH'] = 128 * 1024 * 1024 

# celery from CMD will invoke this instance of celery
celery_app = Celery(flask_app.name, broker=flask_app.config['CELERY_BROKER_URL'])
celery_app.conf.update(flask_app.config)


@flask_app.route('/upload',methods=['POST'])
def upload_file2():
    if request.method=='POST':
        print("\nMethod: ", request.method)
        print("Headers: ", request.headers)
        print("Args: ", request.args)
        print("Form data: ", request.form)
        print("FILE: ", request.files)
        # print("JSON data: ", request.get_json())
        
        #print("Received POST request")
        #print("request", request)

        f=request.files['file']
        #print(f, ) can I print only a few lines? 
        f.save(secure_filename(f.filename)) # 
        if request.headers['dtype']=="enc_key":
            msg = "stored ENCKEY"
        elif request.headers['dtype']=="mul_key":
            msg = "stored MULKEY"
        elif request.headers['dtype']=="conj_key":
            msg = "stored CONJKEY"
        elif request.headers['dtype']=="rot_key":
            msg = "stored ROTKEY"
        elif request.headers['dtype']=="ctxt":
            print("Received ciphertext")
            action = request.headers['action']
            print("Calling HEAAN")
            # 뭔가 이상함. 
            result = call_heaan.apply_async(args=[f.filename, action])
            print("Calculation DONE?")
            # celery.task.apply_async offers more control over the task
            # than .delay()
            # The above decorated function returns "AsyncResult" object
            # MUST call get() or forget() to release the resource
            # propagate: re-raise exception if it fails
            msg = result.get(on_message=on_raw_message, propagate=False)
            msg = "DEBUGGING - SKIP"
        elif request.headers['dtype']=="test":
            print("Received test")
            ready_for_connection_test(f.filename)
            msg = "Connection Check"

        print("[RECEIVING KEY] ", msg)

        return msg#"good"

@flask_app.route('/result', methods=['GET'])
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
    #print("Received: {0!r}".format(body))

# bind하면 self가 필요한 것 같은데, 뭐랑 bind하는 걸까? 
@celery_app.task(bind=True) # bind if access to the instance is needed
def call_heaan(fn, action):
    """Run Deep Learning model on the server.
        parameter
        ---------
        fn: filename of the ciphertext
        action: class of action [1,14]

        
        원래는 대략 아래와 같은 기능을 하는 함수

        1. load ciphertext
        ctxt = heaan.load_ctxt(fn)
        
        2. load FHE DL model
        model = FHE_DL_model(action)
        
        3. run model
        pred = model(ctxt)

        4. save result to file
        heaan.save_ctxt(pred)

    """
    print("HEAAN called", fn, action)
    
    # do calculation
    #with open(fn, "r") as f:
    #    new_fn = f.read().splitlines()[0]
    
    self.update_state(state="PROGRESS")


    self.update_state(state="SUCCESS")

    return "HEAAN Inference done!"


def ready_for_connection_test(fn_in):
    with open(fn_in, "a") as fout:
        fout.write(">>>> Connection GOOD\n")

def is_evaluator_ready():
    state = json.load(open(FN_STATE, 'r'))
    return state['evaluator_context_ready'] == 1

def is_evaluation_complete():
    state = json.load(open(FN_STATE, 'r'))
    return state['evaluation_complete'] == 1



if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--fpga", dest='use_fpga', action='store_true')
    parser.add_argument("--cuda", dest='use_cuda', action='store_true')
    parser.add_argument("--host", dest="HOST", default="localhost")
    args = parser.parse_args()
    server_ip = args.HOST
    print("Starting a server", server_ip)
    if args.use_fpga:
        fase.USE_FPGA = True
    elif args.use_cuda:
        fase.USE_CUDA = True

    # import HEAAN_Evaluator *after* setting which HEAAN variants to use
    from evaluator import HEAAN_Evaluator
    celery_app.tasks.register(HEAAN_Evaluator())

    #evaluator = HE
    flask_app.run(ssl_context=('cert.pem', 'key.pem'), host=server_ip, port=4443)
