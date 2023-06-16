import PaddleOCR_.tools_.program as program
from PaddleOCR_.tools_.infer_kie_token_ser import SerPredictor,draw_ser_results
import logging
from flask_cors import CORS
from flask import Flask, request, jsonify
import cv2
import base64
logging.disable(logging.INFO) 
app = Flask(__name__)
CORS(app)
config, device, logger, vdl_writer = program.preprocess()

print("LayoutXLM模型加载成功......")
ser_engine = SerPredictor(config)

with open("PaddleOCR_/label_name.txt","r",encoding="utf-8") as f:
    label_list=f.read().splitlines()
key_name=[]
for item in label_list:
    first=item.split("_")[0]
    if first not in key_name:
        key_name.append(first)
del key_name[0]

key_eng=["GENDER","AGE","NAME","OCODE","OTYPE","IN","OUT","DAY","PC","PH","JY","OPEN","SK","FH","JS","XX","SKDW",
        "YBLX","HJ","ZC","JC","HY","ZL","SS","WSCL","XY","ZYYP","ZCYF","YBZL","CW","HL","GH","QT","YBTC","TC",
        "XJ","ZH","GRZF","QTZF","ZFY","ZFE"]
        
token2label={}
for a,b in zip(key_name,key_eng):
    token2label[a]=b

label2token={}
for key,value in token2label.items():
    label2token[value]=key

def get_ser(image_path):
    config['Global']['infer_img']=image_path
    data = {'img_path': image_path}
    result, _ = ser_engine(data)
    result_data = result[0]
    img_res = draw_ser_results(image_path, result_data)
    result=[]
    for item in result_data:
        itemjson={}
        if item["pred"]!="O" and item["pred"] not in itemjson.keys():
            itemjson[item["pred"]]=item["transcription"]
        result.append(itemjson)
        
    txt=""
    for i in range(len(result)):
        for key,value in result[i].items():
            txt=txt+key+" : "+value+"\n"
            
    return img_res,txt

@app.route('/SER', methods=['GET','POST'])
def SER():
    print("成功接收数据......")
    R={}
    file=str(request.args['query'])
    path="upload/"+file
    img_res,result=get_ser(path)
    _, buffer = cv2.imencode('.jpg', img_res)
    img_base64 = base64.b64encode(buffer).decode()
    R["image_data"]=img_base64
    R["result"]=result
    
    print(R["result"])
    return jsonify(R)

if __name__ == "__main__":
    app.run(port=82,debug = False)