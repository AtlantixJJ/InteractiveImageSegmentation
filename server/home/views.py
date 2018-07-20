# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from os.path import join as osj
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

WINDOWS = True

def get_png_str(image):
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    imageString = b64encode(buffered.getvalue())
    if WINDOWS:
        return str(imageString)[2:-1]
    else:
        return str(imageString)

def response(image):
    s = get_png_str(image)
    json = '{"ok":"true", "img_h":"%d", "img_w":"%d", \
            "raw_img":"data:image/png;base64,%s"}' % (
        image.size[0], image.size[1], s)
    return HttpResponse(json)

def response_srand(image, style_image):
    imageString = get_png_str(image)
    styleString = get_png_str(style_image)
    json = '{"ok":"true", "img_h":"%d", "img_w":"%d", \
            "raw_img":"data:image/png;base64,%s",\
            "style_img":"data:image/png;base64,%s"}' % (
        image.size[0], image.size[1], imageString, styleString)
    return HttpResponse(json)

def response_submit(image, inp_image, inp_style_image, mask, seg_img, seg_style_img):
    imageString = get_png_str(image)
    imageInpaintString = get_png_str(inp_image)
    imageInpStylizedString = get_png_str(inp_style_image)
    maskString = get_png_str(mask)
    #fused_image = Image.composite(image.point(lambda x:x*1.5), image.point(lambda x:x/2), mask)
    fused_image = Image.composite(inp_style_image.point(lambda x:x*1.5), inp_style_image.point(lambda x:x/2), mask)
    fusedString = get_png_str(fused_image)
    segimgString = get_png_str(seg_img)
    segstyleString = get_png_str(seg_style_img)

    json = '{"ok":"true", "img_h":"%d", "img_w":"%d", \
            "raw_img":"data:image/png;base64,%s", \
            "inp_img":"data:image/png;base64,%s",\
            "inp_style":"data:image/png;base64,%s",\
            "mask":"data:image/png;base64,%s", \
            "fused_image":"data:image/png;base64,%s", \
            "seg_img":"data:image/png;base64,%s", \
            "seg_style_img":"data:image/png;base64,%s"}' % (
        image.size[0], image.size[1],
        imageString, imageInpaintString, imageInpStylizedString,
        maskString, fusedString,
        segimgString, segstyleString)

    return HttpResponse(json)

def index(request):
    return render(request, 'index.html')
    # return HttpResponse(index_temp.render())


@csrf_exempt
def input_image(request):
    form_data = request.POST
    if request.method == 'POST':
        try:
            #imageData = b64decode(form_data['sketch'].split(',')[1])
            imageData =  b64decode(form_data['image'].split(',')[1])
            styleImageData = b64decode(form_data['style_image'].split(',')[1])
            rc = form_data.getlist('rect[]')
            rc = [int(float(item)) for item in rc]
            rect = [min(rc[0], rc[2]), min(rc[1], rc[3]), abs(rc[0] - rc[2]), abs(rc[1] - rc[3])]

            image = Image.open(BytesIO(imageData))
            image_np = np.asarray(image, dtype="uint8")[:, :, :3]
            style_image = Image.open(BytesIO(styleImageData))
            style_image_np = np.asarray(style_image, dtype="uint8")[:, :, :3]

            # segment image; inpainted image; segmentation mask; bounding box
            [seg_img, inp_img, seg_mask, bbox] = api.get_segmentation(image_np, rect)
            inp_style_img = api.get_stylization(inp_img)
            if bbox is not None:
                #img_np_ = np.asarray(inp_style_img, dtype="uint8")[:, :, :3]
                img_np_ = style_image_np[bbox[1]:bbox[1]+bbox[3], bbox[0]:bbox[0] + bbox[2], :]
                seg_style_img = Image.fromarray(img_np_)
            else:
                seg_style_img = inp_style_img
            return response_submit(image, inp_img, inp_style_img, seg_mask, seg_img, seg_style_img)
        except Exception as e:
            print(e)
            return HttpResponse('{}')
    return HttpResponse('{}')


@csrf_exempt
def srand(request):
    form_data = request.POST
    print(form_data)
    if request.method == 'POST':
        try:
            image = Image.open(osj("home", "static", "img", "shenyang3.jpg"))
            shape = (image.size[0] // 4 * 4, image.size[1] // 4  * 4)
            image = image.resize(shape)
            style_image = api.get_stylization(image)
            return response_srand(image, style_image)
        except Exception as e:
            print(e)
            return HttpResponse('{}')
    return HttpResponse('{}')
