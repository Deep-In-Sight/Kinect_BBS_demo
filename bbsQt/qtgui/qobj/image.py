import numpy as np

def get_quotient_remainder(value):
    # while (value > 255):
    #     value -= 256
    #     quotient += 1
    quotient = value // 256
    return quotient, value - 256 * quotient


def _onechannel_to_rgb(img):
    if img.ndim == 3:
        img = img[:,:,0]
    h, w = img.shape
    rgb = np.zeros((h,w,3))

    for i in range(h):
        for j in range(w):
            q, r = get_quotient_remainder(img[i,j])
            rgb[i,j,2] = r # red channel for cv2
            rgb[i,j,1] = q # green channel for cv2
            rgb[i,j,0] = 0 # blue channel for cv2
    return rgb


def onechannel2rgb(img):
    if img.ndim == 3:
        img = img[:,:,0]
    h, w = img.shape
    rgb = np.zeros((h,w,3))
    rgb[:,:,1] = img // 256
    rgb[:,:,2] = img - 256 * rgb[:,:,1]
    return rgb


def rgb2gray(rgb):
    h, w, c = rgb.shape
    gray = np.zeros((h,w,3))
    gray[:,:,0] = rgb[:,:,1] * 256 + rgb[:,:,2]
    gray[:,:,1] = gray[:,:,0]
    gray[:,:,2] = gray[:,:,0]
    return gray


def gray_rescale(gray, minval, maxval):
    gray[:,:,0] = (gray[:,:,0] - minval)/(maxval-minval) * 255
    gray[:,:,0][gray[:,:,0] < 0] = 0
    gray[:,:,0][gray[:,:,0] > 255] = 255
    if gray.shape[2] == 3:
        gray[:,:,1] = gray[:,:,0]
        gray[:,:,2] = gray[:,:,0]
    return gray

def gray_rescale_2d(gray, minval, maxval):
    gray = (gray - minval) / (maxval-minval) * 255
    gray[gray < 0] = 0
    gray[gray > 255] = 255
    return gray


def gray_2_3D(gray, minval, maxval):
    h, w = gray.shape
    ans = np.zeros((h,w,3))
    ans[:,:,0] = (gray[:,:] - minval)/(maxval-minval) * 65535
    ans[:,:,0][ans[:,:,0] < 0] = 0
    ans[:,:,0][ans[:,:,0] > 65535] = 65535

    ans[:,:,1] = ans[:,:,0]
    ans[:,:,2] = ans[:,:,0]
    
    return ans



