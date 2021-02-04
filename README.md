# WinForce
With WinForce you can move your windows on your screen like a Jedi. It uses to [Google MediaPipe](https://github.com/google/mediapipe) detect the hand, swipe gestures to the left, right, up or down move the active window accordingly - similar to winkey + arrowkeys.  
This project was created for the course *Building Interaction Inferfaces at TU Wien*.

![WinForce demo](examples/winforce_demo.gif)

# Dependencies
- the application only works on Windows
- other platforms are supported, but cannot move windows
- Python 3.8
- [Autohotkey](https://www.autohotkey.com/)
- Python packages
  - PySimpleGUI
  - ahk
  - mediapipe
  - opencv-python

# Run the Application
- run `python win_force.py`
- click on 'minimize' to close the big window, in the lower right corner the emoji indicator appears
- a click on the miniature window in the lower right corner will open the big window again

Application screen with displayed camera input  | Miniature indicator with application running in the background
--|--
![WinForce full](examples/winforce_full.png "The WinForce application with camera input and handtracking")  |  ![WinForce Miniature](examples/winforce_miniature.png "The WinForce miniature gesture indicator")


# Detected gestures
- move your hand to the middle of the x or y axis
- after a sound is played and/or the hand emoji is present in the emoji indicator
  - move your hand up or down: the focused window is snapped up or down (analog to `windows + UP/DOWN` on the keyboard)
  - move your hand left or right: the focused window is snapped to the left or right (analog to `windows + LEFT/RIGHT` on the keyboard)
  - form a fist gesture to cancel the current detection of your hand
