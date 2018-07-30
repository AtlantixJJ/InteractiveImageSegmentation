# pytorch
import torch
from torch.utils.serialization import load_lua
from PIL import Image
import numpy as np
import cv2 as cv
from os.path import join as osj
from PIL.Image import fromarray

class Inpainter(object):
    def __init__(self, path, use_gpu=True):
        try:
            data = load_lua(path)
        except:
            data = load_lua(path, long_size=8)
        self.model, self.mean = data['model'], data['mean']
        self.model.evaluate()
        self.mean = self.mean.view(3, 1, 1)
        self.use_gpu = use_gpu
        if self.use_gpu:
            self.model = self.model.cuda()

    def inpaint(self, image, mask):
        """
        image, mask: 0, 1
        """
        mask = mask.copy()
        image = image.copy()
        image_t = torch.Tensor(image).permute(2, 0, 1) / 255.
        mask_t = torch.Tensor(mask) / 255.

        self.image = image_t - self.mean
        mask_t = mask_t.view(1, mask_t.size(0), mask_t.size(1))
        self.image[torch.cat([mask_t]*3)>0.2]=0
        batch_input = torch.cat([self.image, mask_t], 0).view(1, 4, mask_t.size(1), mask_t.size(2))

        if self.use_gpu:
            batch_input = batch_input.cuda()

        output = self.model.forward(batch_input)[0]
        print("=> Network forward done.")

        if self.use_gpu:
            output = output.cpu()

        output = image_t * (1 - mask_t) + output * mask_t
        print(output.max(), output.min(), image_t.max(), image_t.min(), mask_t.max(), mask_t.min())
        output = output.detach().permute(1,2,0)
        output = (output.numpy() * 255).astype("uint8")

        minx = 1e5
        maxx = 1
        miny = 1e5
        maxy = 1
        for x in range(mask.shape[0]):
            for y in range(mask.shape[1]):
                if mask[x, y] == 255:
                    minx = min(minx,x)
                    maxx = max(maxx,x)
                    miny = min(miny,y)
                    maxy = max(maxy,y)
        p_i = (int(miny+(maxy-miny)/2)-1, int(minx+(maxx-minx)/2)-1)
        print(p_i)
        print("=> Post processing")
        dst_i = cv.inpaint(output, mask, inpaintRadius=1, flags=cv.INPAINT_TELEA)
        out_i = dst_i.copy()
        print("=> Poisson fusion")
        cv.seamlessClone(src=output, dst=dst_i, mask=mask, p=p_i, blend=out_i, flags=cv.NORMAL_CLONE)
        print("=> Done")
        return fromarray(out_i)

if __name__ == "__main__":
    import sys
    inpaintor = Inpainter(osj("models", "completionnet_places2.t7"), False)
    img = np.asarray(Image.open(sys.argv[1]))
    mask = np.asarray(Image.open(sys.argv[2]))
    result = inpaintor.inpaint(img, mask)
    result.save(open("tmp.jpg", "wb"), format="JPEG")

