from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
#from datetime import datetime
import multiprocessing as mp
#import matplotlib.pyplot as plt
import time
import numpy as np
#from PIL import Image
import pandas as pd
#import src.image as imgutil
import os
import cv2
import pwd

import pickle



from bbsQt.model import kinect_utils as ku 
from bbsQt.model import rec_utils as ru

WAIT = 0.01

def do_save_multiproc(path_root, data, idx0, Locale, ID):
    i = 0
    print(path_root)
    for color in data:
        cv2.imwrite(f"./{Locale}/{str(ID).zfill(3)}/RGB/{str((i+idx0) + 1).zfill(4)}.jpg", color)
        i = i + 1


class qThreadRecord(QThread):
    
    def __init__(self, k4a, bt, LbFPS, qScenario, PWD, camera_num):
        super().__init__()
        self.stackColor = []
        self.stackIR = []
        self.stackDepth = []
        self.stackJoint = []
        self.k4a = k4a
        self.bt = bt
        self.isRun = False
        self.LbFPS = LbFPS
        self.qScenario = qScenario
        self.Ncpu = 2
        self.pic_Count = 0
        self.PWD = PWD
        self.camera_num = camera_num

    def setRun(self, Run):
        self.isRun = Run


    def init(self, PWD, Locale, SubjectID, btn):
        self.PWD = PWD
        self.Locale = Locale
        self.SubjectID = SubjectID
        self.btn = btn

        if self.k4a is not None:
            self.path_save = f"{self.PWD}/{str(self.SubjectID).zfill(3)}"
        else:
            self.path_save = f"{self.PWD}/images"

    def reset(self, k4a, bt):
        self.k4a = k4a
        self.bt = bt

    def mkd(self, Locale, SubjectID):
        self.Locale = Locale
        self.SubjectID = SubjectID
        
        self.path_color = f"{self.PWD}/{self.Locale}/{str(self.SubjectID).zfill(3)}/RGB"
        self.path_bt = f"{self.PWD}/{self.Locale}/{str(self.SubjectID).zfill(3)}/BT"

        os.makedirs(self.path_color, exist_ok = True)
        os.makedirs(self.path_bt, exist_ok = True)

    def __del__(self):
        print(".... end thread.....")
        self.wait()        

    def resetstate(self):
        self.stackColor = []
        self.stackIR = []
        self.stackDepth = []
        self.stackJoint = []
        self.pic_Count = 0

    def is_recoding(self):
        return self.isRun 
    
    def run(self):
        t_elapsed = 0
        nframes = 0
        i = 0

        t0 = time.time()
        self.resetstate()
        while (self.btn.endtime.text() == "F"):
            try:
                capture = self.k4a.update()
                body_frame = self.bt.update()

                rat, color = capture.get_color_image()
                    
                ret, dc_image = capture.get_colored_depth_image()
                ret, b_image = body_frame.get_segmentation_image()
                s_image = cv2.addWeighted(dc_image, 0.6, b_image, 0.4, 0)
                s_image = cv2.cvtColor(s_image, cv2.COLOR_BGR2RGB)
                joint = body_frame.ex_joints(s_image) # extract joint

                capture.reset()
                body_frame.reset()
            except:
                pass
            else:
                self.stackColor.append(color)
                self.stackJoint.append(joint) # joints are stored here
                self.pic_Count += 1

                
                nframes += 1
                t1 = time.time()
                t_elapsed += t1-t0

                self.btn.capturetime.setText(str(round(t_elapsed,2)))

                t0 = t1
        self.isRun = False


    def getcnt(self):
        return self.pic_Count

    def get_color(self):
        return self.stackColor

    # todo data tree  
    def save_multiproc(self, q1, e_sk):
        #Ncpu = self.Ncpu
        self.stackColor = np.array(self.stackColor)
        pickle.dump(self.stackJoint, open(f"{self.path_bt}/bodytracking_data.pickle", "wb"))
        #skeleton =  skeleton_to_arr_direct(self.stackJoint)
        scene = ku.kinect2mobile_direct(self.stackJoint)

        nframe = 10 
        sub = ru.smoothed_frame_N(scene, nframe=nframe, shift=1)
        skeleton = ru.ravel_rec(sub)[np.newaxis, :]




        #print("is e_sk set?0", e_sk.is_set())
        #self.stackJoint = 
        #arr = pickle.load(open("/home/hoseung/Work/data/BBS/npy_a/1/0/031/a_031_1_0_0.npy", "rb"))
        #q1.put({"skeleont":arr})
        q1.put({"skeleton": skeleton})
        #print("is q1 empty?", q1.empty())
        e_sk.set()
        #print("is e_sk set?1", e_sk.is_set())
        
        #uid = pwd.getpwnam("etri_ai2").pw_uid
        #os.chown(f"{self.path_bt}/bodytracking_data.pickle", uid, -1)

        idx = list(range(self.pic_Count))
        #idx = np.array_split(idx, Ncpu);

        #for i in range(int(Ncpu)):
        #idx[i] = idx[i].tolist()

        print("Number of frames", len(self.stackColor))
        # queues = [Queue() for i in range(Ncpu)]
        t0 = time.time()
        #print(self.path_save)
        #args = [(self.path_save, self.stackColor[idx[i]], idx[i][0], self.Locale, self.SubjectID) for i in range(Ncpu)]
        #jobs = [mp.Process(target = do_save_multiproc, args=(a)) for a in args]
        #c(path_root, data, idx0, Locale, ID
        if self.camera_num == 1 :
            self.camera_num = 'a_'
        else:
            self.camera_num = 'e_'

        for i, color in enumerate(self.stackColor):
            cv2.imwrite(f"./{self.Locale}/{str(self.SubjectID).zfill(3)}/RGB/{self.camera_num+str((i+idx[i]) + 1).zfill(4)}.jpg", color)

        #print(f"Dumping {self.pic_Count} images using {Ncpu} done {time.time() - t0:.2f}")

        # for j in jobs: 
        #     j.start(); 
        # for j in jobs: 
        #     j.join();    

