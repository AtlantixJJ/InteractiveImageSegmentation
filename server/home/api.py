import sys
sys.path.insert(0, "../..")
import cv2 as cv
from PIL.Image import fromarray
from os.path import join as osj
import numpy as np
import threading
from ns.api import NeuralStyle

class InteractiveSegmentation(object):
    def __init__(self, image=None):
        self.image = image
        self.raw_mask = None
        self.mask = None

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
        
        cv.grabCut(self.image, self.raw_mask, tuple(rect), self.bgdmodel,self.fgdmodel,1,cv.GC_INIT_WITH_RECT)
        self.mask = np.where((self.raw_mask==1) + (self.raw_mask==3), 255, 0).astype('uint8')
        output = cv.bitwise_and(self.image,self.image,mask=self.mask)
        seg_img = output
        seg_mask = self.mask

        try:
            bbox = cv.boundingRect(cv.findNonZero(seg_mask))
        except:
            bbox = None

        img_inpainted = cv.inpaint(self.image, self.mask, 3, cv.INPAINT_TELEA)

        return seg_img, img_inpainted, seg_mask, bbox

    def inpaint_image(self, image):
        """
        Inpaint image by original mask
        """
        assert(image.size == self.mask.size, "inpaint image: image and mask size inconsistent")
        return cv.inpaint(image, self.mask, 3, cv.INPAINT_TELEA)

segmentor = InteractiveSegmentation()
stylizor = NeuralStyle("../models/feathers.ckpt-done")

def get_segmentation(image, rect):
    segmentor.set_image(image)
    seg_img, inp_img, mask, bbox = segmentor.segment_rect(rect)
    if bbox is not None:
        seg_img = seg_img[bbox[1]:bbox[1]+bbox[3], bbox[0]:bbox[0] + bbox[2], :]
        seg_img = fromarray(seg_img)
        seg_img.putalpha(fromarray(mask[bbox[1]:bbox[1]+bbox[3], bbox[0]:bbox[0] + bbox[2]]))

    return seg_img, fromarray(inp_img), fromarray(mask), bbox

def get_stylization(image):
    return fromarray(stylizor.stylize_single(image))