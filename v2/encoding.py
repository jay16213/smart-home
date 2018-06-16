import face_recognition
import pickle
import numpy as np
import os

def saveEncoding():
    all_face_encodings = {}

    print("Loading images and get encodings")
    img1 = face_recognition.load_image_file("jay.jpg")
    all_face_encodings["jay"] = face_recognition.face_encodings(img1, num_jitters=100)[0]
    img2 = face_recognition.load_image_file("jay1.jpg")
    all_face_encodings["jay1"] = face_recognition.face_encodings(img2, num_jitters=100)[0]
    img3 = face_recognition.load_image_file("jay2.jpg")
    all_face_encodings["jay2"] = face_recognition.face_encodings(img3, num_jitters=100)[0]

    print("Saving encodings")
    with open('dataset_faces.dat', 'wb') as f:
        pickle.dump(all_face_encodings, f)

    return

def loadEncoding(path):
    # Load face encodings
    with open(os.path.join(path, 'dataset_faces.dat'), 'rb') as f:
        all_face_encodings = pickle.load(f)

    # Grab the list of names and the list of encodings
    face_names = list(all_face_encodings.keys())
    face_encodings = np.array(list(all_face_encodings.values()))

    return face_encodings, face_names

if __name__ == '__main__':
    saveEncoding()
