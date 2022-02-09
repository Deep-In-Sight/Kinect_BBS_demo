#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
os.environ["CUDA_VISIBLE_DEVICES"]="1"

# In[2]:


import numpy as np
import pickle
import torch
import matplotlib.pyplot as plt 
#from fase.core import heaan

from fase import HEAAN
from fase import HEAAN as he
from typing import List, Callable

from fase import hnrf as hnrf

from fase.hnrf.tree import NeuralTreeMaker
from fase.hnrf import heaan_nrf 
from fase.hnrf.hetree import HomomorphicModel 

#import importlib

from time import time


# # Train a RF model  -- smaller example
# 

# In[5]:


#model_dir = "/home/hoseung/Dropbox/DeepInsight/2021ETRI/BBS_data/Frame8_models/"

model_dir = "/home/hoseung/Work/Kinect_BBS_demo/nbs/"

CAM_LIST= {1: "e",
           2: "e",
           3: "a",
           4: "e",
           5: "e",
           6: "e",
           7: "e",
           8: "a",
           9: "a",
           10:"e",
           11:"e",
           12:"e",
           13:"a",
           14:"e"}
#for action in np.arange(1,15): 
# 3, 9는 아직 없음 , 12번 다시. 
action = 1
cam = CAM_LIST[action]


# In[4]:


fn_model_out = f"trained_model_{action}_{cam}.pickle"
fn_data_out = f"BBS_dataset_{action}_{cam}.pickle"

fn_model = model_dir + fn_model_out
fn_dat = model_dir + fn_data_out

rf_model = pickle.load(open(fn_model, "rb"))

print("model's depth:", rf_model.max_depth)
print("model's tree count:", rf_model.n_estimators)


#####
dataset = pickle.load(open(fn_dat, "rb"))

X_train = dataset["train_x"]
y_train = dataset["train_y"]
X_valid = dataset["valid_x"]
y_valid = dataset["valid_y"]

print("min max of input dataset")
print(X_train.min(), X_train.max())
print(X_valid.min(), X_valid.max())

#####
from sklearn.tree import BaseDecisionTree
from fase.hnrf.tree import NeuralRF

dilatation_factor = 10
polynomial_degree = 10

estimators = rf_model.estimators_

my_tm_tanh = NeuralTreeMaker(torch.tanh, 
                            use_polynomial=True,
                            dilatation_factor=dilatation_factor, 
                            polynomial_degree=polynomial_degree)


# In[6]:


from fase.hnrf.hetree import HNRF
action = 1
cam = CAM_LIST[action]
Nmodel = pickle.load(open(f"Nmodel_{action}_{cam}.pickle", "rb"))

fn_model_out = f"trained_model_{action}_{cam}.pickle"
fn_data_out = f"BBS_dataset_{action}_{cam}.pickle"
fn_dat = model_dir + fn_data_out
fn_model = model_dir + fn_model_out

rf_model = pickle.load(open(fn_model, "rb"))

#####
dataset = pickle.load(open(fn_dat, "rb"))

X_train = dataset["train_x"]
y_train = dataset["train_y"]
X_valid = dataset["valid_x"]
y_valid = dataset["valid_y"]


pred = rf_model.predict(X_valid)

with torch.no_grad():
    neural_pred = Nmodel(torch.tensor(X_valid).float()).argmax(dim=1).numpy()

print(f"Original accuracy : {(pred == y_valid).mean()}")
print(f"Accuracy : {(neural_pred == y_valid).mean()}")
print(f"Same output : {(neural_pred == pred).mean()}")


h_rf = HNRF(Nmodel)


# In[7]:


logq = 540
logp = 30
logn = 14
n = 1*2**logn
slots = n


do_reduction=False

from fase.core.common import HEAANContext

logq = 540
logp = 30 
logn = 14
hec = HEAANContext(logn, logp, logq, rot_l=[1], 
                   key_path="/home/hoseung/Work/Kinect_BBS_demo/serkey/",
                   FN_SK="secret.key",
                   boot=False, 
                   is_owner=True,
                   load_sk=True
                  )

cc = hec.encrypt([1,2,3,4])

dd = hec.lrot(cc, 1)

hec.decrypt(dd)


# In[10]:


#server_path = "/home/hoseung/Work/Kinect_BBS_demo/server/"
t0 = time()

#action = 1
#cam = "e"

#fn = server_path+f"models/Nmodel_{action}_{cam}.pickle"
#Nmodel = pickle.load(open(fn, "rb"))

#h_rf = HNRF(Nmodel)

my_tm_tanh = NeuralTreeMaker(torch.tanh, 
             use_polynomial=True,
             dilatation_factor=10, 
             polynomial_degree=10)

#nrf_evaluator = heaan_nrf.HETreeEvaluator.from_model(h_rf,
nrf_evaluator = heaan_nrf.HETreeEvaluator(h_rf,
                                          hec._scheme,
                                          hec.parms,
                                          my_tm_tanh.coeffs,
                                          do_reduction = False,
                                          sk=hec.sk
                                          )
print(f"[EVAL.model_loader] HNRF model loaded for class {action} in {time() - t0:.2f} seconds")


# In[11]:


featurizer = heaan_nrf.HETreeFeaturizer(h_rf.return_comparator(), hec._scheme, hec.parms)


# In[ ]:


for xx, yy in zip(X_valid[:9], y_valid[:9]):
    t0 = time()
    #print(len(xx))
    ctx = featurizer.encrypt(xx)
    result = nrf_evaluator(ctx)
    #print(f"Took {time() - t0:.2f} seconds")

    pred = []
    for res in result:
        dec = hec.decrypt(res)
        pred.append(np.sum(dec))

    print(f"Prediction: {np.argmax(pred)} == {yy}?") 
    neural_pred = Nmodel(torch.tensor(xx.reshape(1,-1)).float())
    print(pred)
    print(neural_pred)
    print(f"{time() - t0} seconds")


# In[ ]:





# In[35]:


dec


# In[34]:


pred


# 성능 확실함 

# ## Live skeleton

# In[19]:


ctxt = he.Ciphertext(hec.parms.logp, hec.parms.logq, hec.parms.n)
he.SerializationUtils.readCiphertext(ctxt, "/home/hoseung/Work/Kinect_BBS_demo/ctx_01_e_.dat")

ddl = hec.decrypt(ctxt)


# # 두 skeleton의 분포 차이 

# In[20]:


fig, axs = plt.subplots(3,3)
axs = axs.ravel()

for i, (xx, yy) in enumerate(zip(X_valid[:5], y_valid[:5])):
    ctx = featurizer.encrypt(xx)
    dd = hec.decrypt(ctx)
    
    axs[i].hist(dd[:240])
    
    
axs[-1].hist(ddl[:240])


# In[51]:


neural_pred = Nmodel(torch.tensor(X_train[1].reshape(1,-1)).float())


# In[52]:


neural_pred


# In[36]:


xx.max()


# In[40]:


neural_pred = Nmodel(torch.tensor(X_train[:1]).float())
#Nmodel(torch.tensor(X_valid[:1]))


# In[41]:


neural_pred


# 여기서 만든 h_rf와 새로 만든 h_rf의 모양, 값 차이 비교

# min = 0, 
# max = 1인데.. 왜 -1보다 작아질까...? 

# In[23]:


pred


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[57]:


from fase.core import commonAlgo
class HETreeEvaluator:
    """Evaluator which will perform homomorphic computation"""

    def __init__(self, 
                 b0: np.ndarray, w1, b1, w2, b2,
                 scheme,
                 parms,
                 activation_coeffs: List[float], 
                 #polynomial_evaluator: Callable,
                 
                 #relin_keys: seal.RelinKeys, galois_keys: seal.GaloisKeys, scale: float,
                 do_reduction=True):
        """Initializes with the weights used during computation.

        Args:
            b0: bias of the comparison step

        """
        self.sk = secretKey ######### 
        self.scheme = scheme
        self.algo = he.SchemeAlgo(scheme)
        self.commonAlgo = commonAlgo.CommonAlgorithms(scheme, "HEAAN")
        # scheme should hold all keys
        self.parms = parms
        
        self._activation_coeff = activation_coeffs
        self._activation_poly_degree = len(activation_coeffs) -1
        self.do_reduction = do_reduction

        # 10-degree activation -> up to 5 multiplications 
        logq_w1 = self.parms.logq - 5 * self.parms.logp
        logq_b1 = logq_w1 - self.parms.logp
        logq_b2 = logq_b1 - 5*self.parms.logp

        self.b0_ctx = self.encrypt(b0)
        #self.b0 = b0
        self.w1 = [self.to_double(w) for w in w1]
        #self.b1 = b1
        self.w2 = [self.to_double(w) for w in w2]
        #self.b2 = [w for w in b2]
        
#         self.w1_ctx = []
#         for w in w1:
#             #print('w', w)
#             temp = self.encrypt(w) 
#             scheme.modDownToAndEqual(temp, logq_w1)
#             self.w1_ctx.append(temp)
#         #self.w1_ctx = [self.encrypt(w, logq=logq_w1) for w in w1]
            
        self.b1_ctx = self.encrypt(b1, logq=logq_b1)
#         self.w2_ctx = [self.encrypt(w, logq=logq_2) for w in w2]
        self.b2_ctx = [self.encrypt(b, logq=logq_b2) for b in b2]

        self.setup_summary()      
    
    def setup_summary(self):
        print("CKKS paramters:")
        print("---------------------------")
        print(f"n = {self.parms.n}")
        print(f"logp = {self.parms.logp}")
        print(f"logq = {self.parms.logq}")
        print(f"tanh activation polynomial coeffs = {self._activation_coeff}")
        print(f"tanh activation polynomial degree = {self._activation_poly_degree}")
        
        print("\nNeural RF")
        print("---------------------------")
        print(f"")
    
    def heaan_double(self, val):
        mvec = np.zeros(self.parms.n)
        mvec[:len(val)] = np.array(val)
        return he.Double(mvec)

    def decrypt_print(self, ctx, n=20):
        res1 = self.decrypt(ctx)
        print("_____________________")
        print(res1[:n])
        print(res1.min(), res1.max())
        print("---------------------")

    def decrypt(self, enc):
        temp = self.scheme.decrypt(self.sk, enc)
        arr = np.zeros(self.parms.n, dtype=np.complex128)
        temp.__getarr__(arr)
        return arr.real
        
    def encrypt_ravel(self, val, **kwargs):
        """encrypt a list
        """
        return self.encrypt(np.array(val).ravel(), **kwargs)

    def encrypt(self, val, n=None, logp=None, logq=None):
        if n == None: n = self.parms.n
        if logp == None: logp = self.parms.logp
        if logq == None: logq = self.parms.logq
            
        ctxt = he.Ciphertext()
        vv = np.zeros(n) # Need to initialize to zero or will cause "unbound"
        vv[:len(val)] = val
        self.scheme.encrypt(ctxt, he.Double(vv), n, logp, logq)
        del vv
        return ctxt
    
    def to_double(self, val):
        n = self.parms.n
        vv = np.zeros(n) # Need to initialize to zero or will cause "unbound"
        vv[:len(val)] = val
        return he.Double(vv)
        
        
    def activation(self, ctx):
        output = he.Ciphertext()
        #output = self.commonAlgo.function_poly(ctx, 
        #               he.Double(self._activation_coeff))
        output = he.Ciphertext()
        self.algo.function_poly(output, 
                    ctx, 
                    he.Double(self._activation_coeff), 
                    self.parms.logp, 
                    self._activation_poly_degree)
        return output        
        

    def __call__(self, ctx):
        # First we add the first bias to do the comparisons
        ctx = self.compare(ctx)
        print("After compare")
        self.decrypt_print(ctx)
        ctx = self.match(ctx)
        print("after match")
        self.decrypt_print(ctx)
        outputs = self.decide(ctx)
        if self.do_reduction:
            outputs = self.reduce(outputs)

        return outputs

    def compare(self, ctx, debug=False):
        """Calculate first layer of the HNRF
        
        ctx = featurizer.encrypt(x)
        
        Assuming n, logp, logq are globally available
        
        """
        b0_ctx = self.b0_ctx
        self.scheme.addAndEqual(ctx, b0_ctx)
        # Activation
        output = self.activation(ctx)
            
        del b0_ctx, ctx

        return output
    
    def _mat_mult(self, diagonals, ctx):
        """
        Take plain vector 
        """
        scheme = self.scheme
        n = self.parms.n
        logp = self.parms.logp
        #logq = self.parms.logq

        ctx_copy = he.Ciphertext()
        ctx_copy.copy(ctx)
        
        for i, diagonal in enumerate(diagonals):
            #print("logq in mat_mult", diagonal.logq, ctx_copy.logq)
            #scheme.modDownToAndEqual(diagonal, ctx.logq)
            if i > 0: scheme.leftRotateFastAndEqual(ctx_copy, 1) # r = 1

            # Multiply with diagonal
            dd = he.Ciphertext()
            #print("diagonal")
            #self.decrypt_print(diagonal,10)
            #print("ctx")
            #self.decrypt_print(ctx_copy,10)
            #scheme.mult(dd, diagonal, ctx_copy)
            
            # Reduce the scale of diagonal
            scheme.multByConstVec(dd, ctx_copy, diagonal, logp)
            scheme.reScaleByAndEqual(dd, logp)
            #print('dd')
            #print(dd)
            
            
            if i == 0:
                mvec = np.zeros(n)
                temp = he.Ciphertext()
                scheme.encrypt(temp, he.Double(mvec), n, logp, ctx_copy.logq - logp)
                ##scheme.modDownToAndEqual(temp, ctx_copy.logq)
                #print("temp",i)
                #print(temp)
                #self.decrypt_print(temp,10)
            
            # match scale 
            scheme.addAndEqual(temp, dd)

            #print("temp",i)
            #self.decrypt_print(temp,10)
            
            del dd
        del ctx_copy
        return temp


    def match(self, ctx):
        """Applies matching homomorphically.

        First it does the matrix multiplication with diagonals, then activate it.
        """
        output = self._mat_mult(self.w1, ctx)

        #print(f"MATCH:: 'output.logq', {output.logq} == {self.b1_ctx.logq}?")
        self.scheme.addAndEqual(output, self.b1_ctx)
        
        output = self.activation(output)
        return output

    def decide(self, ctx):
        """Applies the decisions homomorphically.

        For each class, multiply the ciphertext with the corresponding weight of that class and
        add the bias afterwards.
        """
        # ww와 bb도 미리 modDowntoAndEqual 가능 
        outputs = []

        for ww, bb in zip(self.w2, self.b2_ctx):
            output = he.Ciphertext()
            
            # Multiply weights            
            #self.scheme.mult(output, ww, ctx)
            
            scheme.multByConstVec(output, ctx, ww, ctx.logp)
            #print("ctx", ctx)
            #print("bb", bb)
            self.scheme.reScaleByAndEqual(output, ctx.logp)
            
            # Add bias
            self.scheme.addAndEqual(output, bb)
            
            outputs.append(output)
        return outputs

    def _sum_reduce(self, ctx, logn, scheme):
        """
        return sum of a Ciphertext (repeated nslot times)
        
        example
        -------
        sum_reduct([1,2,3,4,5])
        >> [15,15,15,15,15]
        """
        output = he.Ciphertext()
        
        for i in range(logn):
            
            if i == 0:
                temp = he.Ciphertext(ctx.logp, ctx.logq, ctx.n)
                #print(i, ctx, temp)
                #print("reduce: ctx before rot")
                # self.decrypt_print(ctx,10)
                
                scheme.leftRotateFast(temp, ctx, 2**i)
                #print(i, ctx, temp)
                #print("reduce: before add")
                # self.decrypt_print(temp,10)
                scheme.add(output, ctx, temp)
                #print("reduce: after add")
                # self.decrypt_print(output,10)
            else:
                scheme.leftRotateFast(temp, output, 2**i)
                #print(i, output, temp)
                #print("reduce: before add")
                # self.decrypt_print(output,10)
                # self.decrypt_print(temp,10)
                scheme.addAndEqual(output, temp)
                #print("reduce: after add")
                # self.decrypt_print(output,10)
        return output


    def reduce(self, outputs):
        logp = self.parms.logp
        scheme = self.scheme

        for i, output in enumerate(outputs):
            # print("reduce before",)
            # self.decrypt_print(output,10)
            #output = sum_reduce(output, self.parms.logn, self.scheme)
            output = self._sum_reduce(output, self.parms.logn, self.scheme)

            # print("reduce after",)
            # self.decrypt_print(output,10)

            mask = np.zeros(self.parms.n)
            mask[0] = 1
            mask_hedb = he.ComplexDouble(mask)
            if i == 0:
                scores = he.Ciphertext()
                scheme.multByConstVec(scores, output, mask_hedb, logp)
                # print("reduce score",i)
                # self.decrypt_print(scores,10)
                # print("before rescale", scores)
                scheme.reScaleByAndEqual(scores, logp)
                # print("before rescale", scores)
            else:
                temp = he.Ciphertext()
                scheme.multByConstVec(temp, output, mask_hedb, logp)
                # print("reduce score",i)
                # self.decrypt_print(scores,10)
                # print("before rescale", scores)
                scheme.reScaleByAndEqual(temp, logp)
                # print("after rescale", scores)
                scheme.rightRotateFastAndEqual(temp, i)
                scheme.addAndEqual(scores, temp)

        return scores


    @classmethod
    def from_model(cls, model,
                   scheme,
                   parms,
                   activation_coeffs: List[float],
                   do_reduction=False):
        """Creates an Homomorphic Tree Evaluator from a model, i.e a neural tree or
        a neural random forest. """
        b0, w1, b1, w2, b2 = model.return_weights()

        return cls(b0, w1, b1, w2, b2, scheme, parms, activation_coeffs, do_reduction)

