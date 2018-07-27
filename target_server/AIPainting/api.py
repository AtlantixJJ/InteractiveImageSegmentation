import sys
sys.path.insert(0, "../")
sys.path.insert(0, "../..")
sys.path.insert(0, "../../ns/")
import cv2 as cv
from PIL.Image import fromarray
from os.path import join as osj
import numpy as np
import threading

from inpaint import Inpainter

"""
import platform
if platform.system() == "Linux":
    DEBUG_EDIT = False
else:
    DEBUG_EDIT = True
    #export CUDA_VISIBLE_DEVICES=0
"""
DEBUG_EDIT = True
from ns.api import NeuralStyle
### [MERGE] comment out this line to use our own stylization
stylizor = NeuralStyle(osj("..", "..", "models", "feathers.ckpt-done"))

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

    def set_mask(self, mask):
        self.raw_mask = mask

    def segment(self, rect, mask=None):
        self.setup_vars()
        if mask is None:
            cv.grabCut(self.image, self.raw_mask, tuple(rect), self.bgdmodel,self.fgdmodel,1,cv.GC_INIT_WITH_RECT)
        else:
            cv.grabCut(self.image, self.raw_mask, tuple(rect), self.bgdmodel,self.fgdmodel,1,cv.GC_INIT_WITH_MASK)
        self.mask = np.where((self.raw_mask==1) + (self.raw_mask==3), 255, 0).astype('uint8')
        output = cv.bitwise_and(self.image,self.image,mask=self.mask)
        seg_img = output
        seg_mask = self.mask

        try:
            bbox = cv.boundingRect(cv.findNonZero(seg_mask))
        except:
            bbox = None

        print(bbox)
        if bbox[2] < 2 or bbox[3] < 2:
            bbox = None
        cv.imwrite("tmp.png", self.image[:, :, ::-1])
        t_ = self.image[:, :, ::-1].copy()
        cv.rectangle(t_ ,(rect[0], rect[1]),(rect[0]+rect[2],rect[1]+rect[3]),[255,0,0],2)
        cv.imwrite("rect.png", t_)
        
        #img_inpainted = cv.inpaint(self.image, self.mask, 3, cv.INPAINT_TELEA)

        return seg_img, seg_mask, bbox

    def inpaint_image(self, image):
        """
        Inpaint image by original mask
        """
        assert(image.size == self.mask.size, "inpaint image: image and mask size inconsistent")
        return cv.inpaint(image, self.mask, 3, cv.INPAINT_TELEA)

segmentor = InteractiveSegmentation()
inpaintor = Inpainter(osj("..", "..", "models", "completionnet_places2.t7"), use_gpu=True)

def get_segmentation(image, rect, user_mask=None):
    segmentor.set_image(image); segmentor.set_mask(user_mask)
    seg_img, mask, bbox = segmentor.segment(rect, user_mask)

    if bbox is not None:
        #inp_img = fromarray(cv.inpaint(image, segmentor.mask, 3, cv.INPAINT_TELEA)
        inp_img = inpaintor.inpaint(segmentor.image, segmentor.mask)
        seg_img = seg_img[bbox[1]:bbox[1]+bbox[3], bbox[0]:bbox[0] + bbox[2], :]
        print(seg_img.shape)
        seg_img = fromarray(seg_img)
        seg_img.putalpha(fromarray(mask[bbox[1]:bbox[1]+bbox[3], bbox[0]:bbox[0] + bbox[2]]))
    else:
        inp_img = fromarray(seg_img)
        seg_img = fromarray(seg_img)
    return seg_img, inp_img, fromarray(mask), bbox

def get_stylization(image):
    return fromarray(stylizor.stylize_single(image))