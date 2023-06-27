import numpy as np

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