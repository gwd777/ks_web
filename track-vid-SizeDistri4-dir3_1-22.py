"""
Author: ps
Date: 2024-12-22
LastEditors: ps
LastEditTime: 2025-01-04
Describe:
    批量搜索并处理一个目录和子目录中所有视频，或处理指定路径单个视频，并将结果可视化视频存放在指定目录。
    同时打印到当前帧为止检测到的矿石数量和累积粒度分布。
    打印信息示例与说明：
        18 18 D5:132.8 | D20:163.4 | D50:255.0 | Xc:263.5 | D75:293.4 | D80:298.4 | D90:337.0
        分布左侧两个数据从左到右为：最大追踪ID，根据追踪ID统计到的目标数；
    YOLO支持批量视频检测与跟踪：https://docs.ultralytics.com/zh/modes/predict/#inference-sources
        YOLO追踪的原理：对视频中的每一帧（或每几帧）检测一次，获得检测结果后，用跟踪算法（bytetrack或botsort）获得目标在视频所有帧中的唯一跟踪ID。
        输入源为多个视频时，处理完上一个视频的最后一帧图片后马上处理下一个视频的第一帧，中间没有停顿或间隔。
"""
from collections import defaultdict  # ps modify
import cv2
import numpy as np  # ps modify
from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator, colors
import pandas as pd  # ps add
import os  # ps add
import pickle
import math

def splitFilePath(filePath):  # 返回路径中各文件夹名列表、文件名（文件名.扩展名）、文件名（仅文件名）
    folders = []
    drive, path_and_file = os.path.splitdrive(filePath)  # 分割驱动器和目录
    if drive != '':
        folders.append(drive[0])  # 获取驱动器中的盘符，仅Windows下不为空
    path, file = os.path.split(path_and_file)  # 分割路径和文件名
    if path != '':  # 处理路径
        for i in path.split('/'):  # 将路径按/分隔
            if i != '':
                folders.append(i)
    if file != '':  # 处理文件名
        fileNameExt = os.path.splitext(file)
        folders.append(file)
    # print([drive,folders,file,fileNameExt])  # 打印分隔结果
    return drive, folders, file, fileNameExt

"""
输入所有矿石长宽字典（maxWHDict），返回该字典中所有矿石的质量分数分布
输入示例：[wn, hn, wn * hn, wn * RIrateW, hn * RIrateH]
    {
        1: [0.09828853607177734, 0.11099578440189362, 0.010909613159000742, 139.0732479658004, 157.05335397416235],
        2: [0.124353788793087, 0.2497282475233078, 0.03105465374818117, 175.95424650213766, 353.3526887256826],
        。。。
    }
返回值示例：
    {'D5': 57.3, 'D20': 121.0, 'D50': 178.1, 'Xc': 217.0, 'D75': 265.4, 'D80': 284.2, 'D90': 284.2}
"""
def getOreSizeDistribution(vidOreWHDict,sDratesDict):
    # sDratesDict = {'D5': 0.05, 'D20': 0.2, 'D50': 0.5, 'Xc': 0.632, 'D75': 0.75, 'D80': 0.8,
    #                'D90': 0.9}  # 可设置的参数，即累计粒度分布百分数    #ps add
    # 矿石粒径分布计算参数（得到合理的粒径分布）
    ellipseCoefficient = 1  # 内接椭圆系数，1时为最大内接椭圆
    volDetectedRate = 0.95  # 检出率，检出体积占总体积百分数，值为0.95~1之间时对结果有影响
    sVDRR = 0.4  # 某粒径矿石检出体积与实际总体积比值(sizeVolDetectedRealityRate)，即142行的“z-1=x*k(y-1)”公式中的k

    vidDistriDict = {'D5': 0, 'D20': 0, 'D50': 0, 'Xc': 0, 'D75': 0, 'D80': 0,
                     'D90': 0}  # 粒径分布
    equivalentList = []  # [[等效直径，等效体积，估计的实际体积],[],...]列表
    totalVol = 0  # 累计体积
    maxVol = 0  # 矿石最大体积
    for oreWH in vidOreWHDict.values():
        oreW, oreH = oreWH[3], oreWH[4]
        # boxMaxInlineEllipseArea= math.pi*(oreW/2)*(oreH/2)    #矩形检测框最大内接椭圆面积
        # equivalentR=math.sqrt(boxMaxInlineEllipseArea/math.pi)    #矿石等效半径，RDT-FragNet论文中给的等效直径计算方法
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
        equivalentList[i][0] = round(equivalentList[i][0] * (sVDRR * (volPer - 1) + 1),
                                     1)  # 修正后的粒径，括号中公式为z-1=x*k(y-1)，sVDRR相当于k，volPer相当于y,equivalentList[i][0]相当于x
        equivalentList[i][1] = (4 / 3) * math.pi * pow((equivalentList[i][0] / 2) / 10, 3)  # 修正后的体积
        totalVol += equivalentList[i][1]  # 所有检测到的矿石总体积
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

if __name__ == '__main__':
    #对所有匹配 glob 表达式的图像和视频进行推理，并使用 * 字符
    videoPath='./testVideo/2号鄂破口_163197937-12fps-剪辑截取-10s.mp4'  #单个视频
    # videoPath='./testVideo/12-16/**/*.mp4'    #匹配某目录下所有视频
    vidStride = 5  # 视频输入的帧间距。允许跳过视频中的帧，以加快处理速度，但会牺牲时间分辨率。数值为 1 时会处理每一帧，数值越大越跳帧。
    OreModelPath='./models/v8n-pt_oreDusty320Cls1_imgsz640.pt'  # select your model.pt path
    #输出结果视频存放目录
    videoOutputDir='./videoOutput/'

    model = YOLO(OreModelPath)  # ps modify

    # YOLO官方文档中的推理源说明：https://docs.ultralytics.com/zh/modes/predict/#inference-sources
    # YOLO官方文档中的推理与追踪参数说明：https://docs.ultralytics.com/zh/modes/predict/#inference-arguments
    #                                https://docs.ultralytics.com/zh/modes/track/#tracking-arguments
    # YOLO官方文档中的追踪参数说明：https://docs.ultralytics.com/zh/guides/object-counting/#arguments-modeltrack
    results = model.track(
        source=videoPath,   #指定图片或视频的源目录。支持文件路径和 URL。
        # 模型训练时和推理时应该设置相同输入分辨率，否则跟踪效果很差，目标框乱冒，不稳定。
        # imgsz=3840,       #不指定模式输入分辨率时会使用模型训练时输入分辨率，跟踪效果好
        batch=4,  # 指定推理的批量大小（仅当来源为 目录、视频文件或 .txt 文件).更大的批次规模可以提供更高的吞吐量，缩短推理所需的总时间。
        vid_stride=vidStride,  # 每几个帧处理一次
        show_labels=False,  # 不展示标签
        stream=True,  # 推理视频时设为true，防止爆内存
        # project='runs/detect',
        # name='exp',
        persist=True,   #关键设置，可在帧间持续跟踪对象，在视频序列中保持目标追踪ID。
        tracker="botsort.yaml",  # 指定要使用的跟踪算法，例如 bytetrack.yaml 或 botsort.yaml。 botsort.yaml更适合于场景中有中断或遮挡的情况，能够在目标丢失后再次出现时继续追踪。
        save=False,  # 可将检测结果图像或视频保存到文件中。使用CLI 时默认为 True，在Python 中使用时默认为 False。
        # save_txt=True,      #将检测结果保存在文本文件中，格式如下 [class] [x_center] [y_center] [width] [height] [confidence].有助于与其他分析工具集成。
        # save_conf=True,     #在保存的文本文件中包含置信度分数。增强了后期处理和分析的细节。
        # classes=0,
    )

    sDratesDict = {'D5': 0.05, 'D20': 0.2, 'D50': 0.5, 'Xc': 0.632, 'D75': 0.75, 'D80': 0.8,
                   'D90': 0.9}  # 可设置的参数，即累计粒度分布百分数    #ps add
    # sDrates = [0.05, 0.2, 0.5, 0.632, 0.75, 0.8, 0.9]  # 可设置的参数，即累计粒度分布百分数，对应D5、D20、...、D90    #ps add
    RIrateH = (360 + 250) / (0.266667 + 0.164444)  # Reality现实（单位mm）与Image图片值（高相对于整张图片的比例）换算比例
    RIrateW = RIrateH

    # 批量处理视频参数
    prevFilePath = ''  # 上一个处理的视频路径
    currFilePath = ''  # 当前处理的视频路径

    # 和官方例子一样for循环不能省，省去模型不启动
    for r in results:
        # print(r)

        if currFilePath != r.path:  # 当前帧属于新一个视频
            # 前一个视频的扫尾工作
            prevFilePath = currFilePath  # 先记下前一个文件路径
            if prevFilePath != '':  # 一开始没有前一个视频，除一开始外，结束上一个视频的处理
                print(currFilePath, 'detect finished')
                print('final size distribution:','\n',maxSizeDistriDict)
                out.release()  # 释放 VideoWriter 对象，结束前一个视频的处理
            # 开始处理下一个视频
            currFilePath = r.path  # 当前处理的视频路径
            frameShape = r.orig_shape  # 帧尺寸
            defaultSaveDir = r.save_dir  # 跟踪的视频默认保存路径
            frameShape1 = r.boxes.orig_shape  # 帧尺寸
            drive, folders, file, fileNameExt = splitFilePath(currFilePath)
            print(file, fileNameExt, frameShape, defaultSaveDir, frameShape1,currFilePath)

            #获取视频参数
            cap = cv2.VideoCapture(currFilePath)  # ps add
            assert cap.isOpened(), "Error reading video file"
            vidW, vidH, fps = (int(cap.get(x)) for x in
                               (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS))
            cap.release()
            frame_width = vidW
            frame_height = vidH
            # 如果输出结果视频存放文件夹不存在
            videoOutputDir1=os.path.abspath(videoOutputDir)
            print(videoOutputDir1)
            if not os.path.exists(videoOutputDir1):
                os.makedirs(videoOutputDir1)
                print('创建目录成功：', videoOutputDir1)
            videoOutputPath=os.path.join(videoOutputDir1,file)
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # 使用 mp4v 编解码器
            out = cv2.VideoWriter(videoOutputPath, fourcc, fps / vidStride, (frame_width, frame_height))

            # 存储追踪历史 #ps modify
            track_history = defaultdict(lambda: [])  # ps modify

            # maxSizeList = []  # 被检测到的矿石的历史最大值列表，“model.track(persist=True,)”参数下才能使用
            maxWHDict = {}  # 被检测到的矿石的历史最大值字典，“model.track(persist=True,)”参数下才能使用
            # maxSizeDistriDict = {}  # 矿石粒度分布字典，依次是D5、D20、D50、Xc...、D90   #ps add

        boxes = r.boxes  # Boxes object for bbox outputs
        # print(boxes)
        if (r.boxes.id == None):  # 未检测到目标
            continue
        image = r.orig_img
        image = cv2.resize(image, (frame_width, frame_height))  # 调整图像尺寸以匹配视频输出尺寸 (frame_width, frame_height)
        # 转换tensor为python列表
        xyxy_list = boxes.xyxy.tolist()
        # conf_list = boxes.conf.tolist()

        # 获取框和追踪ID #ps modify
        xywhs = r.boxes.xywh.cpu()
        xywhns = r.boxes.xywhn.cpu().tolist();  # print(xywhns)
        track_ids = r.boxes.id.int().cpu().tolist()
        # print(len(conf_list),len(track_ids))

        # # Visualize the results on the frame
        # annotated_frame = r.plot()

        # 按跟踪ID遍历新的一帧中检测到的矿石
        for xywhn,xywh,xyxy, track_id in zip(xywhns,xywhs,xyxy_list, track_ids):
            # print(track_id,xywhn,xywh)
            x, y, w, h = xywh
            # print(x,y,(float(x), float(y)))
            track = track_history[track_id]
            track.append((float(x), float(y)))  # x, y中心点
            if len(track) > 60:  # 在90帧中保留90个追踪点
                track.pop(0)
            # 绘制追踪线
            points = np.hstack(track).astype(np.int32).reshape((-1, 1, 2))
            cv2.polylines(image, [points], isClosed=False, color=(230, 230, 0), thickness=10)
            # cv2.polylines(annotated_frame, [points], isClosed=False, color=(230, 230, 0), thickness=10)

            # 记录每个跟踪ID对应矿石翻滚过程中最大的长宽
            xn, yn, wn, hn = xywhn
            if track_id not in maxWHDict.keys():  # 以前没出现过该矿石
                maxWHDict[track_id] = [wn, hn, wn * hn, wn * RIrateW, hn * RIrateH]  # 添加该矿石信息
            elif wn * hn > maxWHDict[track_id][2]:
                maxWHDict[track_id] = [wn, hn, wn * hn, wn * RIrateW, hn * RIrateH]  # 更新该矿石信息

            # 绘制矩形框
            x_min, y_min, x_max, y_max = xyxy
            y_max_float = y_max
            x_min = int(x_min)
            y_min = int(y_min)
            x_max = int(x_max)
            y_max = int(y_max)
            cv2.rectangle(image, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)  # 绘制矩形框，(0, 255, 0) 表示绿色，2 为边框宽度
        # print(len(maxWHDict),maxWHDict)
        maxSizeDistriDict=getOreSizeDistribution(maxWHDict,sDratesDict)     #获取视频开始到现在为止的粒径分布
        track_ids1 = sorted(track_ids)
        # print(list(maxWHDict.keys()))       #发现检测到的跟踪ID不连续，所以下面的目标数远少于最大跟踪ID
        print(track_ids1[-1], len(maxWHDict), maxSizeDistriDict)  # 跟踪ID最大值、已检测到的矿石历史最大值列表、视频开始到现在为止的粒径分布

        out.write(image)  # 将图像写入视频文件

    #最后一个视频也要结束处理
    print(currFilePath,'detect finished')
    print('final size distribution:','\n',maxSizeDistriDict)
    out.release()  # 释放 VideoWriter 对象，结束最后一个视频的处理