from flask import Flask 
from flask import request
from werkzeug.utils import secure_filename
from flask import send_from_directory
from celery import Celery

app = Flask(__name__,static_folder='./static',template_folder = './templates')

# Configure the redis server
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['result_backend'] = 'redis://localhost:6379/0'

# celery from CMD will invoke this instance of celery
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

@app.route('/upload',methods=['POST'])
def upload_file2():
    if request.method=='POST':
        f=request.files['file']
        f.save(secure_filename(f.filename)) # 
        if request.headers['dtype']=="enc_key":
            msg = "stored ENCKEY"
        elif request.headers['dtype']=="ctxt":
            print("Received ciphertext")
            action = request.headers['action']
            print("Calling HEAAN")
            result = call_heaan.delay(f.filename, action)
            # celery.task.apply_async offers more control over the task
            # than .delay()
            # The above decorated function returns "AsyncResult" object
            # MUST call get() or forget() to release the resource
            # propagate: re-raise exception if it fails
            msg = result.get(on_message=on_raw_message, propagate=False)

        return "good"

@app.route('/result',methods=['GET'])
def get_result():
    """GET method. 
    계산이 끝나고 파일이 준비되면 클라이언트가 GET을 성공하게 될 것.
    """
    if request.method=='GET':
        return send_from_directory("result/", "pred_0.dat")

def on_raw_message(body):
    print("Received: {0!r}".format(body))

@celery.task(bind=True) # bind if access to the instance is needed
def call_heaan(self, fn, action):
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
    print("HEAAN called")
    
    # do calculation
    with open(fn, "r") as f:
        new_fn = f.read().splitlines()[0]
    
    self.update_state(state="PROGRESS")
        
    with open(new_fn, "w") as f:
        f.write("New file\n")
        f.write(f"Action == {action}")

    self.update_state(state="SUCCESS")

    return "HEAAN Inference done!"


if __name__=="__main__":
    app.run(host="192.168.0.18")
