from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os
import openai

app = Flask(__name__)

# 設定 LineBot 的資訊
line_bot_api = LineBotApi('iDjMaHRLHqMapczUxFZl4snKGjDQgHbfDj1e9HIGFTeHDruGq7ckV2d8fz7XA6fyZ0qAhB6xtSyeTj0yf6nepK+jcdY0G7YFoMWnQHfegMoXZfdSSehQPLAPrIbGItfMiZ4NePvoI0hjTWyhAEIiwwdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('e34a22c11a857de4dec2c631b43e59d2')

# 設定您的 ChatGPT API 存取權杖
openai.api_key = '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'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # 從使用者取得訊息內容
    user_message = event.message.text

    # 使用 ChatGPT 生成回覆
    chatgpt_response = generate_chatgpt_response(user_message)

    # 回覆 ChatGPT 生成的訊息
    reply_message = TextSendMessage(text=chatgpt_response)
    line_bot_api.reply_message(event.reply_token, reply_message)

def generate_chatgpt_response(input_text):
    # 調用 ChatGPT API 生成回覆
    response = openai.Completion.create(
        engine="davinci",  # 選擇適合的引擎
        prompt=input_text,
        max_tokens=50  # 控制回覆長度
    )
    return response.choices[0].text.strip()

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
