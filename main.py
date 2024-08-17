import re
import cv2
import os
from ScreenCapture import ScreenCapture
from paddleocr import PaddleOCR
import time
import logging
from functools import reduce
from pprint import pprint
from PIL import Image, ImageDraw, ImageFont
from translate import trans, trans_esay
import numpy as np

from cache import Cache

global result

mem = Cache()
# 缓存翻译结果
def get_result(text):
    c = mem.get(text)
    if c:
        return c 
    else:
        logging.info(f'**cache miss, text: {text}')
        mem.set(text, trans_esay(text))
        return mem.get(text)
# box [[384.0, 113.0], [1914.0, 113.0], [1914.0, 139.0], [384.0, 139.0]] 
def draw_box_and_textes(img, box_trans_result, text_color=(0, 0, 255),
                         rect_color=(0, 255, 0), rect_fill_color=(255,255,255),
                        font_size=70):
    img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("SanJiBangKaiJianTi-2.ttf", font_size)
    for box, text, trans_res in box_trans_result:
        if not trans_res:
            continue
        # box [[384.0, 113.0], [1914.0, 113.0], [1914.0, 139.0], [384.0, 139.0]]
        # 转成int
        box = [tuple(map(int, i)) for i in box]
        rect_box = [box[0][0], box[0][1], box[2][0], box[2][1]]
        # 填充
        draw.rectangle(rect_box, outline=rect_color, width=2, fill=rect_fill_color)
        draw.text(box[0], text=trans_res, font=font, fill=text_color)
    return cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)

def run(sc):
    # 实例化ocr
    ocr = PaddleOCR(use_angle_cls=True, lang="en", modele='en_PP-OCRv3_rec', use_gpu=True, drop_score=0.8, debug=False)
    # 循环体
    while True:
        # cv2 array
        img = sc.grab_screen_mss()

        cv2.namedWindow(sc.window_name, cv2.WINDOW_NORMAL)  # cv2.WINDOW_NORMAL 根据窗口大小设置图片大小

        cv2.resizeWindow(sc.window_name, 1920, 1080)

        # 创建识别对象
        result = ocr.ocr(img)
        if not result:
            print("识别失败")
            continue
        result = result[0]
        logging.debug(result)
        if not result:
            continue

        # 按照文本长度排序
        result = sorted(result, key=lambda x: len(x[1][0]), reverse=True)
        
        #保留前5个（长度大于4）
        result = list(filter(lambda x: len(x[1][0]) > 4, result))
        result = result[:5]
        box_trans_result = []
        for b, t in result:
            # b: [[384.0, 113.0], [1914.0, 113.0], [1914.0, 139.0], [384.0, 139.0]]
            # t ('console.bce.baidu.com/support/#/api?product=Al&project=ls*i&parent=X*i-i&api=rpc%2F2.0%2', 0.9732790589332581)
            query_text = t[0]
            trans_res = get_result(query_text)
            logging.info(f'query_text: {query_text}, trans_res: {trans_res}')
            box_trans_result.append([b, t, trans_res])
        img = draw_box_and_textes(img, box_trans_result)
        # resize image
        cv2.resize(img, (1920, 1080))
        cv2.imshow(sc.window_name, img)
        if cv2.waitKey(200) == sc.exit_code:  # 默认：ESC

            cv2.destroyAllWindows()

            os._exit(0)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    sc = ScreenCapture(capture_region=(1, 1), screen_resolution=(3200, 2000))
    try:
        run(sc)
    except KeyboardInterrupt:
        print("退出..")
        mem.save()
