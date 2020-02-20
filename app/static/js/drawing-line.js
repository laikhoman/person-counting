var letsdraw;
var startX;
var startY;
var endX;
var endY;

var start

var theCanvas = document.getElementById('canvas');
var ctx = theCanvas.getContext('2d');

var canvasOffset = $('#canvas').offset();

$('#canvas').mousemove(function(e) {
    if (letsdraw) {
      ctx.clearRect(0,0,theCanvas.width,theCanvas.height);
      ctx.strokeStyle = 'blue';
      ctx.lineWidth = 1;
      ctx.beginPath();

      ctx.moveTo(letsdraw.x, letsdraw.y);

      ctx.lineTo(e.pageX - canvasOffset.left, e.pageY - canvasOffset.top);
      endX = e.pageX - canvasOffset.left;
      endY = e.pageY - canvasOffset.top;
      ctx.stroke();
    }
});

$('#canvas').mousedown(function(e) {
    letsdraw = {
      x:e.pageX - canvasOffset.left,
      y:e.pageY - canvasOffset.top
    }
    startX = letsdraw.x;
    startY = letsdraw.y;
});

$(window).mouseup(function() {
    letsdraw = null;
    input_tag_x1 = document.getElementById("x1");
    input_tag_y1 = document.getElementById("y1");
    input_tag_x2 = document.getElementById("x2");
    input_tag_y2 = document.getElementById("y2");
    input_tag_x1.value = Math.round(startX)
    input_tag_y1.value = Math.round(startY)
    input_tag_x2.value = Math.round(endX)
    input_tag_y2.value = Math.round(endY)
});
