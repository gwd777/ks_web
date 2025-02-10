from flask import Flask, Response, render_template, jsonify
from collections import defaultdict
import os
import cv2
import numpy as np
import math

from ultralytics import YOLO
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

app = Flask(__name__, template_folder='templates')

# 初始化对象计数器
videoPath='static/source/1336-38.mp4'
vidStride = 5       # 视频输入的帧间距。允许跳过视频中的帧，以加快处理速度，但会牺牲时间分辨率。数值为 1 时会处理每一帧，数值越大越跳帧。
OreModelPath='v8n-pt_oreDusty320Cls1_imgsz640.pt'
model = YOLO(OreModelPath)  # ps modify


#获取视频参数
cap = cv2.VideoCapture(videoPath)  # ps add
assert cap.isOpened(), "Error reading video file"
vidW, vidH, fps = (int(cap.get(x)) for x in(cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS))
cap.release()
frame_width = vidW
frame_height = vidH
RIrateH = (360 + 250) / (0.266667 + 0.164444)  # Reality现实（单位mm）与Image图片值（高相对于整张图片的比例）换算比例
RIrateW = RIrateH
sDratesDict = {'D5': 0.05, 'D20': 0.2, 'D50': 0.5, 'Xc': 0.632, 'D75': 0.75, 'D80': 0.8, 'D90': 0.9}
track_history = defaultdict(lambda: [])     # 存储追踪历史 #ps modify
maxWHDict = {}                              # 被检测到的矿石的历史最大值字典，“model.track(persist=True,)”参数下才能使用


sdict_list = []  # 定义一个全局字典用于存储 sdic 数据
def getOreSizeDistribution(vidOreWHDict, sDratesDict):
    global sdict_list  # 使用全局字典
    sdict_list.clear()

    # sDratesDict = {'D5': 0.05, 'D20': 0.2, 'D50': 0.5, 'Xc': 0.632, 'D75': 0.75, 'D80': 0.8, 'D90': 0.9}  # 可设置的参数，即累计粒度分布百分数    #ps add
    # 矿石粒径分布计算参数（得到合理的粒径分布）
    ellipseCoefficient = 1  # 内接椭圆系数，1时为最大内接椭圆
    volDetectedRate = 0.95  # 检出率，检出体积占总体积百分数，值为0.95~1之间时对结果有影响
    sVDRR = 0.4  # 某粒径矿石检出体积与实际总体积比值(sizeVolDetectedRealityRate)，即142行的“z-1=x*k(y-1)”公式中的k

    vidDistriDict = {'D5': 0, 'D20': 0, 'D50': 0, 'Xc': 0, 'D75': 0, 'D80': 0, 'D90': 0}  # 粒径分布
    equivalentList = []  # [[等效直径，等效体积，估计的实际体积],[],...]列表
    totalVol = 0  # 累计体积
    maxVol = 0  # 矿石最大体积
    for oreWH in vidOreWHDict.values():
        oreW, oreH = oreWH[3], oreWH[4]
        # boxMaxInlineEllipseArea= math.pi*(oreW/2)*(oreH/2)          #矩形检测框最大内接椭圆面积
        # equivalentR=math.sqrt(boxMaxInlineEllipseArea/math.pi)      #矿石等效半径，RDT-FragNet论文中给的等效直径计算方法
        eR = ellipseCoefficient * math.sqrt((oreW / 2) * (oreH / 2))  # 矿石等效半径，圆周率pi约掉了
        eVolume = (4 / 3) * math.pi * pow(eR / 10, 3)  # 矿石等效体积
        # totalVol += eVolume  # 所有检测到的矿石总体积
        # print(oreW,oreH,eR,eVolume)
        equivalentList.append([eR * 2, eVolume])
    equivalentList.sort(key=lambda x: x[1])  # 对两层嵌套列表按第二层列表中第2个元素排序
    maxVol = equivalentList[-1][1]
    for i in range(len(equivalentList)):
        volPer = equivalentList[i][1] / maxVol  # 当前矿石与最大矿石体积比
        # equivalentList[i][2]=equivalentList[i][1]/(sVDRR*(volPer-1)+1)  #括号中公式为z-1=x*k(y-1)
        # totalVol+=equivalentList[i][2]
        equivalentList[i][0] = round(equivalentList[i][0] * (sVDRR * (volPer - 1) + 1), 1)  # 修正后的粒径，括号中公式为z-1=x*k(y-1)，sVDRR相当于k，volPer相当于y,equivalentList[i][0]相当于x
        equivalentList[i][1] = (4 / 3) * math.pi * pow((equivalentList[i][0] / 2) / 10, 3)  # 修正后的体积
        totalVol += equivalentList[i][1]    # 所有检测到的矿石总体积
        sdict_list.append(equivalentList[i][0])

    undetectedFineOreVol = (1 - volDetectedRate) / volDetectedRate * totalVol  # 未检测到的细碎矿石总体积
    totalVol += undetectedFineOreVol  # 检测和未检测到的总体积
    sDIndex = 0  # 粒径分布序号
    accuVol = undetectedFineOreVol  # 到当前矿石的累计体积
    sDkey = list(sDratesDict.keys())
    # print(sDkey,totalVol)
    count = 0
    # print(equivalentList[0])
    for eq in equivalentList:
        # print(eq)
        count += 1
        if sDIndex >= len(sDratesDict):
            break
        accuVol += eq[1]  # 计算到该粒径为止的累计体积
        # print(sDratesDict[sDkey[sDIndex]])
        if accuVol >= totalVol * sDratesDict[sDkey[sDIndex]]:  # 累计体积达到总体积的0.05、0.2、0.5 ......
            vidDistriDict[sDkey[sDIndex]] = eq[0]  # 修正后的等效粒径
            # print(sDIndex,count, accuVol, totalVol * sDratesDict[sDkey[sDIndex]])
            count = 0
            sDIndex += 1
    for i in range(sDIndex, len(vidDistriDict)):  # 如果出现D90为空，说明最大的石头太大，其余的石头太小，让D90=D80
        vidDistriDict[sDkey[i]] = vidDistriDict[sDkey[sDIndex - 1]]  # 修正后的等效粒径
    # print(vidOreWHDict,'\n',vidDistriDict)
    return vidDistriDict


maxSizeDistriDict = {}
def generate_frames():
    global sdict_list  # 使用全局字典
    global maxSizeDistriDict  # 使用全局字典

    results = model.track(
        source=videoPath,  # 指定图片或视频的源目录。支持文件路径和 URL。
        # 模型训练时和推理时应该设置相同输入分辨率，否则跟踪效果很差，目标框乱冒，不稳定。
        # imgsz=3840,       #不指定模式输入分辨率时会使用模型训练时输入分辨率，跟踪效果好
        batch=4,  # 指定推理的批量大小（仅当来源为 目录、视频文件或 .txt 文件).更大的批次规模可以提供更高的吞吐量，缩短推理所需的总时间。
        vid_stride=vidStride,  # 每几个帧处理一次
        show_labels=False,  # 不展示标签
        stream=True,  # 推理视频时设为true，防止爆内存
        # project='runs/detect',
        # name='exp',
        persist=True,  # 关键设置，可在帧间持续跟踪对象，在视频序列中保持目标追踪ID。
        tracker="botsort.yaml",
        # 指定要使用的跟踪算法，例如 bytetrack.yaml 或 botsort.yaml。 botsort.yaml更适合于场景中有中断或遮挡的情况，能够在目标丢失后再次出现时继续追踪。
        save=False,  # 可将检测结果图像或视频保存到文件中。使用CLI 时默认为 True，在Python 中使用时默认为 False。
        # save_txt=True,            #将检测结果保存在文本文件中，格式如下 [class] [x_center] [y_center] [width] [height] [confidence].有助于与其他分析工具集成。
        # save_conf=True,           #在保存的文本文件中包含置信度分数。增强了后期处理和分析的细节。
        # classes=0,
    )

    for r in results:
        boxes = r.boxes                             # Boxes object for bbox outputs
        if (r.boxes.id == None):  # 未检测到目标
            continue
        image = r.orig_img
        image = cv2.resize(image, (frame_width, frame_height))  # 调整图像尺寸以匹配视频输出尺寸 (frame_width, frame_height)

        # 获取框和追踪ID #ps modify
        xyxy_list = boxes.xyxy.tolist()     # 转换tensor为python列表
        xywhs = r.boxes.xywh.cpu()
        xywhns = r.boxes.xywhn.cpu().tolist()
        track_ids = r.boxes.id.int().cpu().tolist()

        # 按跟踪ID遍历新的一帧中检测到的矿石
        for xywhn, xywh, xyxy, track_id in zip(xywhns, xywhs, xyxy_list, track_ids):
            x, y, w, h = xywh
            track = track_history[track_id]
            track.append((float(x), float(y)))  # x, y中心点
            if len(track) > 60:                 # 在90帧中保留90个追踪点
                track.pop(0)
            # 绘制追踪线
            points = np.hstack(track).astype(np.int32).reshape((-1, 1, 2))
            cv2.polylines(image, [points], isClosed=False, color=(230, 230, 0), thickness=10)

            # 记录每个跟踪ID对应矿石翻滚过程中最大的长宽
            xn, yn, wn, hn = xywhn
            if track_id not in maxWHDict.keys():  # 以前没出现过该矿石
                maxWHDict[track_id] = [wn, hn, wn * hn, wn * RIrateW, hn * RIrateH]  # 添加该矿石信息
            elif wn * hn > maxWHDict[track_id][2]:
                maxWHDict[track_id] = [wn, hn, wn * hn, wn * RIrateW, hn * RIrateH]  # 更新该矿石信息

            # 绘制矩形框
            x_min, y_min, x_max, y_max = xyxy
            x_min = int(x_min)
            y_min = int(y_min)
            x_max = int(x_max)
            y_max = int(y_max)
            cv2.rectangle(image, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)  # 绘制矩形框，(0, 255, 0) 表示绿色，2 为边框宽度

        maxSizeDistriDict = getOreSizeDistribution(maxWHDict, sDratesDict)  # 获取视频开始到现在为止的粒径分布
        track_ids1 = sorted(track_ids)
        print(track_ids1[-1], len(maxWHDict), maxSizeDistriDict)  # 跟踪ID最大值、已检测到的矿石历史最大值列表、视频开始到现在为止的粒径分布

        ret, buffer = cv2.imencode('.jpg', image)  # 将帧编码为JPEG格式
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')  # 生成符合MJPEG格式的帧

@app.route('/dx_sdict')
def get_dx_sdict():
    jsonData = jsonify(maxSizeDistriDict)
    return jsonData.json

@app.route('/sdict')
def get_sdict():
    my_dict = {
        'X<5': 0, '5<X<20': 0, '20<X<50': 0,
        '50<X<75': 0, '75<X<80': 0, '80<X<90': 0,
        '>90': 0, 'max': 0, 'min': 0
    }

    for value in sdict_list:
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

    my_dict['max'] = max(sdict_list)
    my_dict['min'] = min(sdict_list)

    jsonData = jsonify(my_dict)
    return jsonData.json


@app.route('/video_feed')
def video_feed():
    """提供视频流的路由，在HTML的<img>标签中使用此路由。"""
    print('-------------video_feed RUN ------------')
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/index')
def index_view():
    return render_template('views/web_stone.html')

@app.route('/')
def hello_world():
    return '欢迎使用微信云托管！'

# http://127.0.0.1:5000/index
if __name__ == '__main__':
    print('stone_v2_run:----------------------->')
    # app.run(host='0.0.0.0', port=6000, debug=True)
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 80)))