#from fase import HEAAN
import zipfile
import fase.HEAAN as he
import numpy as np
import os 
import pickle
import time
from glob import glob 
from bbs_client.constants import CAM_NAMES, HEAAN_CONTEXT_PARAMS, DEBUG
from time import sleep
from fase.hnrf.hetree import HNRF
from fase.core.heaan import HEAANContext

from bbs_client.model.data_preprocessing import shift_to_zero, measure_lengths
#from client_comm import ClientCommunicator
from featurizer import HETreeFeaturizer
import hashlib

class Param():
    """FHE parameters used by the HEAAN Encryptor.
    """
    def __init__(self, n=None, logn=None, logp=None, logq=None, logQboot=None):
        self.n = n
        self.logn = logn
        self.logp = logp
        self.logq = logq 
        self.logQboot = logQboot
        if self.logn == None:
            self.logn = int(np.log2(n))
            
class HEAANEncryptor():
    """Encrypt skeleton and communicate with server.

    Encryptor is responsible for encrypting the skeleton data and
    decrypting the results from the server. 
    HTTPS communication is handled by ClientCommunicator.
    """
    def __init__(self, work_dir="./", 
                debug=True):
        # Setup work directories
        self.work_dir = work_dir
        self._model_dir = os.path.join(work_dir, "models")
        if debug: print("[ENCRYPTOR] key path", work_dir)
        self.model_dir =  os.path.join(self.work_dir, "models")
        if not os.path.isdir(work_dir): os.mkdir(work_dir)

        # FHE context        
        logq = HEAAN_CONTEXT_PARAMS['logq']#540
        logp = HEAAN_CONTEXT_PARAMS['logp']#30
        logn = HEAAN_CONTEXT_PARAMS['logn']#14
        n = 1*2**logn

        self.parms = Param(n=n, logp=logp, logq=logq)
        self.hec = HEAANContext(self.parms.logn, 
                                self.parms.logp, 
                                self.parms.logq, 
                                rot_l=[1], 
                                key_path=self.work_dir,
                                FN_SK="secret.key",
                                boot=False, 
                                is_owner=True,
                                load_sk=False
                                )
        
        # self.ctx1 = he.Ciphertext(logp, logq, self.parms.n)

        # print("FHE Keys are set", self.work_dir)
        # if not self.comm.send_keys(self.work_dir):
        #     raise ConnectionError("Can't send keys to the server")
                
        if debug: print("[Encryptor] HEAAN is ready")
        self.set_featurizers()
        self.load_scalers()
        
        self._fn_chekcsum = os.path.join(self.work_dir, "checksum.txt")
        self._fn_keys = ["EncKey.txt", "MulKey.txt", "RotKey_1.txt", "secret.key"]
        self._fn_preds = ["pred_0.dat", "pred_1.dat", "pred_2.dat", "pred_3.dat", "pred_4.dat"]

    def _calculate_checksum(self):
        dd = []
        for key in self._fn_keys:
            fn = os.path.join(self.work_dir, key)
            dd.append((key, self._get_md5sum(fn)))

        return dict(dd)

    def save_checksum(self):
        sums = self._calculate_checksum()
        with open(self._fn_chekcsum, "w") as f:
            for key in self._fn_keys:
                f.write(f"{self._get_md5sum(key)}  {key}\n")
    
    def _get_md5sum(self, file):
        md5_hash = hashlib.md5()
        with open(file, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                md5_hash.update(chunk)
        return md5_hash.hexdigest()

    def _read_checksum(self):
        """Read the checksum from the checksum file."""
        dd = []
        with open(self._fn_chekcsum, "r") as f:
            for l in f.readlines():
                sum, key = l.split()
                dd.append((key,sum))   
        return dict(dd)
        
    def _check_checksum(self):
        """Check if the checksum is correct."""
        return self._calculate_checksum() == self._read_checksum()

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

    def encrypt(self, sk):#, e_sk):
        """Consumes skeleton from q_sk, encrypt it, send to server, and get the result.
        1. If skeleton is ready (e_sk) 
        2. get the skeleton from q_sk
        3. encrypt and store it as ctx_{i}.dat file
        #4. send the encrypted skeleton to the server
        #5. wait for the result from the server
        #6. decrypt the result and send it to GUI (q_answer)
        """
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
        # print("[ENCRYPROR>>>>>] FINAL SKELETON", final_skeleton)
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
            
    def get_answer(self, q_answer):
            ## TODO: 
            ## separate out decryptor
            self.unzip_new_zip()
            # Load predictions
            print("[encryptor] Prediction files are ready:", self._fn_preds)
            
            # Decrypt answers
            answer = self.decrypt_answer(self._fn_preds)
            answer_str = f"Predicted score: {answer}"
            # 복호화된 결과 QT로 전송
            q_answer.put(answer_str)  ## FLOW CONTROL
            #e_answer.set()  ## FLOW CONTROL

    def decrypt_answer(self, fn_preds):
        """Decrypt all prediction files and reutrn the answer."""
        preds=[]
        for fn_ctx in fn_preds:
            preds.append(self.load_and_decrypt(fn_ctx))

        return np.argmax(preds)

    def unzip_new_zip(self):
        zip_list = glob("*.zip")
        print("[encryptor] zip files", zip_list)
        zip_list.sort(key=os.path.getmtime, reverse=True)
        while len(zip_list) > 0:
            if self.extract_if_contains(zip_list.pop(), "pred_0.dat"):
                break
            
    def load_and_decrypt(self, fn_ctx):
        """Load ciphertext from file and decrypt it.

        Args:
            fn_ctx (str): filename of the ciphertext
            ctxt_ref (Ciphertext): reference ciphertext to get the parameters
        """
        # print("[encryptor] make an empty ctxt")
        ctx_pred = he.Ciphertext(self.parms.logp, self.parms.logq, self.parms.n)
        # print("[encryptor] load ctxt", fn_ctx)
        he.SerializationUtils.readCiphertext(ctx_pred, fn_ctx)
        print("[encryptor] decrypt ctxt", ctx_pred)
        dec = self.decrypt(self.hec._scheme, self.hec.sk, ctx_pred, self.parms)
        # print("[encryptor] decrypted prediction array", dec[:10])
        del ctx_pred
        return np.sum(dec) # Must sum the whole vector. partial sum gives wrong answer

    @staticmethod
    def extract_if_contains(zip_file_path, target_file_name, extract_to_folder = "./"):
        """
        Extracts the contents of a ZIP file to the specified folder if it contains a file with the given name.

        :param zip_file_path: Path to the ZIP file.
        :param target_file_name: Name of the file to check for in the ZIP file.
        :param extract_to_folder: Directory where the contents of the ZIP file will be extracted.
        """
        # Check if the ZIP file exists
        if not os.path.exists(zip_file_path):
            print(f"ZIP file not found: {zip_file_path}")
            return

        # Open the ZIP file
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            # Check if the target file is in the ZIP file
            if any(target_file_name == os.path.basename(file.filename) for file in zip_ref.infolist()):
                # Create the extract folder if it doesn't exist
                if not os.path.exists(extract_to_folder):
                    os.makedirs(extract_to_folder)
                # Extract all the contents
                zip_ref.extractall(extract_to_folder)
                print(f"ZIP file extracted to {extract_to_folder}")
                return True
            else:
                print(f"The file '{target_file_name}' was not found in the ZIP file.")
                return False

    @staticmethod    
    def decrypt(scheme, secretKey, enc, parms):
        featurized = scheme.decrypt(secretKey, enc)
        arr = np.zeros(parms.n, dtype=np.complex128)
        featurized.__getarr__(arr)
        return arr.real