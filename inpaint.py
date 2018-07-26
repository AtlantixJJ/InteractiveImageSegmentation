# pytorch
import torch
from torch.utils.serialization import load_lua
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

        if use_gpu:
            self.model = self.model.cuda()

    def inpaint(self, image, mask):
        """
        image, mask: 0, 1
        """
        image_t = torch.Tensor(image).permute(2, 0, 1) / 255.
        mask = torch.Tensor(mask) / 255.
        self.image = image_t - self.mean
        mask = mask.view(1, mask.size(0), mask.size(1))
        self.image[torch.cat([mask,mask,mask])>0.2]=0
        batch_input = torch.cat([self.image, mask], 0).view(1, 4, mask.size(1), mask.size(2))

        output = self.model.forward(batch_input)[0]
        output = image_t * (1 - mask) + output * mask
        print(output.max(), output.min(), image_t.max(), image_t.min(), mask.max(), mask.min())
        output = output.permute(1,2,0).numpy() * 255
        return fromarray(output.astype("uint8"))