# 下载相关依赖和安装clip

## wsm_pro.ipynb

下载和安装相关依赖（强烈建议在anaconda虚拟环境下进行，避免破坏本机环境，我的python版本是3.8

```shell
!git clone https://github.com/openai/CLIP.git
!pip install -r requirements.txt
```

安装CLIP包

```shell
!pip install .\CLIP
```

由于clip内部设置和网络的原因，下面这步中``` Vit-B-32-pt```这个模型在下载的时候会有问题，所以我预先下载了

```python
model, preprocess = clip.load("ViT-B-32.pt", device=device)
```

其余部分为统计图片数量和计算图片特征并存储，注意将路径改为**本地路径**

## search.ipynb

基于之前算出的特征进行查询，可以自行定义查询语句和返回图片数量

## 参考

[haltakov/natural-language-image-search: Search photos on Unsplash using natural language (github.com)](https://github.com/haltakov/natural-language-image-search)