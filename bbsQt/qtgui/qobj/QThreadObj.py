from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap, QImage, QFont
from PyQt5.QtPrintSupport import *
import time
import numpy as np
import os
import cv2
import pickle
import mediapipe as mp
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils 
mp_drawing_styles = mp.solutions.drawing_styles
import matplotlib.pyplot as plt 

from bbsQt.model import kinect_utils as ku 
from bbsQt.model import rec_utils as ru
from bbsQt.constants import NFRAMES, VERBOSE, FN_SCORES, mp_pose_lm_name
from bbsQt.model.Fall_predict import Score_updator
WAIT = 0.01

def is_valid_skeleton(skeleton):
    return np.all(skeleton['frame'] != 0)


class qThreadRecord(QThread):
    
    def __init__(self, cap, mp_pose, qScenario, PWD, imgviwerRGB, q1, e_sk, e_ans, q_answer):
        super().__init__()
        self.stackColor = []
        self.stackDepth = []
        self.stackJoint = []
        self.cap = cap
        self.mp_pose = mp_pose
        self.isRun = False
        self.qScenario = qScenario
        self.Ncpu = 2
        self.pic_Count = 0
        self.PWD = PWD
        self.q1 = q1
        self.e_sk = e_sk
        self.e_ans = e_ans
        self.q_answer = q_answer
        self.imgviwerRGB = imgviwerRGB

    def setRun(self, Run):
        self.isRun = Run

    def init(self, PWD, btn):
        self.PWD = PWD
        self.btn = btn
        self.path_save = f"{self.PWD}/images"
        

    def reset(self, k4a, bt):
            self.k4a = k4a
            self.bt = bt

    def mkd(self, ScenarioNo):
        """Make directory for saving data"""
        self.ScenarioNo = ScenarioNo
        
        self.path_color = f"{self.PWD}/RGB"
        self.path_bt = f"{self.PWD}/BT"

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
        #i = 0

        t0 = time.time()
        self.resetstate()
        
        joint = np.zeros((33,3))
        #joint[:,0] = mp_pose_lm_name
        #while (self.btn.endtime.text() == "F"):
        while self.isRun:
            #try:
            success, image = self.cap.read()
            if success:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                results = self.mp_pose.process(image)

                mp_drawing.draw_landmarks(
                    image,
                    results.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS,
                    landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())

                self.imgviwerRGB.setImg(cv2.flip(image, 1))

                if results.pose_landmarks:
                    for i, lm in enumerate(results.pose_landmarks.landmark):
                        joint[i][0] = lm.x 
                        joint[i][1] = lm.y
            #except:
            #    pass
            #else:
                self.stackColor.append(image)
                self.stackJoint.append(joint) # joints are stored here
                self.pic_Count += 1
                
                nframes += 1
                t1 = time.time()
                t_elapsed += t1-t0

                self.btn.capturetime.setText(str(round(t_elapsed,2)))

                t0 = t1
        self.isRun = False

    # todo data tree  
    def save_multiproc(self):
        self.stackColor = np.array(self.stackColor)
        # 모든 스켈레톤이 다있는 프레임 
        
        # In case no skeleton was captured
        try:
            self.skarr = ku.kinect2mobile_direct_lists(self.stackJoint)
            #print("SKARR LIST", self.skarr)

            # prepare image 
            img = np.array(self.stackColor[-1]).astype(np.uint8)
            img = cv2.resize(img, (320, 240))
            height, width, channel = img.shape
            bytesPerLine = 3 * width
            pixmap   = QPixmap(QImage(img, width, height, bytesPerLine, QImage.Format_RGB888))
            return pixmap
        except:
            self.qScenario.viewInfo.setText(f"Failed to detect any skeleton, Try again")
            font = QFont()
            #font.setBold(True)
            font.setPointSize(14)
            self.qScenario.viewInfo.setFont(font)
            return -1
    

    def select_sk(self, skindex=0):
        """No selection needed anymore. MP finds only one skeleton"""
        #pickle.dump(self.stackJoint, open(f"{self.path_bt}/bodytracking_data.pickle", "wb"))
        
        if VERBOSE: print(f'[Qthread obj] skeleton index : {skindex}')
        
        # Safety check
        if not hasattr(self, 'skarr'):
            print("[QThreadObj.select_sk] No skeleton list")
            return 
        if not is_valid_skeleton(self.skarr):
            print("[QThreadObj.select_sk] Invalid skeleton")
            return 
        
       # print("~~~~~~!!!!!!!!~~~~~~~")
       # print(self.skarr)
        #scene = ku.kinect2mobile_direct(self.stackJoint)
        
        # FIX   20210107
        this_scenario = self.btn.action_num.currentText()
        this_score = self.btn.score_num.currentText()
        
        sub = ru.smoothed_frame_N(self.skarr, 
                                nframe=NFRAMES[f'{this_scenario}'],
                                shift=1)
        skeleton = ru.ravel_rec(sub)[np.newaxis, :]

        camera_num = 'e'

        tm = time.localtime()
        time_mark = f"{tm.tm_mon:02d}{tm.tm_mday:02d}{tm.tm_hour:02d}{tm.tm_min:02d}{tm.tm_sec:02d}"
        sav_dir = f"BT/"
        if not os.path.isdir(sav_dir): os.mkdir(sav_dir)
        pickle.dump(self.skarr, open(sav_dir+"f{camera_num}_{time_mark}_{this_scenario}_{this_score}_skeleton.pickle", "wb"))
        
        

        self.q1.put({"action":this_scenario,
                     "cam":camera_num, 
                     "skeleton": skeleton})
        print("[QtThreadObj] Skeleton sent to encryptor")
        self.e_sk.set()
        print("[QtThreadObj] Waiting for Evaluator's response...")

        #############
        # Encryptor runs...
        # Then send ctxt to server
        # and Wait for server's answer
        self.e_ans.wait()
        self.e_sk.clear() # Just in case...
        
        answer = self.q_answer.get()
        answer_int = int(answer.split(":")[-1])

        # Update this score
        scu = Score_updator(FN_SCORES)
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
        """Skeleton viewer"""
        left_arms = ['l_shoulder', 'l_elbow', 'l_hand']
        right_arms = ['head', 'r_shoulder',  'r_elbow', 'r_hand']
        body = ['head','l_shoulder', 'r_shoulder', 'r_hip', 'l_hip', 'l_shoulder']
        leg = ['r_foot', 'r_knee', 'r_hip', 'l_hip', 'l_knee', 'l_foot']
        bodyparts = [left_arms, right_arms, body, leg]

        #print(json_to_arr_list.shape)

        fig, ax = plt.subplots(figsize=(16,9))
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
        plt.close()

    def load_image(self, idx):
        fn_img = f'image/img_00{idx}.jpg'
        img = cv2.imread(fn_img)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        #img = imgutil.rgb2gray(img)
        img = cv2.resize(img, (320, 240))
        img = np.array(img).astype(np.uint8)
        height, width, channel = img.shape
        bytesPerLine = 3 * width
        pixmap   = QPixmap(QImage(img, width, height, bytesPerLine, QImage.Format_RGB888))
        return pixmap

