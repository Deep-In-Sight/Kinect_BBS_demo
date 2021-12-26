import cv2, re
import pyrealsense2 as rs
import datetime as dt
import mediapipe as mp
import numpy as np
import time
from collections import deque
import copy
import itertools
from model import KeyPointClassifier


keypoint_classifier = KeyPointClassifier()


def calc_landmark_list(image, landmarks):
    image_width, image_height = image.shape[1], image.shape[0]

    landmark_point = []

    # Keypoint
    for _, landmark in enumerate(landmarks.landmark):
        landmark_x = min(int(landmark.x * image_width), image_width - 1)
        landmark_y = min(int(landmark.y * image_height), image_height - 1)
        # landmark_z = landmark.z

        landmark_point.append([landmark_x, landmark_y])

    return landmark_point


def pre_process_landmark(landmark_list):
    temp_landmark_list = copy.deepcopy(landmark_list)

    # Convert to relative coordinates
    base_x, base_y = 0, 0
    for index, landmark_point in enumerate(temp_landmark_list):
        if index == 0:
            base_x, base_y = landmark_point[0], landmark_point[1]

        temp_landmark_list[index][0] = temp_landmark_list[index][0] - base_x
        temp_landmark_list[index][1] = temp_landmark_list[index][1] - base_y

    # Convert to a one-dimensional list
    temp_landmark_list = list(
        itertools.chain.from_iterable(temp_landmark_list))

    # Normalization
    max_value = max(list(map(abs, temp_landmark_list)))

    def normalize_(n):
        return n / max_value

    temp_landmark_list = list(map(normalize_, temp_landmark_list))

    return temp_landmark_list



def draw_point_history(image, point_history):
    for index, point in enumerate(point_history):
        if point[0] != 0 and point[1] != 0:
            cv2.circle(image, (int(point[0]*0.50), int(point[1]*0.66)), 1 + int(index / 2),
                      (152, 251, 152), 2)

    return image


class mmp:
    # 리얼 센스 실행 함수
    def run(self, q1, q2, q3, lock):

        # facemesh and hand
        facmesh = mp.solutions.face_mesh
        face = facmesh.FaceMesh(static_image_mode=True, min_tracking_confidence=0.6, min_detection_confidence=0.6)
        mp_hands = mp.solutions.hands
        hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)

        # draw
        draw = mp.solutions.drawing_utils

        # Coordinate history #################################################################
        history_length = 16
        point_history = deque(maxlen=history_length)
        # 해상도
        resolution_width = 1280  # pixels 640
        resolution_height = 720  # pixels  480
        frame_rate = 15  # fps


        # Camera 3 가운데 카메라
        pipeline_3 = rs.pipeline()
        config_3 = rs.config()
        config_3.enable_device('116622071019')
        config_3.enable_stream(rs.stream.depth, resolution_width, resolution_height, rs.format.z16, frame_rate)
        config_3.enable_stream(rs.stream.color, resolution_width, resolution_height, rs.format.bgr8, frame_rate)
        config_3.enable_stream(rs.stream.infrared, resolution_width, resolution_height, rs.format.y8, frame_rate)


        # Start streaming from both cameras
        pipeline_3.start(config_3)
        print("실행")
        while True :
            try:
                # 프로세스의 작업이 끝날때 까지 잠금을 걸어주는 함수
                lock.acquire()

                # Camera 3
                # Wait for a coherent pair of frames: depth and color
                frames_3 = pipeline_3.wait_for_frames()
                depth_frame_3 = frames_3.get_depth_frame()
                color_frame_3 = frames_3.get_color_frame()
                infrared_frame_3 = frames_3.get_infrared_frame()

                # Camera 3의 프레임이 들어 왔는지 확인
                if not depth_frame_3 or not color_frame_3 or not infrared_frame_3:
                    continue
                # Convert images to numpy arrays
                depth_image_3 = np.asanyarray(depth_frame_3.get_data())
                color_image_3 = np.asanyarray(color_frame_3.get_data())
                color_image_3 = cv2.cvtColor(cv2.flip(color_image_3, 1), cv2.COLOR_BGR2RGB)

                color_image_3_copy = color_image_3.copy()  # 720*1280
                color_image_3_copy_resize = cv2.resize(color_image_3_copy, dsize=(640, 480))
                color_image_3_copy_resize = cv2.cvtColor(color_image_3_copy_resize, cv2.COLOR_RGB2BGR)
                facetype_image = color_image_3_copy_resize.copy()
                infrared_image_3 = np.asanyarray(infrared_frame_3.get_data())

                # Apply colormap on depth image (image must be converted to 8-bit per pixel first)
                # depth_colormap_3 = cv2.applyColorMap(cv2.convertScaleAbs(depth_image_3, alpha=0.5),
                #                                      cv2.COLORMAP_JET)

                ######################### Hand ############################
                color_image_3.flags.writeable = False
                res = hands.process(color_image_3)

                # Draw the hand annotations on the image.
                color_image_3.flags.writeable = True
                image = cv2.cvtColor(color_image_3, cv2.COLOR_RGB2BGR)

                Left_Click = False
                Right_Click = False

                # cv2.rectangle(image, (frameR, frameR), (wCam - frameR, hCam - frameR),
                #               (255, 0, 255), 2)
                if res.multi_hand_landmarks:
                    for hand_landmarks in res.multi_hand_landmarks:
                        landmark_list = calc_landmark_list(image, hand_landmarks)
                        # Conversion to relative coordinates / normalized coordinates
                        pre_processed_landmark_list = pre_process_landmark(
                            landmark_list)

                        # Hand sign classification
                        hand_sign_id = keypoint_classifier(pre_processed_landmark_list)
                        if hand_sign_id == 2:  # Point gesture
                            point_history.append(landmark_list[8])
                            point_history.append([0, 0])
                            # todo 핸드 제스처 정밀도늘 높일 필요가 있다.
                            if point_history[0][0]-10 > point_history[2][0] > point_history[4][0] > point_history[6][0] > point_history[8][0] + 15:
                                #print("Left")
                                Left_Click = True
                            elif point_history[0][0] + 15 < point_history[2][0] < point_history[4][0] < point_history[6][0] < point_history[8][0]-10:
                                #print("Right")
                                Right_Click = True
                            else:
                                Left_Click = False
                                Right_Click =False
                else:
                    point_history.append([0, 0])
                # todo 코드 정리 필요
                color_image_3_copy_resize = draw_point_history(color_image_3_copy_resize, point_history)
                Click_list = [Left_Click, Right_Click]


                # facemesh를 띠워줄 공간을 만들기 위해서 board 생성
                color_colormap_dim = color_image_3_copy.shape
                board = np.ones(color_colormap_dim, np.uint8) * 0

                h, w, c = color_image_3_copy_resize.shape
                # facemesh
                op = face.process(color_image_3_copy_resize)
                if op.multi_face_landmarks:
                    for i in op.multi_face_landmarks:
                        #draw.draw_landmarks(color_image_3_copy_resize, i, landmark_drawing_spec=draw.DrawingSpec(color=(0, 255, 0), circle_radius=1))  # facmesh.FACE_CONNECTIONS -> 얼굴 라인
                        draw.draw_landmarks(board, i, facmesh.FACEMESH_TESSELATION, landmark_drawing_spec=draw.DrawingSpec(color=(255, 255, 0), circle_radius=0))
                    cx_min = w
                    cy_min = h
                    cx_max = cy_max = 0
                    for id, lm in enumerate(i.landmark):
                        cx, cy = int(lm.x * w), int(lm.y * h)
                        if cx < cx_min:
                            cx_min = cx
                        if cy < cy_min:
                            cy_min = cy
                        if cx > cx_max:
                            cx_max = cx
                        if cy > cy_max:
                            cy_max = cy
                    #cv2.rectangle(color_image_3_copy_resize, (cx_min-90, cy_min-100), (cx_max+90, cy_max+90), (255, 255, 0), 2)
                    # IndexError 예외 처리 랜드마크가 있으면 실행
                    try:
                        facetype_image = facetype_image[cy_min-100:cy_max+90, cx_min-90:cx_max+90]
                    except:
                        pass

                # facetype_image 이미지 리사이즈
                #facetype_image = cv2.resize(facetype_image, dsize=(480, 360))

                # board를 리사이징해 Meshimage 확대
                img_res = board[160:560, 440:840]
                img_res_resize = cv2.resize(img_res, dsize=(480, 360))

                RGB_image = cv2.cvtColor(color_image_3_copy_resize, cv2.COLOR_BGR2RGB)
                RGB_image_resize = cv2.resize(RGB_image, dsize=(480, 360))
                Mesh_image = cv2.cvtColor(img_res_resize, cv2.COLOR_BGR2RGB)
                image_list = [color_image_3,  infrared_image_3, img_res, Click_list, facetype_image]

                q1.put(RGB_image_resize)
                q2.put(Mesh_image)
                q3.put(image_list)

                cv2.waitKey(1)
            finally:
                # 프로세스의 작업이 끝나고 잠금을 풀어주는 함수
                lock.release()

