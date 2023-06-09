# Python Inference

- [1. Layout Structured Analysis](#1)
  - [1.1 layout analysis + table recognition](#1.1)
  - [1.2 layout analysis](#1.2)
  - [1.3 table recognition](#1.3)
- [2. Key Information Extraction](#2)

<a name="1"></a>
## 1. Layout Structured Analysis
Go to the `ppstructure` directory

```bash
cd ppstructure
````

download model

```bash
mkdir inference && cd inference
# Download the PP-Structurev2 layout analysis model and unzip it
wget https://paddleocr.bj.bcebos.com/ppstructure/models/layout/picodet_lcnet_x1_0_layout_infer.tar && tar xf picodet_lcnet_x1_0_layout_infer.tar
# Download the PP-OCRv3 text detection model and unzip it
wget https://paddleocr.bj.bcebos.com/PP-OCRv3/chinese/ch_PP-OCRv3_det_infer.tar && tar xf ch_PP-OCRv3_det_infer.tar
# Download the PP-OCRv3 text recognition model and unzip it
wget https://paddleocr.bj.bcebos.com/PP-OCRv3/chinese/ch_PP-OCRv3_rec_infer.tar && tar xf ch_PP-OCRv3_rec_infer.tar
# Download the PP-Structurev2 form recognition model and unzip it
wget https://paddleocr.bj.bcebos.com/ppstructure/models/slanet/ch_ppstructure_mobile_v2.0_SLANet_infer.tar && tar xf ch_ppstructure_mobile_v2.0_SLANet_infer.tar
cd ..
```
<a name="1.1"></a>
### 1.1 layout analysis + table recognition
```bash
python3 predict_system.py --det_model_dir=inference/ch_PP-OCRv3_det_infer \
                          --rec_model_dir=inference/ch_PP-OCRv3_rec_infer \
                          --table_model_dir=inference/ch_ppstructure_mobile_v2.0_SLANet_infer \
                          --layout_model_dir=inference/picodet_lcnet_x1_0_layout_infer \
                          --image_dir=./docs/table/1.png \
                          --rec_char_dict_path=../ppocr_/utils/ppocr_keys_v1.txt \
                          --table_char_dict_path=../ppocr_/utils/dict/table_structure_dict_ch.txt \
                          --output=../output \
                          --vis_font_path=../doc/fonts/simfang.ttf
```
After the operation is completed, each image will have a directory with the same name in the `structure` directory under the directory specified by the `output` field. Each table in the image will be stored as an excel, and the picture area will be cropped and saved. The filename of excel and picture is their coordinates in the image. Detailed results are stored in the `res.txt` file.

<a name="1.2"></a>
### 1.2 layout analysis
```bash
python3 predict_system.py --layout_model_dir=inference/picodet_lcnet_x1_0_layout_infer \
                          --image_dir=./docs/table/1.png \
                          --output=../output \
                          --table=false \
                          --ocr=false
```
After the operation is completed, each image will have a directory with the same name in the `structure` directory under the directory specified by the `output` field. Each picture in image will be cropped and saved. The filename of picture area is their coordinates in the image. Layout analysis results will be stored in the `res.txt` file

<a name="1.3"></a>
### 1.3 table recognition
```bash
python3 predict_system.py --det_model_dir=inference/ch_PP-OCRv3_det_infer \
                          --rec_model_dir=inference/ch_PP-OCRv3_rec_infer \
                          --table_model_dir=inference/ch_ppstructure_mobile_v2.0_SLANet_infer \
                          --image_dir=./docs/table/table.jpg \
                          --rec_char_dict_path=../ppocr_/utils/ppocr_keys_v1.txt \
                          --table_char_dict_path=../ppocr_/utils/dict/table_structure_dict_ch.txt \
                          --output=../output \
                          --vis_font_path=../doc/fonts/simfang.ttf \
                          --layout=false
```
After the operation is completed, each image will have a directory with the same name in the `structure` directory under the directory specified by the `output` field. Each table in the image will be stored as an excel. The filename of excel is their coordinates in the image.

<a name="2"></a>
## 2. Key Information Extraction

```bash
cd ppstructure

mkdir inference && cd inference
# download model
wget https://paddleocr.bj.bcebos.com/ppstructure/models/vi_layoutxlm/ser_vi_layoutxlm_xfund_infer.tar && tar -xf ser_vi_layoutxlm_xfund_infer.tar
cd ..
python3 kie/predict_kie_token_ser.py \
  --kie_algorithm=LayoutXLM \
  --ser_model_dir=../inference/ser_vi_layoutxlm_xfund_infer \
  --image_dir=./docs/kie/input/zh_val_42.jpg \
  --ser_dict_path=../ppocr_/utils/dict/kie_dict/xfund_class_list.txt \
  --vis_font_path=../doc/fonts/simfang.ttf \
  --ocr_order_method="tb-yx"
```

After the operation is completed, each image will store the visualized image in the `kie` directory under the directory specified by the `output` field, and the image name is the same as the input image name.
