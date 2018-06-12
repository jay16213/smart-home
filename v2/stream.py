# This is a demo of running face recognition on a Raspberry Pi.
# This program will print out the names of anyone it recognizes to the console.

# To run this, you need a Raspberry Pi 2 (or greater) with face_recognition and
# the picamera[array] module installed.
# You can follow this installation instructions to get your RPi set up:
# https://gist.github.com/ageitgey/1ac8dbe8572f3f533df6269dab35df65

import face_recognition
import numpy as np
import cv2
from encoding import loadEncoding

font = cv2.FONT_HERSHEY_DUPLEX

print("Initialize camera (use OpenCV)")
camera = cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
camera.set(cv2.CAP_PROP_FPS, 24)

# Load a sample picture and learn how to recognize it.
print("Loading known face encodings")
known_face_encodings, known_names = loadEncoding()

# Initialize some variables
face_locations = []
face_encodings = []

while True:
    rval, frame = camera.read()
    frame = cv2.flip(frame, -1) # Flip vertically
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

    # covert frame from BGR(opencv use) to RGB(face_recognition use)
    # rgb_small_frame = small_frame[:, :, ::-1]

    # Find all the faces and face encodings in the current frame of video
    face_locations = face_recognition.face_locations(small_frame)
    face_encodings = face_recognition.face_encodings(small_frame, face_locations)

    predice_name = []
    # Loop over each face found in the frame to see if it's someone we know.
    for face_encoding in face_encodings:
        # See if the face is a match for the known face(s)
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        for idx in range(len(matches)):
            if matches[idx]:
                predice_name.append(known_names[idx])
            else:
                predice_name.append("Unknown")

    # draw the result
    i = 0
    for (top, right, bottom, left) in face_locations:
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4
        if(predice_name[i] == "Unknown"):
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
        else:
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        cv2.putText(frame, predice_name[i], (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
        i += 1

    cv2.imshow('Video', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

camera.release()
cv2.destroyAllWindows()
