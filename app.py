# app.py

import os
import logging
import sys
from flask import Flask ,render_template,redirect,url_for
import cloudinary
import cloudinary.uploader
from cloudinary.uploader import upload
import cloudinary.api
from cloudinary.utils import cloudinary_url


app = Flask(__name__)

#ログを標準出力にする
app.logger.addHandler(logging.StreamHandler(sys.stdout))

#Cloudinary設定
cloudinary.config(
    cloud_name = "yu1991ta",
    api_key = "648747536824239",
    api_secret = "F_PpehZ1SXIZKIYTZMynMHTENzw"
)

#初期画面
@app.route("/")
def index():
    return render_template('index.html')

#スライドショー
@app.route("/phote_slide")
def phote_slide():

    #TODO:DBから画像URLを取得できるように修正

    #Cloudinaryから画像一覧を取得
    #直近15枚の画像を取得
    img_list = cloudinary.api.resources(type="upload",max_results=15,direction = -1)

    #ログ　取得したリソース情報を表示
    for image in img_list["resources"]:
        print(image)

    #スライドショー画面遷移　パラメータ：画像一覧
    return render_template('phote_slide.html',img_list=img_list["resources"])


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True)
    #Heroku用
    #app.run(host='0.0.0.0', port=port)



