import sys

import numpy as np
from pyKinectAzure import pyKinectAzure, _k4a
from kinectBodyTracker import kinectBodyTracker, _k4abt
import cv2

modulePath = 'C:\\Program Files\\Azure Kinect SDK v1.4.1\\sdk\\windows-desktop\\amd64\\release\\bin\\k4a.dll' 
bodyTrackingModulePath = 'C:\\Program Files\\Azure Kinect Body Tracking SDK\\sdk\\windows-desktop\\amd64\\release\\bin\\k4abt.dll'
'''
class qSkeleton():

	def bodytracking(img):
		depth_image_handle = img

		pyK4A.bodyTracker_update()

		depth_image = pyK4A.image_convert_to_numpy(depth_image_handle)
		depth_color_image = cv2.convertScaleAbs (depth_image, alpha=0.05)  #alpha is fitted by visual comparison with Azure k4aviewer results 
		depth_color_image = cv2.cvtColor(depth_color_image, cv2.COLOR_GRAY2RGB) 


		body_image_color = pyK4A.bodyTracker_get_body_segmentation()

		combined_image = cv2.addWeighted(depth_color_image, 0.8, body_image_color, 0.2, 0)

		for body in pyK4A.body_tracker.bodiesNow:
			skeleton2D = pyK4A.bodyTracker_project_skeleton(body.skeleton)
			print(skeleton2D)
			combined_image = pyK4A.body_tracker.draw2DSkeleton(skeleton2D, body.id, combined_image)

		return combined_image
'''