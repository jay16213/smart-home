import cv2
import os
import math

cam = cv2.VideoCapture(0)
cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640) # set video width
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480) # set video height

front_face_detector = cv2.CascadeClassifier('Cascades/lbpcascade_frontalface_improved.xml')
profile_face_detector = cv2.CascadeClassifier('Cascades/haarcascade_profileface.xml')

# For each person, enter one numeric face id
face_id = input('\n enter user id end press <return> ==>  ')

print("\n [INFO] Initializing face capture. Look the camera and wait ...")

# Initialize individual sampling face count
num_front_samples = 0
num_profile_samples = 0

detected_frontfaces = []
detected_profilefaces = []

while(True):
    ret, img = cam.read()
    img = cv2.flip(img, -1) # flip video image vertically
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    if(num_front_samples < 100):
        front_faces =  front_face_detector.detectMultiScale(gray, 1.3, 5)
    else:
        profile_faces = None

    if(num_profile_samples < 30):
        profile_faces = profile_face_detector.detectMultiScale(gray, 1.3, 5)
    else:
        profile_faces = None

    for (x,y,w,h) in front_faces:
        # diameter = round(math.sqrt((w / 2)**2 + (h / 2)**2))
        # cv2.circle(img, (int(x + round(w/2)), int(y + round(h/2))), diameter, (255, 0, 0), 2)
        cv2.rectangle(img, (x,y), (x+w,y+h), (255,0,0), 2)
        detected_frontfaces.append(gray[y:y+h,x:x+w])
        num_front_samples += 1

    for (x,y,w,h) in profile_faces:
        cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0), 2)
        detected_profilefaces.append(gray[y:y+h,x:x+w])
        num_profile_samples += 1

    cv2.imshow('image', img)
    k = cv2.waitKey(1) & 0xff # Press 'ESC' for exiting video
    if k == 27:
        break
    elif num_front_samples >= 100 and num_profile_samples >= 30:
        break

# Do a bit of cleanup
print("\n [INFO] Collected 100 front faces and 30 profile faces. Cleanup stuff")
cam.release()
cv2.destroyAllWindows()

print("\n [INFO] Save face data and exiting Program")

count = 0
for face in detected_frontfaces:
    cv2.imwrite("dataset/User." + str(face_id) + '.' + str(count) + "f.jpg", face)
    count += 1

count = 0
for face in detected_profilefaces:
    cv2.imwrite("dataset/User." + str(face_id) + '.' + str(count) + "p.jpg", face)
    count += 1
