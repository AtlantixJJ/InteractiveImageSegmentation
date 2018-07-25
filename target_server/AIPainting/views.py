# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt



import urllib
#[Atlantix]
import skimage.io
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

def homepage(request):
    #myapp = app.GlamorousApp()
    #myapp.initialize('/home/lljbash/data')
    description = request.GET.get("description")
    style = request.GET.get("style")
    adj = request.GET.get("adj")

    if(description == None):
        if DEBUG_EDIT:
            return HttpResponseRedirect("/consequence?description=%s&content=%s&style=%s&adj=%s&image=%s&video=%s" % ("plane", "req_0_content.jpg", "4", "sorrowful", 'req_0_style.jpg', 'req_0_draw.mp4'))
        else:
            return render_to_response("AIPainting.html")
    else:
        global reqid
        (id,reqid)=(reqid+1,reqid+1)

        description = str(description)
        style = int(str(style))
        print(description, style, adj)
        
        portno = random.randint(23000, 23111)
        
        if not DEBUG_EDIT:
            os.system('./testapp %s %d %s %s' % (description, style, adj, 'req_'+str(id)))
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

        return HttpResponseRedirect("/consequence?description=%s&content=%s&style=%s&adj=%s&image=%s&video=%s"%(description, 'req_%d_content.jpg' % id, style, adj, 'req_%d_style.jpg' % id, 'req_%d_draw.mp4' % id))

def consequence(request):
    if request.method == "GET":
        description = str(request.GET.get("description"))
        content     = str(request.GET.get("content")    )
        style       = str(request.GET.get("style")      )
        adj         = str(request.GET.get("adj")        )
        style = int(style)
        
        stylelist = ['Abstract painting','Post-impression','Neo-impression','Chinese ink painting','Suprematism','Impressionism']
        order = int(style) - 1
        
        print(request.GET.get("image"), type(request.GET.get("image")))

        #[Atlantix]
        image = osj('static', request.GET.get("image"))
        video = osj('static', request.GET.get("video"))
        #image = 'static/' + request.GET.get("image").decode('utf-8')
        #video = 'static/' + request.GET.get("video").decode('utf-8')
        
        return render_to_response("Paintcons.html", {
            'description': description,
            'style':stylelist[order], 'adj':adj,
            'image_name': request.GET.get("image"),
            'video_name': request.GET.get("video"),
            'content':content, 'image':image, 'video':video
            })
            
@csrf_exempt
def edit(request):
    if request.method == "GET":
        form_data = request.GET

        description = str(form_data.getlist("description")[0])
        content     = str(form_data.getlist("content")    [0])
        style       = str(form_data.getlist("style")      [0])
        adj         = str(form_data.getlist("adj")        [0])
        image       = str(form_data.getlist("image")      [0])
        video       = str(form_data.getlist("video")      [0])

        ind = content.find("_", 4)
        cur_id = int(content[4:ind])

        rc = form_data.getlist('rect[]')
        rc = [int(float(item)) for item in rc]
        rect = [min(rc[0], rc[2]), min(rc[1], rc[3]), abs(rc[0] - rc[2]), abs(rc[1] - rc[3])]
        #rect = [rect[1], rect[0], rect[3], rect[2]]

        content_image = Image.open(osj("static", content))
        print(content_image.size, rect)

        shape = (content_image.size[0] // 4 * 4, content_image.size[1] // 4  * 4)
        content_image = content_image.resize(shape)
        style_image = Image.open(osj("static", image))
        content_image_np = np.asarray(content_image, dtype="uint8")[:, :, :3]
        style_image_np = np.asarray(style_image, dtype="uint8")[:, :, :3]

        # segment image; inpainted image; segmentation mask; bounding box
        [seg_img, inp_img, seg_mask, bbox] = api.get_segmentation(content_image_np, rect)
        inp_style_img = api.get_stylization(inp_img)
        
        print(seg_img.size, inp_img.size, seg_mask.size, inp_style_img.size, bbox)
        
        if bbox is not None:
            #img_np_ = np.asarray(inp_style_img, dtype="uint8")[:, :, :3]
            n1 = style_image_np[bbox[1]:bbox[1]+bbox[3], bbox[0]:bbox[0] + bbox[2], :]
            n2 = np.asarray(seg_img, dtype="uint8")[:, :, 3:]

            img_np_ = np.concatenate([n1, n2], axis=2)
            seg_style_img = Image.fromarray(img_np_)
        else:
            seg_style_img = inp_style_img
            return HttpResponse('{"ok":"0"}')
        
        fused_img = Image.composite(inp_style_img.point(lambda x:x*1.5), inp_style_img.point(lambda x:x/2), seg_mask)

        inp_img.save(open(      osj("static", "req_%d_inpcontent.jpg" % cur_id), "wb"), format="JPEG")
        seg_mask.save(open(     osj("static", "req_%d_mask.png"       % cur_id), "wb"), format="PNG")
        inp_style_img.save(open(osj("static", "req_%d_inpstyle.jpg"   % cur_id), "wb"), format="JPEG")
        fused_img.save(open(    osj("static", "req_%d_fused.jpg"      % cur_id), "wb"), format="JPEG")
        seg_style_img.save(open(osj("static", "req_%d_segstyle.png"   % cur_id), "wb"), format="PNG")

        image = osj('static', form_data.getlist("image")[0])
        video = osj('static', form_data.getlist("video")[0])

        json = '{"description":"%s","style":"%s","adj":"%s","image_name":"%s","video_name":"%s","content":"%s","image":"%s","video":"%s","mask_image":"%s","inp_image":"%s","fused_image":"%s","seg_style":"%s","st_x":"%d","st_y":"%d","ok":"%d"}' % (
                description, style, adj,
                form_data.get("image"), form_data.get("video"),
                content, image, video,
                osj("static", "req_%d_mask.png"       % cur_id),
                osj("static", "req_%d_inpstyle.jpg"   % cur_id),
                osj("static", "req_%d_fused.jpg"      % cur_id),
                osj("static", "req_%d_segstyle.png"   % cur_id),
                bbox[1], bbox[0], 1
            )
        json = json.replace("\\", "\\\\")
        print(json)
        return HttpResponse(json)

    return HttpResponse('{}')
    

