import cv2
import mediapipe as mp
from ahk import AHK
from ahk.window import Window
import time
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
ahk = AHK()
from mediapipe.framework.formats import landmark_pb2

ahk.run_script('Run Notepad')
win = ahk.active_window
def winMin():
  win.minimize()

def winMax():
  win.maximize()

def winRight():
  win.move(x=1920, y=0, width=1920, height=2160)

def winLeft():
  win.move(x=0, y=0, width=1920, height=2160)

# For webcam input:
hands = mp_hands.Hands(
    min_detection_confidence=0.5, min_tracking_confidence=0.5)
cap = cv2.VideoCapture(0)
framecounter = 0
cnt = 0
while cap.isOpened():
  success, image = cap.read()
  if not success:
    print("Ignoring empty camera frame.")
    continue
  framecounter += 1
  # Flip the image horizontally for a later selfie-view display, and convert
  # the BGR image to RGB.
  image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
  # To improve performance, optionally mark the image as not writeable to
  # pass by reference.
  image.flags.writeable = False
  # result contains landmarks of hands and classification if hand is left or right
  results = hands.process(image)

  # GESTURE RECOGNITION
  if results.multi_hand_landmarks:
    landmarklist = results.multi_hand_landmarks[0]
    # we look at hand position every fourth frame for efficiency
    if framecounter % 4 == 0:
      #wrist = landmarklist.landmark[0]
      mcp_middle_finger = landmarklist.landmark[9]

      # hand is approx. in the middle of the image
      if mcp_middle_finger.x > 0.4 and mcp_middle_finger.x < 0.6:
        cnt += 1
        # if hand was in the middle for a certain time, determine if it was moved to left or right
      else:
        if cnt > 1: # threshold could be further increased to prevent mismatches
          # TODO: give feedback to user that hand was detected in the middle
          if mcp_middle_finger.x >= 0.6:
            print('###########RIGHT###########')
            winRight()
            # TODO: call ahk action
          elif mcp_middle_finger.x <= 0.4:
            print('###########LEFT###########')
            winLeft()
            # TODO: call ahk action
          cnt = 0


      print(cnt)

  # Draw the hand annotations on the image.
  image.flags.writeable = True
  image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
  if results.multi_hand_landmarks:
    for hand_landmarks in results.multi_hand_landmarks:
      mp_drawing.draw_landmarks(
          image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
  cv2.imshow('MediaPipe Hands', image)
  if cv2.waitKey(5) & 0xFF == 27:
    break
hands.close()
cap.release()
