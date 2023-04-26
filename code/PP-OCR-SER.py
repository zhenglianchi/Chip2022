import os
from paddleocr import PaddleOCR
import similar
import warnings
from datasets import load_dataset
warnings.filterwarnings("ignore")

traindata=load_dataset("csv",data_files="datasets\大赛1000训练用数据集.csv")
mark=traindata["train"]

markdata={}
value={}
name="001bfce2288c0cbe0a2811"
lastname=""
for item in mark:
    if item["图名"]!=name:
        markdata[lastname]=value
        value={}
        name=item["图名"]
    value[item["属性名"]]=item["正确值"]
    lastname=item["图名"]

markdata[mark[-1]["图名"]]=value

def is_Chinese(word):
    for ch in word:
        if '\u4e00' <= ch <= '\u9fff':
            return True
    return False


test="性别年龄医院名称组织机构代码医疗机构类型入院日期出院日期住院天数票据代码票据号码校验码开票日期收款人复核人价税合计大写小写收款单位医保类型诊查费检查费化验费治疗费手术费卫生材料费西药费中药饮片中成药一般诊疗床位护理挂号其他收费项目合计金额医保统筹基金支付个人先进个人账户"
for key,value in markdata.items():
    for a,b in value.items():
        for item in str(b):
            if is_Chinese(item):
                test+=str(item)

temp=set(list(test))

def save_ocr_res(img_folder_path):
    NUM=0
    def get_imlist(path):
        return [os.path.join(path,f) for f in os.listdir(path)]
    test=get_imlist(img_folder_path)
    for item in test:
        _,filename=os.path.split(item)
        result=ocr.ocr(item, cls=True)
        for i in range(len(result)):

            result[i][1]=list(result[i][1])
            result[i][1][0]=list(result[i][1][0])

            for j in range(len(result[i][1][0])):
                c=str(result[i][1][0][j])
                if not is_Chinese(c):
                    continue
                max=0
                zi=""
                for item in temp:
                    score=similar.similar(c,item)
                    if score>max:
                        max=score
                        zi=item
                if max>=0.85:
                    result[i][1][0][j]=zi
            s=""
            for q in result[i][1][0]:
                s+=str(q)
            result[i][1][0]=s
            del result[i][1][1]
    

        with open("train.txt","a",encoding="utf-8") as f:
            s=filename+"\t"+str(result)+"\n"
            f.write(s)
        NUM+=1
        print("已经写入第",NUM,"行")



ocr = PaddleOCR(lang="ch",drop_score=0.65)


img_folder_path = r'datasets/大赛1000训练用数据集'
save_ocr_res(img_folder_path)

