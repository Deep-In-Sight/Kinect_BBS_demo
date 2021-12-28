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