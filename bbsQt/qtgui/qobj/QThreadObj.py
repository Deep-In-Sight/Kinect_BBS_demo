from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtPrintSupport import *
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
from functools import partial
import pickle

import matplotlib.pyplot as plt 


from bbsQt.model import kinect_utils as ku 
from bbsQt.model import rec_utils as ru
from bbsQt.constants import NFRAMES

WAIT = 0.01


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

        print("QTrhead record", self.k4a)

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

    def mkd(self, Locale, SubjectID, ScenarioNo):
        self.Locale = Locale
        self.SubjectID = SubjectID
        self.ScenarioNo = ScenarioNo
        
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
    def save_multiproc(self):
        self.stackColor = np.array(self.stackColor)
        # 모든 스켈레톤이 다있는 프레임 
        maxValue = len(self.stackJoint[0])
        maxframe_idx = 0
        for idx, i in enumerate(range(1, len(self.stackJoint))):
            if maxValue < len(self.stackJoint[i]):
                maxValue = len(self.stackJoint[i])
                maxframe_idx = idx
        
        print('[Qthread obj] maxperson', maxValue)
        print('[Qthread obj] maxframe idx',maxframe_idx)
        self.skarr  = ku.kinect2mobile_direct_lists(self.stackJoint)
        self.sk_viewer(self.skarr, self.stackColor, maxframe_idx, 1)

        skimage = self.load_image(maxframe_idx)
        
        ## IMAGE SAVE 
        idx = list(range(self.pic_Count))

        print("[Qthread obj] Number of frames", len(self.stackColor))
        # queues = [Queue() for i in range(Ncpu)]
        t0 = time.time()
        if self.camera_num == 1 :
            camera_num = 'e_'
        elif self.camera_num == 0:
            camera_num = 'a_'
        
        bt_path = f"./{self.Locale}/{str(self.SubjectID).zfill(3)}/BT/{camera_num}.pickle"
        pickle.dump(self.skarr, open(bt_path, "wb"))

        for i, color in enumerate(self.stackColor):
            cv2.imwrite(f"./{self.Locale}/{str(self.SubjectID).zfill(3)}/RGB/{camera_num+str((idx[i]) + 1).zfill(4)}.jpg", color)

        #print(f"Dumping {self.pic_Count} images using {Ncpu} done {time.time() - t0:.2f}")

        # 저장한 이미지의 인덱스를 읽어서 뷰어에 연결해주는 함수 
        return skimage


    def sk_viewer(self, json_to_arr_list, jpg_list, idx=0, save=1):
        left_arms = ['l_shoulder', 'l_elbow', 'l_hand']
        right_arms = ['head', 'r_shoulder',  'r_elbow', 'r_hand']
        body = ['head','l_shoulder', 'r_shoulder', 'r_hip', 'l_hip', 'l_shoulder']
        leg = ['r_foot', 'r_knee', 'r_hip', 'l_hip', 'l_knee', 'l_foot']
        ii = [left_arms, right_arms, body, leg]

        #print(json_to_arr_list.shape)

        fig, ax = plt.subplots(figsize=(16,9))
        #im = plt.imread(jpg_list[idx])
        im = jpg_list[idx]
        
        im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)

        ax.imshow(im, zorder=1)
        for color_idx, i in enumerate(json_to_arr_list):
            if color_idx == 0: 
                color = 'tab:blue'
            elif color_idx == 1:
                color = 'tab:orange'
            else:
                color = 'tab:green'
            for j in ii:
                ax.plot([i['x'+sa][idx]*2.3 + 30 for sa in j if i['x'+sa][idx] !=0], 
                        [i['y'+sa][idx]*1.8 for sa in j if i['x'+sa][idx] !=0],
                        color=color, lw=10)
                ax.axes.xaxis.set_visible(False)
                ax.axes.yaxis.set_visible(False)        
        if save == 1:
            os.makedirs('image', exist_ok=True)
            plt.savefig(f'image/img_00{idx}.jpg', bbox_inches='tight')
        #plt.show()

    def load_image(self, idx):
        fn_img = f'image/img_00{idx}.jpg'
        img = cv2.imread(fn_img)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        #img = imgutil.rgb2gray(img)
        img = cv2.resize(img, (270, 270))
        img = np.array(img).astype(np.uint8)
        height, width, channel = img.shape
        bytesPerLine = 3 * width
        pixmap   = QPixmap(QImage(img, width, height, bytesPerLine, QImage.Format_RGB888))
        return pixmap