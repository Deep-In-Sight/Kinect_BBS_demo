from fase import HEAAN
import fase.HEAAN as he
import numpy as np
import os

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


class HEAAN_Evaluator():
    def __init__(self, e_key, lock, key_path, e_ans):
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
        
        e_key.wait()
        if not key_found(key_path):
            self.get_keys()
        
        self.scheme = he.Scheme(self.ring, True, key_path)
        self.algo = he.SchemeAlgo(self.scheme)
        self.scheme.loadLeftRotKey(1)
        print("[Encryptor] HEAAN is ready")
        e_ans.set()


    def _quick_check(self):
        scheme = self.scheme

        return True

    def get_keys(self):
        #print("good to go") 
        #sk = q1.get()
        pass

    def start_encrypt_loop(self, q1, e_enc, e_ans):
        pass