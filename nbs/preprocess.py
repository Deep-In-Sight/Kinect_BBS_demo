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
    for line in sub:
        vec.extend([line[ff] for ff in line.dtype.names if ff not in "frame"])

    return np.array(vec)