===================================================================

------- author:  郑连驰 ; organization: zut-2022-cv  -------
===================================================================

Before all: 配置环境
我在这里准备了两个环境，一个是paddleocr的paddlepaddle环境一个是bert的huggingface环境
可参考代码文件中的requirements文件

paddlepaddle: requirements1.txt
huggingface: requirements2.txt

-------------------------------------------------------------------
Step1: 准备数据
------------------
1.调整目录
1.1将大赛训练集和B榜集解压放在datasets文件夹下
目录结构为code/datasets/大赛B榜测试用数据集、code/datasets/大赛1000训练用数据集、code/datasets/大赛1000训练用数据集.csv、code/datasets/TestB.csv
1.2将大赛1000训练用数据集下的图片放入train_data/fp/train/img
1.3将大赛B榜测试用数据集改名为test放入PaddleOCR-release-2.6下方便最后推理
1.4提前创建train_out_txt，test_out_txt等文件夹

2.准备NER标注前数据
直接运行PP-OCR.py将训练用数据集以及B榜数据中的图片经过OCR得到其识别结果：train_out_txt，test_out_txt
第26行和30行可以设置输出文件夹
样例：text_save_folder = 'train_out_txt'

第27行和31行设置识别图片文件夹
样例：img_folder_path = r'datasets/大赛1000训练用数据集'

3.准备SER标注前数据
直接运行PP-OCR-SER.py将训练集中的图片经过OCR再经过单字纠错的处理得到其预处理结果：train.txt

-------------------------------------------------------------------
Step2: 数据标注
------------------
1. 标注NER数据
运行NER-datalabel.ipynb文件，在第19，15，22单元格第39行设置输出路径
样例：with open("NER_dataset/fp_res.json", 'w', encoding="utf-8") as write_f:
得到结果为：NER_dataset文件夹，其中discharge_res.json为出院小结标注文件，medicines_res.json为购药发票标注文件，fp_res.json为购药发票和住院发票标注文件


2. 标注SER数据
运行SER-datalabel.ipynb文件，可以得到train_data/fp/train/train.txt，train_data/fp/val/val.txt

PS：提前创建好train_data/fp/等文件夹并且将label_name.txt以及label_list.txt放入train_data/fp下

Step3: 模型训练
------------------
1.NER的训练
分别运行discharge-train.ipynb，medicines-train.ipynb，fp-train.ipynb
其中dirpath变量为本地设置的环境变量用于下载huggingface社区模型
推送模型到huggingface社区可以设置为自己的key来登录推送
最后一个代码块为模型名
样例：tokenizer.push_to_hub("dis-ner")
model.push_to_hub("dis-ner")

指标：precision=1.0，recall=1.0，f1=1.0，accuracy=1.0
PS：由于训练集中O较多，导致标签不均衡，所以准确率等较高

2.SER的训练
进入PaddleOCR-release-2.6修改configs/kie/vi_layoutxlm/ser_vi_layoutxlm_xfund_zh.yml为ser_vi_layoutxlm_fp_zh.yml（其中训练内容修改为自己的内容）
在终端运行python3 tools/train.py -c configs/kie/vi_layoutxlm/ser_vi_layoutxlm_fp_zh.yml开启训练
所有模型输出在PaddleOCR-release-2.6/output/ser_vi_layoutxlm_fp_zh中

指标：hmean: 1.0, precision: 1.0, recall: 1.0, fps: 71.15125118481403, best_epoch: 200

Step4: 模型推理
------------------
1.SER对于B榜数据的推理
在终端运行python3 tools/infer_kie_token_ser.py -c configs/kie/vi_layoutxlm/ser_vi_layoutxlm_fp_zh.yml -o Architecture.Backbone.checkpoints=./output/ser_vi_layoutxlm_fp_zh/best_accuracy Global.infer_img=./test
结果保存在PaddleOCR-release-2.6/output/ser/fp/res

PS：将output中的best_accuracy模型以及推理结果res拿出像该文件夹一样可直接运行get-res.ipynb得到推理后的TestB.csv

2.NER与SER结合对B榜数据进行推理
直接运行get-res.ipynb文件
在最后一个代码块写入要插入的csv结果文件路径
样例：insertcsv('datasets/TestB.csv',key,value)

PS：其中也设置了环境变量可删除，其中NER的模型为huggingface社区我以及训练好的pipeline，SER模型的best_accuracy为我训练好的SER模型，该模型已保存在代码文件中

Step5: 模型部署
------------------

使用jeecg进行部署，使用jeecg-boot-v3.4.0，前端为design/page.vue，后端为flask代码，其中由于导入包冲突问题修改PaddleOCR文件名和内部文件名，然后将训练好的模型放入best_accuary中方便推理，以下为界面图：

- ![example](/example.png)

