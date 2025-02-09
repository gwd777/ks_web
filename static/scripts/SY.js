window.onload = function() {
    var content = '中国科学院自动化研究所';
    var canvas = document.createElement('canvas');
    canvas.className = 'watermark-canvas'; // 给canvas添加类名以便应用样式
    var ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    document.body.appendChild(canvas);
    ctx.fillStyle = 'rgba(0, 0, 0, 0.3)'; // 设置水印颜色和透明度
    ctx.font = '20px Arial'; // 设置字体大小
    ctx.textAlign = 'center';

    // 计算单个水印的宽度和高度
    var textWidth = ctx.measureText(content).width;
    var textHeight = 50; // 根据字体大小设置高度

    // 计算水平和垂直方向上可以放置的水印数量
    var horizontalCount = Math.floor(window.innerWidth / (textWidth + 50)); // 水印之间的水平间隔设置为50
    var verticalCount = Math.floor(window.innerHeight / (textHeight + 50)); // 水印之间的垂直间隔设置为50

    // 循环绘制水印
    for (var i = 0; i < horizontalCount; i++) {
      for (var j = 0; j < verticalCount; j++) {
        // 计算每个水印的位置
        var x = i * (textWidth + 50) + (window.innerWidth - horizontalCount * (textWidth + 50)) / 2;
        var y = j * (textHeight + 50) + (window.innerHeight - verticalCount * (textHeight + 50)) / 2;

        // 绘制水印
        ctx.fillText(content, x, y + textHeight / 2); // 调整y坐标以垂直居中
      }
    }
};