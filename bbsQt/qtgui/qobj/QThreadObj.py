from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtPrintSupport import *
import time
import numpy as np
import os
import cv2
import pickle

import matplotlib.pyplot as plt 

from bbsQt.model import kinect_utils as ku 
from bbsQt.model import rec_utils as ru
from bbsQt.constants import NFRAMES, VERBOSE
from bbsQt.model.Fall_predict import Score_updator

WAIT = 0.01

class qThreadRecord(QThread):
    
    def __init__(self, k4a, bt, LbFPS, qScenario, PWD, camera_num, q1, e_sk, e_ans, q_answer):
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
        self.q1 = q1
        self.e_sk = e_sk

        self.e_ans = e_ans
        self.q_answer = q_answer

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


    # def getcnt(self):
    #     return self.pic_Count

    # def get_color(self):
    #     return self.stackColor

    # todo data tree  
    def save_multiproc(self):
        self.stackColor = np.array(self.stackColor)
        # 모든 스켈레톤이 다있는 프레임 
        
        # In case on skeleton was captured
        try:
            self.skarr_list  = ku.kinect2mobile_direct_lists(self.stackJoint)
        except:
            self.qScenario.viewInfo.setText(f"Failed to detect any skeleton, Try again")
            font = QFont()
            #font.setBold(True)
            font.setPointSize(14)
            self.qScenario.viewInfo.setFont(font)
            return -1

        nframes = len(self.skarr_list[0])
        
        i_person_exist = np.ones(nframes, dtype=bool)
        for karr in self.skarr_list:
            i_non_empty = np.ones(nframes, dtype=bool)
            for name in karr.dtype.names:
                i_non_empty *= np.array(karr[name] > 0)
            i_person_exist *= i_non_empty
        
        maxframe_idx = np.argmin(i_person_exist)
        print('[Qthread obj] maxframe idx',maxframe_idx)

        self.sk_viewer(self.skarr_list, self.stackColor, maxframe_idx, 1)
        skimage = self.load_image(maxframe_idx)
        
        ## IMAGE SAVE 
        idx = list(range(self.pic_Count))

        print("[Qthread obj] Number of frames", len(self.stackColor))
        # queues = [Queue() for i in range(Ncpu)]
        t0 = time.time()
        #args = [(self.path_save, self.stackColor[idx[i]], idx[i][0], self.Locale, self.SubjectID) for i in range(Ncpu)]
        #jobs = [mp.Process(target = do_save_multiproc, args=(a)) for a in args]
        #c(path_root, data, idx0, Locale, ID
        if self.camera_num == 1 :
            camera_num = 'a_'
        elif self.camera_num == 0:
            camera_num = 'e_'

        #for i, color in enumerate(self.stackColor):
        #Save only one jpg
        i = maxframe_idx
        color = self.stackColor[i]
        cv2.imwrite(f"./{self.Locale}/{str(self.SubjectID).zfill(3)}/RGB/{camera_num+str((i+idx[i]) + 1).zfill(4)}.jpg", color)

        #print(f"Dumping {self.pic_Count} images using {Ncpu} done {time.time() - t0:.2f}")
        # 저장한 이미지의 인덱스를 읽어서 뷰어에 연결해주는 함수 
        return skimage

    def select_sk(self, skindex=0):
        """! Skeleton selector
        
        @param skindex index of the main skeleton in the skeleton list
        
        @return None

        @see 

        @remark
        

        문장

        """
        
        #pickle.dump(self.stackJoint, open(f"{self.path_bt}/bodytracking_data.pickle", "wb"))
        
        if not VERBOSE: print(f'[Qthread obj] skeleton index : {skindex}')
        if not VERBOSE: print("[Qthread obj] camera_num", self.camera_num)
        
        #scene = ku.kinect2mobile_direct(self.stackJoint)
        
        # FIX   20210107
        # this_scenario = self.qScenario.class_num.currentText()
        # this_score = self.qScenario.score_num.currentText()

        # self.action_num.currentText()랑 연결
        this_scenario = self.btn.action_num.currentText()
        this_score = self.btn.score_num.currentText()
        
        sub = ru.smoothed_frame_N(self.skarr_list[skindex], 
                                nframe=NFRAMES[f'{this_scenario}'],
                                shift=1)
        skeleton = ru.ravel_rec(sub)[np.newaxis, :]

        if self.camera_num == 0:
            camera_num = 'a'
        elif self.camera_num == 1:
            camera_num = 'e'

        tm = time.localtime()
        time_mark = f"{tm.tm_mon:02d}{tm.tm_mday:02d}{tm.tm_hour:02d}{tm.tm_min:02d}{tm.tm_sec:02d}"

        pickle.dump(self.skarr_list[skindex], open(f"{self.Locale}/BT/{camera_num}_{time_mark}_{this_scenario}_{this_score}_skeleton.pickle", "wb"))
        
        fn_scores = f"{self.Locale}/{str(self.SubjectID).zfill(3)}/Scores_{str(self.SubjectID).zfill(3)}.txt"

        #if DEBUG_FLAG1:
        #    pass
        #else:

        self.q1.put({"action":this_scenario,
                     "cam":camera_num, 
                     "skeleton": skeleton})
        self.e_sk.set()
        #############
        # Encryptor runs...
        # Then send ctxt to server
        # and Wait for server's answer
        self.e_ans.wait()
        self.e_sk.clear() # Just in case...
        
        answer = self.q_answer.get()
        answer_int = int(answer.split(":")[-1])

        # Update this score
        scu = Score_updator(fn_scores)
        scu.update(int(this_scenario), answer_int)
        all_txt = scu.text_output()
        scu.write_txt()
        fall_pred = scu.get_fall_prediction()
        if fall_pred == -1:
            self.qScenario.viewInfo.setText(f'Action #{this_scenario} \n {answer}\n\n' + all_txt + "\n")
        else:
            self.qScenario.viewInfo.setText(f'Action #{this_scenario} \n {answer}\n\n' + all_txt + "\n" + fall_pred)

        font = QFont()
        #font.setBold(True)
        font.setPointSize(14)
        self.qScenario.viewInfo.setFont(font)

        self.e_ans.clear()
        
            
    def sk_viewer(self, json_to_arr_list, jpg_list, idx=0, save=1):
        left_arms = ['l_shoulder', 'l_elbow', 'l_hand']
        right_arms = ['head', 'r_shoulder',  'r_elbow', 'r_hand']
        body = ['head','l_shoulder', 'r_shoulder', 'r_hip', 'l_hip', 'l_shoulder']
        leg = ['r_foot', 'r_knee', 'r_hip', 'l_hip', 'l_knee', 'l_foot']
        bodyparts = [left_arms, right_arms, body, leg]

        #print(json_to_arr_list.shape)

        fig, ax = plt.subplots(figsize=(16,9))
        #im = plt.imread(jpg_list[idx])
        im = jpg_list[idx]
        
        im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)

        ax.imshow(im, zorder=1)
        for color_idx, skarr in enumerate(json_to_arr_list):
            if color_idx == 0: 
                color = 'tab:blue'
            elif color_idx == 1:
                color = 'tab:orange'
            else:
                color = 'tab:green'
            for j in bodyparts:
                ax.plot([skarr['x'+sa][idx]*2.3 + 30 for sa in j if skarr['x'+sa][idx] !=0], 
                        [skarr['y'+sa][idx]*1.8 for sa in j if skarr['x'+sa][idx] !=0],
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