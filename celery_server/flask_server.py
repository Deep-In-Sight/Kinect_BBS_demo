from flask import Flask 
from flask import request
from werkzeug.utils import secure_filename
from flask import send_from_directory
from celery import Celery
import json
from bbsconfig import FN_STATE, REDIS_BROKER_URL, REDIS_RESULT_URL
from utils import gen_empty_state

import fase
import argparse
from logging.config import dictConfig

server_ip = ["192.168.0.18", "127.0.0.1"][1]
server_port = ["5000"][0]


dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})


app = Flask(__name__,static_folder='./static',template_folder = './templates')

# Configure the redis server
app.config['CELERY_BROKER_URL'] = REDIS_BROKER_URL
app.config['result_backend'] = REDIS_RESULT_URL

# celery from CMD will invoke this instance of celery
celery_app = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery_app.conf.update(app.config)


tasks = celery_app.tasks.keys()
print(tasks)

def ready_for_connection_test(fn_in):
    with open(fn_in, "a") as fout:
        fout.write(">>>> Connection GOOD\n")

def is_evaluator_ready():
    state = json.load(open(FN_STATE, 'r'))
    return state['evaluator_context_ready'] == 1

def is_evaluation_complete():
    state = json.load(open(FN_STATE, 'r'))
    return state['evaluation_complete'] == 1

@app.route('/upload',methods=['POST'])
@celery_app.task(name='webserver.get_post')
def get_post():
    if request.method=='POST':
        
        f=request.files['file']
        f.save(secure_filename(f.filename)) # 
        if request.headers['dtype']=="enc_key":
            msg = "stored ENCKEY"
            app.logger.info("Received ENCKEY")
        elif request.headers['dtype']=="mul_key":
            msg = "stored MULKEY"
            app.logger.info("Received MULKEY")
        elif request.headers['dtype']=="ctxt":
            if not is_evaluator_ready():
                app.logger.info("Evaluator not ready")
                return "evaluator not ready"
        
            app.logger.info("Received ciphertext")
            action = request.headers['action']
            # The following task MUST be sent to a specific queue/worker
            # to avoid re-initializing the evaluator.
            tid = celery_app.send_task('my_app.tasks.HEAAN_Evaluator', args=(f.filename, action))
            app.logger.info("Sent task to evaluator")
            msg = "task assigned"
        elif request.headers['dtype']=="test":
            print("Received test")
            ready_for_connection_test(f.filename)
            msg = "Connection Check"

        return msg

@app.route('/result',methods=['GET'])
@celery_app.task(name='webserver.give_result')
def give_result():
    """GET method. 
    계산이 끝나고 파일이 준비되면 클라이언트가 GET을 성공하게 될 것.
    """
    if request.method=='GET':
        if not is_evaluation_complete:
            return "evaluation not complete. Please try again later"
        # May also check if action is correct
        print("Evaluation complete. Sending result")
        return send_from_directory("result/", "test_out.txt")#"pred_0.dat")

def on_raw_message(body):
    print("Received: {0!r}".format(body))

if __name__=="__main__":
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
    #from evaluator import HEAAN_Evaluator
    celery_app.tasks.register(HEAAN_Evaluator())
    
    gen_empty_state()

    app.run(host=server_ip, debug=True, port=server_port)

