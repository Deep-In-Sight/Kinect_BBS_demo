
FN_KEYS = ["ENCRYPTION.txt",
           "MULTIPLICATION.txt",
           "ROTATION_1.txt"]

FN_PREDS = 'preds.tar.gz'

HEAAN_CONTEXT_PARAMS = {'logq':540,
                        'logp':30,
                        'logn':14,
                        'n':1*2**14}

location = ['DI', 'ETRI', 'local'][0]

#def set_tcp(location):
if location == "DI":
    HOST = '10.100.82.55'
    PORT = 2345
elif location == "local":
    HOST = '127.0.0.1'
    PORT = 2345
elif location == "ETRI":
    HOST = '?.?.?.?'
    PORT = 6543
    
#    return HOST, PORT
