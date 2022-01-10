import numpy as np 



def fn_npy(cam, ID, class_name, score,idx):
    return f'{class_name}/{score}/{ID}/{cam}_{ID}_{class_name}_{score}_{idx}.npy'

def merge_main_npy(main_list, prefix=""):
    scene = []
    main_person = []
    with open(main_list, "r") as f:
        _ = f.readline() # 첫 줄은 가짜.
        for l in f.readlines():
            fn, idx = l.rstrip().split(" ")
            # 정정한 경우 처리
            if idx == "bad":
                # remove last line 
                scene.pop(), main_person.pop()
                #and ignore this line
                continue

            fn = fn.split("/")[-1]
            scene.append(fn)
            main_person.append(int(idx))

    main = np.zeros(len(scene), dtype=[("cam", object), 
                                       ('ID',int),
                                       ('class',int), 
                                       ('score',int),
                                       ('main', int), 
                                       ('jpg', object),
                                       ('npy', object)
                                      ])

    for i, (ss, mp) in enumerate(zip(scene, main_person)):
        cam, ID, class_name, score = ss.split("_")
        main[i]['cam'] = cam
        main[i]['ID'] = int(ID)
        main[i]['class'] = int(class_name)
        main[i]['score'] = int(score)
        main[i]['main'] = int(mp)
        main[i]['jpg'] = ss
        main[i]['npy'] = prefix+fn_npy(cam, ID, class_name, score, mp)
    return main

##### Standardization

from bbsQt.model import BBS_pp_utils as bbpp
common_joints = bbpp.COMMON_JOINT
xy_joint_inds = dict([(name,i) for i, name in enumerate([prefix+cj for cj in common_joints for prefix in ["x", "y"]])])

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