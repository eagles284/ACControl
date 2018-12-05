from PIL import ImageGrab
import pyautogui as gui
import numpy as np
import cv2
import win32gui
import win32ui
from ctypes import windll
from PIL import Image
import argparse
import imutils
import time

def getCCTVImread():
    hwnd = win32gui.FindWindow(None, 'IP Camera Viewer')

    # Change the line below depending on whether you want the whole window
    # or just the client area. 
    # left, top, right, bot = win32gui.GetClientRect(hwnd)
    left, top, right, bot = win32gui.GetWindowRect(hwnd)
    w = right - left
    h = bot - top

    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()

    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)

    saveDC.SelectObject(saveBitMap)

    # Change the line below depending on whether you want the whole window
    # or just the client area.
    # result = windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 1)
    result = windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 0)
    # print(result)

    bmpinfo = saveBitMap.GetInfo()
    bmpstr = saveBitMap.GetBitmapBits(True)

    im = Image.frombuffer(
        'RGB',
        (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
        bmpstr, 'raw', 'BGRX', 0, 1)

    win32gui.DeleteObject(saveBitMap.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwndDC)

    if result == 1:
        # PrintWindow Succeeded
        im.save("imread.png")
        pass

    x,y,w,h = (120,270,570,280)
    return cv2.imread('imread.png')[y:y+h, x:x+w]

def preview():
    cv2.imshow('Aplikasi Penglihat CCTV by Arya Adyatma (CH 4)', getCCTVImread())

    if cv2.waitKey(25) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
    pass

baseFrame = cv2.GaussianBlur(cv2.cvtColor(cv2.imread('base.png'), cv2.COLOR_RGB2GRAY), (21,21), 0)

def motionDetection(grayImread, min_area=500, preview=False):
    global firstFrame

    frame = cv2.GaussianBlur(grayImread, (21, 21), 0)

    # compute the absolute difference between the current frame and
    # first frame
    frameDelta = cv2.absdiff(baseFrame, frame)
    thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]

    # dilate the thresholded image to fill in holes, then find contours
    # on thresholded image
    thresh = cv2.dilate(thresh, None, iterations=2)
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)

    # loop over the contours
    for c in cnts:

        # if the contour is too small, ignore it
        if cv2.contourArea(c) < min_area:
            continue

        # compute the bounding box for the contour, draw it on the frame,
        # and update the text
        (x, y, w, h) = cv2.boundingRect(c)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
    
    if preview:
        frames = frameDelta
        cv2.putText(frames,'Biaya AC / Bulan: Rp.63.592',(5,15), cv2.FONT_HERSHEY_SIMPLEX, 0.4,(255,255,255),1,cv2.LINE_AA)
        cv2.imshow('Sensor Deteksi Gerak by Arya Adyatma (CH 4)', frameDelta)
        
        if cv2.waitKey(25) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
    return thresh


queue = None
intent = None
startTime = time.time()

def filterLogic(grayImread):
    global queue, intent, startTime

    cd = int(time.time() - startTime)

    if (cd % 10 == 5) & (queue is not None):
        queue = None
        print('Clearing Queue')
        startTime += 4

    filtered = grayImread

    in_x, in_y, in_w, in_h = (349,180,450,343)
    in_filter = filtered[in_y:in_h, in_x:in_w]

    out_x, out_y, out_w, out_h = (220,220,342,343)
    out_filter = filtered[out_y:out_h, out_x:out_w]

    # cv2.imshow('Aplikasi Penglihat CCTV by Arya Adyatma (CH 4)', out_filter)
    # cv2.imshow('Aplikasi Penglihat CCTV by Arya Adyatma (CH 4)', in_filter)

    if cv2.waitKey(25) & 0xFF == ord('q'):
        cv2.destroyAllWindows()

    in_value = int(np.sum(in_filter) / 1000)
    out_value = int(np.sum(out_filter) / 1000)

    if (queue is None) & (in_value > 500):
        queue = 'out_pending'
        print('Orang mau keluar...')
    if (out_value > 300) & (queue == 'out_pending'):
        queue = None
        intent = 'Kamar kosong'
        print(intent)
        triggerFunction('out')
        return

    if (queue is None) & (out_value > 600):
        queue = 'in_pending'
        print('Orang mau masuk')
    if (in_value > 400) & (queue == 'in_pending'):
        queue = None
        intent = 'Orang sedang didalam kamar'
        print(intent)
        triggerFunction('in')
        return

    print('\nDekat Pintu:', in_value, '\nJauh Pintu:',out_value,'\nCurrent Queue:', queue)

def triggerFunction(outIn):
    if outIn == 'in':
        time.sleep(2)
        gui.click(90,436)
        pass
    else:
        time.sleep(2)
        gui.click(90,436)
        pass
    pass

def main():
    global intent

    gray = cv2.cvtColor(getCCTVImread(), cv2.COLOR_RGB2GRAY)
    motions = motionDetection(gray, preview=True)
    filterLogic(motions)

    print(intent)

if __name__ == "__main__":
    while True:
        main()
        time.sleep(0.1)