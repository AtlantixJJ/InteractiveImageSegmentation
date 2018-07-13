#!/usr/bin/env python
'''
===============================================================================
Interactive Image Segmentation using GrabCut algorithm.
This sample shows interactive image segmentation using grabcut algorithm.
USAGE:
    python grabcut.py <filename>
README FIRST:
    Two windows will show up, one for input and one for output.
    At first, in input window, draw a rectangle around the object using
mouse right button. Then press 'n' to segment the object (once or a few times)
For any finer touch-ups, you can press any of the keys below and draw lines on
the areas you want. Then again press 'n' for updating the output.
Key '0' - To select areas of sure background
Key '1' - To select areas of sure foreground
Key '2' - To select areas of probable background
Key '3' - To select areas of probable foreground
Key 'n' - To update the segmentation
Key 'r' - To reset the setup
Key 's' - To save the results
===============================================================================
'''

# Python 2/3 compatibility
from __future__ import print_function
from ns import api
import threading, time
import numpy as np
import cv2 as cv
import sys

BLUE = [255,0,0]        # rectangle color
RED = [0,0,255]         # PR BG
GREEN = [0,255,0]       # PR FG
BLACK = [0,0,0]         # sure BG
WHITE = [255,255,255]   # sure FG

DRAW_BG = {'color' : BLACK, 'val' : 0}
DRAW_FG = {'color' : WHITE, 'val' : 1}
DRAW_PR_FG = {'color' : GREEN, 'val' : 3}
DRAW_PR_BG = {'color' : RED, 'val' : 2}

# setting up flags
rect = (0,0,1,1)
dragging = False            # flag for dragging
drag_over = False
has_result = False      # flag for having sementation result
drawing = False         # flag for drawing curves
resume_dragging = False
rectangle = False       # flag for drawing rect
rect_over = False       # flag to check if rect drawn
rect_or_mask = 100      # flag for selecting rect or mask mode
value = DRAW_FG         # drawing initialized to FG
thickness = 3           # brush thickness

drag_st = []

seg_img, seg_mask = np.zeros((10, 10, 3)), np.zeros((10, 10, 3))

need_stylization = False

bbox = [0, 0, 1, 1]

class StylizationThread(threading.Thread):
    def __init__(self, model_file="models/starrynight.ckpt-done"):
        threading.Thread.__init__(self)

        self.stylized_image = np.zeros((10, 10, 3))
        self.content_image = np.zeros((10, 10, 3))
        self.stylizer = api.NeuralStyle(model_file)

        self.need_stylization = False

    def run(self):
        while True:
            if self.need_stylization:
                self.need_stylization = False
                self.stylized_image = self.stylizer.stylize_single(self.content_image)[:, :, ::-1]
            if not self.need_stylization:
                time.sleep(0.1)

def onmouse(event,x,y,flags,param):
    global img,img2,drawing,value,mask,rectangle,rect,rect_or_mask,ix,iy,rect_over

    global resume_dragging, dragging, has_result, drag_st, prev_img

    global img_inpainted, need_stylization, thr

    # Draw Rectangle
    if event == cv.EVENT_RBUTTONDOWN:
        rectangle = True
        ix,iy = x,y

    elif event == cv.EVENT_MOUSEMOVE:
        if rectangle == True:
            img = img2.copy()
            cv.rectangle(img,(ix,iy),(x,y),BLUE,2)
            rect = (min(ix,x),min(iy,y),abs(ix-x),abs(iy-y))
            rect_or_mask = 0

        elif dragging == True:
            delta = [x - drag_st[0], y - drag_st[1]]
            delta = delta[::-1]

    elif event == cv.EVENT_RBUTTONUP:
        rectangle = False
        rect_over = True
        cv.rectangle(img,(ix,iy),(x,y),BLUE,2)
        rect = (min(ix,x),min(iy,y),abs(ix-x),abs(iy-y))
        rect_or_mask = 0
        print(" Now press the key 'n' a few times until no further change \n")

    # draw touchup curves

    if event == cv.EVENT_LBUTTONDOWN:
        if rect_over == False:
            print("first draw rectangle \n")
        elif drag_over or not dragging:
            drawing = True
            cv.circle(img,(x,y),thickness,value['color'],-1)
            cv.circle(mask,(x,y),thickness,value['val'],-1)
        
        if has_result and not drag_over:
            # start drag
            if not resume_dragging:
                dragging = True
                prev_img = img_inpainted.copy()
                drag_st = [x, y]
            else:
                prev_img = img_inpainted.copy()
                resume_dragging = False

    elif event == cv.EVENT_MOUSEMOVE:
        if drawing == True:
            cv.circle(img,(x,y),thickness,value['color'],-1)
            cv.circle(mask,(x,y),thickness,value['val'],-1)
        
        if dragging and not resume_dragging:
            #prev_img = (255 - img_inpainted) * (255 - seg_mask[:, :, None].astype(img_inpainted.dtype))
            img = prev_img.copy()
            if delta[0] > 0 and delta[1] > 0:
                img[delta[0]:, delta[1]:] = (256 - prev_img[delta[0]:, delta[1]:]) * (255 - seg_mask[:-delta[0], :-delta[1], None]) + (256 - seg_img[:-delta[0], :-delta[1]]) * seg_mask[:-delta[0], :-delta[1], None]
            elif delta[0] < 0 and delta[1] > 0:
                img[:delta[0], delta[1]:] = (256 - prev_img[:delta[0], delta[1]:]) * (255 - seg_mask[-delta[0]:, :-delta[1], None]) + (256 - seg_img[-delta[0]:, :-delta[1]]) * seg_mask[-delta[0]:, :-delta[1], None]
            elif delta[0] > 0 and delta[1] < 0:
                img[delta[0]:, :delta[1]] = (256 - prev_img[delta[0]:, :delta[1]]) * (255 - seg_mask[:-delta[0], -delta[1]:, None])+ (256 - seg_img[:-delta[0], -delta[1]:]) * seg_mask[:-delta[0], -delta[1]:, None]
            elif delta[0] < 0 and delta[1] < 0:
                img[:delta[0], :delta[1]] = (256 - prev_img[:delta[0], :delta[1]]) * (255 - seg_mask[-delta[0]:, -delta[1]:, None])+ (256 - seg_img[-delta[0]:, -delta[1]:]) * seg_mask[-delta[0]:, -delta[1]:, None]
            
            thr.content_image = img
            thr.need_stylization = True


    elif event == cv.EVENT_LBUTTONUP:
        if drawing == True:
            drawing = False
            cv.circle(img,(x,y),thickness,value['color'],-1)
            cv.circle(mask,(x,y),thickness,value['val'],-1)
        
        if dragging == True:
            resume_dragging = True
            #dragging = False

if __name__ == '__main__':

    # print documentation
    print(__doc__)

    # stylization
    thr = StylizationThread(sys.argv[2])

    # Loading images
    filename = sys.argv[1] # for drawing purposes

    img = cv.imread(filename)
    img2 = img.copy()                               # a copy of original image
    mask = np.zeros(img.shape[:2],dtype = np.uint8) # mask initialized to PR_BG
    output = np.zeros(img.shape,np.uint8)           # output image to be shown

    # input and output windows
    cv.namedWindow('segmentation')
    cv.namedWindow('stylization')
    cv.namedWindow('input')
    cv.setMouseCallback('input',onmouse)
    cv.moveWindow('input',img.shape[1]+10,90)

    print(" Instructions: \n")
    print(" Draw a rectangle around the object using right mouse button \n")

    thr.content_image = img2
    thr.need_stylization = True
    thr.start()

    while True:
        cv.imshow('segmentation', seg_img[bbox[1]:bbox[1]+bbox[3], bbox[0]:bbox[0] + bbox[2], :])
        cv.imshow('input', img)
        cv.imshow('stylization', thr.stylized_image)
        k = cv.waitKey(1)

        # key bindings
        if k == 27:         # esc to exit
            break
        elif k == ord('0'): # BG drawing
            print(" mark background regions with left mouse button \n")
            value = DRAW_BG
        
        elif k == ord('1'): # FG drawing
            print(" mark foreground regions with left mouse button \n")
            value = DRAW_FG
        
        elif k == ord('2'): # PR_BG drawing
            value = DRAW_PR_BG
        
        elif k == ord('3'): # PR_FG drawing
            value = DRAW_PR_FG

        elif k == ord('s'): # save image
            bar = np.zeros((img.shape[0],5,3),np.uint8)
            res = np.hstack((img2,bar,img,bar,output))

            has_result = True

            seg_img = output
            seg_mask = mask2
            bbox = cv.boundingRect(cv.findNonZero(seg_mask))

            cv.imwrite('grabcut_output.png',res)
            print(" Result saved as image \n")

        elif k == ord('r'): # reset everything
            print("resetting \n")
            rect = (0,0,1,1)
            drawing = False
            dragging = False
            resume_dragging = False
            drag_over = False
            rectangle = False
            rect_or_mask = 100
            rect_over = False
            value = DRAW_FG
            has_result = False
            img = img2.copy()
            mask = np.zeros(img.shape[:2],dtype = np.uint8) # mask initialized to PR_BG
            output = np.zeros(img.shape,np.uint8)           # output image to be shown

        elif k == ord("d"):
            drag_over = True

        elif k == ord('n'): # segment the image
            print(""" For finer touchups, mark foreground and background after pressing keys 0-3
            and again press 'n' \n""")

            if (rect_or_mask == 0):         # grabcut with rect
                bgdmodel = np.zeros((1,65),np.float64)
                fgdmodel = np.zeros((1,65),np.float64)
                cv.grabCut(img2,mask,rect,bgdmodel,fgdmodel,1,cv.GC_INIT_WITH_RECT)
                rect_or_mask = 1
            elif rect_or_mask == 1:         # grabcut with mask
                bgdmodel = np.zeros((1,65),np.float64)
                fgdmodel = np.zeros((1,65),np.float64)
                cv.grabCut(img2,mask,rect,bgdmodel,fgdmodel,1,cv.GC_INIT_WITH_MASK)

            mask2 = np.where((mask==1) + (mask==3),255,0).astype('uint8')
            output = cv.bitwise_and(img2,img2,mask=mask2)
            seg_img = output
            seg_mask = mask2
            bbox = cv.boundingRect(cv.findNonZero(seg_mask))
            
            # inpaint
            img_inpainted = cv.inpaint(img2, mask2, 3, cv.INPAINT_TELEA) #INPAINT_TELEA

    cv.destroyAllWindows()
