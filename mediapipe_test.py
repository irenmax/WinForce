import cv2
import beepy
import mediapipe as mp
from ahk import AHK
from ahk.window import Window
import time
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
ahk = AHK()

#ahk.run_script('Run Notepad')
#win = ahk.active_window
def winMin():
  win = ahk.active_window
  win.minimize()

def winMax():
  win = ahk.active_window
  win.maximize()

def winRight():
  #win = ahk.active_window
  #win.move(x=1920, y=0, width=1920, height=2160)
  ahk.send_input('{LWin Down}{Right}{LWin Up}')
  time.sleep(0.1)
  ahk.key_press('Escape')

def winLeft():
  #win = ahk.active_window
  #win.move(x=0, y=0, width=1920, height=2160)
  ahk.send_input('{LWin Down}{Left}{LWin Up}')
  time.sleep(0.1)
  ahk.key_press('Escape')


# For webcam input:
hands = mp_hands.Hands(
    min_detection_confidence=0.7, min_tracking_confidence=0.7)
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
  # result contains landmarks of hands and classification if hand is left or right
  image.flags.writeable = False
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
        if cnt > 3:
          beepy.beep(sound=1)
      else:
        if cnt > 1: # threshold could be further increased to prevent mismatches
          win = ahk.active_window
          print(win.title)

          # only trigger left or right snap if focused window is not the camera preview
          # snaping the camera preview causes crash
          if(win.title != b'Hand Preview'):
            if mcp_middle_finger.x >= 0.6:
              print('###########RIGHT###########')
              winRight()
            elif mcp_middle_finger.x <= 0.4:
              print('###########LEFT###########')
              winLeft()
          cnt = 0

      print(cnt)
  # Draw the hand annotations on the image.
  image.flags.writeable = True
  image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
  if results.multi_hand_landmarks:
    for hand_landmarks in results.multi_hand_landmarks:
      mp_drawing.draw_landmarks(
          image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
  cv2.imshow('Hand Preview', image)
  if cv2.waitKey(5) & 0xFF == 27:
    break
hands.close()
cap.release()
