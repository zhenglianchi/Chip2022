
# PP-OCR模型库
PP-OCR模型一节主要补充一些OCR模型的基本概念以及如何快速运用PP-OCR模型库中的模型。

本节包含两个部分，首先在[PP-OCR模型下载](./models_list.md)中解释PP-OCR模型的类型概念，并提供所有模型的下载链接。然后在[基于Python引擎的PP-OCR模型库推理](./inference_ppocr_.md)中介绍PP-OCR模型库的使用方法，可以通过Python推理引擎快速利用丰富的模型库模型获得测试结果。

------

下面我们首先了解一些OCR相关的基本概念：

- [1. OCR 简要介绍](#1-ocr-----)
  * [1.1 OCR 检测模型基本概念](#11-ocr---------)
  * [1.2 OCR 识别模型基本概念](#12-ocr---------)
  * [1.3 PP-OCR模型](#13-pp-ocr--)

<a name="1-ocr-----"></a>
## 1. OCR 简要介绍
本节简要介绍OCR检测模型、识别模型的基本概念，并介绍PaddleOCR的PP-OCR模型。

OCR（Optical Character Recognition，光学字符识别）目前是文字识别的统称，已不限于文档或书本文字识别，更包括识别自然场景下的文字，又可以称为STR（Scene Text Recognition）。

OCR文字识别一般包括两个部分，文本检测和文本识别；文本检测首先利用检测算法检测到图像中的文本行；然后检测到的文本行用识别算法去识别到具体文字。

<a name="11-ocr---------"></a>
### 1.1 OCR 检测模型基本概念

文本检测就是要定位图像中的文字区域，然后通常以边界框的形式将单词或文本行标记出来。传统的文字检测算法多是通过手工提取特征的方式，特点是速度快，简单场景效果好，但是面对自然场景，效果会大打折扣。当前多是采用深度学习方法来做。

基于深度学习的文本检测算法可以大致分为以下几类：
1. 基于目标检测的方法；一般是预测得到文本框后，通过NMS筛选得到最终文本框，多是四点文本框，对弯曲文本场景效果不理想。典型算法为EAST、Text Box等方法。
2. 基于分割的方法；将文本行当成分割目标，然后通过分割结果构建外接文本框，可以处理弯曲文本，对于文本交叉场景问题效果不理想。典型算法为DB、PSENet等方法。
3. 混合目标检测和分割的方法；

<a name="12-ocr---------"></a>
### 1.2 OCR 识别模型基本概念

OCR识别算法的输入数据一般是文本行，背景信息不多，文字占据主要部分，识别算法目前可以分为两类算法：
1. 基于CTC的方法；即识别算法的文字预测模块是基于CTC的，常用的算法组合为CNN+RNN+CTC。目前也有一些算法尝试在网络中加入transformer模块等等。
2. 基于Attention的方法；即识别算法的文字预测模块是基于Attention的，常用算法组合是CNN+RNN+Attention。

<a name="13-pp-ocr--"></a>
### 1.3 PP-OCR模型

PaddleOCR 中集成了很多OCR算法，文本检测算法有DB、EAST、SAST等等，文本识别算法有CRNN、RARE、StarNet、Rosetta、SRN等算法。

其中PaddleOCR针对中英文自然场景通用OCR，推出了PP-OCR系列模型，PP-OCR模型由DB+CRNN算法组成，利用海量中文数据训练加上模型调优方法，在中文场景上具备较高的文本检测识别能力。并且PaddleOCR推出了高精度超轻量PP-OCRv2模型，检测模型仅3M，识别模型仅8.5M，利用[PaddleSlim](https://github.com/PaddlePaddle/PaddleSlim)的模型量化方法，可以在保持精度不降低的情况下，将检测模型压缩到0.8M，识别压缩到3M，更加适用于移动端部署场景。
