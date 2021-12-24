import json
import numpy as np
import os
import shutil
import pathlib
from glob import glob


cc6={'1':[1,2,6,7],
     '4':[4,3,5],
     '13':[13,14,11],
     '12':[12],
     '8':[8],
     '9':[9,10]}

cc5={'1':[1,2,6,7],
     '4':[4,3,5],
     '13':[13,14,11,9,10],
     '12':[12],
     '8':[8]}

cc14=dict([(str(i),[i]) for i in range(1,15)])

# ID는 애자일그로스에서 메일로 알려줌 
chunk_14 = [1, 2, 3, 4, 5, 6, 7, 8, 44, 45, 54, 55, 56, 
            57, 58, 59, 60, 61, 82, 83, 84, 85, 86, 87, 88]
chunk_6 = np.arange(9, 33)
chunk_6 = np.append(chunk_6, 36)
chunk_5 = np.array([i for i in range(1,421) if i not in chunk_14 and i not in chunk_6])

## Split RGB images

class Img_dir():
    def __init__(self, fn):
        base, main = fn.split("/g1/")
        self.base_dir = base+"/g1"
        self.cam, self.num, _, self.type, _, self.action, self.score, self.fname = main.split("/")
    
    def __repr__(self):
        return self._gen_fn()
    
    def _gen_fn(self):
        return "/".join([self.base_dir, self.cam, self.num, 'BBS', self.type,
                         self.action, self.score])
    
    def new_action(self, action):
        self.action = str(action)
        return self._gen_fn()
    
    def update(self, type=None, cam=None, action=None):
        if type is not None:
            self.type = type
        if cam is not None:
            self.cam = cam
        if action is not None:
            self.action = str(action)
        
        return self._gen_fn()

def list_all_imgs(fn, img_cam):
    fn = Img_dir(fn)
    img_dir = fn.update(type="RGB", cam=img_cam)
    # 왜 어떤 애들은 L 이고 어떤 애들은 a냐고... 
    img_dir = img_dir.replace("RGB/", "RGB/*/")

    all_imgs = glob(img_dir+"/*.jpg")
    all_imgs.sort()
    return all_imgs
    
def split_img_list(fn, ccs, img_cam): 
    all_imgs = list_all_imgs(fn, img_cam)
    #print(all_imgs)
    # IMG list
    with open(fn) as f:
        ll = f.readlines()
        if len(ll) == 1: 
            # 1-class point_data.csv has "" in the first line. --very annoying... 
            ll = [0]
        else:
            # A few files have trailing empty line ('\n')
            ll = [int(l.rstrip().split(",")[-1]) for l in ll[:len(ccs)]]

    ll = ll + [len(all_imgs)]

    img_lists=[all_imgs[ll[i]:ll[i+1]] for i in range(len(ccs)) ]
    return img_lists

def do_split(fn, ccs, img_cam=None):
    _, score = fn.split("/")[-3:-1]
    #print(_, score)
    img_lists = split_img_list(fn, ccs, img_cam)
    print(img_lists)
    for img_list, new_cc in zip(img_lists, ccs):
        new_dir = Img_dir(img_list[0])
        nd = new_dir.update(action=new_cc)
        if not os.path.isdir(nd):
            #print(nd)
            #os.mkdir(nd)
            pathlib.Path(nd).mkdir(parents=True, exist_ok=True)
            for img in img_list:
                fname = img.split("/")[-1]
                shutil.move(img, "/"+nd+"/"+fname)
            

### SPLIT predition .json

def read_points_csv(fn, ccs):
    with open(fn) as f:
        ll = f.readlines()
        if len(ll) == 1: 
            # 1-class point_data.csv has "" in the first line. --very annoying... 
            ll = [0]
        else:
            # A few files have trailing empty line ('\n')
            ll = [int(l.rstrip().split(",")[-1]) for l in ll[:len(ccs)]]

    return ll

def split_lines(fn_pred, bins):
    with open(fn_pred) as json_file:
        ll = json_file.readlines()
        bins = bins + [len(ll)+1]
        j_lines = [list() for i in range(len(bins)-1)]
        for iframe, l in enumerate(ll):
            jl = json.loads(l)
            j_lines[np.digitize(jl['frame'], bins)-1].append(jl)
            
    return j_lines

def write_jsonl(fn, data):
    with open(fn, 'w') as f:
        for jj in data:
            f.write(json.dumps(jj)+'\n')