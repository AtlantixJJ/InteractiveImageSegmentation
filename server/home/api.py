import sys
sys.path.insert(0, "..")
import cv2 as cv
from PIL.Image import fromarray
import numpy as np
import threading
from ns.api import NeuralStyle

class InteractiveSegmentation(object):
    def __init__(self, image=None):
        self.image = image
        self.raw_mask = None

    def setup_vars(self):
        if self.image is None:
            return False
        
        if self.raw_mask is None or self.image.shape[:2] != self.raw_mask.shape:
            # mask initialized to PR_BG
            self.raw_mask = np.zeros(self.image.shape[:2], dtype=np.uint8) 
        
        self.bgdmodel = np.zeros((1,65),np.float64)
        self.fgdmodel = np.zeros((1,65),np.float64)

    def set_image(self, image):
        self.image = image

    def segment_rect(self, rect):
        self.setup_vars()

        cv.imwrite("rect.png", self.image[rect[0]:rect[0]+rect[2], rect[1]:rect[1]+rect[3]])
        cv.grabCut(self.image, self.raw_mask, tuple(rect), self.bgdmodel,self.fgdmodel,1,cv.GC_INIT_WITH_RECT)
        mask2 = np.where((self.raw_mask==1) + (self.raw_mask==3), 255, 0).astype('uint8')
        output = cv.bitwise_and(self.image,self.image,mask=mask2)
        seg_img = output
        seg_mask = mask2

        try:
            bbox = cv.boundingRect(cv.findNonZero(seg_mask))
        except:
            pass

        return seg_img, seg_mask, bbox

segmentor = InteractiveSegmentation()
stylizor = NeuralStyle("../models/feathers.ckpt-done")

def get_segmentation(image, rect):
    segmentor.set_image(image)
    img, mask, bbox = segmentor.segment_rect(rect)
    return fromarray(img), fromarray(mask), bbox

def get_stylization(image):
    return fromarray(stylizor.stylize_single(image))