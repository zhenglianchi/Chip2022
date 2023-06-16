from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers import pipeline
import os
from flask_cors import CORS
from flask import Flask, request, jsonify
from process import get_ocr_res
app = Flask(__name__)
CORS(app)
dirpath=os.environ["HF_HOME"]

discharge_tokenizer = AutoTokenizer.from_pretrained("zhenglianchi/dis-ner",cache_dir=dirpath)

discharge_model = AutoModelForTokenClassification.from_pretrained("zhenglianchi/dis-ner",cache_dir=dirpath)

discharge_ner = pipeline("token-classification", tokenizer=discharge_tokenizer,model=discharge_model)

medicines_tokenizer = AutoTokenizer.from_pretrained("zhenglianchi/med-ner",cache_dir=dirpath)

medicines_model = AutoModelForTokenClassification.from_pretrained("zhenglianchi/med-ner",cache_dir=dirpath)

medicines_ner = pipeline("token-classification", tokenizer=medicines_tokenizer,model=medicines_model)

outpatient_hospitalization_tokenizer = AutoTokenizer.from_pretrained("zhenglianchi/fp-ner",cache_dir=dirpath)

outpatient_hospitalization_model = AutoModelForTokenClassification.from_pretrained("zhenglianchi/fp-ner",cache_dir=dirpath)

outpatient_hospitalization_ner = pipeline("token-classification", tokenizer=outpatient_hospitalization_tokenizer,model=outpatient_hospitalization_model)
print("加载NER所有模型成功......")
#出院小结
def get_discharge():
    discharge_summary={
        "性别":"无","年龄":"无","医院名称":"无","入院日期":"无","出院日期":"无",
        "组织机构代码":"无","医疗机构类型":"无","住院天数":"无"
        }
    return discharge_summary

#购药发票
def get_medicines():
    medicines_invoice={
        "票据代码":"无","票据号码":"无","校验码":"无",
        "开票日期":"无","收款人":"无","复核人":"无","价税合计（大写）":"无","（小写）":"无"
        }
    return medicines_invoice

#住院发票
def get_hospitalization():
    hospitalization_invoice={
        "性别":"无","住院天数":"无","票据代码":"无","票据号码":"无","校验码":"无","开票日期":"无","收款单位":"无","入院日期":"无","出院日期":"无",
        "收款人":"无","复核人":"无","医疗机构类型":"无","医保类型":"无","合计金额（大写）":"无","（小写）":"无",
        "诊查费":"无","检查费":"无","化验费":"无","治疗费":"无","手术费":"无","卫生材料费":"无",
        "西药费":"无","中药饮片":"无","中成药费":"无","一般诊疗费":"无","床位费":"无","护理费":"无",
        "挂号费":"无","其他收费项目":"无","医保统筹基金支付":"无","统筹支付":"无","个人现金支付":"无","个人账户支付":"无",
        "个人自付":"无","其他支付":"无","自付一":"无","自付二":"无"
    }
    return hospitalization_invoice

dis_token2label={"性别":"G","年龄":"A","医院名称":"N","组织机构代码":"C","医疗机构类型":"L","住院天数":"D","入院日期":"IN","出院日期":"OUT"}
dis_label2token={}
for key,value in dis_token2label.items():
    dis_label2token[value]=key


med_token2label={ "票据代码": "PD","票据号码": "PH","校验码": "JY",  "开票日期": "PR", 
"收款人": "SR", "复核人": "FR", "价税合计（大写）":"JD","（小写）":"JX"}
med_label2token={}
for key,value in med_token2label.items():
    med_label2token[value]=key


fp_token2label = {"性别": "G", "入院日期":"IN","出院日期":"OUT","住院天数": "D", "票据代码": "PD","票据号码": "PH", "校验码": "JY", "开票日期": "PR", 
"收款单位": "SD", "收款人": "SR", "复核人": "FR", "医疗机构类型": "L", "医保类型": "YL", "诊查费": "ZC", 
"检查费": "JC",  "化验费": "HY", "治疗费": "ZL", "手术费": "S",  "卫生材料费": "WC", "西药费": "WY", 
"中药饮片": "ZY",  "中成药费": "ZCY", "一般诊疗费": "YZL","床位费": "CW",  "护理费": "HL",  "挂号费": "GH", 
"其他收费项目": "ELE", "合计金额（大写）": "HJD", "（小写）": "HJX",  "医保统筹基金支付": "YTC",
"统筹支付": "TC", "个人现金支付": "PX", "个人账户支付": "PP", 
"个人自付": "PO", "其他支付": "ELP",  "自付一": "POO", "自付二": "PW"}
fp_label2token={}
for key,value in fp_token2label.items():
    fp_label2token[value]=key

def return_res(res,label2token,datajson):
    test={}
    item=""
    for i in range(len(res)):
        type1=res[i]["entity"][2:]
        if i==(len(res)-1):
            type3=res[i-1]["entity"][2:]
            if type1==type3:
                item+=res[i]["word"]
                if type1 not in test.keys():
                    test[type1]=item
            else:
                item+=res[i]["word"]
                if type1 not in test.keys():
                    test[type1]=item
            break

        type2=res[i+1]["entity"][2:]
        if type1 != type2:
            item+=res[i]["word"]
            if type1 not in test.keys():
                test[type1]=item
            item=""
        else:
            item+=res[i]["word"]
    

    for key,value in test.items():
        key=label2token[key]
        value=value.replace("#","")
        if key in datajson.keys() and (datajson[key]=="空" or datajson[key]=="无"):
            datajson[key]=value

    return datajson

def process(dic):
    txt=""
    for key,value in dic.items():
        txt=txt+key+" : "+value+"\n"
    return txt


def get_ner(rec,type):
    if type=="出院小结":
        datajson=get_discharge()
        res=discharge_ner(rec)
        result=process(return_res(res,dis_label2token,datajson))

    elif type=="购药发票":
        datajson=get_medicines()
        res=medicines_ner(rec)
        result=process(return_res(res,med_label2token,datajson))

    else:
        datajson=get_hospitalization()
        res=outpatient_hospitalization_ner(rec)
        result=process(return_res(res,fp_label2token,datajson))

    return result

@app.route('/NER', methods=['GET','POST'])
def NER():
    print("成功接收数据......")
    R={}
    file=str(request.args['query'])
    type=str(request.args['invoiceType'])
    
    path="upload/"+file
    rec=get_ocr_res(path)
    R["result"]=get_ner(rec,type)
    print(R["result"])
    return jsonify(R)

if __name__ == "__main__":
    app.run(port=81,debug = False)