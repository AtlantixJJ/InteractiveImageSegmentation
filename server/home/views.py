# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.template import loader, Context
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import home.api as api
from io import BytesIO
from PIL import Image
from base64 import b64encode, b64decode

index_temp = loader.get_template("index.html")


def response(image):
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    imageString = b64encode(buffered.getvalue())
    json = '{"ok":"true", "img_h":%d, "img_w":%d, "img":"data:image/png;base64,%s"}' % (
        image.size[0], image.size[1], imageString)
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
            if not api.model_exist(model):
                return HttpResponse('{}')

            imageData = b64decode(form_data['sketch'].split(',')[1])
            z = b64decode(form_data['z'])
            c = b64decode(form_data['c'])

            image = Image.open(BytesIO(imageData))
            [sketch, mask] = api.get_array(model, image)
            gen, z, c = api.generate_image(model, sketch, mask, z, c)

            return response(gen, z, c)
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
            image = Image.open("home/static/img/shenyang.jpg")
            return response(image)
        except Exception as e:
            print(e)
            return HttpResponse('{}')
    return HttpResponse('{}')
