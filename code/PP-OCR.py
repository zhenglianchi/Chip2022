import os
from paddleocr import PaddleOCR, draw_ocr
from PIL import Image
from tqdm.auto import tqdm

def save_ocr_res(text_save_folder,img_folder_path):
    def get_imlist(path):
        return [os.path.join(path,f) for f in os.listdir(path)]
    test=get_imlist(img_folder_path)
    bar=tqdm(range(len(test)))
    for item in test:
        result=ocr.ocr(item, cls=True)
        boxes = [line[0] for line in result]
        txts = [line[1][0] for line in result]
        scores = [line[1][1] for line in result]
        file=open(os.path.join(text_save_folder,os.path.basename(item)+'.txt'),'a',encoding='utf-8')
        file.writelines(str(txts))
        file.writelines("\n")
        file.writelines(str(scores))
        file.close()
        bar.update(1)

ocr = PaddleOCR(use_angle_cls=True, lang="ch",drop_score=0.5)


text_save_folder = 'train_out_txt'
img_folder_path = r'datasets/大赛1000训练用数据集'
save_ocr_res(text_save_folder,img_folder_path)

text_save_folder = 'test_out_txt'
img_folder_path = r'datasets/大赛B榜测试用数据集'
save_ocr_res(text_save_folder,img_folder_path)