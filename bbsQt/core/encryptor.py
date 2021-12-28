from fase import HEAAN
import fase.HEAAN as he
import numpy as np
import os 
import pickle
import tarfile
from bbsQt.constants import FN_KEYS, HEAAN_CONTEXT_PARAMS
from fase.hnrf.cryptotree import HomomorphicNeuralRandomForest
from sklearn import preprocessing

from time import time
#from fase.hnrf.cryptotree import HomomorphicNeuralRandomForest
#from fase.hnrf import heaan_nrf 

# FN_KEYS = ["ENCRYPTION.txt",
#            "MULTIPLICATION.txt",
#            "ROTATION_1.txt"]

class HomomorphicTreeFeaturizer:
    """Featurizer used by the client to encode and encrypt data.
       모든 Context 정보를 다 필요로 함. 이것만 따로 class를 만들고 CKKS context 보내기 좀 귀찮은데? 
    """
    def __init__(self, comparator: np.ndarray,
                 scheme, 
                 ckks_parms,
                 use_symmetric_key=False):
        self.comparator = comparator
        self.scheme = scheme
        #self.encoder = encoder
        self._parms = ckks_parms
        self.use_symmetric_key = use_symmetric_key

    def encrypt(self, x: np.ndarray):
        features = x[self.comparator]
        features[self.comparator == -1] = 0
        features = list(features)

        ctx = self._encrypt(features)
        return ctx

    def _encrypt(self, val, n=None, logp=None, logq=None):
        if n == None: n = self._parms.n
        if logp == None: logp = self._parms.logp
        if logq == None: logq = self._parms.logq

        ctxt = HEAAN.Ciphertext()#logp, logq, n)
        vv = np.zeros(n) # Need to initialize to zero or will cause "unbound"
        vv[:len(val)] = val
        self.scheme.encrypt(ctxt, HEAAN.Double(vv), n, logp, logq)
        del vv
        return ctxt

    def save(self, path:str):
        pickle.dump(self.comparator, open(path, "wb"))


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
    def __init__(self, q_text, e_key, lock, key_path, 
                debug=True, tar=True, test=False):
        #lock.acquire()# 이렇게 하는건가? 

        logq = HEAAN_CONTEXT_PARAMS['logq']#540
        logp = HEAAN_CONTEXT_PARAMS['logp']#30
        logn = HEAAN_CONTEXT_PARAMS['logn']#14
        n = 1*2**logn

        self.parms = Param(n=n, logp=logp, logq=logq)
        self.key_path = key_path
        if debug: print("[ENCRYPTOR] key path", key_path)

        is_serialized = True

        self.ring = he.Ring()
        
        self.secretKey = HEAAN.SecretKey(self.ring)
        self.scheme = he.Scheme(self.secretKey, self.ring, is_serialized, key_path)
        self.algo = he.SchemeAlgo(self.scheme)
        self.scheme.addLeftRotKey(self.secretKey, 1)

        self.set_featurizers()
        self.load_scalers()
        if tar:
            if test:
                # Very small file for test purpose
                # Real files should had been passed to the server in advance.
                fn_tar = "test.tar.gz"
            else:
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

    def set_featurizers(self):
        scheme = self.scheme
        parms = self.parms

        featurizers =[]
        
        for action in range(1,2):
            t0 = time()
            Nmodel = pickle.load(open(f"./models/trained_NRF_{action}.pickle", "rb"))
            
            h_rf = HomomorphicNeuralRandomForest(Nmodel)
            #h_rf = pickle.load(open(f"./trained_rf_{action}.pickle", "rb"))
            featurizers.append((action,HomomorphicTreeFeaturizer(h_rf.return_comparator(), scheme, parms)))
            print(f"Loading featurizer took {time() - t0:.2f} s")
        self.featurizers = dict(featurizers)

    def load_scalers(self):
        scalers =[]
        for action in [1,13]:#range(1,15):
            sc = pickle.load(open(f'./models/scaler_a{action}.pickle', "rb"))
            scalers.append((action, sc))
            
        self.scalers = dict(scalers)

    def _quick_check(self):
        scheme = self.scheme

        return True

    def get_keys(self):
        #print("good to go") 
        #sk = q1.get()
        pass

    def start_encrypt_loop(self, q1, q_text, q_answer, e_sk, e_enc, e_ans, e_enc_ans, debug=True):
        """
        When skeleton is ready (e_sk), get the skeleton from q1, 
        encrypt, and store it as ctx_{i}.dat file. 
        """
        scheme = self.scheme
        parms = self.parms

        

        i=0
        while True:
            e_sk.wait()  ## FLOW CONTROL
            print("[Encryptor] good to go") 
            sk = q1.get()  ## FLOW CONTROL
            
            e_sk.clear()  ## FLOW CONTROL: reset skeleton event
            
            if not 'skeleton' in sk.keys():
                raise LookupError("Can't find skeleton in queue")    
            if debug: print("[Encryptor] Got a skeleton, Encrypting...")
            if debug: print("[Encryptor] Length of the skeleton:", len(sk["skeleton"]))
            action = sk['action']

            sc = self.scalers[action]
            fn = f"ctx_a{action:02d}_{i}.dat"
            #ctx1 = encrypt(scheme, sk['skeleton'][0], self.parms)
            

            featurizer = self.featurizers[action]
            #print(len(sk['skeleton']))
            print("+++++++++++++++  SKELETON POINTS  ++++++++++++++++")
            print(sk['skeleton'])
            
            print("Featurizing skeleton...")
            t0 = time()
            
            ##### 스켈레톤 하나만 선정해서 들어오는데 리스트에 싸여있을 이유가 없음... [0] 없애자. 
            rav_sub = sk['skeleton'][0]
            
            scaled = sc.transform(rav_sub.reshape(1,-1))
            ctx1 = featurizer.encrypt(scaled[0])
            pickle.dump(scaled[0], open("scaled.pickle", "wb"))
            print(f"Featurizing done in {time() - t0:.2f}s")
            print(ctx1.n, ctx1.logp, ctx1.logq)
            if debug: print("[Encryptor] Ctxt encrypted")
            he.SerializationUtils.writeCiphertext(ctx1, fn)
            if debug: print("[Encryptor] Ctxt wrote")

            ############
            ddd = decrypt(self.scheme, self.secretKey, ctx1, self.parms)
            ctx2 = he.Ciphertext(self.parms.logp, self.parms.logq, self.parms.n)
            he.SerializationUtils.readCiphertext(ctx2, fn)
            ddd2 = decrypt(self.scheme, self.secretKey, ctx2, self.parms)
            print(ddd)
            print(ddd2)
            ###########
            q1.put({"fn_enc_skeleton": fn})  ## FLOW CONTROL
            if debug: print("[Encryptor] skeleton encrypted and saved as", fn)
            e_enc.set()  ## FLOW CONTROL: encryption is done and file is ready
            
            if debug: print("[Encryptor] Waiting for prediction...")

            # Decrypt answer
            e_enc_ans.wait()  ## FLOW CONTROL
            preds = []
            fn_preds = q_text.get()  ## FLOW CONTROL
            print("fn_preds", fn_preds)
            for fn_ctx in fn_preds:
                print("[encryptor] make an empty ctxt")
                ctx_pred = he.Ciphertext(ctx1.logp, ctx1.logq, ctx1.n) # 나중에 오는 애는 logq가 다를 수도 있음
                print("[encryptor] load ctxt", fn_ctx)
                he.SerializationUtils.readCiphertext(ctx_pred, fn_ctx)
                print("[encryptor] decrypt ctxt", ctx_pred)
                dec=decrypt(self.scheme, self.secretKey, ctx_pred, self.parms)
                print("[encryptor] append decrypted ctxt")
                preds.append(np.sum(dec))
                print("[encryptor] decrypted prediction array", dec[:10])
                del ctx_pred
            del ctx1 


            ##########################
            with open("params.txt", "r") as ll:
                s = ll.readline().split(" ")
                llogp1, llogq1, ln1 = int(s[0]),int(s[1]),int(s[2])
                s = ll.readline().split(" ")
                llogp2, llogq2, ln2 = int(s[0]),int(s[1]),int(s[2])
                s = ll.readline().split(" ")
                llogp3, llogq3, ln3 = int(s[0]),int(s[1]),int(s[2])
            
            ctx = he.Ciphertext(llogp1, llogq1, ln1) # 나중에 오는 애는 logq가 다를 수도 있음
            print("[encryptor] b1_ctxt", ctx)
            he.SerializationUtils.readCiphertext(ctx, "b1_ctx.dat")
            print(decrypt(self.scheme, self.secretKey, ctx, self.parms))
            del ctx
            
            ctx = he.Ciphertext(llogp2, llogq2, ln2) # 나중에 오는 애는 logq가 다를 수도 있음
            print("[encryptor] compare_after_activation", ctx)
            he.SerializationUtils.readCiphertext(ctx, "compare_after_add.dat")
            print(decrypt(self.scheme, self.secretKey, ctx, self.parms))
            del ctx

            ctx = he.Ciphertext(llogp3, llogq3, ln3) # 나중에 오는 애는 logq가 다를 수도 있음
            print("[encryptor] compare_after_activation", ctx)
            he.SerializationUtils.readCiphertext(ctx, "compare_after_activation.dat")
            print(decrypt(self.scheme, self.secretKey, ctx, self.parms))
            del ctx

            ###########################

            print("preds", preds)
            ans_str = f"Predicted score: {np.argmax(preds)}"
            print(ans_str)
            e_enc_ans.clear()  ## FLOW CONTROL
            
            # 복호화된 결과 QT로 전송
            q_answer.put(ans_str)  ## FLOW CONTROL
            e_ans.set()  ## FLOW CONTROL

            i+=1


