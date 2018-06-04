import cv2
import numpy as np
from PIL import Image
import os

# Path for face image database
path = 'dataset'

front_recognizer = cv2.face.LBPHFaceRecognizer_create()
profile_recognizer = cv2.face.LBPHFaceRecognizer_create()
front_face_detector = cv2.CascadeClassifier('Cascades/lbpcascade_frontalface_improved.xml')
profile_face_detector = cv2.CascadeClassifier('Cascades/haarcascade_profileface.xml')

# function to get the images and label data
def getImagesAndLabels(path):
    imagePaths = [os.path.join(path,f) for f in os.listdir(path)]
    front_faceSamples = []
    profile_faceSamples = []
    front_ids = []
    profile_ids = []
    for imagePath in imagePaths:
        PIL_img = Image.open(imagePath).convert('L') # convert it to grayscale
        img_numpy = np.array(PIL_img,'uint8')

        id = int(os.path.split(imagePath)[-1].split(".")[1])

        frontfaces = front_face_detector.detectMultiScale(img_numpy)
        profilefaces = profile_face_detector.detectMultiScale(img_numpy)

        for (x,y,w,h) in frontfaces:
            front_faceSamples.append(img_numpy[y:y+h,x:x+w])
            front_ids.append(id)

        for (x,y,w,h) in profilefaces:
            profile_faceSamples.append(img_numpy[y:y+h,x:x+w])
            profile_ids.append(id)

    return front_faceSamples, front_ids, profile_faceSamples, profile_ids

print ("\n [INFO] Loading images and labels. It will take a few seconds. Wait ...")
ffaces, fids, pfaces, pids = getImagesAndLabels(path)

print ("[STEP 1] Training front faces. It will take a few seconds. Wait ...")
front_recognizer.train(ffaces, np.array(fids))

print ("[STEP 2] Training profile faces. It will take a few seconds. Wait ...")
profile_recognizer.train(pfaces, np.array(pids))

# Save the model into trainer/trainer.yml
print ("[INFO] Finished training. Output the model")
front_recognizer.write('trainer/fronttrainer.yml') # recognizer.save() worked on Mac, but not on Pi
profile_recognizer.write('trainer/profiletrainer.yml') # recognizer.save() worked on Mac, but not on Pi

# Print the numer of faces trained and end program
ids = np.unique(fids.append(pids))
print("[INFO] {0} faces trained. Exiting Program".format(len(np.unique(ids))))
