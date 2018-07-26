'use strict';

var video_width = null,
    video_height = null,
    original_width = null,
    original_height = null,
    im_ratio = 1.0;

function record_size(height, width, resize_ratio) {
    original_width = width;
    original_height = height;
    im_ratio = resize_ratio;
}

function get_ratio() {return im_ratio;}

function cvd(){
    video_width = document.getElementById("image").width;
    video_height = document.getElementById("image").height;
    /*
    document.getElementById("vivideo").width = wid;
    document.getElementById("vivideo").height = hei;
    document.getElementById("mypic").style.display = "none";
    */
}