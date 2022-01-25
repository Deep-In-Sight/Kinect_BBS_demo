import os
#from glob import glob 
#import cv2
#import matplotlib.pyplot as plt 
import numpy as np
#import PIL

#from .BBS_pp_utils import json_to_arr
from . import BBS_pp_utils as bbpp

class Coord2name():
    
    def __init__(self):
        dtypes = bbpp.get_dtypes(ignored_joints=[])
        names = list(dtypes.names) + [" ", " "]
        self.names = np.array(names[1:]).reshape(6,6).T # 
        self.xbins = np.array([414, 838, 1262, 1696, 2120]) / 2
        self.ybins = np.array([392, 822, 1250, 1680, 2108]) / 2 
    
    def _coord_to_ind(self, coords):
        i = np.digitize(coords[0], self.xbins)
        j = np.digitize(coords[1], self.ybins)
        return [i,j]
    
    def coord2feature(self, coords):
        ind = self._coord_to_ind(coords)
        return self.names[ind[0], ind[1]]


def fixed_parse(l):
    """ 
    c4_fix_feature.txt readlines
    ex) l = 'a_125_4_3.png 144 547'
    """
    _, ID, action, score = l.split(".png")[0].split("_")
    _, x, y = l.split(".png")[1].split(" ")
    return int(action), int(score), int(ID), (int(x), int(y))


# fixed 2021.12.15
def feature_preprocessing(sk, feature):
    if len(sk) > 1:
        ind_list = np.where(~((sk[0][feature] == 0)*(sk[1][feature] == 0)))[0]
    else:
        ind_list = np.where(~((sk[0][feature] == 0)))[0]
        
    good_arrs = [arr[ind_list] for arr in sk] 

    for iframe in range(1, len(good_arrs[0])):#len(good_arrs[0])):
            # if i < 90:
            #     continue
            old = [arr[iframe-1][feature] for arr in good_arrs]
            new = [arr[iframe][feature] for arr in good_arrs]

            matrix = np.zeros((len(new), len(old)))
            for i, new_arr in enumerate(new):
                for j, old_arr in enumerate(old):
                    matrix[i,j] = np.abs(new_arr - old_arr)

            inds=[]
            while(not np.all(matrix==np.inf)):
                #print(matrix)
                ind = matrix_argmin(matrix)
                #print(ind)
                inds.append(ind)
                matrix[ind[0],:] = np.inf
                matrix[:,ind[1]] = np.inf

            tmps = [ar[iframe].copy() for ar in good_arrs]
            for ind in inds:
                good_arrs[ind[0]][iframe] = tmps[ind[1]]
    
    for ss, ga in zip(sk, good_arrs):
        ss[ind_list] = ga
    
    return sk

# fixed 2021.12.15
def matrix_argmin(mat):
    return np.unravel_index(mat.argmin(), mat.shape)     

# fixed 2021.12.15
def convert_frame_num(arrs):
    for arr in arrs:
        arr['frame'] = arr['frame']- arr['frame'][0]+1
    return arrs

# fixed 2021.12.15
def save_npy(root, file_name, arr):
    """ ex)
    root = '/home/eckim/workspace/fhe_etri/Data/BBS/Sample_BBS/BBS'
    file_name = ll.skel_fn()  #/home/eckim/workspace/fhe_etri/Data/BBS/Sample_BBS/BBS/Preds/c4/a_014_4_3.json
    arr = feature_preprocessing() 
    """
    if not os.path.isdir(root+'/npy'):
        for i in range(1, 15): # create classes dir
            os.makedirs(root+'/npy/'+str(i), exist_ok=True)
            for j in range(5):     # create scores  dir
                os.makedirs(root+'/npy/'+str(i)+'/'+str(j), exist_ok=True)

    name = file_name.split('/')[-1].split('.')[0]
    class_name = file_name.split('/')[-2][-1]
    score = file_name.split('/')[-1].split('.')[0][-1]
    ID = file_name.split('/')[-1].split('.')[0][2:5]
    if not os.path.isdir(f'{root}/npy/{class_name}/{score}/{ID}'):
        os.makedirs(f'{root}/npy/{class_name}/{score}/{ID}')
        
    for idx, i in enumerate(arr):
        np.save(f'{root}/npy/{class_name}/{score}/{ID}/{name}_{idx}.npy', i)
        

def shift_to_zero(skeleton, nframe=2, njoints=30):
    early_frame_x = skeleton[:nframe*njoints:2]
    early_frame_y = skeleton[1:nframe*njoints:2]

    ix_nz = np.nonzero(early_frame_x)
    iy_nz = np.nonzero(early_frame_y)

    mean_x = np.mean(early_frame_x[ix_nz])
    mean_y = np.mean(early_frame_y[iy_nz])
    
    skeleton[::2] -= mean_x 
    skeleton[1::2] -= mean_y 
    return skeleton



from .BBS_pp_utils import COMMON_JOINT
# 키 normalize 
## 어깨 - 팔꿈치 / 허벅지 / 종아리 


xy_joint_inds = dict([(name,i) for i, name in enumerate([prefix+cj for cj in COMMON_JOINT for prefix in ["x", "y"]])])

def joint_length(joint, j1:str, j2:str):
    """measure lentgh of a joint from j1 to j2"""
    x1 = joint[xy_joint_inds["x"+j1]]
    x2 = joint[xy_joint_inds["x"+j2]]
    y1 = joint[xy_joint_inds["y"+j1]]
    y2 = joint[xy_joint_inds["y"+j2]]
    return np.sqrt((x1-x2)**2 + (y1-y2)**2)
    

def arms_and_legs(skeleton, topk=2):
    """
    get representative length of arms and legs
    """
    lls = []
    rls = []
    las = []
    ras = []
    for sk in skeleton.reshape(-1, 30):
        lls.append(joint_length(sk, 'l_hip', 'l_knee'))
        rls.append(joint_length(sk, 'r_hip', 'r_knee'))
        las.append(joint_length(sk, 'l_elbow', 'l_shoulder'))
        ras.append(joint_length(sk, 'r_elbow', 'r_shoulder')) 

    out = []    
    for arr in (lls, rls, las, ras):
        out.append(arr[np.argsort(arr)[-topk]])
    return out

PAIRS = {'larm':('l_elbow', 'l_shoulder'),
         'rarm':('r_elbow', 'r_shoulder'), 
         'lleg':('l_hip', 'l_knee'),
         'rleg':('r_hip', 'r_knee'),
         'body':('neck', 'pelvis')}

def measure_lengths(skeleton, topk=2):
    """
    get representative lengths of joints
    """
    
    out = []
    for pair in PAIRS:
        lengths = []
        for sk in skeleton.reshape(-1, 30):
            lengths.append(joint_length(sk, *PAIRS[pair]))
            
        out.append((pair,lengths[np.argsort(lengths)[-topk]]))
            
    return dict(out)