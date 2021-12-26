import cv2


fps = 15
import cv2
for j in range(1, 11) :
    frame_array = []
    for i in range(45, 0, -1) :
        img = cv2.imread(f"CD/{i}.png")
        img = cv2.resize(img, dsize=(1920, 1080), interpolation=cv2.INTER_LINEAR)
        height, width, layers = img.shape
        size = (width, height)
        frame_array.append(img)
    for i in range(0,1800) : 
        img = cv2.imread(f"S{j}/{i}.png")
        img = cv2.resize(img, dsize=(1920, 1080), interpolation=cv2.INTER_LINEAR)
        height, width, layers = img.shape
        size = (width, height)
        frame_array.append(img)
    for i in range(0,30) : 
        img = cv2.imread(f"END/1.png")
        img = cv2.resize(img, dsize=(1920, 1080), interpolation=cv2.INTER_LINEAR)
        height, width, layers = img.shape
        size = (width, height)
        frame_array.append(img)
    out = cv2.VideoWriter(f"S{j}.mp4",cv2.VideoWriter_fourcc(*'DIVX'), fps, size)
    for i in range(len(frame_array)):
        # writing to a image array
        out.write(frame_array[i])
    out.release()