#!/usr/bin/env python
import platform
import time
from threading import Thread
import numpy as np
import cv2
import mediapipe as mp
import PySimpleGUI as sg
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

is_windows = platform.system() == 'Windows'
if is_windows:
    import winsound
    from ahk import AHK
    from ahk.window import Window
    ahk = AHK()

    soundpath = "C:/Windows/Media/"
    soundfiles = ['chimes.wav', 'ding.wav', 'chord.wav', 'tada.wav']

threshold_middleduration = 3
middle_left = 0.3
middle_right = 0.7
middle_up = 0.3
middle_bottom = 0.7

emoji_list = {
    'idle': '\U0001F440',
    'detecting': '\U0001F44B',
    'left': '\U00002B05',
    'right': '\U000027A1',
    'down': '\U00002B07',
    'up': '\U00002B06',
    'cancel': '\U0000274C'
}


def play_sound(sound):
    #winsound.PlaySound(soundfile, winsound.SND_FILENAME|winsound.SND_ASYNC)
    winsound.PlaySound(
        soundpath + soundfiles[sound], winsound.SND_ALIAS | winsound.SND_ASYNC)


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


def calc_initial_coordinates(cap):
    _, image = cap.read()
    window_height, window_width, _ = image.shape
    screen_width, screen_height = sg.Window.get_screen_size()

    x_main = screen_width / 2 - window_width / 2
    # y_main = screen_height / 2 - window_height / 2
    y_main = 0

    x_mini = screen_width - 95
    y_mini = screen_height - 110

    return (x_main, y_main), (x_mini, y_mini)


def make_main_window(pos, start_value):
    emoji = sg.Text(start_value, font='Helvetica 40', enable_events=True)
    main_layout = [
        [sg.Image(filename='', key='image')],
        [sg.Button('Minimize', size=(10, 1), font='Helvetica 14')]
    ]

    if is_windows:
        main_layout = [
            [sg.Image(filename='', key='image')],
            [sg.Button('Minimize', size=(10, 1), font='Helvetica 14'),
             emoji]
        ]

    return emoji, sg.Window('Gesture control', main_layout, location=pos, finalize=True)


def make_mini_window(pos, start_value):
    emoji = sg.Text(start_value, font='Helvetica 40', enable_events=True)
    mini_layout = [[emoji]]
    return emoji, sg.Window('Gesture control', mini_layout, location=pos, alpha_channel=.7,
                            background_color=None, grab_anywhere=False, no_titlebar=True,
                            keep_on_top=True, finalize=True)


def update_emojis(emojis, type):
    for emoji in emojis:
        emoji.Update(value=emoji_list[type])


def main():
    # initialize camera
    cap = cv2.VideoCapture(0)

    # initialize hand tracking
    hands = mp_hands.Hands(
        min_detection_confidence=0.7, min_tracking_confidence=0.7)

    # calc initial window position

    pos_main, pos_mini = calc_initial_coordinates(cap)

    # create main window
    main_emoji, main_window = make_main_window(pos_main, emoji_list['idle'])

    # create mini window
    emoji, mini_window = make_mini_window(pos_mini, emoji_list['idle'])
    mini_window.Hide()

    if is_windows:
        emojis = [main_emoji, emoji]
    else:
        emojis = [emoji]

    # loop variables
    isMinimized = False
    framecounter = 0
    cnt_x = 0
    cnt_y = 0
    cnt_none = 0

    while True:
        # read windows
        _, event, values = sg.read_all_windows(timeout=20)

        if event == sg.WIN_CLOSED:
            hands.close()
            cap.release()
            return

        elif event == 'Minimize':
            main_window.Hide()
            mini_window.UnHide()

        elif event in emoji_list.values():
            mini_window.Hide()
            main_window.UnHide()

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
            is_detecting_hand = results.multi_hand_landmarks

            if is_detecting_hand:

                landmarklist = results.multi_hand_landmarks[0]

                #wrist = landmarklist.landmark[0]
                mcp_middle_finger = landmarklist.landmark[9]
                tip_middle_finger = landmarklist.landmark[12]

                # fist should cancel
                if tip_middle_finger.y < mcp_middle_finger.y:
                    cnt_none = 0
                    # hand is approx. in the middle of the image
                    # check left or right
                    if mcp_middle_finger.x > middle_left and mcp_middle_finger.x < middle_right:
                        cnt_x += 1

                        if cnt_x == threshold_middleduration:
                            #winsound.PlaySound("nudge", winsound.SND_ALIAS|winsound.SND_ASYNC)
                            if is_windows:
                                play_sound(1)
                            update_emojis(emojis, 'detecting')

                    elif cnt_x > threshold_middleduration:
                        if mcp_middle_finger.x >= middle_right:
                            print('###########RIGHT###########')
                            # emoji.Update(value=emoji_list['right'])
                            # main_emoji.Update(value=emoji_list['right'])
                            update_emojis(emojis, 'right')

                            if is_windows:
                                winRight()
                        if mcp_middle_finger.x <= middle_left:
                            print('###########LEFT###########')
                            # emoji.Update(value=emoji_list['left'])
                            # main_emoji.Update(value=emoji_list['left'])
                            update_emojis(emojis, 'left')

                            if is_windows:
                                winLeft()
                        cnt_x = 0

                    if mcp_middle_finger.y > middle_up and mcp_middle_finger.y < middle_bottom:
                        cnt_y += 1

                        if cnt_y == threshold_middleduration:
                            if is_windows:
                                play_sound(2)
                            # emoji.Update(value=emoji_list['detecting'])
                            # main_emoji.Update(value=emoji_list['detecting'])
                            update_emojis(emojis, 'detecting')

                    elif cnt_y > threshold_middleduration:
                        if mcp_middle_finger.y <= middle_up:
                            print('###########UP###########')
                            # emoji.Update(value=emoji_list['up'])
                            # main_emoji.Update(value=emoji_list['up'])
                            update_emojis(emojis, 'up')

                            if is_windows:
                                winUp()
                        if mcp_middle_finger.y >= middle_bottom:
                            print('###########DOWN###########')
                            # emoji.Update(value=emoji_list['down'])
                            # main_emoji.Update(value=emoji_list['down'])
                            update_emojis(emojis, 'down')

                            if is_windows:
                                winDown()
                        cnt_y = 0
                else:
                    cnt_none += 1
                    if cnt_x > 0 or cnt_y > 0:
                        print('!!!!!!!!!!!! C A N C E L !!!!!!!!!!!!!!!!')
                        # emoji.Update(value=emoji_list['cancel'])
                        # main_emoji.Update(value=emoji_list['cancel'])
                        update_emojis(emojis, 'cancel')

                        if is_windows:
                            play_sound(3)
                    cnt_x = 0
                    cnt_y = 0

                    if cnt_none == 7:
                        # emoji.Update(value=emoji_list['idle'])
                        # main_emoji.Update(value=emoji_list['idle'])
                        update_emojis(emojis, 'idle')

            else:
                cnt_none += 1
                if cnt_none == 3:
                    if cnt_x > 0 or cnt_y > 0:
                        if is_windows:
                            play_sound(3)
                        # emoji.Update(value=emoji_list['cancel'])
                        # main_emoji.Update(value=emoji_list['cancel'])
                        update_emojis(emojis, 'cancel')

                    cnt_x = 0
                    cnt_y = 0
                elif cnt_none == 10:
                    # emoji.Update(value=emoji_list['idle'])
                    # main_emoji.Update(value=emoji_list['idle'])
                    update_emojis(emojis, 'idle')

            print(cnt_x, cnt_y, cnt_none)

        # Draw the hand annotations on the image.
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        height = image.shape[0]
        width = image.shape[1]
        color = (255, 0, 0)
        thickness = 2

        left_x = int(width * middle_left)
        right_x = int(width * middle_right)
        upper_y = int(height * middle_up)
        lower_y = int(height * middle_bottom)

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

        imgbytes = cv2.imencode('.png', image)[1].tobytes()
        main_window['image'].update(data=imgbytes)

    hands.close()
    cap.release()


main()
