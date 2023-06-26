import numpy as np
import tarfile
import pickle
import torch
from time import time, sleep

from bbsQt.constants import HEAAN_CONTEXT_PARAMS, CAM_NAMES

DEBUG = True

from fase.core.heaan import he
from fase.hnrf.hetree import HNRF
from fase import hnrf as hnrf
from fase.hnrf.tree import NeuralTreeMaker
from fase.hnrf import heaan_nrf 
from fase.core.heaan import HEAANContext


def slow_print(line):
    for xx in line:
        sleep(0.005)
        print(hex(xx), end='\\')

def encrypt(scheme, val, parms):
    ctxt = he.Ciphertext()#logp, logq, n)
    vv = np.zeros(parms.n) # Need to initialize to zero or will cause "unbound"
    vv[:len(val)] = val
    scheme.encrypt(ctxt, he.Double(vv), parms.n, parms.logp, parms.logq)
    del vv
    return ctxt

class Param():
    def __init__(self, n=None, logn=None, logp=None, logq=None, logQboot=None):
        self.n = n
        self.logn = logn
        self.logp = logp
        self.logq = logq 
        self.logQboot = logQboot
        if self.logn == None:
            self.logn = int(np.log2(n))


def compress_files(fn_tar, fn_list):
    with tarfile.open(fn_tar, "w:gz") as tar:
        for name in fn_list:
            tar.add(name)


def print_binary(s):
    return ' '.join(map('{:02X}'.format, s))

def show_file_content(fn):
    with open(fn, 'rb') as fbin:
        line = fbin.read(200)
        print("\n <<<<file in HEX>>>>")
        slow_print(line)


class HEAAN_Evaluator():
    def __init__(self, server_path, evaluator_ready=None):

        logq = HEAAN_CONTEXT_PARAMS['logq']#540
        logp = HEAAN_CONTEXT_PARAMS['logp']#30
        logn = HEAAN_CONTEXT_PARAMS['logn']#14
        #logq = 150
        #logn = 14
        
        n = 1*2**logn
        print("XXXXXXXXXXXXXXX", logn, logp, logq)

        self.parms = Param(n=n, logp=logp, logq=logq)
        self.server_path = server_path
        self.key_path = server_path
        print("[ENCRYPTOR] key path", self.key_path)
        
        
        self.hec = HEAANContext(logn, logp, logq, rot_l=[1], 
                   key_path=self.key_path,
                   FN_SK="secret.key",
                   boot=False, 
                   is_owner=False,
                   load_sk=False
                  )

        ## DEBUGGING
        #self.sk = he.SecretKey(self.key_path + 'secret.key')
        self.prepare_model_load()

        print("[Encryptor] HEAAN is ready")
        if evaluator_ready is not None: evaluator_ready.set()

    def prepare_model_load(self,
                           dilatation_factor = 10,
                           polynomial_degree = 10):
        """
        Prepare a polynomial form of tanh function
        to load requested models.

        Models will be stored as dict
        """
        self.models = {}
        
        self.my_tm_tanh = NeuralTreeMaker(torch.tanh, 
                            use_polynomial=True,
                            dilatation_factor=dilatation_factor, 
                            polynomial_degree=polynomial_degree)

    def load_model(self, action, cam):
        print("[Evaluator] Loading trained NRF models")

        t0 = time()
        fn = self.server_path+f"models/Nmodel_{action}_{cam}.pickle"
        Nmodel = pickle.load(open(fn, "rb"))
        
        h_rf = HNRF(Nmodel)
        try:
            sk = self.hec.sk
        except:
            sk = None
        nrf_evaluator = heaan_nrf.HETreeEvaluator(h_rf,
                                                    self.hec._scheme,
                                                    self.hec.parms,
                                                    self.my_tm_tanh.coeffs,
                                                    do_reduction = False,
                                                    sk = sk,#self.hec.sk ### DEBUGGING
                                                    silent=False)
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

        print("[EVALUATOR] running model...", model)
        return model(ctx)

    def start_evaluate_loop(self, q_text, e_enc):
        """
        filename : ctxt_a05_{i}.dat, where a05 means action #5.
        """
        print("[EVALUATOR] evaluate_loop started")
        while True:
            e_enc.wait()
            if DEBUG: print("[EVALUATOR] e_enc set")
            #fn_data = self.server_path + q_text.get()
            fn_data = q_text.get()
            if DEBUG: print("[EVALUATOR] got a file", fn_data)
            _, action, _cam, _ = fn_data.split("/")[-1].split("_")
            action = int(action)
            cam = CAM_NAMES[action]

            if DEBUG: print("[EVALUATOR] action class:", action)
            
            ctx = he.Ciphertext(self.parms.logp, self.parms.logq, self.parms.n)
            he.SerializationUtils.readCiphertext(ctx, fn_data)
            show_file_content(fn_data)
            e_enc.clear()
            
            t0 = time()
            
            # debugging = True
            # if debugging:
            #     fn_preds = []
            #     for i in range(5):
            #         fn = self.server_path+f"pred_{i}.dat"
            #         fn_preds.append(fn)
            #     fn_tar = FN_PREDS#"preds.tar.gz"
            #     print("@@@@@@@@@@@@ compressing files")
            #     compress_files(fn_tar, fn_preds)
            #     q_text.put({"root_path":self.server_path,  # Not using root path
            #             "filename":self.server_path+fn_tar})
            #     e_ans.set()run_model
            #     continue

            # ###############################################

            # # DEBUGGING
            # #print("CTX OK?")
            # #print(self.hec.decrypt(ctx))
            # ###############################################

            preds = self.run_model(action, cam, ctx)
            print(f"[EVALUATOR] Prediction took {time()-t0:.2f} seconds")

            fn_preds = []
            for i, pred in enumerate(preds):
                print("PRED", i, pred)
                fn = self.server_path+f"pred_{i}.dat"
                he.SerializationUtils.writeCiphertext(pred, fn)
                fn_preds.append(f"pred_{i}.dat")
            # if tar:
            #     fn_tar = FN_PREDS#"preds.tar.gz"
            #     compress_files(fn_tar, fn_preds)
            #     q_text.put({"root_path":self.server_path,  # Not using root path
            #             "filename":fn_tar})
            #             #"filename":self.server_path+fn_tar})
            # e_ans.set()

    def eval_once(self, fn_data, action):
        ctx = he.Ciphertext(self.parms.logp, self.parms.logq, self.parms.n)
        he.SerializationUtils.readCiphertext(ctx, fn_data)
        show_file_content(fn_data)

        print("action", action)
        cam = CAM_NAMES[action]
        print("cam", cam)

        t0 = time()
        preds = self.run_model(action, cam, ctx)
        print(f"[EVALUATOR] Prediction took {time()-t0:.2f} seconds")

        fn_preds = []
        for i, pred in enumerate(preds):
            #print("PRED", i, pred)
            
            fn = self.server_path+f"predict{i}.dat" # name changed
            he.SerializationUtils.writeCiphertext(pred, fn)
            fn_preds.append(fn)
