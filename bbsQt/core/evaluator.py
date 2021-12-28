from bbsQt.core.encryptor import encrypt
from fase import HEAAN
import fase.HEAAN as he
import numpy as np
import os
import tarfile
import pickle

FN_KEYS = ["ENCRYPTION.txt",
           "MULTIPLICATION.txt",
           "ROTATION_1.txt"]

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


class HEAAN_Evaluator():
    def __init__(self, lock, key_path, e_ans):
        lock.acquire()# 이렇게 하는건가? 

        logq = 540
        logp = 30
        logn = 14
        n = 1*2**logn

        self.parms = Param(n=n, logp=logp, logq=logq)
        self.key_path = key_path
        print("[ENCRYPTOR] key path", key_path)

        do_reduction = False
        is_serialized = True

        self.ring = he.Ring()
        
        if not key_found(key_path):
            self.get_keys()
        
        self.scheme = he.Scheme(self.ring, True, key_path)
        self.algo = he.SchemeAlgo(self.scheme)
        self.scheme.loadLeftRotKey(1)
        print("[Encryptor] HEAAN is ready")

        models = []
        for i in range(1,15):
            model = BBS_Evaluator_model(action=i, 
                    trained_model_path='./trained_models/')
            models.append((f"{i}",model))
        self.models = dict(models)
        print(self.models)
        e_ans.set()


    def _quick_check(self):
        scheme = self.scheme
        return True

    def get_keys(self):
        #print("good to go") 
        #sk = q1.get()
        pass

    def run_model(self, cc, data):
        print("Running model for class", cc)
        model = self.models[f"{cc}"]
        #return model.predict(data)
        return self.predict(data)

    def start_evaluate_loop(self, q1, q_text, e_enc, e_ans, tar=True):
        """
        filename : ctxt_a05_{i}.dat, wherer a05 means action #5.
        """
        while True:
            e_enc.wait()
            fn_data = q_text.get()
            #fn_data = data['filename']
            print(fn_data)
            action = int(fn_data.split("ctx_a")[1][:2])
            print("[evaluator] action class:", action)
            ctx = he.Ciphertext()
            he.SerializationUtils.readCiphertext(ctx, fn_data)
            e_enc.clear()
            preds = self.run_model(action, ctx)

            fn_preds = []
            for i, pred in enumerate(preds):
                fn = f"pred_{i}.dat"
                he.SerializationUtils.writeCiphertext(pred, fn)
                fn_preds.append(fn)
            if tar:
                fn_tar = "preds.tar.gz"
                compress_files(fn_tar, fn_preds)
                q_text.put({"root_path":'./', 
                        "keys_to_share":fn_tar})
            e_ans.set()


    def predict(self, ctx):
        Nscore = 5
        preds = []
        for i in range(Nscore):
            pp = np.random.rand(self.parms.n)
            ctx = encrypt(self.scheme, pp, self.parms)
            preds.append(ctx)
        return preds

class BBS_Evaluator_model():
    """ All 14 models share the same context. 
        Only 
    """
    def __init__(self, action, trained_model_path="./"):
        #Nmodel = pickle.load(trained_model_path+f"bbs_trained_{action}.pickle")
        #self.evaluator = N
        pass
    
    def predict(self, ctxt):
        Nscore = 5
        preds = []
        for i in range(Nscore):
            pp = np.random.rand(self.parms.n)
            ctx = encrypt(self.scheme, pp, self.parms)
            preds.append(ctx)
        return preds