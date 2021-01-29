#!/usr/bin/env python
import PySimpleGUI as sg
import cv2
import numpy as np
import mediapipe as mp
import beepy
# from ahk import AHK
# from ahk.window import Window
import time
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
# ahk = AHK()


def calc_initial_coordinates(cap):
    _, image = cap.read()
    window_height, window_width, _ = image.shape
    screen_width, screen_height = sg.Window.get_screen_size()

    x_main = screen_width / 2 - window_width / 2
    # y_main = screen_height / 2 - window_height / 2
    y_main = 0

    x_mini = screen_width - 0
    y_mini = screen_width - 0

    return (x_main, y_main), (x_mini, y_mini)


def make_main_window(pos):
    main_layout = [
        [sg.Image(filename='', key='image')],
        [sg.Button('Minimize', size=(10, 1), font='Helvetica 14')]
    ]
    return sg.Window('Gesture control', main_layout, location=pos, finalize=True)


def make_mini_window(pos, start_value):
    emoji = sg.Text(start_value, font='Helvetica 40', enable_events=True)
    mini_layout = [[emoji]]
    return emoji, sg.Window('Gesture control', mini_layout, location=pos, alpha_channel=.7,
                     background_color=None, grab_anywhere=True, no_titlebar=True, keep_on_top=True,
                     finalize=True)


def main():
    # initialize camera
    cap = cv2.VideoCapture(0)

   # initialize hand tracking
    hands = mp_hands.Hands(
        min_detection_confidence=0.7, min_tracking_confidence=0.7)

    # calc initial window position
    pos_main, pos_mini = calc_initial_coordinates(cap)

    # create main window
    main_window = make_main_window(pos_main)

    # create mini window
    emoji_list = {
        'idle': '\U0001F440',
        'detecting': '\U0001F44B',
        'left': '\U00002B05',
        'right': '\U000027A1',
        'down': '\U00002B07',
        'up': '\U00002B06'
    }
    emoji, mini_window = make_mini_window(pos_mini, emoji_list['idle'])
    mini_window.Hide()

    # loop variables
    isMinimized = False
    framecounter = 0
    cnt = 0

    # event loop
    while True:

        # read windows
        _, event, values = sg.read_all_windows(timeout=20)

        # listen for events
        if event == sg.WIN_CLOSED:
            return
        elif event == 'Minimize':
            main_window.Hide()
            mini_window.UnHide()
        elif event in emoji_list.values():
            mini_window.Hide()
            main_window.UnHide()

        # read image
        _, image = cap.read()

        framecounter += 1

        # flip image and convert colors
        image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)

        # for performance
        image.flags.writeable = False

        # hand tracking
        results = hands.process(image)

        # GESTURE RECOGNITION

        is_detecting_hand = results.multi_hand_landmarks

        if is_detecting_hand:
            landmarklist = results.multi_hand_landmarks[0]
            # we look at hand position every fourth frame for efficiency
            if framecounter % 4 == 0:
                # wrist = landmarklist.landmark[0]
                mcp_middle_finger = landmarklist.landmark[9]

                # hand is approx. in the middle of the image
                # TODO: split up for x and y axis
                hand_is_in_center = mcp_middle_finger.x > 0.4 and mcp_middle_finger.x < 0.6 and mcp_middle_finger.y > 0.4 and mcp_middle_finger.y < 0.6

                if hand_is_in_center:
                    cnt += 1

                    # if hand was in the middle for a certain time, determine if it was moved to left or right
                    if cnt == 3:
                        beepy.beep(sound=1)
                        emoji.Update(value=emoji_list['detecting'])
                else:
                    if cnt >= 3:  # threshold could be further increased to prevent mismatches
                        # win = ahk.active_window
                        # print(win.title)

                        # only trigger left or right snap if focused window is not the camera preview
                        # snaping the camera preview causes crash

                        if mcp_middle_finger.x >= 0.6:
                            print('###########RIGHT###########')
                            emoji.Update(value=emoji_list['right'])
                           # winRight()
                        elif mcp_middle_finger.x <= 0.4:
                            print('###########LEFT###########')
                            emoji.Update(value=emoji_list['left'])
                            # winLeft()
                        elif mcp_middle_finger.y >= 0.6:
                            print('###########DOWN###########')
                            emoji.Update(value=emoji_list['down'])
                            # winDown()
                        elif mcp_middle_finger.y <= 0.4:
                            print('###########UP###########')
                            emoji.Update(value=emoji_list['up'])
                            # winUp()
                        cnt = 0

                print(cnt)
        else:
            # TODO: counter for hand not detected -> reset cnt if hand was not detected for x frames
            cnt = 0
            emoji.Update(value=emoji_list['idle'])

        # Draw the hand annotations on the image.
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        height = image.shape[0]
        width = image.shape[1]
        color = (255, 0, 0)
        thickness = 2

        left_x = int(width * 0.4)
        right_x = int(width * 0.6)
        upper_y = int(height * 0.4)
        lower_y = int(height * 0.6)

        # draw grid on image
        image = cv2.line(image, (left_x, 0),
                         (left_x, height), color, thickness)
        image = cv2.line(image, (right_x, 0),
                         (right_x, height), color, thickness)
        image = cv2.line(image, (0, upper_y),
                         (width, upper_y), color, thickness)
        image = cv2.line(image, (0, lower_y),
                         (width, lower_y), color, thickness)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        imgbytes = cv2.imencode('.png', image)[1].tobytes()  # ditto
        main_window['image'].update(data=imgbytes)

    hands.close()
    cap.release()


main()
