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
