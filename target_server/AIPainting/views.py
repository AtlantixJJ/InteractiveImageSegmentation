from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt
from PIL import Image

import urllib
import urllib2

import socket
import sys
import os
import thread
import time
import random

#from ctypes import byref, cdll, c_int
#import ctypes
#lualib = ctypes.CDLL("/home/lljbash/torch/install/lib/libluajit.so", mode=ctypes.RTLD_GLOBAL)
#import app

reqid=0

def homepage(request):
    #myapp = app.GlamorousApp()
    #myapp.initialize('/home/lljbash/data')
    content = request.GET.get("content")
    style = request.GET.get("style")
    adj = request.GET.get("adj")

    if(content == None):
        return render_to_response("AIPainting.html")
    else:
        global reqid
        (id,reqid)=(reqid+1,reqid+1)
				
        content = str(content)
        style = int(str(style))
        print(content, style, adj)
        
        portno = random.randint(23000, 23111)
        
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
    content = request.GET.get("content")
    style = request.GET.get("style")
    adj = request.GET.get("adj")
    content = str(content)
    style = int(str(style))
    adj = str(adj)
    stylelist = ['Abstract painting','Post-impression','Neo-impression','Chinese ink painting','Suprematism','Impressionism']
    order = int(style) - 1
    
    image = 'static/' + request.GET.get("image").decode('utf-8')
    video = 'static/' + request.GET.get("video").decode('utf-8')
    
    return render_to_response("Paintcons.html", {'content':content, 'style':stylelist[order], 'adj':adj, 'image':image, 'video':video})

