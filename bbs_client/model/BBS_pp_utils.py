import numpy as np

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