from glob import glob 
import numpy as np
import cv2
import PIL
from BBS_pp_utils import json_to_arr
import matplotlib.pyplot as plt 
import os

# Path
img_base_dir = "/home/eckim/workspace/fhe_etri/Data/BBS/Sample_BBS/BBS/RGB/"
skel_base_dir ="/home/eckim/workspace/fhe_etri/Data/BBS/Sample_BBS/BBS/Preds/"


class Loader():
    
    def __init__(self, action=0, score=1, ID=0, cam="a", img_base_dir=img_base_dir, skel_base_dir=skel_base_dir, dtypes=None):
        self.action = action
        self.score = score 
        self.ID = ID
        self.cam = cam 
        self.__skel_base = skel_base_dir
        self.__img_base = img_base_dir
        self.dtypes = dtypes
    
    
    @property
    def action(self):
        return self.__action
    
    @action.setter
    def action(self, v):
        if v is not None: self.__action = v
        
    @property
    def score(self):
        return self.__score
    
    @score.setter
    def score(self, v):
        if v is not None: self.__score = v
        
    @property
    def ID(self):
        return self.__ID
    
    @ID.setter
    def ID(self, v):
        if v is not None: self.__ID = v
                
    @property
    def cam(self):
        return self.__cam
    
    @cam.setter
    def cam(self, v):
        if v is not None: self.__cam = v
        # update fn? 
            
    def _update(self, action=None, score=None, ID=None, cam=None):
        self.action = action
        self.score = score
        self.ID = ID    
        self.cam = cam

    def skel_fn(self, action=None, score=None, ID=None, cam=None):
        # Update if not None
        self._update(action, score, ID, cam)
        return self.__skel_base+f"c{self.action}/{self.cam}_{self.ID:03d}_{self.action}_{self.score}.json"
    
    def img_fn_prefix(self, action=None, score=None, ID=None, cam=None):
        # Update if not None
        self._update(action, score, ID, cam)
        return self.__img_base+f'{self.action}/{self.score}/{self.ID:03d}/'
    
    def get_jpg_list(self, action=None, score=None, ID=None, cam=None):
        # Update if not None
        self._update(action, score, ID, cam)
        fn_list = glob(self.img_fn_prefix()+"*.jpg")
        fn_list.sort()
        return fn_list
    
    def get_id(self, action=None, score=None):
        # Update if not None
        self.action = action
        self.score = score
        id_list = os.listdir((self.__img_base+f'{self.action}/{self.score}'))
        id_list.sort()
        return id_list

    def load_skel(self, fn=None, parms=None):
        """If fn is given, others are ignored
        """
        if fn is None:
            try:
                fn = self.skel_fn(*parms)
                return json_to_arr(fn, self.dtypes)
            except FileNotFoundError:
                print(fn, "not found -- faield to detect skeleton?")
                return None
        
        