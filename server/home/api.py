import sys
sys.path.insert(0, "..")
import cv2 as cv
import numpy as np
import threading
#import ns

class InteracctiveSegmentation(object):
    def __init__(self, image=None):
        self.image = image
        self.mask = None

    def setup_vars(self):
        if self.image is None:
            return False
        
        if self.raw_mask is None or self.image.shape[:2] != self.raw_mask.shape:
            # mask initialized to PR_BG
            self.raw_mask = np.zeros(self.image.shape[:2], dtype=np.uint8) 
            
    def set_image(self, image):
        self.image = image

    def segment_rect(self, rect):
        if self.image is None:
            return None
        
        cv.grabCut(self.image, self.raw_mask,rect,self.bgdmodel,self.fgdmodel,1,cv.GC_INIT_WITH_MASK)
        mask2 = np.where((mask==1) + (mask==3),255,0).astype('uint8')
        output = cv.bitwise_and(img2,img2,mask=mask2)
        seg_img = output
        seg_mask = mask2
        bbox = cv.boundingRect(cv.findNonZero(seg_mask))
