import cv2
import numpy as np
import os
import math

# Path for face image database
dataPath = 'dataset'

# front_face_detector = cv2.CascadeClassifier('Cascades/lbpcascade_frontalface_improved.xml')
front_recognizer = cv2.face.LBPHFaceRecognizer_create()

# function to get the images and label data
def getImagesAndLabels(dataPath):
    imageDirs = [os.path.join(dataPath, f) for f in os.listdir(dataPath)]
    total_samples = []

    for imageDir in imageDirs:
        imagePaths = [os.path.join(imageDir, f) for f in os.listdir(imageDir)]
        face_id = int(imageDir.split('/')[1])

        for imagePath in imagePaths:
            img = cv2.imread(imagePath)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            total_samples.append((gray, face_id))

    print(' [INFO] load total {} images'.format(len(total_samples)))
    return total_samples

def getTrainingSamples(samples):
    n_trainings = math.floor(len(samples) * 0.8)
    np.random.shuffle(samples)
    training_samples = []
    ids = []
    for i in range(n_trainings):
        training_samples.append(samples[i][0])
        ids.append(samples[i][1])

    return training_samples, ids

def test(samples):
    total_confidence = 0
    right = 0
    total = len(samples)
    arr_c = []
    for sample, _id in samples:
        id, confidence = front_recognizer.predict(sample)
        total_confidence += confidence
        arr_c.append(confidence)
        right += (id == _id)

    mean = np.mean(arr_c)
    std = np.std(arr_c, ddof=1)
    thresh = mean + 3 * std
    print("train: {}, {}, {}".format(float(right) / total, mean, std))
    print("{}".format(thresh))

print ("\n [INFO] Loading images and labels. It will take a few seconds. Wait ...")
total_samples = getImagesAndLabels(dataPath)
training_samples, fids = getTrainingSamples(total_samples)

print (" [INFO] Training front faces using {} images".format(len(training_samples)))
front_recognizer.train(training_samples, np.array(fids))

# Save the model into trainer/trainer.yml
print (" [INFO] Finished training. Output the model")
front_recognizer.write('trainer/trainer100.yml') # recognizer.save() worked on Mac, but not on Pi

# Print the numer of faces trained and end program
print(" [INFO] {0} faces trained. Test model".format(len(np.unique(fids))))
test(total_samples)
