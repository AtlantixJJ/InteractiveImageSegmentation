import torch
import torchvision.transforms as T
import PIL.Image as Image
from PIL.Image import fromarray
import skimage.io as io
import numpy as np
from torch.utils.serialization import load_lua
from os.path import join as osj


IS_GPU = False

image_file = osj("images", "example.png")
mask_file = osj("images", "example_mask.png")

class Inpainter(object):
    def __init__(self):
        try:
            data = load_lua(osj("models", "completionnet_places2.t7"))
        except:
            data = load_lua(osj("models", "completionnet_places2.t7"), long_size=8)
        self.model, self.mean = data['model'], data['mean']
        self.model.evaluate()
        self.mean = self.mean.view(3, 1, 1)

        if IS_GPU:
            self.model = self.model.cuda()

    def inpaint(self, image, mask):
        """
        image, mask: 0, 1
        """
        image = torch.Tensor(image).permute(2, 0, 1)
        mask = torch.Tensor(mask)
        self.image = image - self.mean
        mask = mask.view(1, mask.size(0), mask.size(1))
        self.image[torch.cat([mask,mask,mask])>0.2]=0
        batch_input = torch.cat([self.image, mask], 0).view(1, 4, mask.size(1), mask.size(2))

        output = self.model.forward(batch_input)[0]
        output = image * (1 - mask) + output * mask
        output = output.permute(1,2,0).numpy() * 255
        print(output.max(), output.min(), mask.max(), mask.min())
        return fromarray(output.astype("uint8"))

image = io.imread(image_file).astype("float32")/255.
mask = io.imread(mask_file).astype("float32")/255.

inpainter = Inpainter()
res = inpainter.inpaint(image, mask)
res.save(open("tmp.jpg", "wb"), format="JPEG")