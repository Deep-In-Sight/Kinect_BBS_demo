from fase import HEAAN
import numpy as np

def decrypt(scheme, secretKey, enc):
    featurized = scheme.decrypt(secretKey, enc)
    arr = np.zeros(enc.n, dtype=np.complex128)
    featurized.__getarr__(arr)
    return arr.real

def encrypt(scheme, val, parms):
    ctxt = HEAAN.Ciphertext()
    vv = np.zeros(parms.n) 
    vv[:len(val)] = val
    scheme.encrypt(ctxt, HEAAN.Double(vv), parms.n, parms.logp, parms.logq)
    del vv
    return ctxt

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

class HEAAN_Encryptor():
    def __init__(self, key_path = "/home/hoseung/Work/fhe-ai-sw-etri/fase/HEAAN/run/here/"):
        logq = 540
        logp = 30
        logn = 14
        n = 1*2**logn
        self.parms = Param(n=n, logp=logp, logq=logq)

        self.do_reduction=False
        Nclass = 2

        self.key_path = key_path

        ring = HEAAN.Ring()
        self.ring = ring 

        self.secretKey = HEAAN.SecretKey(ring)
        scheme = HEAAN.Scheme(self.secretKey, ring, isSerialized=True, root_path=key_path)
        self.scheme0 = scheme
        
        

        # reduction때는 right rotation N_class개 필요.
        if self.do_reduction:
            scheme.addLeftRotKeys(self.secretKey)
            for i in range(Nclass):
                scheme.addRightRotKey(self.secretKey, i+1) #
        else:
            # reduction 안 하면 하나짜리 rotation만 여러번 반복.
            scheme.addLeftRotKey(self.secretKey, 1)


        if False:
            n = self.parms.n
            logp = self.parms.logp
            logq = self.parms.logq
            
            
            ctx12 = HEAAN.Ciphertext(logp, logq, n)#pqn
            print("ctx, ", ctx12)
            HEAAN.SerializationUtils.readCiphertext(ctx12, "./ctx1.dat")
            print("ctx, ", ctx12)

            print("decrypting..")
            res = decrypt(self.scheme0, self.secretKey, ctx12)#, self.parms)
            print(res)
        #ctx12 = HEAAN.Ciphertext(logp, logq, n)#pqn
        #print("ctx, ", ctx12)
        #HEAAN.SerializationUtils.readCiphertext(ctx12, "./ctx1.dat")
        #print("ctx, ", ctx12)

        #print("decrypting..")
        #res = decrypt(self.scheme0, self.secretKey, ctx12)#, self.parms)
        #print(res)


    def do_encryption(self):
        ring2 = HEAAN.Ring()

        scheme = HEAAN.Scheme(ring2, isSerialized=True, root_path=self.key_path)
        
        #self.scheme = scheme
        self.algo = HEAAN.SchemeAlgo(scheme)

        ctx1 = encrypt(scheme, [1,2,3,4,5,6,7], self.parms)
        HEAAN.SerializationUtils.writeCiphertext(ctx1, "./ctx1.dat")


    def do_decryption(self):
        n = self.parms.n
        logp = self.parms.logp
        logq = self.parms.logq
        
        
        ctx12 = HEAAN.Ciphertext(logp, logq, n)#pqn
        print("ctx, ", ctx12)
        HEAAN.SerializationUtils.readCiphertext(ctx12, "./ctx1.dat")
        print("ctx, ", ctx12)

        print("decrypting..")
        res = decrypt(self.scheme0, self.secretKey, ctx12)#, self.parms)
        print(res)
        
        

henc = HEAAN_Encryptor()

henc.do_encryption()
henc.do_decryption()

