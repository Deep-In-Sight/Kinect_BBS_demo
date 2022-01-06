
FN_KEYS = ["ENCRYPTION.txt",
           "MULTIPLICATION.txt",
           "ROTATION_1.txt"]

FN_PREDS = 'preds.tar.gz'

HEAAN_CONTEXT_PARAMS = {'logq':540,
                        'logp':30,
                        'logn':14,
                        'n':1*2**14}

location = ['DI', 'ETRI', 'local'][2]

NFRAMES={'1':6,
         '2':6,
         '3':6,
         '4':6,
         '5':6,
         '6':6,
         '7':6,
         '8':6,
         '9':6,
         '10':6,
         '11':6,
         '12':6,
         '13':6,
         '14':6}

if location == "DI":
    HOST = '10.100.82.55'
    PORT = 2345
    BIN_PYTHON='/home/hoseung/anaconda3/envs/deepinsight/bin/python'
    COPY_SCRIPT='send_key.py'
    DIR_KEY_SERVER = "/home/etri_ai2/work/Kinect_BBS_demo/server/serkey/"
    BIN_PLAYER = "/usr/bin/totem" 
    DIR_VIDEO = "/home/hoseung/Work/Kinect_BBS_demo/videos/"
    S_ACCOUNT = 'etri_ai2'
    S_PASSWORD = 'etri_ai2'
elif location == "local":
    HOST = '127.0.0.1'
    PORT = 2345
    DIR_KEY_SERVER = "/home/hoseung/Work/Kinect_BBS_demo/server/serkey/"
    BIN_PYTHON='/home/hoseung/anaconda3/envs/deepinsight/bin/python'
    COPY_SCRIPT='send_key_cp.py'
    BIN_PLAYER = "/usr/bin/totem" 
    DIR_VIDEO = "/home/hoseung/Work/Kinect_BBS_demo/videos/"

elif location == "ETRI":
    HOST = '61.74.232.166'
    PORT = 2345
    DIR_KEY_SERVER = "/home/etri_ai1/work/Kinect_BBS_demo/server/serkey/"
    S_ACCOUNT = 'etri_ai1'
    S_PASSWORD = 'etri_ai1'
    BIN_PYTHON='/home/etri_he1/anaconda3/envs/bbs/bin/python'
    COPY_SCRIPT='send_key.py'
    BIN_PLAYER = "/usr/bin/mpv" 
    DIR_VIDEO = "/home/etri_he1/work/Kinect_BBS_demo/videos/"
    
SCP_PORT = 22

FPGA=False

############# DEBUGGING ##############
DEBUG_FLAG1 = True
TEST_CLIENT=False
DEBUG=False
