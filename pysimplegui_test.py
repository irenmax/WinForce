#!/usr/bin/env python
import PySimpleGUI as sg
import cv2
import numpy as np
import mediapipe as mp
from ahk import AHK
from ahk.window import Window
import time
import winsound
from threading import Thread
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
ahk = AHK()

soundpath="C:/Windows/Media/"
threshold_middleduration = 3
middle_left = 0.4
middle_right = 0.6
middle_up = 0.4
middle_bottom = 0.6

def play_sound(sound):
  soundfile = soundpath;
  if sound == 1:
    soundfile = soundfile + 'chimes.wav'
  elif sound == 2:
    soundfile = soundfile + 'ding.wav'
  elif sound == 3:
    soundfile = soundfile + 'chord.wav'
  else: 
    soundfile = soundfile + 'tada.wav'

  #winsound.PlaySound(soundfile, winsound.SND_FILENAME|winsound.SND_ASYNC)
  winsound.PlaySound(soundfile, winsound.SND_ALIAS|winsound.SND_ASYNC)

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
                       layout, location=(800, 400), keep_on_top=True)

    # ---===--- Event LOOP Read and display frames, operate the GUI --- #
    cap = cv2.VideoCapture(0)
    recording = False
    framecounter = 0
    cnt_x = 0
    cnt_y = 0
    cnt_none = 0

    while True:
        event, values = window.read(timeout=20)
        if event == 'Exit' or event == sg.WIN_CLOSED:
          hands.close()
          cap.release()
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
            # we look at hand position every fourth frame for efficiency
            if framecounter % 2 == 0:
              if results.multi_hand_landmarks:
                cnt_none = 0
                landmarklist = results.multi_hand_landmarks[0]
                
                #wrist = landmarklist.landmark[0]
                mcp_middle_finger = landmarklist.landmark[9]

                # hand is approx. in the middle of the image
                # check left or right 
                if mcp_middle_finger.x > middle_left and mcp_middle_finger.x < middle_right:
                  cnt_x += 1

                  if cnt_x == threshold_middleduration:
                    #winsound.PlaySound("nudge", winsound.SND_ALIAS|winsound.SND_ASYNC)
                    play_sound(1)
                                  
                elif cnt_x > threshold_middleduration:
                  if mcp_middle_finger.x >= middle_right:
                    print('###########RIGHT###########')
                    winRight()
                  if mcp_middle_finger.x <= middle_left:
                    print('###########LEFT###########')
                    winLeft()
                  cnt_x = 0

                if mcp_middle_finger.y > middle_up and mcp_middle_finger.y < middle_bottom:
                  cnt_y += 1
                  
                  if cnt_y == threshold_middleduration:
                    play_sound(2)

                elif cnt_y > threshold_middleduration:
                  if mcp_middle_finger.y <= middle_up:
                    print('###########UP###########')
                    winUp()
                  if mcp_middle_finger.y >= middle_bottom:
                    print('###########DOWN###########')
                    winDown()
                  cnt_y = 0

                  
              else:
                cnt_none += 1
                if cnt_none > 2:
                  if cnt_x > 0 or cnt_y > 0:
                    play_sound(3)
                  cnt_x = 0
                  cnt_y = 0

              print(cnt_x, cnt_y, cnt_none)

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




            imgbytes = cv2.imencode('.png', image)[1].tobytes()
            window['image'].update(data=imgbytes)


    hands.close()
    cap.release()

main()
