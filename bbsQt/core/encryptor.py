#from fase import HEAAN
import fase.HEAAN as he
import numpy as np
import os 
import pickle
import time
import tarfile
from bbsQt.constants import CAM_LIST, CAM_NAMES, FN_KEYS, HEAAN_CONTEXT_PARAMS, DEBUG, FN_SK
from fase.hnrf.hetree import HNRF
from fase.hnrf import heaan_nrf
from fase.hnrf.tree import NeuralTreeMaker
import torch
from time import sleep
import requests

sleep_time = 60 # allow server at least 60s to run inference

from bbsQt.model.data_preprocessing import shift_to_zero, measure_lengths
class HETreeFeaturizer:
    """Featurizer used by the client to encode and encrypt data.
       모든 Context 정보를 다 필요로 함. 
       이것만 따로 class를 만들고 CKKS context 보내기 좀 귀찮은데? 
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

        ctxt = he.Ciphertext()#logp, logq, n)
        vv = np.zeros(n) # Need to initialize to zero or will cause "unbound"
        vv[:len(val)] = val
        self.scheme.encrypt(ctxt, he.Double(vv), n, logp, logq)
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
    def __init__(self, server_url, key_path="./serkey/", 
                debug=True):
        
        self.server_url = f"http://{server_url}"
        print("Paired with server at", self.server_url)
        self.model_dir = "./models/"

        logq = HEAAN_CONTEXT_PARAMS['logq']#540
        logp = HEAAN_CONTEXT_PARAMS['logp']#30
        logn = HEAAN_CONTEXT_PARAMS['logn']#14
        n = 1*2**logn
        is_serialized = True

        self.parms = Param(n=n, logp=logp, logq=logq)
        self.key_path = key_path
        if debug: print("[ENCRYPTOR] key path", key_path)

        # Make dir for keys
        if not os.path.isdir(key_path): os.mkdir(key_path)

        self.ring = he.Ring()
        print("Loading secret key", key_path+FN_SK)
        self.secretKey = he.SecretKey(key_path+FN_SK)
        self.scheme = he.Scheme(self.ring, is_serialized, key_path)
        self.algo = he.SchemeAlgo(self.scheme)

        self.set_featurizers()
        self.load_scalers()

        if debug: print("[Encryptor] HEAAN is ready")

    def set_featurizers(self):
        scheme = self.scheme
        parms = self.parms

        featurizers =[]
        for action in range(1,15):
            cam = CAM_NAMES[action]
            Nmodel = pickle.load(open(self.model_dir+f"Nmodel_{action}_{cam}.pickle", "rb"))
            h_rf = HNRF(Nmodel)
            featurizers.append((f"{action}_{cam}", HETreeFeaturizer(h_rf.return_comparator(), scheme, parms)))
                
        self.featurizers = dict(featurizers)

    def load_scalers(self):
        
        scalers =[]
        for action in range(1,15):
            cam = CAM_NAMES[action]
            sc = pickle.load(open(self.model_dir+f'scaler_{action}_{cam}.pickle', "rb"))
            scalers.append((f"{action}_{cam}", sc))
            
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

        while True:
            e_sk.wait()  ## FLOW CONTROL
            print("[Encryptor] good to go") 
            sk = q1.get()  ## FLOW CONTROL
            "++++++++++++++++++++++++++ SKELETON POINTS ++++++++++++++++++++++"
            print(sk)
            
            e_sk.clear()  ## FLOW CONTROL: reset skeleton event
            
            if not 'skeleton' in sk.keys():
                raise LookupError("Can't find skeleton in queue")    
            if debug: print("[Encryptor] Got a skeleton, Encrypting...")
            if debug: print("[Encryptor] Length of the skeleton:", len(sk["skeleton"]))
            action = int(sk['action'])
            #cam = sk['cam']
            cam = CAM_NAMES[action] # No need to depend on the undeterministic camera order.

            sc = self.scalers[f"{action}_{cam}"]
            fn = f"ctx_{action:02d}_{cam}_.dat"
           
            t0 = time.time()            

            skeleton = sk['skeleton']

            # if DEBUG:
            #     scaled = sc.transform(skeleton)
            # else:
            #     rav_sub = skeleton[0]
            #     scaled = sc.transform(rav_sub.reshape(1,-1))
            
            if DEBUG:
                print("[ENCRYPTOR] DEBUGGING MODE !!!!!!!")
                scaled = sc.transform(skeleton)
            else:
                rav_sub = skeleton#[0]
                skeleton = shift_to_zero(skeleton)
                body = measure_lengths(skeleton)
                skeleton /= body['body'] 
                pickle.dump(skeleton, open("skeleton_org.pickle", "wb"))
                print("rav_sub", rav_sub.min(), rav_sub.max())
                scaled = sc.transform(rav_sub.reshape(1,-1))
                sc0 = scaled[0]
            
            
            #print("scaled", scaled.shape)
            print("Check for scales", sc0.min(), sc0.max())

            # Still some values can surpass 1.0. 
            # I need a more strict rule for standardization.. 
            # The following is an ad-hoc measure.
            

            featurizer = self.featurizers[f"{action}_{cam}"]
            if debug: print("Featurizing skeleton...")
            t0 = time.time()
            ctx1 = featurizer.encrypt(sc0)
            print("Encryption done in ", time.time() - t0, "seconds")
            pickle.dump(sc0, open("scaled.pickle", "wb"))
            if debug: print(f"Featurizing done in {time.time() - t0:.2f}s")
            if debug: print(ctx1.n, ctx1.logp, ctx1.logq)
            if debug: print("[Encryptor] Ctxt encrypted")


            he.SerializationUtils.writeCiphertext(ctx1, fn)
            if debug: print("[Encryptor] Ctxt wrote")

            # q1.put({"fn_enc_skeleton": fn})  ## FLOW CONTROL
            # if debug: print("[Encryptor] skeleton encrypted and saved as", fn)
            # e_enc.set()  ## FLOW CONTROL: encryption is done and file is ready
            #set_ctxt_to_server

            print(f"Uploading {fn} to the server")
            print("action", action)

            ret = requests.post(self.server_url + "/upload", 
                        files={"file": open(fn, "rb")},
                        headers={"dtype":"ctxt", "action":str(action)})
            
            if ret != 200:
                # HTTP error handling
                print(ret.status_code)
                print("Error in uploading the file to the server.")
                pass

            if debug: print("[Encryptor] Waiting for prediction...")
            sleep(sleep_time)

            while True:
                #
                # server file
                #
                ret = requests.get(self.server_url + "/result", 
                        files={"ctxt": open(fn, "rb")},
                        headers={"dtype":"ctxt", "action":str(action)})
                if ret.status == 200: #??
                    print(ret.text) # 
                    break

            # Decrypt answer
            #e_enc_ans.wait()  ## FLOW CONTROL
            fn_preds = ret.files["pred"] # ?? 
            #fn_preds = q_text.get()  ## FLOW CONTROL

            #fn_preds = [f"pred_{i}.dat" for i in range(5)]
            # Load predictions
            print("fn_preds", fn_preds)
            logq = 180
            preds=[]
            t0 = time()
            for fn_ctx in fn_preds:
                print("[encryptor] make an empty ctxt")
                # readCiphertext할 때 logp, logq, logn을 미리 알아야함? 
                ctx_pred = he.Ciphertext(ctx1.logp, logq, ctx1.n) # 나중에 오는 애는 logq가 다를 수도 있음
                print("[encryptor] load ctxt", fn_ctx)
                he.SerializationUtils.readCiphertext(ctx_pred, fn_ctx)
                print("[encryptor] decrypt ctxt", ctx_pred)
                dec=decrypt(self.scheme, self.secretKey, ctx_pred, self.parms)
                print("[encryptor] append decrypted ctxt")
                preds.append(np.sum(dec))# Must sum the whole vector. partial sum gives wrong answer
                print("[encryptor] decrypted prediction array", dec[:10])
                del ctx_pred
            print("Decryption done in ", time() - t0, "seconds")
            del ctx1 

            ###########################
            print("preds", preds)
            ans_str = f"Predicted score: {np.argmax(preds)}"
            print(ans_str)
            e_enc_ans.clear()  ## FLOW CONTROL
            
            # 복호화된 결과 QT로 전송
            q_answer.put(ans_str)  ## FLOW CONTROL
            e_ans.set()  ## FLOW CONTROL
            #print("is e_sk set?", e_sk.is_set())

            #i+=1
    
    def setup_eval(self, server_path="./"):
        logq = HEAAN_CONTEXT_PARAMS['logq']#540
        logp = HEAAN_CONTEXT_PARAMS['logp']#30
        logn = HEAAN_CONTEXT_PARAMS['logn']#14
        n = 1*2**logn

        self.parms2 = Param(n=n, logp=logp, logq=logq)
        self.server_path2 = server_path
        self.key_path2 = server_path + 'serkey/'
        print("[ENCRYPTOR] key path", self.key_path2)

        self.ring2 = he.Ring()
        
        self.scheme2 = he.Scheme(self.ring2, True, self.server_path2)
        self.algo2 = he.SchemeAlgo(self.scheme2)
        self.scheme2.loadLeftRotKey(1)

    def load_models(self):
        self.models = {}
        dilatation_factor = 10
        polynomial_degree = 10

        self.my_tm_tanh = NeuralTreeMaker(torch.tanh, 
                            use_polynomial=True,
                            dilatation_factor=dilatation_factor, 
                            polynomial_degree=polynomial_degree)
        
    def load_model(self, action, cam):
        
        print("[Evaluator] Loading trained NRF models")

        t0 = time.time()
        fn = f"./models/Nmodel_{action}_{cam}.pickle"
        Nmodel = pickle.load(open(fn, "rb"))
        #print("Loaded a model...", fn)
        
        h_rf = HNRF(Nmodel)
        #print("[EVAL.model_loader] HRF loaded for class", action)
        nrf_evaluator = heaan_nrf.HETreeEvaluator.from_model(h_rf,
                                                            self.scheme2,
                                                            self.parms2,
                                                            self.my_tm_tanh.coeffs,
                                                            do_reduction = False,
                                                            #save_check=True
                                                            )
        print("[EVAL.model_loader] HNRF model loaded for class", action)
            
        #allmodels.append((f"{action}",nrf_evaluator))
        self.models.update({f"{action}_{cam}":nrf_evaluator})    
        
        print("updated models", self.models)    


    def run_model(self, action, cam, ctx):
        self.load_models()
        print("Running model for class", action)
        try:
            model = self.models[f"{action}_{cam}"]
        except:
            self.load_model(action, cam)
            print(f"Loading model for class {action} and camera {cam}")
            model = self.models[f"{action}_{cam}"]

        #featurizer = self.models[f"{cc}"]['featurizer']
        print("[Evaluator] running model...")
        #ctx = featurizer.encrypt(data)
        return model(ctx)
        #return self.predict(data)

    @staticmethod
    def key_found(key_path):
        all_found = []
        for fn in FN_KEYS:
            this_fn = key_path + fn
            found = os.path.isfile(this_fn)
            all_found.append(found)
            print(f"{this_fn} is","found" if found else "missing" )
        
        return np.all(all_found)

