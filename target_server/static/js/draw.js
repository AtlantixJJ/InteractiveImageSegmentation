'use strict';

var graph = null;

// preview, editing, finish
var ctrl_state = null;
var ratio = null;
var first_load = false;
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
// labeling
var label_type = "object",
    pixel_labeling = false,
    resume_labeling = false;

var rect_st = {},
    rect_ed = {},
    drawing_rect = false;

var mask              = null,
    seg_st            = {},
    inp_image         = null,
    inp_style_image   = null,
    fused_image       = null,
    seg_img           = null,
    seg_style_img     = null,
    image             = null;

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
    if (resume_labeling) {
      resume_labeling = false;
      pixel_labeling = true;
    }
  }
}

function onMouseUp(event) {
  var mouse = getMouse(event);
  if (drawing_rect && mouse) {
    console.log(rect_ed, mouse);
    //rect_ed = mouse;
  }
  if (pixel_labeling) {
    resume_labeling = true;
    pixel_labeling = false;
  }
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
    } else if (pixel_labeling) {
      drawPath(mouseOld.x, mouseOld.y, mouse.x, mouse.y);
    } else if (dragging) {
      if (canvas_img != "inp_style_image") {
        canvas_img = "inp_style_image";
        $('#refine-btn').prop('hidden', true);
        $('#type-selector').prop('hidden', true);
        $('#canvas').css('background-image', 'url(' + inp_style_image.src + ')');
        $('#image').attr('src', inp_style_image.src);
        $('#canvas').attr('height', img_h);
        $('#canvas').attr('width', img_w);
      }
      graph.clear();
      graph.drawImage(drag_img, mouse.x - drag_img.width / 2, mouse.y - drag_img.height / 2);
      seg_st.x = mouse.x - drag_img.width / 2;
      seg_st.y = mouse.y - drag_img.height / 2;
    }
    //drawShape(mouseOld.x, mouseOld.y, mouse.x, mouse.y);
    mouseOld = mouse;
  }
}

function image_from_static_url(url) {
  var img = new Image();
  img.src = "static/" + url + "?" + new Date().getTime();
  return img;
}

function set_state_finetuning() {
  //toastr.info("Orange line for object.\nGreen line for background.");
  //toastr.info("Please label part of object and background.", {timeOut: 5000});
  label_type = "object";
  //$("#indicator2").prop("hidden", false);
  $("#label-btn").prop("hidden", false);
  $("#submit-btn").prop("hidden", false);
  $("#edit-btn").prop("hidden", true);
  //document.getElementById('indicator').textContent = "Refine";
  //document.getElementById('label-btn').textContent = "Background";

  $('#refine-btn').prop('hidden', true);
  $('#submit-btn').prop('hidden', false);
  $('#type-selector').prop('hidden', false);
  var fore = document.getElementById('type-foreground');
  fore.checked = true;
  graph.setLineWidth(5);
  graph.setCurrentColor("#f0ad4e");

  ctrl_state = "finetuning";
  resume_labeling = true;
  pixel_labeling = false;
}

function set_state_dragging() {
  graph.has_result = true;
  dragging = true;
  resume_dragging = false;
  resume_labeling = false;
  pixel_labeling = false;
  ctrl_state = "finish";
  document.getElementById("edit-btn").textContent = "Dragging done";
  document.getElementById("edit-btn").hidden = false;
}

function set_state_boxing() {
  $("#down-image-href").prop("hidden", true);
  //$("#view-image-href").prop("hidden", true);
  $("#back-href").prop("hidden", false);
  //$("#indicator").prop("hidden", false);
  $("#cancel-btn").prop("hidden", false);
  //document.getElementById("indicator").textContent = "Draw a box";
  document.getElementById("edit-btn").hidden = true;
  document.getElementById("submit-btn").hidden = false;

  toastr.info('Draw a box to select an object');
  graph.setLineWidth(5);
  graph.setCurrentColor("#000000");
  ctrl_state = "editing";
}

function delayed_toaster(text, time) {
  setTimeout(function(){toastr.info(text)}, time);
}

/// The callback of image segmentation
function setSegmentationImage(data) {
  // close spinning
  setLoading(false);
  // check data
  var ok = false;
  if (data) {
    jdata = JSON.parse(data);
    if (jdata.ok == 1) ok = 1;
  }
  
  $('#refine-btn').prop('hidden', false);
  $('#cancel-btn').prop('hidden', false);
  
  if (!ok) {
    // line width and color
    toastr.info('Sorry, please refine the object by drawing simple lines.');
    set_state_finetuning();
    spinner.spin();
    return false;
  }

  toastr.info('You can drag the object to another place.', {timeOut: 10000});
  if (ctrl_state != 'finetuning')
    delayed_toaster('Or you can refine the object by drawing simple lines.', 5000);
  // read data
  seg_style_img = image_from_static_url(jdata.seg_style);
  seg_style_img.onload = function(event) {
    drag_img = seg_style_img;
    drag_img.width = Math.ceil(drag_img.width / ratio);
    drag_img.height = Math.ceil(drag_img.height / ratio);
    seg_st.x = Math.floor(jdata.st_y / ratio);
    seg_st.y = Math.floor(jdata.st_x / ratio);
    graph.drawImage(seg_style_img, seg_st.x, seg_st.y);
    graph.setLineWidth(5);
    graph.setCurrentColor("#f0ad4e");
  }
  mask            = image_from_static_url(jdata.mask_image);
  inp_style_image = image_from_static_url(jdata.inp_image);
  fused_image     = image_from_static_url(jdata.fused_image);
  fused_image.onload = function (event) {
    $('#image').attr('src', fused_image.src);
    $('#canvas').css('background-image', 'url(' + fused_image.src + ')');
    $('#canvas').attr('height', img_h);
    $('#canvas').attr('width', img_w);
    canvas_img = 'fused_image';
    // set flags to dragging
    set_state_dragging();

  }
  console.log(graph.ctx.lineWidth);
  // modify indicator
  // document.getElementById("indicator").textContent = "Drag around";
  // document.getElementById("edit-btn").textContent = "Done";
  spinner.spin();
}

function setFinalImage(data) {
  console.log("set final result");
  // close spinning
  setLoading(false);
  // check data
  var ok = false;
  if (data) {
    jdata = JSON.parse(data);
    if (jdata.ok == 1) ok = 1;
  }
  if (!ok) {
    spinner.spin();
    return false;
  }

  inp_image = image_from_static_url(jdata.inp_image);
  inp_image.onload = function (event) {
    style_image.src = inp_image.src;
    $('#image').attr('src', style_image.src);
    $('#canvas').css('background-image', 'url(' + style_image.src + ')');
    canvas_img = "style_image";
    $('#canvas').attr('height', img_h);
    $('#canvas').attr('width', img_w);
    graph.clear();
    ctrl_state = "preview";
  }

  //video.onloadstart = function() {play_video();};
  //video.src = "static/" + jdata.video + '?' + new Date().getTime();
  
  //console.log(video);

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
  console.log("On clear");
  graph.clear();

  $('#image').attr('src', style_image.src);
  $('#canvas').css('background-image', 'url(' + style_image.src + ')');
  canvas_img = "style_image";
  //$('#canvas').attr('height', img_h);
  //$('#canvas').attr('width', img_w);

  graph.setLineWidth(5);
  graph.setCurrentColor("#000000");

  //$("#down-image-href").prop("hidden", true);
  //$("#view-image-href").prop("hidden", true);
  //$("#indicator").prop("hidden", false);
  $("#cancel-btn").prop("hidden", false);
  set_state_boxing();
  ctrl_state = "editing";
  resume_labeling = true;
  pixel_labeling = false;
  dragging = false;
  drawing_rect = false;
  graph.has_result = false;
}

/// Submit to segmentation
function onSubmit() {
  $('#submit-btn').prop('hidden', true);
  $('#back-href').prop('hidden', true);
  $('#cancel-btn').prop('hidden', true);
  $('#type-selector').prop('hidden', true);
  toastr.info('Please wait for a few moments.');
  if (graph && !loading) {
    setLoading(true);
    console.log(ratio);
    var rect = [
      Math.floor(rect_st.x * ratio),
      Math.floor(rect_st.y * ratio),
      Math.floor(rect_ed.x * ratio),
      Math.floor(rect_ed.y * ratio)]
    var canvas_data = graph.getImageData();

    var formData = {
      description: description,
      content: content,
      style: style_word,
      adj: adj_word,
      image: image_name,
      video: video_name,
      rect: rect,
    };

    if (ctrl_state == "finetuning") {
      formData.sketch = canvas_data;
      $.post("edit", formData, setSegmentationImage);
    } else {
      formData.sketch = null;
      $.get("edit", formData, setSegmentationImage);
    }
  }
}

/// Refine object by drwing lines
function onRefine() {
  set_state_finetuning();
}

function onGetFinalResult() {
  if (graph && !loading) {
    setLoading(true);
    var pos = [
      Math.floor(seg_st.x * ratio),
      Math.floor(seg_st.y * ratio)]
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
      seg_st: pos,
      rect: rect
    };
    $.get("done", formData, setFinalImage);
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

  canvas_img = '';
  first_load = true;
  image = document.getElementById('image');
  $("#label-btn").prop("hidden", true);
  ctrl_state = "preview";

  style_image = new Image();
  style_image.src = image.src + "?" + new Date();

  style_image.onload = function () {
    console.log("style image onload");
    if (!first_load) return;
    console.log("style image load");
    first_load = false;
    if(this.width / this.height > 1161 / 708){
      record_size(this.height, this.width, this.width / 1161);
      this.height = this.height * 1161 / this.width;
      this.width = 1161;
      cvd();
    } else {
      record_size(this.height, this.width, this.height / 708);
      this.width = this.width * 708 / this.height;
      this.height = 708;
      cvd();
    }
    img_h = this.height;
    img_w = this.width;
    this.hidden = true;
    $('#canvas').css('background-image', 'url(' + style_image.src + ')');
    canvas_img = 'style_image';
    $('#canvas').attr('height', img_h);
    $('#canvas').attr('width', img_w);
    if (!ratio)
      ratio = get_ratio();
    //$('#edit-btn').prop('hidden', false);
  };

  if (canvas_img == '') {
    $('#canvas').css('background-image', 'url(' + style_image.src + ')');
    canvas_img = 'style_image';
    $('#canvas').attr('height', img_h);
    $('#canvas').attr('width', img_w);
    //$('#edit-btn').prop('hidden', false);
  }
}

function onEdit() {
  console.log("in start edit");
  if (ctrl_state == "preview") {
    set_state_boxing();
  } else if (ctrl_state == "editing") {
    ctrl_state = "finish";

    //onSubmit();
    //graph.setLineWidth(5);
    //graph.setCurrentColor("#D2691E");
    //document.getElementById('indicator2').textContent = "Foreground";
    //document.getElementById('label-btn').style.color = "#008B8B";
    //document.getElementById('indicator2').style.color = "#D2691E";
  } else if (ctrl_state == "finetuning") {
    //$("#indicator2").prop("hidden", true);
    $('#refine-btn').prop("hidden", true);
    $("#label-btn").prop("hidden", true);
    ctrl_state = "finish";
    resume_labeling = false;
    pixel_labeling = false;
  }
  
  if (ctrl_state == "finish") {
    onGetFinalResult();
    toastr.info('Please wait for a few moments.');
    graph.has_result = false;
    dragging = false;
    resume_dragging = false;
    canvas_img = "";

    $("#down-image-href").prop("hidden", false);
    //$("#view-image-href").prop("hidden", false);
    $("#refine-btn").prop("hidden", true);
    $("#cancel-btn").prop("hidden", true);
    $("#type-selector").prop("hidden", true);
    $("#back-href").prop("hidden", false);
    //$("#indicator").prop("hidden", true);
    //$("#clear-btn").prop("hidden", true);
    //document.getElementById("indicator").textContent = "Indicator";
    document.getElementById("edit-btn").innerHTML = "Edit<br>";
    $("#edit-btn").hide().show(0);
    $("#label-btn").prop("hidden", true);
    $('#submit-btn').prop("hidden", true);

    //played = true;
    //play_video();
  }
}

function onSelectForeground() {
  graph.setLineWidth(5);
  graph.setCurrentColor("#f0ad4e");
}

function onSelectBackground() {
  graph.setLineWidth(5);
  graph.setCurrentColor("#5cb85c");
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
  $('#submit-btn').click(onSubmit);
  $('#refine-btn').click(onRefine);
  $('#cancel-btn').click(onClear);
  //$('#label-btn').click(onChangeLabel);
  $('#type-foreground').click(onSelectForeground);
  $('#type-background').click(onSelectBackground);

  toastr.options.positionClass = "toast-top-center";

});
