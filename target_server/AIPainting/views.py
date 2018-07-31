# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt



import urllib
#[Atlantix]
from base64 import b64encode, b64decode
import skimage.io
from os.path import join as osj
from PIL.Image import fromarray
from django.template import loader, Context
from django.views.decorators.csrf import csrf_exempt
import AIPainting.api as api
from IPython.core.debugger import Tracer 
from io import BytesIO
from PIL import Image
import numpy as np
from base64 import b64encode, b64decode
import time
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
STATIC_DIR = "."
### Set this for interctive image edit debugging
"""
import platform
if platform.system() == "Linux":
    DEBUG_EDIT = False
else:
    DEBUG_EDIT = True
"""
DEBUG_EDIT = False

def now_milliseconds():
   return int(time.time() * 1000)

def homepage(request):
    #myapp = app.GlamorousApp()
    #myapp.initialize('/home/lljbash/data')
    description = request.GET.get("description")
    style = request.GET.get("style")
    adj = request.GET.get("adj")

    if(description == None):
        if DEBUG_EDIT:
            inp_img = Image.open("req_0_content.jpg")
            inp_style_img = api.get_stylization(inp_img)
            inp_style_img.save(open(osj(STATIC_DIR, "req_0_style.jpg"), "wb"), format="JPEG")
            return HttpResponseRedirect("/consequence?description=%s&content=%s&style=%s&adj=%s&image=%s&video=%s" % ("plane", "req_0_content.jpg", "4", "sorrowful", 'req_0_style.jpg', 'req_0-oilpaint_video.mp4'))
        else:
            return render_to_response("AIPainting.html")
    else:
        global reqid
        id, reqid = reqid+1, reqid+1

        description = "\'" + str(description) + "\'"
        style = int(str(style))
        print(description, style, adj)

        portno = random.randint(23000, 23111)
        
        if not DEBUG_EDIT:
            os.system('./testapp %s %d %s %s' % (description, style, adj, 'req_'+str(id)))
            cmd = "/usr/bin/ffmpeg -i %s -ac 2 -b:v 2000k -c:a aac -c:v libx264 -b:a 160k -vprofile high -bf 0 -strict experimental -f mp4 -y %s &" % ('req_%d-oilpaint_video.avi' % id, 'req_%d-oilpaint_video.mp4' % id)
            os.system(cmd)
            print(cmd)
            #print("________________")
            #os.system("which ffmpeg")
            content_image = Image.open("req_%d-google.jpg" % id)
            style_image = Image.open("req_%d.jpg" % id)
            os.system("cp req_%d.jpg req_%d_style.jpg" % (id, id))
            content_image.resize(style_image.size).save("req_%d_content.jpg" % id)

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

        video_name = 'req_%d-oilpaint_video.mp4' % (id)

        return HttpResponseRedirect("/consequence?description=%s&content=%s&style=%s&adj=%s&image=%s&video=%s"%(description, 'req_%d_content.jpg' % id, style, adj, 'req_%d_style.jpg' % id, video_name))

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

def get_style_id(style):
    stylelist = ['Abstract painting','Post-impression','Neo-impression','Chinese ink painting','Suprematism','Impressionism']
    for i in range(len(stylelist)):
        if stylelist[i] == style:
            return i
    return 0

@csrf_exempt
def edit_done(request):
    if request.method == "GET":
        form_data = request.GET
        description = str(form_data.getlist("description")[0])
        content     = str(form_data.getlist("content")    [0])
        style       = str(form_data.getlist("style")      [0])
        adj         = str(form_data.getlist("adj")        [0])
        image       = str(form_data.getlist("image")      [0])
        video       = str(form_data.getlist("video")      [0])
        seg_st      =     form_data.getlist("seg_st[]")
        seg_st = [int(item) for item in seg_st]

        style_id = get_style_id(style)
        
        rc = form_data.getlist('rect[]')
        rc = [int(float(item)) for item in rc]
        rect = [min(rc[0], rc[2]), min(rc[1], rc[3]), abs(rc[0] - rc[2]), abs(rc[1] - rc[3])]
        #rect = [rect[1], rect[0], rect[3], rect[2]]

        ind = content.find("_", 4)
        cur_id = int(content[4:ind])

        inp_content_image = Image.open(osj(STATIC_DIR, "req_%d_inpcontent.jpg" % cur_id)).convert("RGBA")
        s = [inp_content_image.size[1], inp_content_image.size[0]]
        inp_content_image_np = np.asarray(inp_content_image)
        seg_mask_np = np.ones((s[0], s[1], 4), dtype="uint8")

        seg_image = Image.open(osj(STATIC_DIR, "req_%d_seg.png" % cur_id))
        seg_image_np = np.asarray(seg_image, dtype="uint8")
        bg_x, ed_x = seg_st[1], seg_st[1] + seg_image_np.shape[0]
        bg_y, ed_y = seg_st[0], seg_st[0] + seg_image_np.shape[1]

        content_image = Image.open(osj(STATIC_DIR, "req_%d_content.jpg" % cur_id))
        content_image_np=np.asarray(content_image)

        mask = Image.open(osj(STATIC_DIR, "req_%d_mask.png" % cur_id))
        mask_np = np.asarray(mask).copy()
    
        if ed_x > seg_mask_np.shape[0]:
            ed_x = seg_mask_np.shape[0]
        if ed_y > seg_mask_np.shape[1]:
            ed_y = seg_mask_np.shape[1]
        stc_x = stc_y = 0
        if bg_x < 0:
            stc_x = -bg_x
            bg_x = 0
        if bg_y < 0:
            stc_y = - bg_y
            bg_y = 0
        len_x = ed_x - bg_x
        len_y = ed_y - bg_y
        print(bg_x, ed_x, bg_y, ed_y)

        seg_mask_np[bg_x:ed_x, bg_y:ed_y] = seg_image_np[stc_x:len_x, stc_y:len_y]
        seg_mask = fromarray(seg_mask_np)
        fused_content_image = Image.alpha_composite(inp_content_image, seg_mask).convert("RGB")

        #newmask = np.zeros_like(mask_np)
        #newmask[rect[0]+stc_x:rect[0]+stc_x+len_x, rect[1]+stc_y:rect[1]+stc_y+len_y].fill(1)
        #mask_np *= newmask
        #fromarray(mask_np).save(open(osj(STATIC_DIR, "req_%d_testmask.png" % cur_id), "wb"))
        #fused_content_image = api.seamlessClone(
        #    content_image_np, mask_np,
        #    content_image_np, (bg_x, bg_y))

        ### [MERGE] change this to ordinary stylization, with video generation
        if DEBUG_EDIT:
            fused_style_image = api.get_stylization(fused_content_image)
        else:
            file_name = osj(STATIC_DIR, "req_%d_content.jpg" % cur_id)
            fused_content_image.save(open(file_name, "wb"), format="JPEG")
            os.system('./testapp %s %d %s %s' % (file_name, style_id, adj, 'req_'+str(cur_id)))
            cmd = "/usr/bin/ffmpeg -i %s -ac 2 -b:v 2000k -c:a aac -c:v libx264 -b:a 160k -vprofile high -bf 0 -strict experimental -f mp4 -y %s &" % ('req_%d-oilpaint_video.avi' % cur_id, 'req_%d-oilpaint_video.mp4' % cur_id)
            os.system(cmd)
            print(cmd)
            fused_style_image = Image.open("req_%d.jpg" % cur_id)
            #video = 'req_%d-oilpaint_video.mp4?%d' % (cur_id, now_milliseconds())
        ###

        fused_content_image.save(open(osj(STATIC_DIR, "req_%d_content.jpg" % cur_id), "wb"), format="JPEG")
        fused_style_image.save(open(  osj(STATIC_DIR, "req_%d_style.jpg" % cur_id), "wb"), format="JPEG")

        json = '{"description":"%s","style":"%s","adj":"%s","image_name":"%s","video_name":"%s","content":"%s","image":"%s","video":"%s","inp_image":"%s","ok":"%d"}' % (
                description, style, adj,
                form_data.get("image"), form_data.get("video"),
                content, image, video,
                osj(STATIC_DIR, "req_%d_style.jpg"   % cur_id),
                1)
        json = json.replace("\\", "\\\\")
        print(json)
        return HttpResponse(json)

@csrf_exempt
def edit(request):
    if request.method == "GET":
        form_data = request.GET
    elif request.method == "POST":
        form_data = request.POST

    try:
        description = str(form_data.getlist("description")[0])
        content     = str(form_data.getlist("content")    [0])
        style       = str(form_data.getlist("style")      [0])
        adj         = str(form_data.getlist("adj")        [0])
        image       = str(form_data.getlist("image")      [0])
        video       = str(form_data.getlist("video")      [0])
        
        style_id = get_style_id(style)

        print("=> Collect user sketch")
        try:
            sketch = b64decode(form_data['sketch'].split(',')[1])
        except Exception as e:
            sketch = None
            print("Sketch decode error")
            print(e)

        ind = content.find("_", 4)
        cur_id = int(content[4:ind])

        rc = form_data.getlist('rect[]')
        rc = [int(float(item)) for item in rc]
        rect = [min(rc[0], rc[2]), min(rc[1], rc[3]), abs(rc[0] - rc[2]), abs(rc[1] - rc[3])]
        #rect = [rect[1], rect[0], rect[3], rect[2]]

        content_image = Image.open(osj(STATIC_DIR, content))

        user_mask = None
        if sketch is not None:
            sketch = Image.open(BytesIO(sketch))
            sketch = sketch.resize(content_image.size)
            sketch_np = np.asarray(sketch, dtype="uint8")[:, :, :3]
            user_mask = np.zeros((sketch_np.shape[0], sketch_np.shape[1]), dtype="uint8")
            user_mask.fill(2)
            user_mask[sketch_np[:, :, 0] > 200] = 1
            user_mask[sketch_np[:, :, 2] > 90] = 0
            print(user_mask.max(), user_mask.min())
            fromarray(user_mask*127).save(open(osj(STATIC_DIR, "req_%d_userinput.png" % cur_id), "wb"))
            #fromarray(sketch_np[:, :, 0]).save(open(osj(STATIC_DIR, "req_%d_test.png" % cur_id), "wb"))

        shape = (content_image.size[0] // 4 * 4, content_image.size[1] // 4  * 4)
        content_image = content_image.resize(shape)
        style_image = Image.open(osj(STATIC_DIR, image))
        content_image_np = np.asarray(content_image, dtype="uint8")[:, :, :3]
        style_image_np = np.asarray(style_image, dtype="uint8")[:, :, :3]

        # segment image; inpainted image; segmentation mask; bounding box
        print("=> Do segmentation")
        [seg_img, inp_img, seg_mask, bbox] = api.get_segmentation(content_image_np, rect, user_mask)

        file_name = osj(STATIC_DIR, "req_%d_inpcontent.jpg" % cur_id)
        inp_img.save(open(      file_name, "wb"), format="JPEG")
        seg_img.save(open(      osj(STATIC_DIR, "req_%d_seg.png"        % cur_id), "wb"), format="PNG")
        seg_mask.save(open(     osj(STATIC_DIR, "req_%d_mask.png"       % cur_id), "wb"), format="PNG")

        if DEBUG_EDIT:
            inp_style_img = api.get_stylization(inp_img)
        else:
            os.system('./testapp %s %d %s %s' % (file_name, style_id, adj, 'req_fusedstyle_'+str(cur_id)))
            inp_style_img = Image.open("req_fusedstyle_%d.jpg" % cur_id)
        print("=> Content image size: ", content_image.size)
        print("=> User rect: ", rect)
        print("=> Segmentation done, size: ", seg_img.size)
        print(inp_img.size, seg_mask.size, inp_style_img.size, bbox)
        
        if bbox is not None:
            n1 = style_image_np[bbox[1]:bbox[1]+bbox[3], bbox[0]:bbox[0] + bbox[2], :]
            n2 = np.asarray(seg_img, dtype="uint8")[:, :, 3:]

            img_np_ = np.concatenate([n1, n2], axis=2)
            seg_style_img = Image.fromarray(img_np_)
        else:
            seg_style_img = inp_style_img
            return HttpResponse('{"ok":"0"}')
        
        fused_img = Image.composite(inp_style_img.point(lambda x:x*1.5), inp_style_img.point(lambda x:x/2), seg_mask)


        inp_style_img.save(open(osj(STATIC_DIR, "req_%d_inpstyle.jpg"   % cur_id), "wb"), format="JPEG")
        fused_img.save(open(    osj(STATIC_DIR, "req_%d_fused.jpg"      % cur_id), "wb"), format="JPEG")
        seg_style_img.save(open(osj(STATIC_DIR, "req_%d_segstyle.png"   % cur_id), "wb"), format="PNG")


        image = osj('static', form_data.getlist("image")[0])
        video = osj('static', form_data.getlist("video")[0])

        json = '{"description":"%s","style":"%s","adj":"%s","image_name":"%s","video_name":"%s","content":"%s","image":"%s","video":"%s","mask_image":"%s","inp_image":"%s","fused_image":"%s","seg_style":"%s","st_x":"%d","st_y":"%d","ok":"%d"}' % (
                description, style, adj,
                form_data.get("image"), form_data.get("video"),
                content, image, video,
                osj(STATIC_DIR, "req_%d_mask.png"       % cur_id),
                osj(STATIC_DIR, "req_%d_inpstyle.jpg"   % cur_id),
                osj(STATIC_DIR, "req_%d_fused.jpg"      % cur_id),
                osj(STATIC_DIR, "req_%d_segstyle.png"   % cur_id),
                bbox[1], bbox[0], 1
            )
        json = json.replace("\\", "\\\\")
        print(json)
        return HttpResponse(json)
    except Exception as e:
        print(e)
        return HttpResponse('{}')
    

