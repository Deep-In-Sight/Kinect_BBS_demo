from flask import Flask 
from flask import request
from werkzeug.utils import secure_filename
from flask import send_from_directory
from celery import Celery
import json
from config import FN_STATE, REDIS_BROKER_URL, REDIS_RESULT_URL
from utils import gen_empty_state

from logging.config import dictConfig

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
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)


def is_evaluator_ready():
    state = json.load(open(FN_STATE, 'r'))
    return state['evaluator_context_ready'] == 1

def is_evaluation_complete():
    state = json.load(open(FN_STATE, 'r'))
    return state['evaluation_complete'] == 1

@app.route('/upload',methods=['POST'])
@celery.task(name='webserver.get_post')
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
            tid = celery.send_task('HEAAN_Evaluator.eval_once', args=(f.filename, action))
            app.logger.info("Sent task to evaluator")
            msg = "task assigned"

        return msg

@app.route('/result',methods=['GET'])
@celery.task(name='webserver.give_result')
def give_result():
    """GET method. 
    계산이 끝나고 파일이 준비되면 클라이언트가 GET을 성공하게 될 것.
    """
    if request.method=='GET':
        if not is_evaluation_complete:
            return "evaluation not complete. Please try again later"
        # May also check if action is correct
        return send_from_directory("result/", "pred_0.dat")

def on_raw_message(body):
    print("Received: {0!r}".format(body))

if __name__=="__main__":
    gen_empty_state()
    app.run(host="192.168.0.18", debug=True, port=5000)
