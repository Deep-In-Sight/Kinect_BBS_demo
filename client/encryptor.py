#from fase import HEAAN
import fase.HEAAN as he
import numpy as np
import os 
import pickle
import time
from bbsQt.constants import CAM_NAMES, HEAAN_CONTEXT_PARAMS, DEBUG, SLEEP_TIME
from time import sleep
from fase.hnrf.hetree import HNRF
from fase.core.heaan import HEAANContext

from bbsQt.model.data_preprocessing import shift_to_zero, measure_lengths
from client_comm import ClientCommunicator
from featurizer import HETreeFeaturizer, Param


class HEAANEncryptor():
    """Encrypt skeleton and communicate with server.

    Encryptor is responsible for encrypting the skeleton data and
    decrypting the results from the server. 
    HTTPS communication is handled by ClientCommunicator.
    """
    def __init__(self, server_url, cert, work_dir="./", 
                debug=True):
        #Setup work directories
        self.work_dir = work_dir
        self._model_dir = os.path.join(work_dir, "models")
        if debug: print("[ENCRYPTOR] key path", work_dir)
        self.model_dir =  os.path.join(self.work_dir, "models")
        if not os.path.isdir(work_dir): os.mkdir(work_dir)

        # communicator
        self.comm = ClientCommunicator(f"https://{server_url}", cert)

        # FHE context        
        logq = HEAAN_CONTEXT_PARAMS['logq']#540
        logp = HEAAN_CONTEXT_PARAMS['logp']#30
        logn = HEAAN_CONTEXT_PARAMS['logn']#14
        n = 1*2**logn

        self.parms = Param(n=n, logp=logp, logq=logq)
        self.hec = HEAANContext(logn, logp, logq, rot_l=[1], 
            key_path=self.work_dir,
            FN_SK="secret.key",
            boot=False, 
            is_owner=True,
            load_sk=False
            )

        print("FHE Keys are set", self.work_dir)
        if not self.comm.send_keys(self.work_dir):
            raise ConnectionError("Can't send keys to the server")
        
        self.set_featurizers()
        self.load_scalers()

        if debug: print("[Encryptor] HEAAN is ready")
    
    def set_featurizers(self):
        """Initialize featurizers for each action.
        
        Featurizer transforms skeleton to feature vector.
        Each of 15 action has its own model and featurizer.
        """
        scheme = self.hec._scheme
        parms = self.parms

        featurizers =[]
        for action in range(1,15):
            cam = CAM_NAMES[action]
            Nmodel = pickle.load(open(os.path.join(self.model_dir, f"Nmodel_{action}_{cam}.pickle"), "rb"))
            h_rf = HNRF(Nmodel)
            featurizers.append((f"{action}_{cam}", HETreeFeaturizer(h_rf.return_comparator(), scheme, parms)))
                
        self.featurizers = dict(featurizers)

    def load_scalers(self):
        """Initialize scalers for each action.

        Scaler (from Scikit-learn Random Forest model) is used to 
        normalize the skeleton data.
        """
        scalers =[]
        for action in range(1,15):
            cam = CAM_NAMES[action]
            sc = pickle.load(open(os.path.join(self.model_dir, f'scaler_{action}_{cam}.pickle'), "rb"))
            scalers.append((f"{action}_{cam}", sc))
            
        self.scalers = dict(scalers)

    def _quick_check(self):
        scheme = self.scheme
        return True

    def start_encrypt_loop(self, q_sk, q_answer, e_sk, e_answer):
        """Consumes skeleton from q_sk, encrypt it, send to server, and get the result.

        1. If skeleton is ready (e_sk) 
        2. get the skeleton from q_sk
        3. encrypt and store it as ctx_{i}.dat file
        4. send the encrypted skeleton to the server
        5. wait for the result from the server
        6. decrypt the result and send it to GUI (q_answer)
        """
        while True:
            e_sk.wait()  ## FLOW CONTROL
            print("[Encryptor] good to go") 
            sk = q_sk.get()  ## FLOW CONTROL
            "++++++++++++++++++++++++++ SKELETON POINTS ++++++++++++++++++++++"
            e_sk.clear()  ## FLOW CONTROL: reset skeleton event
            
            if not 'skeleton' in sk.keys():
                raise LookupError("Can't find skeleton in queue")    
            if DEBUG: 
                print("[Encryptor] Got a skeleton, Encrypting...")
                print("[Encryptor] Length of the skeleton:", len(sk["skeleton"]))
            
            action = int(sk['action'])
            cam = CAM_NAMES[action] 

            scaler = self.scalers[f"{action}_{cam}"]
            
            skeleton = sk['skeleton']
        
            if DEBUG:
                print("[ENCRYPTOR] DEBUGGING MODE !!!!!!!")
                final_skeleton = scaler.transform(skeleton)
            else:
                # TODO: copy skeleton? 
                rav_sub = skeleton#[0]
                skeleton = shift_to_zero(skeleton)
                body = measure_lengths(skeleton)
                skeleton /= body['body'] 
                pickle.dump(skeleton, open("skeleton_org.pickle", "wb"))
                #print("rav_sub", rav_sub.min(), rav_sub.max())
                final_skeleton = scaler.transform(rav_sub.reshape(1,-1))[0]
            
            print(f"Check for scales {final_skeleton.min():.2f}, {final_skeleton.max():.2f}")

            featurizer = self.featurizers[f"{action}_{cam}"]
            if DEBUG: print("Featurizing skeleton...")

            t0 = time.time()
            ctx1 = featurizer.encrypt(final_skeleton)
            print(f"Encryption done in {time.time() - t0:.2f} seconds")
            
            if DEBUG: 
                pickle.dump(final_skeleton, open("scaled.pickle", "wb"))
                print(f"Featurizing done in {time.time() - t0:.2f}s")
                print(ctx1.n, ctx1.logp, ctx1.logq)
                print("[Encryptor] Ctxt encrypted")

            fn_ctxt = os.path.join(self.work_dir, f"ctx_{action:02d}_{cam}_.dat")
            he.SerializationUtils.writeCiphertext(ctx1, fn_ctxt)
            print("[Encryptor] Ctxt is written to", fn_ctxt)

            # True if transmission is successful
            if not self.comm.send_ctxt(fn_ctxt, action):
                raise ConnectionError("Can't send ctxt to the server")
            
            if DEBUG: print("[Encryptor] Waiting for prediction...")
            
            sleep(SLEEP_TIME)

            if self.comm.query_ready(retry_interval=5, max_trials = 10):
                fn_preds = self.comm.get_5results(self.work_dir)
            
            # Load predictions
            print("[encryptor] Prediction files are ready:", fn_preds)
            
            # Decrypt answers
            answer = self.decrypt_answer(fn_preds, ctx1)
            answer_str = f"Predicted score: {answer}"
            # 복호화된 결과 QT로 전송
            q_answer.put(answer_str)  ## FLOW CONTROL
            e_answer.set()  ## FLOW CONTROL

    def decrypt_answer(self, fn_preds, ctxt_ref):
        """Decrypt all prediction files and reutrn the answer."""
        preds=[]
        for fn_ctx in fn_preds:
            preds.append(self.load_and_decrypt(fn_ctx, ctxt_ref))
        del ctx1 

        return np.argmax(preds)

    def load_and_decrypt(self, fn_ctx, ctxt_ref=None):
        """Load ciphertext from file and decrypt it.

        Args:
            fn_ctx (str): filename of the ciphertext
            ctxt_ref (Ciphertext): reference ciphertext to get the parameters
        """
        print("[encryptor] make an empty ctxt")
        ctx_pred = he.Ciphertext(ctxt_ref.logp, 180, ctxt_ref.n)
        print("[encryptor] load ctxt", fn_ctx)
        he.SerializationUtils.readCiphertext(ctx_pred, fn_ctx)
        print("[encryptor] decrypt ctxt", ctx_pred)
        dec = self.decrypt(self.hec._scheme, self.hec.sk, ctx_pred, self.parms)
        print("[encryptor] decrypted prediction array", dec[:10])
        del ctx_pred
        return np.sum(dec) # Must sum the whole vector. partial sum gives wrong answer

    @staticmethod    
    def decrypt(scheme, secretKey, enc, parms):
        featurized = scheme.decrypt(secretKey, enc)
        arr = np.zeros(parms.n, dtype=np.complex128)
        featurized.__getarr__(arr)
        return arr.real