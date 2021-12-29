import numpy as np
import os
import tarfile
import pickle
import torch

import fase
fase.USE_FPGA = True
from fase.core.heaan import he
#from fase import heaan_loader
#he = heaan_loader.load()
from fase.hnrf.cryptotree import HomomorphicNeuralRandomForest
from time import time
from fase import hnrf as hnrf
from fase.hnrf.tree import NeuralTreeMaker
from fase.hnrf import heaan_nrf 
#from fase.hnrf.heaan_nrf import HomomorphicModel 

from bbsQt.constants import FN_KEYS, FN_PREDS, HEAAN_CONTEXT_PARAMS

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

def key_found(key_path):
    all_found = []
    for fn in FN_KEYS:
        this_fn = key_path + fn
        found = os.path.isfile(this_fn)
        all_found.append(found)
        print(f"{this_fn} is","found" if found else "missing" )
    
    return np.all(all_found)


def compress_files(fn_tar, fn_list):
    with tarfile.open(fn_tar, "w:gz") as tar:
        for name in fn_list:
            tar.add(name)


def print_binary(s):
    return ' '.join(map('{:02X}'.format, s))

def show_file_content(fn):
    with open(fn, 'rb') as fbin:
        line = fbin.read(100)
        print("file in binary format", line)
        print("file in HEX", print_binary(line))


class HEAAN_Evaluator():
    def __init__(self, lock, key_path, e_ans):
        lock.acquire()# 이렇게 하는건가? 
        logq = HEAAN_CONTEXT_PARAMS['logq']#540
        logp = HEAAN_CONTEXT_PARAMS['logp']#30
        logn = HEAAN_CONTEXT_PARAMS['logn']#14
        n = 1*2**logn

        self.parms = Param(n=n, logp=logp, logq=logq)
        self.key_path = key_path
        print("[ENCRYPTOR] key path", key_path)

        self.ring = he.Ring()
        
        if not key_found(key_path):
            self.get_keys()
        
        self.scheme = he.Scheme(self.ring, True, key_path)
        self.algo = he.SchemeAlgo(self.scheme)
        self.scheme.loadLeftRotKey(1)
        
        self.load_models()
        print("[Encryptor] HEAAN is ready")
        # models = []
        # for i in range(1,15):
        #     model = BBS_Evaluator_model(action=i, 
        #             trained_model_path='./trained_models/')
        #     models.append((f"{i}",model))
        # self.models = dict(models)
        print(self.models)
        e_ans.set()

    def load_models(self):
        print("[Evaluator] Loading trained NRF models")
        dilatation_factor = 10
        polynomial_degree = 10

        my_tm_tanh = NeuralTreeMaker(torch.tanh, 
                            use_polynomial=True,
                            dilatation_factor=dilatation_factor, 
                            polynomial_degree=polynomial_degree)


        t0 = time()
        allmodels = []
        for action in range(1,3):
            try:
                Nmodel = pickle.load(open(f"models/trained_model{action}_e_s.pickle", "rb"))
            except:
                Nmodel = pickle.load(open(f"models/trained_model{action}_a_s.pickle", "rb"))
            h_rf = HomomorphicNeuralRandomForest(Nmodel)
            print("[EVAL.model_loader] HRF loaded for class", action)
            nrf_evaluator = heaan_nrf.HomomorphicTreeEvaluator.from_model(h_rf,
                                                                self.scheme,
                                                                self.parms,
                                                                my_tm_tanh.coeffs,
                                                                do_reduction = False,
                                                                #save_check=True
                                                                )
            print("[EVAL.model_loader] HNRF model loaded for class", action)
            
            allmodels.append((f"{action}",nrf_evaluator))
        self.models = dict(allmodels)

        print(f"generating 14 models took {time() - t0:.2f}")

    def _quick_check(self):
        scheme = self.scheme
        return True

    def get_keys(self):
        #print("good to go") 
        #sk = q1.get()
        pass

    def run_model(self, cc, ctx):
        print("Running model for class", cc)
        model = self.models[f"{cc}"]
        #featurizer = self.models[f"{cc}"]['featurizer']
        print("[Evaluator] running model...")
        #ctx = featurizer.encrypt(data)
        return model(ctx)
        #return self.predict(data)

    def start_evaluate_loop(self, q1, q_text, e_enc, e_ans, tar=True):
        """
        filename : ctxt_a05_{i}.dat, where a05 means action #5.
        """
        while True:
            e_enc.wait()
            fn_data = q_text.get()
            #fn_data = data['filename']
            print(fn_data)
            action = int(fn_data.split("ctx_a")[1][:2])
            print("[evaluator] action class:", action)
            ctx = he.Ciphertext(self.parms.logp, self.parms.logq, self.parms.n)
            he.SerializationUtils.readCiphertext(ctx, fn_data)
            show_file_content(fn_data)
            e_enc.clear()
            preds = self.run_model(action, ctx)

            fn_preds = []
            for i, pred in enumerate(preds):
                fn = f"pred_{i}.dat"
                he.SerializationUtils.writeCiphertext(pred, fn)
                fn_preds.append(fn)
            if tar:
                fn_tar = FN_PREDS#"preds.tar.gz"
                compress_files(fn_tar, fn_preds)
                q_text.put({"root_path":'./',  # Not using root path
                        "filename":fn_tar})
            e_ans.set()

    def predict_test(self, ctx):
        Nscore = 5
        preds = []
        for i in range(Nscore):
            pp = np.random.rand(self.parms.n)
            ctx = encrypt(self.scheme, pp, self.parms)
            preds.append(ctx)
        return preds
