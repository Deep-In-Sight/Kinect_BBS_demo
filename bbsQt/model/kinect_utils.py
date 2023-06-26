import numpy as np
from bbsQt.constants import mp_pose_lm_name

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
    for i, this_joint in enumerate(this_person):
        tdict["x"+mp_pose_lm_name[i]] = this_joint[0]
        tdict["y"+mp_pose_lm_name[i]] = this_joint[1]

def get_a_skel_mp(tdict, this_person):
    tdict["xl_hand"] = this_person[20][0]
    tdict["yl_hand"] = this_person[20][1]
    tdict["xr_hand"] = this_person[19][0]
    tdict["yr_hand"] = this_person[19][1]
    tdict["xl_elbow"] = this_person[18][0]
    tdict["yl_elbow"] = this_person[18][1]
    tdict["xr_elbow"] = this_person[17][0]
    tdict["yr_elbow"] = this_person[17][1]
    tdict["xl_shoulder"] = this_person[16][0]
    tdict["yl_shoulder"] = this_person[16][1]
    tdict["xr_shoulder"] = this_person[15][0]
    tdict["yr_shoulder"] = this_person[15][1]
    tdict["xhead"] = this_person[0][0]
    tdict["yhead"] = this_person[0][1]
    neck = (this_person[11] + this_person[12])/2
    tdict["xneck"] = neck[0]
    tdict["yneck"] = neck[1]
    tdict["xl_foot"] = this_person[31][0]
    tdict["yl_foot"] = this_person[31][1]
    tdict["xr_foot"] = this_person[28][0]
    tdict["yr_foot"] = this_person[28][1]
    tdict["xl_knee"] = this_person[25][0]  
    tdict["yl_knee"] = this_person[25][1]
    tdict["xr_knee"] = this_person[26][0]
    tdict["yr_knee"] = this_person[26][1]
    tdict["xl_hip"] = this_person[23][0]
    tdict["yl_hip"] = this_person[23][1]
    tdict["xr_hip"] = this_person[24][0]
    tdict["yr_hip"] = this_person[24][1]
    pelvis = ((this_person[23] + this_person[24])*2/3 + (this_person[11] + this_person[12])/3)
    tdict["xpelvis"] = pelvis[0]
    tdict["ypelvis"] = pelvis[1]

        
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

def kinect2mobile_direct_lists(klist, remove_zeros=True, nperson_max = 4):
    """fills mobile_skeleton array with Media pipe skeleton 
       
        MP returns 
        per-frame list 
            of per-skeleton list       

        ASSUMES ONLY ONE PERSON PER FRAME!!!!!!!
    """

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

    # Assuming no more than 4 people will be recorded.
    mdtype = bbpp.get_dtypes(skeleton="COMMON")
    marr = np.zeros(len(klist), dtype=mdtype)
    # Initialize temporary dict
    tdict = dict([(prx+name, 0) for name in ORG_KNT_TYPEs for prx in ["x", "y"]])

    for iframe, this_person in enumerate(klist):
        get_a_skel_mp(tdict, this_person)
        for dt in marr.dtype.names:
            if dt == "frame":
                marr[iframe][dt] = iframe +1
            else:
                marr[dt] = tdict[dt]
    return marr