import numpy as np
import os
import sys
import glob
import pickle
import sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn import preprocessing
import pickle


MEDIAPIPE_LANDMARKS = np.array([
    'Nose',
    'Left_eye_inner', 'Left_eye', 'Left_eye_outer',
    'Right_eye_inner','Right_eye','Right_eye_outer',
    'Left_ear',       'Right_ear',
    'Left_mouth',     'Right_mouth',
    'Left_shoulder',  'Right_shoulder',
    'Left_elbow',     'Right_elbow',
    'Left_wrist',     'Right_wrist',
    'Left_pinky',     'Right_pinky',
    'Left_index',     'Right_index',
    'Left_thumb',     'Right_thumb',
    'Left_hip',       'Right_hip',
    'Left_knee',      'Right_knee',
    'Left_ankle',     'Right_ankle',
    'Left_heel',      'Right_heel',
    'Left_foot_index','Right_foot_index'])


KINECT_JOINTS = np.array([
    'PELVIS',        'SPINE_NAVAL',   'SPINE_CHEST', 'NECK',   
    'CLAVICLE_LEFT', 'SHOULDER_LEFT', 'ELBOW_LEFT',  'WRIST_LEFT', 'HAND_LEFT', 'HANDTIP_LEFT',  'THUMB_LEFT', 
    'CLAVICLE_RIGHT','SHOULDER_RIGHT','ELBOW_RIGHT', 'WRIST_RIGHT','HAND_RIGHT','HANDTIP_RIGHT', 'THUMB_RIGHT', 
    'HIP_LEFT',      'KNEE_LEFT',     'ANKLE_LEFT',  'FOOT_LEFT',
    'HIP_RIGHT',     'KNEE_RIGHT',    'ANKLE_RIGHT', 'FOOT_RIGHT', 
    'HEAD',          'NOSE',
    'EYE_LEFT',      'EAR_LEFT', 
    'EYE_RIGHT',     'EAR_RIGHT'])
# "COMMON"인 경우에 순서맞추기
COMMON_JOINTS = np.array([
    "wrist_L",    "elbow_L", "shoulder_L",
    "shoulder_R", "elbow_R", "wrist_R", 
    "nose", 
    "ankle_L",    "knee_L",  "hip_L", 
    "hip_R",      "knee_R",  "ankle_R"])
                        
KINECT_COMMON = {
    "wrist_L"   :"WRIST_LEFT", 
    "elbow_L"   :"ELBOW_LEFT", 
    "shoulder_L":"SHOULDER_LEFT",
    "shoulder_R":"SHOULDER_RIGHT",
    "elbow_R"   :"ELBOW_RIGHT", 
    "wrist_R"   :"WRIST_RIGHT",
    "nose"      :"NOSE",
    "ankle_L"   :"ANKLE_LEFT",
    "knee_L"    :"KNEE_LEFT",  
    "hip_L"     :"HIP_LEFT", 
    "hip_R"     :"HIP_RIGHT", 
    "knee_R"    :"KNEE_RIGHT",
    "ankle_R"   :"ANKLE_RIGHT"}


MEDIAPIPE_COMMON = {
    "wrist_L"   :"Left_wrist",
    "elbow_L"   :"Left_elbow",
    "shoulder_L":"Left_shoulder",
    "shoulder_R":"Right_shoulder",
    "elbow_R"   :"Right_elbow",
    "wrist_R"   :"Right_wrist",
    "nose"      :"Nose",
    "ankle_L"   :"Left_ankle",
    "knee_L"    :"Left_knee",
    "hip_L"     :"Left_hip",
    "hip_R"     :"Right_hip",
    "knee_R"    :"Right_knee",
    "ankle_R"   :"Right_ankle"}



def get_dtypes(skeleton,isAll=True):
    if skeleton == "KINECT":
        if isAll is True:
            joints = KINECT_JOINTS
        else:
            joints = np.array([KINECT_COMMON[key] for key in COMMON_JOINTS])
    elif skeleton == "MEDEAPIPE":
        if isAll is True:
            joints = MEDIAPIPE_JOINTS
        else:
            joints = np.array([MEDIAPIPE_COMMON[key] for key in COMMON_JOINTS])
    elif skeleton == "COMMON":
        joints = COMMON_JOINTS
    else:
        print("[error] skeleton should be KINECT or MEDIAPIPE!")
    
    dtypes = [ (joint+"_"+coordinate,float) for joint in joints for coordinate in ['x','y']]
    dtypes = [ ("frame",int) ] + dtypes
    print("\n=============== [dtype for npy] ===============")
    for dtype in dtypes:
        print(dtype)
    print("=======================================\n")
    dtypes = np.dtype(dtypes)   
    return dtypes





###########################################
# from 2022 branch, B5.build_data_set     #
###########################################


# 전체 frame을 10등분해서 그 10frame만 해당frame기준 5개씩 median 찾아서 
# 10frame의 5장 median결과만 담은 sub를 반환

def smoothed_frame_N(f_scene,nframe=10,window_size=5,shift=0):
    FPS_ORIGINAL = 10
    nskip = int((len(f_scene)-shift)/nframe)   # nskip = (total number of frames) /10
    sub = np.zeros(nframe,dtype=f_scene.dtype) #10 frame만 담겠다?
    for i in range(nframe):
        temp = f_scene[ i*nskip + shift :i*nskip + shift + window_size]
        for feat in temp.dtype.names:
            sub[i][feat] = np.median(temp[feat]) 
    return sub
        
##10프레임(5장median)저장한 sub에서 dtype이런거 없이 벡터구성
def ravel_rec(sub,return_feature=False):
    vec=[]
    if return_feature is True:
        features=[]
        for i,line in enumerate(sub): #10프레임을 열거, 즉, i=0~9, line=(frame#,...)
            this_line=[]
            for name in line.dtype.names: 
                if name != "frame":
                    this_line.append(line[name])
                    features.append(name+f"_{line['frame']}") #frame제외한 좌표이름을 elbow_L_x_215이런식으로 저장
            vec.extend(this_line)
        return features,np.array(vec)
    else:
        for line in sub:
            vec.extend([line[name] for name in line.dtype.names if name not in "frame"])
        return np.array(vec)
    
def creating_training_set(task,test_size=0.7):
    fname  = f"/home/hyoyeonlee/bbs_project/data_processed/_2_training/task{task:02}_"
    data = np.load(fname+"data.npy")
    label = np.load(fname+"label.npy")
    
def modelling_and_training(task,ntree=20,max_depth=6):
    model = RandomForestClassifier(n_estimator=ntree, max_depth=max_depth)
    model.fit