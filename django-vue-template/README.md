前端Vue后端Django，网上偷来的模版，大伙更喜欢用Flask或者其他的也可以换

首先跑一边主目录的wsm_pro.ipynb（也可以进入pipenv环境后再跑），得到预处理目录文件image_dataset（里面有image_dataset和features两个目录）


## 所用工具
用到的有yarn和pipenv，建议用npm安装yarn
```
$ sudo npm install -g yarn
$ yarn --version
```

## 安装配置

```
$ cd django-vue-template
$ vi Pipfile
```
把python_version改成自己的python版本号，默认是3.10
```
$ yarn install
$ pipenv install --dev && pipenv shell
$ pip install whitenoise --upgrade  //这步不做可能会报错
$ python manage.py migrate
```
然后安装clip所需依赖，具体看主目录下的README
把image_dataset和模型ViT-B-32.pt放到backend/media文件下


## 后端运行

```
$ python manage.py runserver
```
默认在localhost:8000

## 前端运行
再新开个终端
```
$ cd django-vue-template
$ yarn serve
```
默认在localhost:8080

什么ui都没写，上传功能也没有，就是测试一下能不能跑的demo😢
前端在src/components/Search.vue里
search的接口实现在backend/api/views.py里的search_images，要加新的接口记得在urls.py文件中的urlpatterns里加一下
感觉不用加新的component了，是不是只用改view.py，urls.py，Search.vue三个文件就行了捏🤔
