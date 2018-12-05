import cv2
import numpy as np
import pyautogui as gui
import time

# gui.click(90,436)

starttime = time.time()

def timer():
    global starttime
    cd = int(time.time() - starttime)
    print(cd)
    if cd % 10 == 5:
        print('reset')
        starttime += 4

while True:
    timer()
    time.sleep(0.1)