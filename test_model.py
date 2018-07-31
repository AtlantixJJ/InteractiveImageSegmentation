from ns import api
import skimage.io as io

stylizer = api.NeuralStyle()

img = io.imread("images/shenyang3.jpg")[:, :, :3]
out = stylizer.stylize_single(img)
io.imsave("tmp.png", out)

"""
http://166.111.139.44:8003/?description=powerplant&style=2&adj=joyful
114.113.33.223:23333/?description=powerplant&style=2&adj=joyful
localhost:2333
"""