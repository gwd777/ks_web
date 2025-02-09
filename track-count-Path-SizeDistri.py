#2024.12.2在耿师兄代码基础上增加绘制追踪路径代码，结合“trackPath.py”和“track-count.py”新建“track-count-Path.py”    #ps modify
from collections import defaultdict #ps modify
import cv2
import numpy as np  #ps modify
from ultralytics import YOLO

if __name__ == '__main__':
    # model = YOLO('OreModels/v8s-p2_Ore_2024-11-21.pt') # select your model.pt path
    # model = YOLO('OreModels/v8n-pt_OreClose99img_2024-11-29.pt')    #ps modify
    model = YOLO('OreModels/v8m-pt_OreClose182img_2024-11-30.pt')  # ps modify
    results=model.track(
                  # source='img.jpeg',
                  source='Datasets/video/2号鄂破口_163197937-12fps-剪辑截取.mp4',
                  # source='Datasets/video/2号鄂破口_163197937-12fps-剪辑截取-10s.mp4',
                  imgsz=3840,
                  show_labels=False,  # 不展示标签
                  stream=True,   #推理视频时设为true，防止爆内存
                  # project='runs/detect',
                  # name='exp',
                  tracker="botsort.yaml",  # 更适合于场景中有中断或遮挡的情况，能够在目标丢失后再次出现时继续追踪。
                  save=False,
                  # classes=0,
                )

    # 定义视频输出参数
    # frame_width, frame_height = results[0].boxes.orig_shape
    frame_width = 3840
    frame_height = 2160
    fourcc = cv2.VideoWriter_fourcc(*'XVID')  # 使用 XVID 编解码器
    out = cv2.VideoWriter('output_video.avi', fourcc, 20.0, (frame_width, frame_height))

    red_line_y = 1900    # 红线 y 值（假设红线是一个 y 坐标，例如 300）
    frame_count = 0     # 手动维护帧数计数器

    big_scale = 0    # 初始化计数器
    middle_scale = 0
    small_scale = 0
    recorder_buffer = ""
    sizeList=[]     #经检测的帧的矿石像素值列表                        #ps add
    sizeDistri=[0,0,0,0,0,0]   #矿石粒度分布，依次是D5、D20、...、D90   #ps add
    sDrate=[0.05,0.2,0.5,0.75,0.8,0.9]                  #可设置的参数，即累计粒度分布百分数，对应D5、D20、...、D90    #ps add

    # 存储追踪历史 #ps modify
    track_history = defaultdict(lambda: [])     #ps modify

    # # 获取框和追踪ID #ps modify
    # xywh = results[0].boxes.xywh.cpu()
    # track_ids = results[0].boxes.id.int().cpu().tolist()
    #
    # # 在帧上展示结果 #ps modify
    # annotated_frame = results[0].plot()

    # 和官方例子一样for循环不能省，省去模型不启动
    for r in results:
        boxes = r.boxes  # Boxes object for bbox outputs
        # print(boxes)

        image = r.orig_img
        image = cv2.resize(image, (frame_width, frame_height))  # 调整图像尺寸以匹配视频输出尺寸 (frame_width, frame_height)

        xyxy_list = boxes.xyxy.tolist()
        conf_list = boxes.conf.tolist()

        # 获取框和追踪ID #ps modify
        xywh = r.boxes.xywh.cpu()
        track_ids = r.boxes.id.int().cpu().tolist()
        # 在帧上展示结果 #ps modify
        # annotated_frame = r.plot()
        # 绘制追踪路径
        for box, track_id in zip(xywh, track_ids):
            x, y, w, h = box
            track = track_history[track_id]
            track.append((float(x), float(y)))  # x, y中心点
            if len(track) > 90:  # 在90帧中保留90个追踪点
                track.pop(0)
            # 绘制追踪线
            points = np.hstack(track).astype(np.int32).reshape((-1, 1, 2))
            cv2.polylines(image, [points], isClosed=False, color=(230, 230, 0), thickness=10)

        # 绘制红线
        cv2.line(image, (0, red_line_y), (frame_width, red_line_y), (0, 0, 255), 3)  # 红色的红线

        for xyxy, conf in zip(xyxy_list, conf_list):
            x_min, y_min, x_max, y_max = xyxy    # 绘制矩形框
            y_max_float = y_max
            x_min = int(x_min)
            y_min = int(y_min)
            x_max = int(x_max)
            y_max = int(y_max)
            cv2.rectangle(image, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)    # 绘制矩形框，(0, 255, 0) 表示绿色，2 为边框宽度

            # 检查框是否过红线（y_max 大于红线 y 值）；round(y_max_float, 2)为四舍五入到小数后两位
            if y_max > red_line_y and str(round(y_max_float, 2)) not in recorder_buffer:
                recorder_buffer = recorder_buffer + str(round(y_max_float, 2)) + " / "
                stone_scale = ((x_max - x_min) + (y_max - y_min))/2
                # print(stone_scale)    #ps add
                # print('=============>', recorder_buffer)
                sizeList.append(stone_scale)    #检测到一个新矿石就往矿石像素值列表里添加
                # if stone_scale < 350.0:
                #     small_scale += 1
                # if stone_scale < 700.0 and stone_scale >= 350:
                #     middle_scale += 1
                # if stone_scale > 700.0:
                #     big_scale += 1
        sizeList.sort()                 #对历史所有矿石像素值排序     #ps add
        sizeListLen = len(sizeList)     #ps add
        for i in range(6):              #得到每个累计粒度分布百分数（D5、D20、...、D90）对应的矿石毫米值     #ps add
            sizeDistri[i]=round(sizeList[int(sizeListLen * sDrate[i])] / 3840 * 1750, 1)    #ps add
            #sizeListLen * sDrate[i]：每个矿石像素值
            #3840：（视频分辨率为3840*2160）
            #1750：项目组大群里量出来鄂破口的长是175cm
        sD = sizeDistri                 #换一个短一点的变量名 #ps add
        # 确保文本不超出图像边界，动态计算位置
        font = cv2.FONT_HERSHEY_SIMPLEX
        # text = f"X<60cm: {small_scale} | 60cm<X<100cm: {middle_scale} | X>100cm: {big_scale}"     #ps modify
        text = f"D5:{sD[0]} | D20:{sD[1]} | D50:{sD[2]} | D75:{sD[3]} | D80:{sD[4]} | D90:{sD[5]}"            #ps add
        text_size = cv2.getTextSize(text, font, 2, 3)[0]  # 获取文本的宽度和高度
        text_width, text_height = text_size
        text_x = frame_width - text_width - 1200  # 右边距为 20 像素
        text_y = 300  # 高度位置为 30，靠近顶部
        cv2.putText(image, text, (text_x, text_y), font, 3, (0, 0, 255), 5, cv2.LINE_AA)    # 在图像上添加文本

        # 显示图像
        # cv2.imshow("Image with Box", image)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        out.write(image)    # 将图像写入视频文件

    out.release()   # 释放 VideoWriter 对象

