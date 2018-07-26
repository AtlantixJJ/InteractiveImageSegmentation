'use strict';

function Graph(document) {
  var canvas = document.getElementById('canvas');
  var ctx = canvas.getContext('2d');

  var width = canvas.width;
  var height = canvas.height;
  var offsetX = canvas.offsetLeft + parseInt(canvas.style.borderBottomWidth);
  var offsetY = canvas.offsetTop + parseInt(canvas.style.borderBottomWidth);

  this.has_result = false;

  ctx.fillStyle = '#000';
  ctx.lineCap = 'round';

  this.getImageData = function () {
    return canvas.toDataURL();
  };

  this.setCurrentColor = function (colorString) {
    ctx.strokeStyle = colorString;
  };

  this.setLineWidth = function (width) {
    ctx.lineWidth = width;
  };

  this.drawLine = function (x1, y1, x2, y2) {
    ctx.beginPath();
    ctx.moveTo(x1, y1);
    ctx.lineTo(x2, y2);
    ctx.stroke();
  };

  this.drawRect = function (x1, y1, x2, y2) {
    if (x2 < x1) [x1, x2] = [x2, x1];
    if (y2 < y1) [y1, y2] = [y2, y1];
    ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);
  };
  
  this.drawImage = function (img, x, y) {
    ctx.drawImage(img, x, y, img.width, img.height);
  };

  this.clear = function () {
    ctx.clearRect(0, 0, 10*width, 10*height);
  };
}