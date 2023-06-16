from flask_cors import CORS
from flask import Flask, request, jsonify
import cv2
import base64

from Shadow_Removal_Network.demo import get_unshadow

app = Flask(__name__)
CORS(app)


@app.route('/shadow', methods=['GET'])
def shadow():
    print("成功接收数据......")
    # 读取图像
    file = str(request.args["query"])
    path = "upload/" + file
    img = cv2.imread(path)
    unshadow_img = get_unshadow(img)
    # 将锐化后的图片编码为 base64 格式
    _, buffer = cv2.imencode('.jpg', unshadow_img)
    img_base64 = base64.b64encode(buffer).decode()
    # 返回 base64 图片数据
    return jsonify(image_data=img_base64)


if __name__ == "__main__":
    app.run(port=84, debug=False)
