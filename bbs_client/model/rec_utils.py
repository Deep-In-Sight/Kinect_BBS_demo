# utils to deal with skeletons in structured arrays in the 'COMMON_JOINT' dtype. 
# Skeletons loaded from raw BBS data set are in multi-line .json format (or something similar), 
# and the skeleton internally from the Kinect QT application are in list of list of list.
# Both should first be converted to recarry, each line of which represents a person in a frame. 
import numpy as np

def smoothed_frame_sample(scene, fps = 1, window_size = 5):
    """일정 시간에 한번씩 ... 영상 길이가 다를 경우에 뒤를 0으로 채워야함 
    """
    FPS_ORIGINAL=10 # 인 것 같음...
    
    nskip = int(FPS_ORIGINAL/fps)
    nframe = np.ceil((len(scene) - window_size)/ nskip).astype(int)

    sub = np.zeros(nframe, dtype=scene.dtype) #scene.dtype - frame

    for i in range(nframe):
        temp = scene[i*nskip:i*nskip+window_size]

        for feat in temp.dtype.names: # recarry라서 한 번에 np.mean 불가능
            sub[i][feat] = np.median(temp[feat])

    return sub


def smoothed_frame_N(scene, nframe = 10, window_size = 5, shift=0):
    FPS_ORIGINAL=10 # 인 것 같음...
    
    nskip = int((len(scene)-shift) / nframe)
    #nframe = np.ceil((len(scene) - window_size)/ nskip).astype(int)

    sub = np.zeros(nframe, dtype=scene.dtype) #scene.dtype - frame

    for i in range(nframe):
        temp = scene[i*nskip+shift:i*nskip+window_size+shift]

        for feat in temp.dtype.names: # recarry라서 한 번에 np.mean 불가능
            sub[i][feat] = np.median(temp[feat])

    return sub


def ravel_rec(sub, return_feature=False):
    vec=[]
    if return_feature:
        features=[]
        for i, line in enumerate(sub):
            this_line=[]
            for ff in line.dtype.names:
                if ff != "frame":
                    this_line.append(line[ff])
                    features.append(ff+f"_{line['frame']}")
            vec.extend(this_line)
                    
        return features, np.array(vec)
    else:
        for line in sub:
            vec.extend([line[ff] for ff in line.dtype.names if ff not in "frame"])

    return np.array(vec)