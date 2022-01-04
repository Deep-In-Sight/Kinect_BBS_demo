import numpy as np

ORG_KNT_TYPEs = ["PELVIS", "SPINE_NAVAL", "SPINE_CHEST", "NECK", "CLAVICLE_LEFT", "SHOULDER_LEFT", "ELBOW_LEFT",
                    "WRIST_LEFT", "HAND_LEFT", "HANDTIP_LEFT", "THUMB_LEFT", "CLAVICLE_RIGHT", "SHOULDER_RIGHT", "ELBOW_RIGHT",
                    "WRIST_RIGHT", "HAND_RIGHT", "HANDTIP_RIGHT", "THUMB_LEFT", "HIP_LEFT", "KNEE_LEFT", "ANKLE_LEFT", "ROOT_LEFT",
                    "HIP_RIGHT", "KNEE_RIGHT", "ANKLE_RIGHT", "FOOT_RIGHT", "HEAD", "NOSE", "EYE_LEFT", "EAR_LEFT","EYE_RIGHT", "EAR_RIGHT"]

K2M = {"SHOULDER_LEFT":"l_shoulder",
       "SHOULDER_RIGHT":"r_shoulder",
       "ELBOW_LEFT":"l_elbow", 
       "ELBOW_RIGHT":"r_elbow", 
       "WRIST_LEFT":"l_hand", 
       "WRIST_RIGHT":"r_hand",
       "HIP_LEFT":"l_hip", 
       "HIP_RIGHT":"r_hip", 
       "KNEE_LEFT":"l_knee", 
       "KNEE_RIGHT":"r_knee",
       "ANKLE_LEFT":"l_foot", 
       "ANKLE_RIGHT":"r_foot",
       "NOSE":"head"}

def get_a_skel(tdict, this_person):
    for this_joint in this_person:
        tdict["x"+this_joint[0]] = this_joint[1]
        tdict["y"+this_joint[0]] = this_joint[2]
        
from . import BBS_pp_utils as bbpp
def kinect2mobile_direct(klist, remove_zeros=True):
    """fills mobile_skeleton array with KINECT_BBS skeleton 
       directly from kinect application
       
       Kinect application passes 
       per-frame list 
           of per-person list 
               of per-skeleton list
       
       KINECT_BBS names are different from 
    """
    
    # K2M = {"SHOULDER_LEFT":"l_shoulder",
    #        "SHOULDER_RIGHT":"r_shoulder",
    #        "ELBOW_LEFT":"l_elbow", 
    #        "ELBOW_RIGHT":"r_elbow", 
    #        "WRIST_LEFT":"l_hand", 
    #        "WRIST_RIGHT":"r_hand",
    #        "HIP_LEFT":"l_hip", 
    #        "HIP_RIGHT":"r_hip", 
    #        "KNEE_LEFT":"l_knee", 
    #        "KNEE_RIGHT":"r_knee",
    #        "ANKLE_LEFT":"l_foot", 
    #        "ANKLE_RIGHT":"r_foot",
    #        "NOSE":"head"} # Assume Kinect nose == common head

    if remove_zeros:
        # remove preceeding non-detections
        while True:
            if len(klist[0]) ==0:
                klist.pop(0)
            else:
                break

        # remove trailing non-detections
        while True:
            if len(klist[-1]) ==0:
                klist.pop(-1)
            else:
                break

    mdtype = bbpp.get_dtypes(skeleton="COMMON")
    marr = np.zeros(len(klist), dtype=mdtype)
    
    # Initialize temporary dict
    tdict = dict([(prx+name, 0) for name in ORG_KNT_TYPEs for prx in ["x", "y"]])

    for iframe, this_frame in enumerate(klist):
        for this_person in this_frame:
            get_a_skel(tdict, this_person)
            
            # Assume neck is the mid point of shoulders
            marr[iframe]['xneck'] = (tdict['xSHOULDER_LEFT'] + tdict['xSHOULDER_RIGHT'])/2
            marr[iframe]['yneck'] = (tdict['ySHOULDER_LEFT'] + tdict['ySHOULDER_RIGHT'])/2

            marr[iframe]['xpelvis'] = (tdict['xHIP_LEFT'] + tdict['xHIP_RIGHT'])/2
            marr[iframe]['ypelvis'] = (tdict['yHIP_LEFT'] + tdict['yHIP_RIGHT'])/2

            for common_field in K2M:
                for prefix in ['x','y']:
                    marr[prefix+K2M[common_field]] = tdict[prefix+common_field]

        marr[iframe]['frame'] = iframe +1
    
    return marr

def kinect2mobile_direct_lists(klist, remove_zeros=True):
    """fills mobile_skeleton array with KINECT_BBS skeleton 
       directly from kinect application
       
       Kinect application passes 
       per-frame list 
           of per-person list 
               of per-skeleton list
       
       KINECT_BBS names are different from 
    """
    
    # K2M = {"SHOULDER_LEFT":"l_shoulder",
    #        "SHOULDER_RIGHT":"r_shoulder",
    #        "ELBOW_LEFT":"l_elbow", 
    #        "ELBOW_RIGHT":"r_elbow", 
    #        "WRIST_LEFT":"l_hand", 
    #        "WRIST_RIGHT":"r_hand",
    #        "HIP_LEFT":"l_hip", 
    #        "HIP_RIGHT":"r_hip", 
    #        "KNEE_LEFT":"l_knee", 
    #        "KNEE_RIGHT":"r_knee",
    #        "ANKLE_LEFT":"l_foot", 
    #        "ANKLE_RIGHT":"r_foot",
    #        "NOSE":"head"} # Assume Kinect nose == common head

    if remove_zeros:
        # remove preceeding non-detections
        while True:
            if len(klist[0]) ==0:
                klist.pop(0)
            else:
                break

        # remove trailing non-detections
        while True:
            if len(klist[-1]) ==0:
                klist.pop(-1)
            else:
                break

    nperson = 4
    mdtype = bbpp.get_dtypes(skeleton="COMMON")
    marrs = [np.zeros(len(klist), dtype=mdtype) for i in range(nperson)]
    
    # Initialize temporary dict
    tdict = dict([(prx+name, 0) for name in ORG_KNT_TYPEs for prx in ["x", "y"]])

    for iframe, this_frame in enumerate(klist):
        for iperson, this_person in enumerate(this_frame):
            marr = marrs[iperson]
            get_a_skel(tdict, this_person)
            
            # Assume neck is the mid point of shoulders
            marr[iframe]['xneck'] = (tdict['xSHOULDER_LEFT'] + tdict['xSHOULDER_RIGHT'])/2
            marr[iframe]['yneck'] = (tdict['ySHOULDER_LEFT'] + tdict['ySHOULDER_RIGHT'])/2

            marr[iframe]['xpelvis'] = (tdict['xHIP_LEFT'] + tdict['xHIP_RIGHT'])/2
            marr[iframe]['ypelvis'] = (tdict['yHIP_LEFT'] + tdict['yHIP_RIGHT'])/2

            for common_field in K2M:
                for prefix in ['x','y']:
                    marr[prefix+K2M[common_field]] = tdict[prefix+common_field]

        marr[iframe]['frame'] = iframe +1
    
    new_marr = []
    for i, mm in enumerate(marrs):
        if np.sum(mm['frame']) >= 0:
            #print("check", i, np.sum(mm['frame']))
            new_marr.append(mm)

    return new_marr
