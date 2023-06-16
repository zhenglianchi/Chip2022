from flask_cors import CORS
from flask import Flask, request, jsonify
from paddleocr import PaddleOCR as PO
import cv2
import numpy as np
import base64
import logging

logging.disable(logging.DEBUG)  # 关闭DEBUG日志的打印
logging.disable(logging.WARNING)  # 关闭WARNING日志的打印

app = Flask(__name__)
CORS(app)

ocr = PO(use_angle_cls=True, lang="ch",drop_score=0.5)
print("加载PPOCR成功......")
def get_ocr_res(img_path):
    result=ocr.ocr(img_path, cls=True)
    txts = [line[1][0] for line in result]

    return " ".join(txts)

@app.route('/recognition', methods=['GET','POST'])
def recognition():
    print("成功接收数据......")
    R={}
    file=str(request.args['query'])
    
    path="upload/"+file
    rec=get_ocr_res(path)
    R["result"]=rec
    
    print(R["result"])
    return jsonify(R)

@app.route('/sourcepic', methods=['GET'])
def sourcepic():
    # 读取图像
    file = str(request.args["query"])
    path = "upload/" + file
    img = cv2.imread(path)
    _, buffer = cv2.imencode('.jpg', img)
    img_base64 = base64.b64encode(buffer).decode()

    # 返回 base64 图片数据
    return jsonify(image_data=img_base64)

@app.route('/sharpen', methods=['GET'])
def sharpen():
    # 读取图像
    file = str(request.args["query"])
    path = "upload/" + file
    img = cv2.imread(path)

    # 进行锐化操作
    kernel_sharpen_1 = np.array(
        [
            [-1, -1, -1],
            [-1, 9, -1],
            [-1, -1, -1],
        ]
    )
    sharpened_img = cv2.filter2D(img, -1, kernel_sharpen_1)

    # 将锐化后的图片编码为 base64 格式
    _, buffer = cv2.imencode('.jpg', sharpened_img)
    img_base64 = base64.b64encode(buffer).decode()
    # 返回 base64 图片数据
    return jsonify(image_data=img_base64)

@app.route('/smooth', methods=['GET'])
def smooth():
    # 读取图像
    file = str(request.args["query"])
    path = "upload/" + file
    img = cv2.imread(path)

    # 进行平滑操作
    smoothed_img = cv2.GaussianBlur(img, (5, 5), 0)

    # 将锐化后的图片编码为 base64 格式
    _, buffer = cv2.imencode('.jpg', smoothed_img)
    img_base64 = base64.b64encode(buffer).decode()

    # 返回 base64 图片数据
    return jsonify(image_data=img_base64)

if __name__ == "__main__":
    app.run(port=90,debug = False)