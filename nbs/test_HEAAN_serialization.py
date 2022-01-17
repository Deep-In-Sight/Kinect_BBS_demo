import numpy as np
from fase import HEAAN

def decrypt(scheme, secretKey, enc):
    featurized = scheme.decrypt(secretKey, enc)
    arr = np.zeros(n, dtype=np.complex128)
    featurized.__getarr__(arr)
    return arr.real

def encrypt(scheme, val):
    ctxt = HEAAN.Ciphertext()#logp, logq, n)
    vv = np.zeros(n) # Need to initialize to zero or will cause "unbound"
    vv[:len(val)] = val
    scheme.encrypt(ctxt, HEAAN.Double(vv), n, logp, logq)
    del vv
    return ctxt


logq = 540
logp = 30
logn = 14
n = 1*2**logn

do_reduction=False
Nclass = 2

key_path = "/home/hoseung/Work/fhe-ai-sw-etri/fase/HEAAN/run/here/"


ring = HEAAN.Ring()

secretKey = HEAAN.SecretKey(ring)
scheme = HEAAN.Scheme(secretKey, ring, isSerialized=True, root_path=key_path)
algo = HEAAN.SchemeAlgo(scheme)

# reduction때는 right rotation N_class개 필요.
if do_reduction:
    scheme.addLeftRotKeys(secretKey)
    for i in range(Nclass):
        scheme.addRightRotKey(secretKey, i+1) #
else:
    # reduction 안 하면 하나짜리 rotation만 여러번 반복.
    scheme.addLeftRotKey(secretKey, 1)



ring2 = HEAAN.Ring()

scheme2 = HEAAN.Scheme(ring2, isSerialized=True, root_path=key_path)

ctx1 = encrypt(scheme2, [1,2,3,4,5,6,7])
HEAAN.SerializationUtils.writeCiphertext(ctx1, "./ctx1.dat")


ctx12 = HEAAN.Ciphertext(ctx1.logp, ctx1.logq, ctx1.n)#pqn
HEAAN.SerializationUtils.readCiphertext(ctx12, "./ctx1.dat")

print("decrypting..")
res = decrypt(scheme, secretKey, ctx12)
print(res)

