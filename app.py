from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os

app = Flask(__name__)

# 設定 LineBot 的資訊
line_bot_api = LineBotApi('YOUR_CHANNEL_ACCESS_TOKEN')
handler = WebhookHandler('YOUR_CHANNEL_SECRET')

@app.route('/callback', methods=['POST'])
def callback():
    # 獲取 X-Line-Signature 進行驗證
    signature = request.headers['X-Line-Signature']

    # 取得請求的內容
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@app.route('/')
def hello():
    return "Hello, this is your Flask server!"


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # 回覆一個固定的文字訊息
    reply_message = TextSendMessage(text="您好，請輸入觀眾意見內容！")
    line_bot_api.reply_message(event.reply_token, reply_message)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
