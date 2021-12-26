from fase import HEAAN
import fase.HEAAN as he
import numpy as np
import os 
import time
import tarfile

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

def decrypt(scheme, secretKey, enc, parms):
    featurized = scheme.decrypt(secretKey, enc)
    arr = np.zeros(parms.n, dtype=np.complex128)
    featurized.__getarr__(arr)
    return arr.real

def encrypt(scheme, val, parms):
    ctxt = he.Ciphertext()#logp, logq, n)
    vv = np.zeros(parms.n) # Need to initialize to zero or will cause "unbound"
    vv[:len(val)] = val
    scheme.encrypt(ctxt, he.Double(vv), parms.n, parms.logp, parms.logq)
    del vv
    return ctxt


def compress_files(fn_tar, fn_list):
    with tarfile.open(fn_tar, "w:gz") as tar:
        for name in fn_list:
            tar.add(name)


class HEAAN_Encryptor():
    def __init__(self, q_text, e_key, lock, key_path, debug=True, tar=True):
        lock.acquire()# 이렇게 하는건가? 

        logq = 540
        logp = 30
        logn = 14
        n = 1*2**logn

        self.parms = Param(n=n, logp=logp, logq=logq)
        self.key_path = key_path
        if debug: print("[ENCRYPTOR] key path", key_path)

        do_reduction = False
        is_serialized = True

        self.ring = he.Ring()
        
        self.secretKey = HEAAN.SecretKey(self.ring)
        self.scheme = he.Scheme(self.secretKey, self.ring, is_serialized, key_path)
        self.algo = he.SchemeAlgo(self.scheme)
        self.scheme.addLeftRotKey(self.secretKey, 1)

        if tar:
            fn_tar = "keys.tar.gz"
            compress_files(fn_tar, [key_path+'serkey/'+fn for fn in FN_KEYS])
            q_text.put({"root_path":key_path, 
                       "keys_to_share":fn_tar})
        else:
            # Keys are ready
            q_text.put({"root_path":key_path + 'serkey/',
                    "keys_to_share":FN_KEYS})
        e_key.set()
        if debug: print("[Encryptor] HEAAN is ready")

        # Check HEAAN
        # val = np.arange(10)
        # ctxt = encrypt(self.scheme, val, self.parms)
        # print(ctxt.n, ctxt.logp, ctxt.logq)
        # del ctxt


        lock.release()

    def _quick_check(self):
        scheme = self.scheme

        return True

    def get_keys(self):
        #print("good to go") 
        #sk = q1.get()
        pass

    def start_encrypt_loop(self, q1, e_sk, e_enc, debug=True):
        """
        When skeleton is ready (e_sk), get the skeleton from q1, 
        encrypt, and store it as ctx_{i}.dat file. 
        """
        scheme = self.scheme
    
        i=0
        while True:
            e_sk.wait()
            print("[Encryptor] good to go") 
            sk = q1.get()
            
            e_sk.clear() # reset skeleton event
            
            if debug: print("[Encryptor] e_enc set?", e_enc.is_set())
            if not 'skeleton' in sk.keys():
                raise LookupError("Can't find skeleton in queue")    
            if debug: print("[Encryptor] Got a skeleton, Encrypting...")
            if debug: print("[Encryptor] Length of the skeleton:", len(sk["skeleton"]))
            fn = f"/home/hoseung/Work/Kinect_BBS_demo/ctx_{i}.dat"
            ctx1 = encrypt(scheme, sk['skeleton'][0], self.parms)

            #val = np.arange(10)
            #print(self.parms.n, self.parms.logp, self.parms.logq)
            #ctx1 = encrypt(scheme, val, self.parms)
            print(ctx1.n, ctx1.logp, ctx1.logq)
            if debug: print("[Encryptor] Ctxt encrypted")
            he.SerializationUtils.writeCiphertext(ctx1, fn)
            if debug: print("[Encryptor] Ctxt wrote")

            q1.put({"fn_enc_skeleton": fn})
            if debug: print("[Encryptor] skeleton encrypted and saved as", fn)
            e_enc.set() # Tell encryption is done and file is ready
            del ctx1 

            time.sleep(1)
            if debug: print("[Encryptor] Waiting...")

