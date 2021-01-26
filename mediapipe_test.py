import cv2
import mediapipe as mp
import time
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
from mediapipe.framework.formats import landmark_pb2

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
  # TODO: Algorithm for gesture recognition
  if results.multi_hand_landmarks:
    landmarklist = results.multi_hand_landmarks[0]
    if framecounter % 4 == 0:
      #wrist = landmarklist.landmark[0]
      mcp_middle_finger = landmarklist.landmark[9]

      if mcp_middle_finger.x > 0.4 and mcp_middle_finger.x < 0.6:
        cnt += 1
      else:
        if cnt > 1:
          if mcp_middle_finger.x >= 0.6:
            print('###########RIGHT###########')
          elif mcp_middle_finger.x <= 0.4:
            print('###########LEFT###########')
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
