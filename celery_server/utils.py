import numpy as np
import json
from time import sleep
from fase.core.heaan import he
from config import FN_STATE, empty_state

def slow_print(line):
    for xx in line:
        sleep(0.005)
        print(hex(xx), end='\\')

def encrypt(scheme, val, parms):
    ctxt = he.Ciphertext()#logp, logq, n)
    vv = np.zeros(parms.n) # Need to initialize to zero or will cause "unbound"
    vv[:len(val)] = val
    scheme.encrypt(ctxt, he.Double(vv), parms.n, parms.logp, parms.logq)
    del vv
    return ctxt

def print_binary(s):
    return ' '.join(map('{:02X}'.format, s))

def show_file_content(fn):
    with open(fn, 'rb') as fbin:
        line = fbin.read(2000)
        print("\n <<<<file in HEX>>>>")
        slow_print(line)

def gen_empty_state():
    with open(FN_STATE, 'w') as f:
        json.dump(empty_state, f)