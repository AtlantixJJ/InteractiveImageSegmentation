'use strict';

var video_width = null,
    video_height = null,
    original_width = null,
    original_height = null,
    im_ratio = null;

var video = null,
    played = false;

function record_size(height, width, resize_ratio) {
    if (im_ratio) return false;
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
    video = document.getElementById("vivideo");
    video.width = video_width;
    video.height = video_height;
    video.hidden = false;
    video.play();
    document.getElementById("image").hidden = true;
    document.getElementById("canvas").hidden = true;
    
    ctrl_state = "finish";
    video.onended = function() {
        console.log('video on end');
        ctrl_state = "preview";
        document.getElementById("canvas").hidden = false;
        document.getElementById("vivideo").hidden = true;
        document.getElementById("edit-btn").hidden = false;
        document.getElementById("down-image-href").hidden = false;
        $('#canvas').css('background-image', 'url(' + document.getElementById("image").src + ')');
        $('#canvas').css('background-size', video_width + 'px ' + video_height + 'px');
        canvas_img = 'style_image';
        $('#canvas').attr('height', video_height);
        $('#canvas').attr('width', video_width);
    };
}

function cvd(){
    if (!played) {
        play_video();
        played = true;
    }
}