# app.py

import os
import logging
import sys
import requests
import glob
from flask import Flask ,render_template,redirect,url_for,request, abort
import cloudinary
import cloudinary.uploader
from cloudinary.uploader import upload
import cloudinary.api
from cloudinary.utils import cloudinary_url
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,ImageMessage,
    VideoMessage,AudioMessage,LocationMessage,StickerMessage,
    FileMessage,
)

app = Flask(__name__)

#ログを標準出力にする
app.logger.addHandler(logging.StreamHandler(sys.stdout))

#Cloudinary設定
cloudinary.config(
    cloud_name = "yu1991ta",
    api_key = "648747536824239",
    api_secret = "F_PpehZ1SXIZKIYTZMynMHTENzw"
)

#Lineチャネル設定
YOUR_CHANNEL_ACCESS_TOKEN = "1z5F956PvFaWUAgqKQftoqvFFWHskSmpCFEQPIxhy1CFd+x+BEro/fNwrZ+77Ww4Wi+Pck3EkUEyG/W2Hj4zB7PpUxCp0fHW6bxs5g/L9stHF7zAH9shKwu/q4v0S0apcrCJlK/TrQCr9tyypYLCYwdB04t89/1O/w1cDnyilFU="
YOUR_CHANNEL_SECRET =  "9bbc72e90a42c22ff505d1541dd8ea49"

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

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

#LineWebhoook取得
@app.route("/callback", methods=['POST'])
def callback():
    # signature取得
    signature = request.headers['X-Line-Signature']

    # リクエストBody取得
    body = request.get_data(as_text=True)

    #ログ　Line(Webhook)リクエストボディ
    app.logger.info("★★.Request body: " + body)

    try:
        #イベントハンドラ
        handler.handle(body, signature)
    except InvalidSignatureError:
        #signatureエラー
        abort(400)
    return 'OK'

#★★以下ハンドラ処理★★

#テキストメッセージの場合
#TODO:オウム返しではなく、メッセージ返せるように修正する
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text))

#画像ファイルの場合
@handler.add(MessageEvent, message=ImageMessage)
def handle_message_image(event):

    #LineからメッセージID取得
    messageId = event.message.id

    #Lineから画像のバイナリデータを取得
    messageContent = line_bot_api.get_message_content(messageId)
    
    #cloudinaryにアプロードするためにローカルに一時保存
    with open(f"static/tmpImage/{messageId}.jpg", "wb") as f:
        # バイナリを1024バイトずつ書き込む
        for chunk in messageContent.iter_content():
            f.write(chunk)

    #ログ　ローカルに保存されているファイルリスト取得
    fileList = glob.glob(f"static/tmpImage/*.jpg")
    for file in fileList:
        app.logger.info("★★fileList: " + file)

    #CloudinaryへUpload
    res = cloudinary.uploader.upload(file=f"static/tmpImage/{messageId}.jpg",folder='01.WeddingPhoteSlide')

    #リプライ
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text='ナイスですね～')
    )

#その他ファイルの場合(音声、動画などなど。。。)
@handler.add(MessageEvent, message=(VideoMessage,AudioMessage,LocationMessage,
StickerMessage,FileMessage))
def handle_message_other(event):
    #リプライ
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text='ありがとう！でもその形式は対応してないよ！ごめんね！')
    )

if __name__ == '__main__':

    #デバッグ用
    #app.run(debug=True)

    #Heroku用
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)



