# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.template import loader, Context
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import home.api as api
from IPython.core.debugger import Tracer 
from io import BytesIO
from PIL import Image
import numpy as np
from base64 import b64encode, b64decode

index_temp = loader.get_template("index.html")


def response(image):
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    imageString = b64encode(buffered.getvalue())
    json = '{"ok":"true", "img_h":"%d", "img_w":"%d", "raw_img":"data:image/png;base64,%s"}' % (
        image.size[0], image.size[1], imageString)
    return HttpResponse(json)

def response2(image, mask, seg_img):
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    imageString = b64encode(buffered.getvalue())

    maskBuffered = BytesIO()
    mask.save(maskBuffered, format="PNG")
    maskString = b64encode(maskBuffered.getvalue())

    fused_image = Image.composite(image.point(lambda x:x*1.5), image.point(lambda x:x/2), mask)
    fusedBuffered = BytesIO()
    fused_image.save(fusedBuffered, format="PNG")
    fusedString = b64encode(fusedBuffered.getvalue())

    segimgBuffer = BytesIO()
    seg_img.save(segimgBuffer, format="PNG")
    segimgString = b64encode(segimgBuffer.getvalue())

    json = '{"ok":"true", "img_h":"%d", "img_w":"%d", \
        "raw_img":"data:image/png;base64,%s", \
            "mask":"data:image/png;base64,%s", \
            "fused_image":"data:image/png;base64,%s", \
            "seg_img":"data:image/png;base64,%s"}' % (
        image.size[0], image.size[1], imageString, maskString, fusedString, segimgString)

    return HttpResponse(json)

def index(request):
    return render(request, 'index.html')
    # return HttpResponse(index_temp.render())


@csrf_exempt
def input_image(request):
    form_data = request.POST
    if request.method == 'POST' and form_data.has_key('sketch') and form_data.has_key('model'):
        try:
            model = form_data['model']

            #imageData = b64decode(form_data['sketch'].split(',')[1])
            imageData =  b64decode(form_data['image'].split(',')[1])
            rc = form_data.getlist('rect[]')
            rc = [int(float(item)) for item in rc]
            rect = [min(rc[0], rc[2]), min(rc[1], rc[3]), abs(rc[0] - rc[2]), abs(rc[1] - rc[3])]
            
            #z = b64decode(form_data['z'])
            #c = b64decode(form_data['c'])

            image = Image.open(BytesIO(imageData))
            image_np = np.asarray(image, dtype="uint8")[:, :, :3]

            [seg_img, seg_mask, bbox] = api.get_segmentation(image_np, rect)
            #gen, z, c = api.generate_image(model, sketch, mask, z, c)

            return response2(image, seg_mask, seg_img)
        except Exception as e:
            print(e)
            return HttpResponse('{}')
    return HttpResponse('{}')


@csrf_exempt
def srand(request):
    form_data = request.POST
    if request.method == 'POST' and form_data.has_key('model'):
        try:
            model = form_data['model']
            image = Image.open("home/static/img/shenyang3.jpg")
            #image = api.get_stylization(image)
            return response(image)
        except Exception as e:
            print(e)
            return HttpResponse('{}')
    return HttpResponse('{}')
