from celery import Task
import numpy as np
import pickle
import torch
from time import time
import json

from constants import FN_PREDS, HEAAN_CONTEXT_PARAMS, CAM_NAMES
from bbsconfig import FN_STATE, REDIS_BROKER_URL, REDIS_RESULT_URL, \
    SEVER_PATH, MODEL_PATH, KEY_PATH

#from hemul.heaan import he   
#from hemul import heaan
#import fase.HEAAN as he
#from fase.heaan_loader import load
#he = load()
#import fase.core.heaan as he
from fase.hnrf.hetree import HNRF
from fase.hnrf import heaan_nrf
from fase.hnrf.tree import NeuralTreeMaker
from fase.core.common import HEAANContext
#from hemul.hnrf.hnrf import HNRF, HETreeEvaluator
#from hemul.hnrf.nrf import NeuralTreeMaker

from utils import show_file_content
#from celery import current_app

class Param():
    def __init__(self, n=None, logn=None, logp=None, logq=None, logQboot=None):
        self.n = n
        self.logn = logn
        self.logp = logp
        self.logq = logq 
        self.logQboot = logQboot
        if self.logn == None:
            self.logn = int(np.log2(n))

class HEAAN_Evaluator(Task):
    """Celery class based Task."""
    name = "my_app.tasks.HEAAN_Evaluator"
    def __init__(self):
        logq = HEAAN_CONTEXT_PARAMS['logq']#540
        logp = HEAAN_CONTEXT_PARAMS['logp']#30
        logn = HEAAN_CONTEXT_PARAMS['logn']#14
        n = 1*2**logn

        self.parms = Param(n=n, logp=logp, logq=logq)
        self.server_path = SEVER_PATH
        self.key_path = KEY_PATH
        self.model_path = MODEL_PATH
        print("[ENCRYPTOR] key path", self.key_path)

        hec = HEAANContext(logn, logp, logq, rot_l=[1], 
                   key_path=self.key_path,
                   #FN_SK="secret.key",
                   boot=False, 
                   is_owner=False
                  )

        ## DEBUGGING
        #self.sk = he.SecretKey(self.key_path + 'secret.key')
        self.hec = hec
        self.models = {} # Models will be stored as dict
        self.activation = self.get_activation()

        print("[Encryptor] HEAAN is ready")
        #if evaluator_ready is not None: 
        evaluator_ready()
        #app.send_task('webserver.ready_for_ctxt', args=[True])


    def get_activation(self,
                           dilatation_factor = 10,
                           polynomial_degree = 10):
        """
        Prepare a polynomial form of tanh function
        to load requested models.
        """
        return NeuralTreeMaker(torch.tanh, 
                            use_polynomial=True,
                            dilatation_factor=dilatation_factor, 
                            polynomial_degree=polynomial_degree)

    def load_model(self, action, cam):
        print("[Evaluator] Loading trained NRF models")

        t0 = time()
        fn = self.model_path+f"Nmodel_{action}_{cam}.pickle"
        Nmodel = pickle.load(open(fn, "rb"))
        
        h_rf = HNRF(Nmodel)
        try:
            sk = self.hec.sk
        except:
            sk = None
        nrf_evaluator = heaan_nrf.HETreeEvaluator(h_rf,
                                        self.hec._scheme,
                                        self.hec.parms,
                                        self.activation.coeffs,
                                        do_reduction = False,
                                        sk = sk,#self.hec.sk ### DEBUGGING
                                        silent=True)
        print(f"[EVAL.model_loader] HNRF model loaded for class {action} in {time() - t0:.2f} seconds")
        #allmodels.append((f"{action}",nrf_evaluator))
        self.models.update({f"{action}_{cam}":nrf_evaluator})            
        #print("Model dict updated")    

    def _quick_check(self):
        scheme = self.scheme
        return True

    def run_model(self, action, cam, ctx):
        """Run model. If a model is not ready, load it first.
        """
        try:
            model = self.models[f"{action}_{cam}"]
        except:
            print("[Evaluator] Model not loaded yet")
            print(f"[Evaluator] Loading model for class {action} and camera {cam}")
            self.load_model(action, cam)
            model = self.models[f"{action}_{cam}"]

        print("[EVALUATOR] running model...")
        return model(ctx)

    def run(self, fn_data, action):
        action = int(action)
        print("[EVALUATOR] loading ciphertext", fn_data)
        print("[EVALUATOR] action", action)        
        cam = CAM_NAMES[action]
        print("cam", cam)

        with open("test_out.txt", "w") as f:
            f.write("test\n")
            f.write(f"{self.parms.logn}\n")
        evaluation_done("test_out.txt", action)
        return 
        ctx = he.Ciphertext(self.parms.logp, self.parms.logq, self.parms.n)
        he.SerializationUtils.readCiphertext(ctx, fn_data)
        show_file_content(fn_data)

        

        t0 = time()
        preds = self.run_model(action, cam, ctx)
        print(f"[EVALUATOR] Prediction took {time()-t0:.2f} seconds")

        fn_preds = []
        for i, pred in enumerate(preds):
            #print("PRED", i, pred)
            
            fn = self.server_path+f"predict{i}.dat" # name changed
            he.SerializationUtils.writeCiphertext(pred, fn)
            fn_preds.append(fn)

        evaluation_done(fn, action)
        #app.send_task('webserver.ready_for_get', kwargs={"action":action})


#current_app.tasks.register(HEAAN_Evaluator())

#app = HEAAN_Evaluator()

# Configure the redis server
#app.config['CELERY_BROKER_URL'] = REDIS_BROKER_URL
#app.config['result_backend'] = REDIS_RESULT_URL

DEBUG = True


def evaluation_done(fn, action):
    state = json.load(open(FN_STATE, 'r'))
    state['evaluation_complete'] = 1
    state['pred_fn'] = fn
    state['current_action'] = action
    json.dump(state, open(FN_STATE, 'w'))

def evaluator_ready():
    state = json.load(open(FN_STATE, 'r'))
    state['evaluator_context_ready'] = 1
    json.dump(state, open(FN_STATE, 'w'))


#if __name__ == '__main__':
    # Set which version of HEAAN to use
    #parser = argparse.ArgumentParser()

    #parser.add_argument("--fpga", dest='use_fpga', action='store_true')
    #parser.add_argument("--cuda", dest='use_cuda', action='store_true')
    #args = parser.parse_args()

    #if args.use_fpga:
    #    hemul.USE_FPGA = True
    #elif args.use_cuda:
    #    hemul.USE_CUDA = True
    # import HEAAN_Evaluator *after* setting which HEAAN variants to use
    #from bbsQt.core.evaluator import HEAAN_Evaluator
    #app.init()
    