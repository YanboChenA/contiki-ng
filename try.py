'''
Author: Yanbo Chen xt20786@bristol.ac.uk
Date: 2024-03-13 17:13:32
LastEditors: YanboChenA xt20786@bristol.ac.uk
LastEditTime: 2024-03-16 19:41:12
FilePath: \contiki-ng\try.py
Description: 
'''
import cv2
import numpy as np

def apply_perspective_transform_and_fill(image_path):
# 读取图像
# 读取图像，确保使用-1来保留PNG图像的透明度通道
    image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    # 如果图像不是四通道的，则将其转换为四通道
    if image.shape[2] < 4:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)

    h, w = image.shape[:2]

    # 定义原图中的四点坐标
    TL = [0, 0]
    TR = [w, 0]
    BL = [0, h]
    BR = [w, h]
    src_points = np.float32([TL, TR, BL, BR])
    # [0,0]: Top left corner
    # [w,0]: Top right corner
    # [0,h]: Bottom left corner
    # [w,h]: Bottom right corner
    # 目标点坐标，根据要求调整右上和右下角的x坐标为原来的一半

    x_offset = 0.45
    y_offset = 0.2
    # New_TL = [0, 0]
    New_TL = [0, h * 0.25]
    New_BL = [0, h]
    
    # New_TR = [w * x_offset, y_offset * h]
    # New_BR = [w * x_offset, (1 - y_offset) * h]

    New_TR = [w * 0.8, 0]
    New_BR = [w * 0.8, h * 0.75]

    dst_points = np.float32([New_TL, New_TR, New_BL, New_BR])

    # 生成透视变换矩阵；进行透视变换
    matrix = cv2.getPerspectiveTransform(src_points, dst_points)
    result = cv2.warpPerspective(image, matrix, (w, h), borderMode=cv2.BORDER_CONSTANT, borderValue=(0,0,0,0))

    # result delete the right part of the image 
    result = result[:, :int(w * 0.8)]

    cv2.imwrite("result.png", result)

    cv2.imshow("result", result)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

apply_perspective_transform_and_fill("Figure_3.png") # 将图像向右旋转90度 