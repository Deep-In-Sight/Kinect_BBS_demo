import subprocess
FN_KEYS = ["ENCRYPTION.txt",
           "MULTIPLICATION.txt",
           "ROTATION_1.txt"]
DIR_WORK = "./" # client work directory
IMG_DIR = "./img/" # instruction image directory
FN_SK = "secret.key"
FN_PREDS = 'preds.tar.gz'
FN_SCORES = DIR_WORK+f"Scores_.txt"

CERTIFICATE = False # Certification file or ignore
SLEEP_TIME = 30 # sleep time for the client to wait for the server


mp_pose_lm_name = ["nose", "l_eye_inner", "l_eye", "l_eye_outer", 'r_eye_inner', "r_eye", "r_eye_outer",
                   "l_ear", "r_ear", "mouth_left", "mouth_right", "l_shoulder", "r_shoulder", 
                   "l_elbow", "r_elbow", "l_wrist", "r_wrist", "l_pinky", "r_pinky", 
                   "l_index", "r_index", "l_thumb", "r_thumb", "l_hip", "r_hip", 
                   "l_knee", "r_knee", "l_ankle", "r_ankle", "l_heel", "r_heel", 
                   "l_foot_index", "r_foot_index"]

HEAAN_CONTEXT_PARAMS = {'logq':540,
                        'logp':30,
                        'logn':14,
                        'n':2**14}

location = ['DI', 'ETRI', 'local'][2]

if location == "DI":
    #HOST = '10.100.82.89'
    PORT = 2345
    BIN_PYTHON='/home/hoseung/anaconda3/envs/deepinsight/bin/python'
    COPY_SCRIPT='send_key.py'
    DIR_KEY_SERVER = "/home/etri_ai2/work/Kinect_BBS_demo/server/serkey/"
    BIN_PLAYER = "/usr/bin/totem" 
    DIR_VIDEO = "videos/"
    S_ACCOUNT = 'etri_ai2'
    S_PASSWORD = 'etri_ai2'
elif location == "ETRI":
    #HOST = '61.74.232.166'
    PORT = 2345
    DIR_KEY_SERVER = "/home/etri_ai1/work/Kinect_BBS_demo/server/serkey/"
    S_ACCOUNT = 'etri_ai1'
    S_PASSWORD = 'etri_ai1'
    BIN_PYTHON='/home/dinsight/anaconda3/envs/deepinsight/bin/python'
    COPY_SCRIPT='send_key.py'
    DIR_VIDEO = "/home/dinsight/Work/Kinect_BBS_demo/videos/"
elif location == "local":
    #HOST = '127.0.0.1'
    PORT = 2345
    DIR_KEY_SERVER = "/home/hoseung/Work/Kinect_BBS_demo/server/serkey/"
    BIN_PYTHON='/home/dinsight/anaconda3/envs/bbs/bin/python'
    COPY_SCRIPT='send_key_cp.py'
    DIR_VIDEO = "videos/"

# set which video player to use
try:
    BIN_PLAYER = "/usr/bin/mpv" 
    p = subprocess.Popen([BIN_PLAYER])
    p.terminate()
    print("Going for MPV")
except:
    print("Failed to find MPV")
    BIN_PLAYER = "/usr/bin/totem" 
    p = subprocess.Popen([BIN_PLAYER])
    p.terminate()
    print("Going for totem")


HOST=None # placeholder

############# DEBUGGING ##############
TEST_CLIENT=False
DEBUG=False
VERBOSE=True
######################################

################
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

CAM_LIST= {1: 1,
           2: 1,
           3: 0,
           4: 1,
           5: 1,
           6: 1,
           7: 1,
           8: 0,
           9: 0,
           10:1,
           11:1,
           12:1,
           13:0,
           14:1}

CAM_NAMES= {1: "e",
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
