'use strict';

var video_width = null,
    video_height = null,
    original_width = null,
    original_height = null,
    im_ratio = 1.0;

var video = null;

function record_size(height, width, resize_ratio) {
    original_width = width;
    original_height = height;
    im_ratio = resize_ratio;
}

function get_ratio() {return im_ratio;}

function play_video() {
    video_width = document.getElementById("image").width;
    video_height = document.getElementById("image").height;
    document.getElementById("edit-btn").hidden = true;
    //document.getElementById("back-href").hidden = true;
    document.getElementById("vivideo").width = video_width;
    document.getElementById("vivideo").height = video_height;
    document.getElementById("vivideo").hidden = false;
    document.getElementById("image").hidden = true;
    document.getElementById("canvas").hidden = true;
    video = document.getElementById("vivideo");
    video.onended = function() {
        document.getElementById("canvas").hidden = false;
        document.getElementById("vivideo").hidden = true;
        document.getElementById("edit-btn").hidden = false;
        $('#canvas').css('background-image', 'url(' + document.getElementById("image").src + ')');
        $('#canvas').css('background-size', video_width + 'px ' + video_height + 'px');
        canvas_img = 'style_image';
        $('#canvas').attr('height', video_height);
        $('#canvas').attr('width', video_width);
    };
}

function cvd(){
    play_video();
}