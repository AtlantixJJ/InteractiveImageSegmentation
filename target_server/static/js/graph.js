'use strict';

function Graph(document) {
  var canvas = document.getElementById('canvas');
  this.ctx = canvas.getContext('2d');
  console.log("init graph", this.ctx.lineWidth);
  var width = canvas.width;
  var height = canvas.height;
  var offsetX = canvas.offsetLeft + parseInt(canvas.style.borderBottomWidth);
  var offsetY = canvas.offsetTop + parseInt(canvas.style.borderBottomWidth);

  this.has_result = false;

  this.ctx.fillStyle = '#000';
  this.ctx.lineCap = 'round';

  this.getImageData = function () {
    return canvas.toDataURL();
  };

  this.setCurrentColor = function (colorString) {
    this.ctx.strokeStyle = colorString;
  };

  this.setLineWidth = function (width) {
    this.ctx.lineWidth = width;
  };

  this.drawLine = function (x1, y1, x2, y2) {
    this.ctx.beginPath();
    this.ctx.moveTo(x1, y1);
    this.ctx.lineTo(x2, y2);
    this.ctx.stroke();
  };

  this.drawRect = function (x1, y1, x2, y2) {
    if (x2 < x1) [x1, x2] = [x2, x1];
    if (y2 < y1) [y1, y2] = [y2, y1];
    this.ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);
  };
  
  this.drawImage = function (img, x, y) {
    console.log("drawImage", this.ctx.lineWidth);
    this.ctx.drawImage(img, x, y, img.width, img.height);
    console.log("After", this.ctx.lineWidth);
  };

  this.clear = function () {
    this.ctx.clearRect(0, 0, 10*width, 10*height);
  };
}