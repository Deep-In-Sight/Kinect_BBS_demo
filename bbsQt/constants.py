
FN_KEYS = ["ENCRYPTION.txt",
           "MULTIPLICATION.txt",
           "ROTATION_1.txt"]

FN_PREDS = 'preds.tar.gz'

HEAAN_CONTEXT_PARAMS = {'logq':540,
                        'logp':30,
                        'logn':14,
                        'n':1*2**14}

location = ['DI', 'ETRI', 'local'][0]

NFRAMES={'1':8,
         '2':8,
         '3':8,
         '4':8,
         '5':8,
         '6':8,
         '7':8,
         '8':8,
         '9':8,
         '10':8,
         '11':8,
         '12':8,
         '13':8,
         '14':8}

if location == "DI":
    HOST = '10.100.82.55'
    PORT = 2345

    BIN_PYTHON='/home/hoseung/anaconda3/envs/deepinsight/bin/python'
    COPY_SCRIPT='send_key.py'
elif location == "local":
    HOST = '127.0.0.1'
    PORT = 2345
    DIR_KEY_SERVER = "./server/"
    BIN_PYTHON='/home/hoseung/anaconda3/envs/deepinsight/bin/python'
    COPY_SCRIPT='send_key_cp.py'
elif location == "ETRI":
    HOST = '61.74.232.166'
    PORT = 2345
    DIR_KEY_SERVER = "/home/etri_ai1/work/Kinect_BBS_demo/server/"
    S_ACCOUNT = 'etri_ai1'
    S_PASSWORD = 'etri_ai1'
    BIN_PYTHON='/home/etri_ai1/anaconda3/envs/bbs/bin/python'
    COPY_SCRIPT='send_key.py'
    
SCP_PORT = 22


TEST_CLIENT=False