#!/usr/bin/env python
import PySimpleGUI as sg
import cv2
import numpy as np
import mediapipe as mp
import beepy
from ahk import AHK
from ahk.window import Window
import time
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
ahk = AHK()

def winRight():
  #win = ahk.active_window
  #win.move(x=1920, y=0, width=1920, height=2160)
  ahk.send_input('{LWin Down}{Right}{LWin Up}')
  time.sleep(0.2)
  ahk.key_press('Escape')

def winLeft():
  #win = ahk.active_window
  #win.move(x=0, y=0, width=1920, height=2160)
  ahk.send_input('{LWin Down}{Left}{LWin Up}')
  time.sleep(0.2)
  ahk.key_press('Escape')

def winUp():
  ahk.send_input('{LWin Down}{Up}{LWin Up}')
  time.sleep(0.2)
  ahk.key_press('Escape')

def winDown():
  ahk.send_input('{LWin Down}{Down}{LWin Up}')
  time.sleep(0.2)
  ahk.key_press('Escape')


def main():
    hands = mp_hands.Hands(
        min_detection_confidence=0.7, min_tracking_confidence=0.7)
    sg.theme('Black')

    # define the window layout
    layout = [[sg.Text('BII Gesture Tracking', size=(40, 1), justification='center', font='Helvetica 20')],
              [sg.Image(filename='', key='image')],
              [sg.Button('Record', size=(10, 1), font='Helvetica 14'),
               sg.Button('Stop', size=(10, 1), font='Any 14'),
               sg.Button('Exit', size=(10, 1), font='Helvetica 14'), ]]

    # create the window and show it without the plot
    window = sg.Window('Demo Application - OpenCV Integration',
                       layout, location=(800, 400), keep_on_top=True, re)

    # ---===--- Event LOOP Read and display frames, operate the GUI --- #
    cap = cv2.VideoCapture(0)
    recording = False
    framecounter = 0
    cnt = 0
    while True:
        event, values = window.read(timeout=20)
        if event == 'Exit' or event == sg.WIN_CLOSED:
            return

        elif event == 'Record':
            recording = True

        elif event == 'Stop':
            recording = False
            img = np.full((480, 640), 255)
            # this is faster, shorter and needs less includes
            imgbytes = cv2.imencode('.png', img)[1].tobytes()
            window['image'].update(data=imgbytes)

        if recording:
            ret, image = cap.read()

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
                if mcp_middle_finger.x > 0.4 and mcp_middle_finger.x < 0.6 and mcp_middle_finger.y > 0.4 and mcp_middle_finger.y < 0.6:
                  cnt += 1
                  # if hand was in the middle for a certain time, determine if it was moved to left or right
                  #if cnt > 3:
                    #beepy.beep(sound=1)
                else:
                  if cnt > 3: # threshold could be further increased to prevent mismatches
                    #win = ahk.active_window
                    #print(win.title)

                    # only trigger left or right snap if focused window is not the camera preview
                    # snaping the camera preview causes crash

                    if mcp_middle_finger.x >= 0.6:
                      print('###########RIGHT###########')
                      winRight()
                    elif mcp_middle_finger.x <= 0.4:
                      print('###########LEFT###########')
                      winLeft()
                    elif mcp_middle_finger.y >= 0.6:
                      print('###########DOWN###########')
                      winDown()
                    elif mcp_middle_finger.y <= 0.4:
                      print('###########UP###########')
                      winUp()
                    cnt = 0

                print(cnt)
            else:
                #TODO: counter for hand not detected -> reset cnt if hand was not detected for x frames
              cnt = 0
            # Draw the hand annotations on the image.
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            height = image.shape[0]
            width = image.shape[1]
            color = (255, 0, 0)
            thickness = 2

            left_x = int(width * 0.4)
            right_x = int(width *0.6)
            upper_y = int(height * 0.4)
            lower_y = int(height * 0.6)

            # draw grid on image
            image = cv2.line(image, (left_x, 0), (left_x, height), color, thickness)
            image = cv2.line(image, (right_x, 0), (right_x, height), color, thickness)
            image = cv2.line(image, (0, upper_y), (width, upper_y), color, thickness)
            image = cv2.line(image, (0, lower_y), (width, lower_y), color, thickness)



            if results.multi_hand_landmarks:
              for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    image, hand_landmarks, mp_hands.HAND_CONNECTIONS)




            imgbytes = cv2.imencode('.png', image)[1].tobytes()  # ditto
            window['image'].update(data=imgbytes)



    hands.close()
    cap.release()

main()
