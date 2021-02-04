#!/usr/bin/env python
import platform
import time
from _thread import start_new_thread
import numpy as np
import cv2
import mediapipe as mp
import PySimpleGUI as sg
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

# import windows specific libraries
is_windows = platform.system() == 'Windows'
if is_windows:
    import winsound
    from ahk import AHK
    from ahk.window import Window
    ahk = AHK()

    # set sounds for windows
    soundpath = "C:/Windows/Media/"
    sounds = {
        'detecting_x': 'chimes.wav',
        'detecting_y': 'ding.wav',
        'cancel': 'chord.wav',
    }
else:
    # set sounds for other OS
    import beepy
    sounds = {
        'detecting_x': 1,
        'detecting_y': 4,
        'cancel': 3
    }

# global variables
threshold_middleduration = 3
threshold_cancleduration = 5

middle_left = 0.3
middle_right = 0.7
middle_up = 0.3
middle_bottom = 0.7

# set emojis
emoji_list = {
    'idle': '\U0001F440',
    'detecting': '\U0001F44B',
    'left': '\U00002B05',
    'right': '\U000027A1',
    'down': '\U00002B07',
    'up': '\U00002B06',
    'cancel': '\U0000274C'
}

# list for mute icons
mute_list = {
    'unmute': '\U0001F508',
    'mute': '\U0001F50A'
}


def play_beepy_sound(sound):
    # thread for sound in non-windows OS
    beepy.beep(sounds[sound])


def play_sound(sound, isMuted):
    if not isMuted:
        if is_windows:
            # play windows sound
            winsound.PlaySound(
                soundpath + sounds[sound], winsound.SND_ALIAS | winsound.SND_ASYNC)
        else:
            # play beepy sound in separate thread
            start_new_thread(play_beepy_sound, (sound,))


def winRight(emojis):
    print('########### RIGHT ###########')
    update_emojis(emojis, 'right')

    if is_windows:
        # move window
        ahk.send_input('{LWin Down}{Right}{LWin Up}')
        time.sleep(0.2)
        ahk.key_press('Escape')


def winLeft(emojis):
    print('########### LEFT ###########')
    update_emojis(emojis, 'left')

    if is_windows:
        # move window
        ahk.send_input('{LWin Down}{Left}{LWin Up}')
        time.sleep(0.2)
        ahk.key_press('Escape')


def winUp(emojis):
    print('########### UP ###########')
    update_emojis(emojis, 'up')

    if is_windows:
        # move window
        ahk.send_input('{LWin Down}{Up}{LWin Up}')
        time.sleep(0.2)
        ahk.key_press('Escape')


def winDown(emojis):
    print('########### DOWN ###########')
    update_emojis(emojis, 'down')

    if is_windows:
        # move window
        ahk.send_input('{LWin Down}{Down}{LWin Up}')
        time.sleep(0.2)
        ahk.key_press('Escape')


def cancel(emojis, isMuted):
    print('!!!!!!!!!!!! C A N C E L !!!!!!!!!!!!!!!!')
    update_emojis(emojis, 'cancel')
    play_sound('cancel', isMuted)


def detecting(emojis, direction, isMuted):
    # play sound according to direction
    update_emojis(emojis, 'detecting')
    if direction == 'vertical':
        play_sound('detecting_y', isMuted)
    elif direction == 'horizontal':
        play_sound('detecting_x', isMuted)


def idle(emojis):
    update_emojis(emojis, 'idle')


def calc_initial_coordinates(cap):
    # read campera input to get size
    _, image = cap.read()
    window_height, window_width, _ = image.shape
    # get screen size
    screen_width, screen_height = sg.Window.get_screen_size()

    # calculate position for main window
    x_main = screen_width / 2 - window_width / 2
    y_main = 20

    # calculate position for mini window
    x_mini = screen_width - 95
    y_mini = screen_height - 110

    return (x_main, y_main), (x_mini, y_mini)


def make_main_window(pos, start_value):
    emoji = sg.Text(start_value, font='Helvetica 40', enable_events=True)
    mute = sg.Button(mute_list['mute'], size=(3, 1), font='Helvetica 14')

    # add emoji to main window only for windows
    if is_windows:
        main_layout = [
            [sg.Image(filename='', key='image')],
            [
                sg.Button('Minimize', size=(10, 1), font='Helvetica 14'),
                mute,
                emoji
            ]
        ]
    else:
        main_layout = [
            [sg.Image(filename='', key='image')],
            [
                sg.Button('Minimize', size=(10, 1), font='Helvetica 14'),
                mute,
            ]
        ]

    return emoji, mute, sg.Window('win force', main_layout, location=pos, finalize=True, keep_on_top=True)


def make_mini_window(pos, start_value):
    emoji = sg.Text(start_value, font='Helvetica 40', enable_events=True)
    mini_layout = [[emoji]]
    return emoji, sg.Window('win force', mini_layout, location=pos, alpha_channel=.7,
                            background_color=None, grab_anywhere=False, no_titlebar=True,
                            keep_on_top=True, finalize=True)


def make_windows(pos_main, pos_mini, start_emoji):
    # create main window
    main_emoji, mute_btn, main_window = make_main_window(pos_main, start_emoji)

    # create mini window
    mini_emoji, mini_window = make_mini_window(pos_mini, start_emoji)

    # list of emojis contains only mini_emoji if not windows
    if is_windows:
        emojis = [main_emoji, mini_emoji]
    else:
        emojis = [mini_emoji]

    return main_window, mini_window, emojis, mute_btn


def update_emojis(emojis, type):
    # update all emojis in list
    for emoji in emojis:
        emoji.Update(value=emoji_list[type])


def toggleMute(isMuted, mute_btn):
    if isMuted:
        mute_btn.Update(mute_list['mute'])
    else:
        mute_btn.Update(mute_list['unmute'])
    return not isMuted


def main():
    # initialize camera
    cap = cv2.VideoCapture(0)

    # initialize hand tracking
    hands = mp_hands.Hands(
        min_detection_confidence=0.7, min_tracking_confidence=0.7)

    # calc initial window position
    pos_main, pos_mini = calc_initial_coordinates(cap)

    # create windows
    main_window, mini_window, emojis, mute_btn = make_windows(
        pos_main, pos_mini, emoji_list['idle'])
    mini_window.Hide()

    # loop variables
    isMinimized = False
    isMuted = False
    framecounter = 0
    cnt_x = 0
    cnt_y = 0
    cnt_none = 0

    while True:
        # read windows
        _, event, values = sg.read_all_windows(timeout=20)

        # handle events
        if event == sg.WIN_CLOSED:
            hands.close()
            cap.release()
            return

        elif event == 'Minimize':
            main_window.Hide()
            mini_window.UnHide()

        elif event in mute_list.values():
            isMuted = toggleMute(isMuted, mute_btn)

        elif event in emoji_list.values():
            mini_window.Hide()
            main_window.UnHide()

        # get camera image
        ret, image = cap.read()
        framecounter += 1

        # flip image and convert colors
        image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)

        # performance improvement
        image.flags.writeable = False

        # get hand positions
        results = hands.process(image)

        # GESTURE RECOGNITION
        # detect hand in every second frame
        if framecounter % 2 == 0:
            is_detecting_hand = results.multi_hand_landmarks

            # if hands found
            if is_detecting_hand:
                landmarklist = results.multi_hand_landmarks[0]

                # get middle finger knuckle and tip
                mcp_middle_finger = landmarklist.landmark[9]
                tip_middle_finger = landmarklist.landmark[12]

                # if hand is not a fist
                if tip_middle_finger.y < mcp_middle_finger.y:
                    cnt_none = 0

                    is_horizontally_centered = mcp_middle_finger.x > middle_left and mcp_middle_finger.x < middle_right
                    is_vertically_centered = mcp_middle_finger.y > middle_up and mcp_middle_finger.y < middle_bottom

                    # if hand is horizontally in the center
                    if is_horizontally_centered:
                        cnt_x += 1

                        if cnt_x == threshold_middleduration:
                            # set emojis and play sound
                            detecting(emojis, 'horizontal', isMuted)

                    # if hand moved away from center
                    elif cnt_x >= threshold_middleduration:
                        if mcp_middle_finger.x >= middle_right:
                            # move window, set emojis and play sound
                            winRight(emojis)
                        if mcp_middle_finger.x <= middle_left:
                            # move window, set emojis and play sound
                            winLeft(emojis)

                        cnt_x = 0

                    # if hand is vertically in the center
                    if is_vertically_centered:
                        cnt_y += 1

                        # execute only if horizontalls has not been executed
                        if cnt_y == threshold_middleduration and not is_horizontally_centered:
                            # move window, set emojis and play sound
                            detecting(emojis, 'vertical', isMuted)

                    # if hand moved away from center
                    elif cnt_y > threshold_middleduration:
                        if mcp_middle_finger.y <= middle_up:
                            # move window, set emojis and play sound
                            winUp(emojis)
                        if mcp_middle_finger.y >= middle_bottom:
                            # move window, set emojis and play sound
                            winDown(emojis)

                        cnt_y = 0

                # if hand is a fist
                else:
                    cnt_none += 1

                    # if hand has been detected before
                    if cnt_x > 0 or cnt_y > 0:
                        # set emojis and play sound
                        cancel(emojis, isMuted)
                    cnt_x = 0
                    cnt_y = 0

                    if cnt_none == 7:
                        # set emojis
                        idle(emojis)

            # if no hands found
            else:
                cnt_none += 1
                if cnt_none == threshold_cancleduration:

                    # if hand has been detected before
                    if cnt_x > 0 or cnt_y > 0:
                        # set emojis and play sound
                        cancel(emojis, isMuted)

                    cnt_x = 0
                    cnt_y = 0

                elif cnt_none == threshold_cancleduration + 7:
                    # set emojis
                    idle(emojis)

            # log current counters
            print(cnt_x, cnt_y, cnt_none)

        # convert colors back
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # make grid lines
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

        # draw hands on image
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        # convert image to bytes and render in window
        imgbytes = cv2.imencode('.png', image)[1].tobytes()
        main_window['image'].update(data=imgbytes)

    # destroy
    hands.close()
    cap.release()


main()
