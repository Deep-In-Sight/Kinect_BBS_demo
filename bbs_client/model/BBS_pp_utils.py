import numpy as np
import os
import json
from numpy.lib.recfunctions import unstructured_to_structured
import matplotlib.pyplot as plt 


_coco_pair_parts = ["eye", "ear", "shoulder", 
                    "elbow", "wrist", "hip", "knee", "ankle"]

COCO_JOINTS = ["nose"] + [ lr+body for lr in ['left_','right_'] for body in _coco_pair_parts]

COCO_JOINTS = np.array(["nose", "left_eye", "right_eye",
                        "left_ear", "right_ear", "left_shoulder", "right_shoulder",
                        "left_elbow", "right_elbow", "left_wrist", "right_wrist",
                        "left_hip", "right_hip", "left_knee", "right_knee",
                        "left_ankle", "right_ankle"])

KINECT_JOINTS = np.array(['PELVIS', 'SPINE_NAVAL', 'SPINE_CHEST', 'NECK',
                        'CLAVICLE_LEFT', 'SHOULDER_LEFT', 'ELBOW_LEFT',
                        'WRIST_LEFT', 'HAND_LEFT', 'HANDTIP_LEFT',
                        'THUMB_LEFT', 'CLAVICLE_RIGHT', 'SHOULDER_RIGHT',
                        'ELBOW_RIGHT', 'WRIST_RIGHT', 'HAND_RIGHT',
                        'HANDTIP_RIGHT', 'THUMB_RIGHT', 'HIP_LEFT',
                        'KNEE_LEFT', 'ANKLE_LEFT', 'FOOT_LEFT',
                        'HIP_RIGHT', 'KNEE_RIGHT', 'ANKLE_RIGHT',
                        'FOOT_RIGHT', 'HEAD', 'NOSE',
                        'EYE_LEFT', 'EAR_LEFT', 'EYE_RIGHT', 'EAR_RIGHT'])

#COMMON ~= Mobile
COMMON_JOINT = np.array(["l_hand", "l_elbow", "l_shoulder",
                        "r_shoulder", "r_elbow", "r_hand", 
                        "head", 'neck', 'pelvis',
                        "l_foot", "l_knee", "l_hip", 
                        "r_hip", "r_knee", "r_foot"])
                        

def get_inds_to_store(dtypes, return_confidence=True):
    """get indices of joints to store.
    
    Parameters
    ----------
    return_confidence: bool [True]
        return indices of confidence value for each joint

    NOTE
    ----
    1. NOT all joints are useful
    2. COCO_JOINTS is a global constant
    3. No 'x' letter allowed in the original COCO_JOINTS list.

    """
    confidence = []
    ind_store = []
    for dt in dtypes.names:
        ind_json = np.where(dt.replace('x','') == COCO_JOINTS)[0]
        if len(ind_json) > 0: 
            ind_json = ind_json.squeeze()
            ind_store.extend([ind_json*3, ind_json*3+1])
            confidence.append(ind_json*3+2)
    if return_confidence:
        return np.array(ind_store), confidence
    else:
        return np.array(ind_store)


def _mean_dtype(arr):
    """Generate dtype for mean of left and right body parts.
    
    example
    -------
    arr.dtype  >>  ['left_hand','right_hand', 'left_knee', 'right_knee']
    
    _mean_dtype(arr)  >> ['hand', 'knee']
    """
    mean_dtypes=[]
    for nn in arr.dtype.names:
        dt = arr.dtype[nn]
        nn=nn.replace("left_",'')
        nn=nn.replace("right_",'')
        
        mean_dtypes.append((nn,dt))
    
    return list(set(mean_dtypes))

def switch_xy(string):
    """'x_left_elbow' -> 'y_left_elbow'

    But, why would I want this?? 
    """
    if string[0] == 'x':
        return 'y'+string[1:]
    elif string[0] == "y":
        return 'x'+string[1:]

def get_dtypes(skeleton = "COCO", 
               ignored_joints = ["left_eye", "right_eye", "left_ear", "right_ear"]):
    if skeleton == "COCO":
        joints = COCO_JOINTS
    elif skeleton == "KINECT":
        joints = KINECT_JOINTS
    elif skeleton == "COMMON":
        joints = COMMON_JOINT

    dtypes = [(dim_+cc, float) for cc in joints for dim_ in ['x','y'] if cc not in ignored_joints]
    dtypes = [("frame", int)] + dtypes
    dtypes = np.dtype(dtypes)
    return dtypes

def json_to_arr(fn, dtypes, credit_threshold = 0.5, maxp=4):
    """Returns list of skeleton arrays. 
    * Identity NOT fixed, yet. 
    
    parameters
    ----------
    credit_threshold : per-frame threshold of each skeleton
    maxp : maximum number of expected people, defaults to 4
    
    NOTE
    ----
    A person's skeleton with at least 1 frame above the credit threshold is stored and returned. 
    Other's are discarded
    
    """
    inds_store = get_inds_to_store(dtypes, return_confidence=False)

    with open(fn) as json_file:
        nframes = len(json_file.readlines())
        json_file.seek(0)

        # Assuming up to maxp people in the scene
        arrs = [np.zeros((nframes, len(dtypes))) for i in range(maxp)]
        for iframe, l in enumerate(json_file.readlines()):
            jl = json.loads(l)
            for ip, pp in enumerate(jl['predictions']):
                arrs[ip][iframe][0] = jl['frame']
                if pp['score'] > credit_threshold:
                    arrs[ip][iframe][1:] = np.array(pp['keypoints'])[inds_store]

        # convert arrays to recarrays
        arrs = [unstructured_to_structured(arr, dtype=dtypes) for arr in arrs if np.sum(arr[:,1:]) > 0]
        
    return arrs


def mean_side(arr):
    """Return left right mean values of SKP. 

    Rationale
    ----------
    Lateral view of a person can miss some parts of body 
    and/or confuse one side with the other.
    If both sides of body are expected to be in sync, 
    we can reduce the number of features 
    at the same time increase robustness of measurements 
    by taking the mean of both measurements.

    NOTE
    ----
    Takes one side value if the other side is not detected. 
    

    """
    mean = np.zeros(len(arr), dtype=_mean_dtype(arr))

    def switch_lr(string):
        if 'left_' in string:
            string = string.replace('left_', 'right_')
            return string
        elif 'right_' in string:
            string = string.replace('right_', 'left_')
            return string

    for dt in arr.dtype.names[3:]:
        missing = np.where(arr[dt] == 0)[0]
        dt2 = switch_lr(dt)
        arr[dt][missing] = arr[dt2][missing]
        mean_dt = dt.replace('right_', '').replace('left_','')
        mean[mean_dt] = np.mean([arr[dt], arr[dt2]], axis=0)

    for dt in arr.dtype.names[:3]:
        mean[dt] = arr[dt]
        
    return mean


def quick_view(arrs, x_feat = 'frame', fn=None):
    """simple plot of skeleton array

    arr can be a skeleton array or a list of skeleton arrays of common dtype
    """
    if isinstance(arrs, list):
        arr = arrs[0]
    else:
        arr = arrs

    # Number of features and
    n_features = len(arr.dtype)
    nx = np.ceil(np.sqrt(n_features)).astype(int)

    fig, axs = plt.subplots(nx, nx)
    fig.set_size_inches(nx*3, nx*3)
    axs = axs.ravel()

    features = arr.dtype.names
    features = [ff for ff in features if ff != x_feat]

    for i, arr in enumerate(arrs):
        for i, feat in enumerate(features):
            ax = axs[i]
            ax.scatter(arr[x_feat], arr[feat], s=2)
            ax.set_title(feat)
            
    plt.tight_layout()
    if fn is not None:
        plt.savefig(fn, dpi=72, facecolor='white')#.split('/')[-1]
        plt.close()
    else:
        plt.show()
        
def sk_viewer(json_to_arr_list, jpg_list, idx=0, save=0):
    '''
    skeleton viewer function 
    parameters
    ----------
    json_to_arr_list : json_to_arr_list function result
    jpg_list : Full frame list
    idx : Frame index that you want to see
    image save = 1 / not image save = 0
    '''
    left_arms = ['left_shoulder', 'left_elbow', 'left_wrist']
    right_arms = ['nose', 'right_shoulder',  'right_elbow', 'right_wrist']
    body = ['nose','left_shoulder', 'right_shoulder', 'right_hip', 'left_hip', 'left_shoulder']
    leg = ['right_ankle', 'right_knee', 'right_hip', 'left_hip', 'left_knee', 'left_ankle']
    ii = [left_arms, right_arms, body, leg]

    fig, ax = plt.subplots(figsize=(16,9))
    im = plt.imread(jpg_list[idx])
    ax.imshow(im, zorder=1)
    for color_idx, i in enumerate(json_to_arr_list):
        if color_idx == 0: 
            color = 'tab:blue'
        elif color_idx == 1:
            color = 'tab:orange'
        else:
            color = 'tab:green'
        for j in ii:
            ax.plot([i['x'+sa][idx] for sa in j if i['x'+sa][idx] !=0], [i['y'+sa][idx] for sa in j if i['x'+sa][idx] !=0], color=color)
    if save == 1:
        os.makedirs('image', exist_ok=True)
        plt.savefig(f'image/img_00{idx}.jpg')
    plt.show()