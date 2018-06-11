import cv2
import os
import math

cam = cv2.VideoCapture(0)
cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640) # set video width
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480) # set video height

face_detector = cv2.CascadeClassifier('Cascades/haarcascade_frontalface_default.xml')

# For each person, enter one numeric face id
face_id = input('\n enter user id end press <return> ==>  ')

print("\n [INFO] Initializing face capture. Look the camera and wait ...")

# Initialize individual sampling face count
num_front_samples = 0
num_profile_samples = 0
MAX_FRONT_SAMPLES = 100

detected_frontfaces = []
detected_profilefaces = []
font = cv2.FONT_HERSHEY_SIMPLEX

while(True):
    ret, img = cam.read()
    img = cv2.flip(img, -1) # flip video image vertically
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    front_faces = face_detector.detectMultiScale(gray, 1.3, 5)

    for (x,y,w,h) in front_faces:
        cv2.rectangle(img, (x,y), (x+w,y+h), (255,0,0), 2)
        detected_frontfaces.append(gray[y:y+h,x:x+w])
        num_front_samples += 1

    cv2.putText(img, str(num_front_samples), (0, 0), font, 1, (255,255,255), 2)
    cv2.imshow('image', img)
    
    k = cv2.waitKey(1) & 0xff # Press 'ESC' for exiting video
    if k == 27:
        break
    elif num_front_samples >= MAX_FRONT_SAMPLES:
        break

# Do a bit of cleanup
print("\n [INFO] Collected {} front faces. Cleanup stuff".format(MAX_FRONT_SAMPLES))
cam.release()
cv2.destroyAllWindows()

print("\n [INFO] Save face data and exiting Program")

savePath = 'dataset/{}'.format(face_id)
if not os.path.exists(savePath):
    os.makedirs(savePath)
os.chdir(savePath)

count = 0
for face in detected_frontfaces:
    cv2.imwrite('{}.jpg'.format(count), face)
    count += 1
