'use strict';

var graph = null;

// preview, editing, finish
var ctrl_state = null;

// form data
var description = null,
    content     = null,
    image_name  = null,
    video_name  = null,
    adj_word    = null,
    style_word  = null;

var mouseOld = {};
var mouseDown = false;
var currentModel = 0;
var loading = false;
var style_image = null,
    img_h = null,
    img_w = null;

var drag_img = null,
    dragging = false,
    drag_over = false,
    resume_dragging = false;

var rect_st = {},
    rect_ed = {},
    drawing_rect = false;

var mask              = null,
    seg_st            = {},
    inp_image         = null,
    inp_style_image   = null,
    fused_image       = null,
    seg_img           = null,
    seg_style_img     = null;

var canvas_img        = null;
var jdata             = null;
var spinner = new Spinner({ color: '#999' });

var COLORS = [
  'black',
  'rgb(208, 2, 27)',
  'rgb(245, 166, 35)',
  'rgb(248, 231, 28)',
  'rgb(139, 87, 42)',
  'rgb(126, 211, 33)',
  'white',
  'rgb(226, 238, 244)',
  'rgb(226, 178, 213)',
  'rgb(189, 16, 224)',
  'rgb(74, 144, 226)',
  'rgb(80, 227, 194)',
];

var MODEL_NAMES = [
  'AI Painting',
  //'人脸草图',
  //'半身草图',
]

Date.prototype.format = function (format) {
  var o = {
    'M+': this.getMonth() + 1, //month
    'd+': this.getDate(), //day
    'h+': this.getHours(), //hour
    'm+': this.getMinutes(), //minute
    's+': this.getSeconds(), //second
    'q+': Math.floor((this.getMonth() + 3) / 3), //quarter
    S: this.getMilliseconds() //millisecond
  };
  if (/(y+)/.test(format)) format = format.replace(RegExp.$1, (this.getFullYear() + '').substr(4 - RegExp.$1.length));
  for (var k in o) {
    if (new RegExp('(' + k + ')').test(format)) format = format.replace(RegExp.$1, RegExp.$1.length == 1 ? o[k] : ('00' + o[k]).substr(('' + o[k]).length));
  }return format;
};

var MAX_LINE_WIDTH = 10;

function drawRect(x1, y1, x2, y2) {
  if (!image) return;
  graph.clear();
  graph.drawRect(x1, y1, x2, y2);
}

function drawPath(x1, y1, x2, y2) {
  if (!image) return;
  graph.drawLine(x1, y1, x2, y2);
}


function getMouse(event) {
  var rect = event.target.getBoundingClientRect();
  var mouse = {
    x: (event.touches && event.touches[0] || event).clientX - rect.left,
    y: (event.touches && event.touches[0] || event).clientY - rect.top
  };
  if (mouse.x > rect.width || mouse.x < 0 || mouse.y > rect.height || mouse.y < 0) return null;
  return mouse;
}

function onMouseDown(event) {
  if (event.button == 2 || loading) {
    mouseDown = false;
    return;
  }
  if (mouseDown) {
    onMouseUp(event);
    return;
  }
  mouseOld = getMouse(event);
  if (mouseOld != null) {
    mouseDown = true;
    if (ctrl_state == "editing" && !graph.has_result) {
      drawing_rect = true;
      rect_st = mouseOld;
    }
    if (graph.has_result) {
      dragging = true;
    }
  }
}

function onMouseUp(event) {
  var mouse = getMouse(event);
  if (drawing_rect && mouse)
    rect_ed = mouse;
  mouseDown = false;
  drawing_rect = false;
}

function onMouseMove(event) {
  event.preventDefault();

  if (mouseDown && !loading) {
    var mouse = getMouse(event);
    if (mouse == null) {
      mouseDown = false;
      return;
    }
    if (drawing_rect) {
      rect_ed = mouse;
      drawRect(rect_st.x, rect_st.y, mouse.x, mouse.y);
    }

    if (dragging) {
      if (canvas_img != "inp_style_image") {
        canvas_img = "inp_style_image";
        $('#canvas').css('background-image', 'url(' + inp_style_image + ')');
      }
      graph.clear();
      graph.drawImage(drag_img, mouse.x - drag_img.width / 2, mouse.y - drag_img.height / 2);
    }
    //drawShape(mouseOld.x, mouseOld.y, mouse.x, mouse.y);
    mouseOld = mouse;
  }
}

function image_from_static_url(url) {
  var img = new Image();
  img.src = url;
  return img;
}

function setImage(data) {
  setLoading(false);

  if (!data) {
    graph.has_result = false;
    dragging = false;
    resume_dragging = false;
    return false;
  }
  jdata = JSON.parse(data);
  if (jdata.ok != 1) {
    graph.has_result = false;
    dragging = false;
    resume_dragging = false;
    return false;
  }
  mask            = image_from_static_url(jdata.mask_image);
  inp_style_image = image_from_static_url(jdata.inp_image);
  fused_image     = image_from_static_url(jdata.fused_image);
  seg_style_img   = image_from_static_url(jdata.seg_style);

  if (fused_image) {
    $('#image').attr('src', fused_image.src);
    $('#canvas').css('background-image', 'url(' + fused_image.src + ')');
    canvas_img = 'fused_image';
  }

  if (seg_style_img) {
    drag_img = seg_style_img;
    var ratio = get_ratio();
    seg_st.x = Math.floor(jdata.st_x / ratio);
    seg_st.y = Math.floor(jdata.st_y / ratio);
    graph.drawImage(drag_img, seg_st.x, seg_st.y);
  }

  $('#image').attr('height', img_h);
  $('#image').attr('width', img_w);

  $('#canvas').attr('height', img_h);
  $('#canvas').attr('width', img_w);
  spinner.spin();
}

function setLoading(isLoading) {
  loading = isLoading;
  $('#srand').prop('disabled', loading);
  $('#submit').prop('disabled', loading);
  $('#spin').prop('hidden', !loading);
  if (loading) {
    $('.image').css('opacity', 0.7);
    spinner.spin(document.getElementById('spin'));
  } else {
    $('.image').css('opacity', 1);
    spinner.stop();
  }
}

function onClear() {
  graph.clear();
  ctrl_state = "editing";
  dragging = false;
  drawing_rect = false;
  graph.has_result = false;
}

function onSubmit() {
  if (graph && !loading) {
    setLoading(true);
    var ratio = get_ratio();
    var rect = [
      Math.floor(rect_st.x * ratio),
      Math.floor(rect_st.y * ratio),
      Math.floor(rect_ed.x * ratio),
      Math.floor(rect_ed.y * ratio)]
    var formData = {
      description: description,
      content: content,
      style: style_word,
      adj: adj_word,
      image: image_name,
      video: video_name,
      rect: rect
    };
    $.get("edit", formData, setImage);
    graph.has_result = true;
    dragging = false;
    resume_dragging = true;
  }
}

function init() {
  COLORS.forEach(function (color) {
    $('#color-menu').append(
      '\n<li role="presentation">\n  <div onclick="setColor(\'' +
      color +
      '\')"\n  >\n    <div class="color-block" style="background-color:' +
      color + ';border:' +
      (color == 'white' ? 'solid 1px rgba(0, 0, 0, 0.2)' : 'none') +
      '"/>\n  </div>\n</li>');
  });

  MODEL_NAMES.forEach(function (model, idx) {
    $('#model-menu').append(
      '<li role="presentation">\n' +
      '  <div class="dropdown-item model-item" onclick="setModel(' + idx + ')">' +
      model +
      '  </div>\n' +
      '</li>\n'
    );
  });

  description = document.getElementById('description').textContent;
  content     = document.getElementById('content').textContent;
  image_name  = document.getElementById('image-name').textContent;
  video_name  = document.getElementById('video-name').textContent;
  adj_word    = document.getElementById('adj-word').textContent;
  style_word  = document.getElementById('style-word').textContent;
  var img = document.getElementById('image');
  style_image = img;
  img_h = img.height;
  img_w = img.width;
  $('image').prop("hidden", true);
  $('#canvas').css('background-image', 'url(' + style_image.src + ')');
  canvas_img = 'style_image';
  $('#canvas').attr('height', img_h);
  $('#canvas').attr('width', img_w);
  $("#edit-btn").prop("hidden", false);
  ctrl_state = "preview";
}

function onEdit() {
  console.log("in start edit");
  if (ctrl_state == "preview") {
    $("#down-image-href").prop("hidden", true);
    $("#view-image-href").prop("hidden", true);
    $("#indicator").prop("hidden", false);
    $("#clear-btn").prop("hidden", false);
    document.getElementById("indicator").textContent = "Draw a box";
    document.getElementById("edit-btn").textContent = "Submit";
    $("#edit-btn").hide().show(0);
    ctrl_state = "editing";
  } else if (ctrl_state == "editing") {
    onSubmit();
    ctrl_state = "finish";
  }
}

$(document).ready(function () {
  graph = new Graph(document);
  init();

  var canvas = document.getElementById('canvas');
  canvas.addEventListener('mousedown', onMouseDown, false);
  canvas.addEventListener('mouseup', onMouseUp, false);
  canvas.addEventListener('mousemove', onMouseMove, false);
  canvas.addEventListener('mouseout', onMouseUp, false);
  canvas.addEventListener('touchstart', onMouseDown, false);
  canvas.addEventListener('touchend', onMouseUp, false);
  canvas.addEventListener('touchmove', onMouseMove, false);
  canvas.addEventListener('touchcancel', onMouseUp, false);

  $('#edit-btn').click(onEdit);
  $('#clear-btn').click(onClear);
});
