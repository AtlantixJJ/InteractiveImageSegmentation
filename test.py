import torch
import torchvision.transforms as T
import PIL.Image as Image
import skimage.io as io
import numpy as np
from torch.utils.serialization import load_lua



IS_GPU = False

image_file = "example.png"
mask_file = "example_mask.png"

data = load_lua("./completionnet_places2.t7")
model, mean = data['model'], data['mean']
model.evaluate()
mean = mean.view(3, 1, 1)

if IS_GPU:
    model = model.cuda()

image = io.imread(image_file).astype("float32")/255.
mask = io.imread(mask_file).astype("float32")/255.

def run(image, mask):
    """
    image, mask: 0, 1
    """
    image = torch.Tensor(image)
    mask = torch.Tensor(mask)
    image = image.permute(2, 0, 1) - mean
    mask = mask.view(1, mask.size(0), mask.size(1))
    image[torch.cat([mask,mask,mask])>0.2]=0
    batch_input = torch.cat([image, mask], 0).view(1, 4, mask.size(1), mask.size(2))

    print(image.shape, image.max(), image.min())
    print(mask.shape, mask.max(), mask.min())

    output = model.forward(batch_input)[0]
    io.imsave("output.png", output.permute(1,2,0).numpy())
    return batch_input, output

inp, out = run(image, mask)
tin = load_lua("input.t7")
print(inp)
print(tin)
#inp, out = run(image, np.zeros((image.shape[0], image.shape[1])))

#io.imsave("mask1.png", mask[0].numpy())
#io.imsave("input1.png", (image+mean).permute(1,2,0).numpy())
#io.imsave("output1.png", output.permute(1,2,0).numpy())