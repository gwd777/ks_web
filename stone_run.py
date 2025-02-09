from flask import Flask, Response, render_template, jsonify
from ultralytics import solutions
import os
import cv2
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

app = Flask(__name__, template_folder='templates')

# 初始化对象计数器
region_points = [(200, 1400), (3800, 1400), (3800, 2100), (200, 2100)]  # For rectangle region counting
counter = solutions.ObjectCounter(
    # show=True,
    region=region_points,
    # model="v8n-pt_OreClose99img_2024-11-29.pt",
    model="v8n-pt_oreDusty320Cls1_imgsz640.pt",
    classes=[0],  # 只统计特定类别（0表示人，可以根据需要更改）
    show_in=True,
    show_out=False,
    line_width=5
)

# 定义一个全局字典用于存储 sdic 数据
sdict = {}

def generate_frames():
    global sdict  # 使用全局字典
    cap = cv2.VideoCapture("static/source/stone.mp4")   # 初始化视频捕获
    while cap.isOpened():
        success, im0 = cap.read()
        if not success:
            break
        im0, sdict = counter.count(im0)  # 使用对象计数器处理帧

        ret, buffer = cv2.imencode('.jpg', im0)     # 将帧编码为JPEG格式
        if not ret:
            continue  # 如果编码失败，跳过当前帧

        frame = buffer.tobytes()

        # 生成符合MJPEG格式的帧
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@app.route('/sdict')
def get_sdict():
    my_dict = {
        'X<5': 0, '5<X<20': 0, '20<X<50': 0,
        '50<X<75': 0, '75<X<80': 0, '80<X<90': 0,
        '>90': 0, 'max': 0, 'min': 0
    }
    temp_list = []
    for key, value in sdict.items():
        value = value * (1750 / 3840)   # 将像素值转化成mm
        temp_list.append(float(value))
        if value < 5:
            my_dict['X<5'] += 1
        elif 5 <= value < 20:
            my_dict['5<X<20'] += 1
        elif 20 <= value < 50:
            my_dict['20<X<50'] += 1
        elif 50 <= value < 75:
            my_dict['50<X<75'] += 1
        elif 75 <= value < 80:
            my_dict['75<X<80'] += 1
        elif 80 <= value < 90:
            my_dict['80<X<90'] += 1
        else:
            my_dict['>90'] += 1

    my_dict['max'] = max(temp_list)
    my_dict['min'] = min(temp_list)

    jsonData = jsonify(my_dict)
    return jsonData.json

@app.route('/video_feed')
def video_feed():
    """提供视频流的路由，在HTML的<img>标签中使用此路由。"""
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/index')
def index_view():
    return render_template('views/web_stone.html')



# http://127.0.0.1:5000/index
if __name__ == '__main__':
    app.run(debug=True)