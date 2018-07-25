# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt



import urllib
#[Atlantix]
from os.path import join as osj
from django.template import loader, Context
from django.views.decorators.csrf import csrf_exempt
import AIPainting.api as api
from IPython.core.debugger import Tracer 
from io import BytesIO
from PIL import Image
import numpy as np
from base64 import b64encode, b64decode
#import urllib2
#import thread

import socket
import sys
import os
import time
import random

#from ctypes import byref, cdll, c_int
#import ctypes
#lualib = ctypes.CDLL("/home/lljbash/torch/install/lib/libluajit.so", mode=ctypes.RTLD_GLOBAL)
#import app

reqid=0

### Set this for interctive image edit debugging
DEBUG_EDIT = True

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

def response_submit(image, inp_image, inp_style_image, mask, seg_img, seg_style_img, rect):
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
            "st_x": "%d", "st_y": "%d", \
            "raw_img":"data:image/png;base64,%s", \
            "inp_img":"data:image/png;base64,%s",\
            "inp_style":"data:image/png;base64,%s",\
            "mask":"data:image/png;base64,%s", \
            "fused_image":"data:image/png;base64,%s", \
            "seg_img":"data:image/png;base64,%s", \
            "seg_style_img":"data:image/png;base64,%s"}' % (
        image.size[0], image.size[1],
        rect[0], rect[1],
        imageString, imageInpaintString, imageInpStylizedString,
        maskString, fusedString,
        segimgString, segstyleString)

    return HttpResponse(json)

def homepage(request):
    #myapp = app.GlamorousApp()
    #myapp.initialize('/home/lljbash/data')
    content = request.GET.get("content")
    style = request.GET.get("style")
    adj = request.GET.get("adj")

    if(content == None):
        if DEBUG_EDIT:
            return HttpResponseRedirect("/consequence?content=%s&style=%s&adj=%s&image=%s&video=%s"%("req_0.jpg", "4", "sorrowful", 'req_0.jpg', 'req_0.mp4'))
        else:
            return render_to_response("AIPainting.html")
    else:
        global reqid
        (id,reqid)=(reqid+1,reqid+1)

        content = str(content)
        style = int(str(style))
        print(content, style, adj)
        
        portno = random.randint(23000, 23111)
        
        if not DEBUG_EDIT:
            os.system('./testapp %s %d %s %s' % (content,style,adj,'req_'+str(id)))
        '''def call_server():
            os.system('./server %d /mnt/share/ky/image_data' % portno)
        thread.start_new_thread(call_server, ())
        time.sleep(10)
        
        #ret = myapp.transfer(content, int(style))

        # Create a TCP/IP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect the socket to the port where the server is listening
        server_address = ('localhost', portno)
        print >>sys.stderr, 'connecting to %s port %s' % server_address
        sock.connect(server_address)
        ret = ''
        try:
            # Send data
            message = '%d%s#%s' % (style, content, adj)
            print >>sys.stderr, 'sending "%s"' % message
            sock.sendall(message)
            # Look for the response
            data = sock.recv(256)
            print >>sys.stderr, 'received "%s"' % data
            ret = data.strip('\0')
        finally:
            print >>sys.stderr, 'closing socket'
            sock.close()
        
        filename = ret.split('&')
        os.popen("ffmpeg -i '{input}' -ac 2 -b:v 2000k -c:a aac -c:v libx264 -b:a 160k -vprofile high -bf 0 -strict experimental -f mp4 '{output}.mp4'".format(input = filename[1], output = filename[1].split('.')[0]))'''

        return HttpResponseRedirect("/consequence?content=%s&style=%s&adj=%s&image=%s&video=%s"%(content, style, adj, 'req_'+str(id)+'.jpg', 'req_'+str(id)+'.mp4'))

def consequence(request):
    if request.method == "GET":
        content = request.GET.get("content")
        style = request.GET.get("style")
        adj = request.GET.get("adj")
        content = str(content)
        style = int(str(style))
        adj = str(adj)
        stylelist = ['Abstract painting','Post-impression','Neo-impression','Chinese ink painting','Suprematism','Impressionism']
        order = int(style) - 1
        
        print(request.GET.get("image"), type(request.GET.get("image")))

        #[Atlantix]
        image = osj('static', request.GET.get("image"))
        video = osj('static', request.GET.get("video"))
        #image = 'static/' + request.GET.get("image").decode('utf-8')
        #video = 'static/' + request.GET.get("video").decode('utf-8')
        
        return render_to_response("Paintcons.html", {
            'content':content, 'style':stylelist[order], 'adj':adj,
            'image':image, 'video':video
            })
            
@csrf_exempt
def edit(request):
    if request.method == "POST":
        form_data = request.POST
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
                n1 = style_image_np[bbox[1]:bbox[1]+bbox[3], bbox[0]:bbox[0] + bbox[2], :]
                n2 = np.asarray(seg_img, dtype="uint8")[:, :, 3:]

                img_np_ = np.concatenate([n1, n2], axis=2)
                seg_style_img = Image.fromarray(img_np_)
            else:
                seg_style_img = inp_style_img
            return response_submit(image, inp_img, inp_style_img,
                                seg_mask, seg_img, seg_style_img,
                                bbox)
        except Exception as e:
            print(e)
            return HttpResponse('{}')
    return HttpResponse('{}')

