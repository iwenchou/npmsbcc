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

def generate_official_response(feedback, initial_response):
    prompt = f"觀眾反應：{feedback}\n業管單位的初步回應：{initial_response}\n正式回覆："
    
    response = openai.Completion.create(
        model="text-davinci-003",  # 或其他您喜歡的模型
        prompt=prompt,
        max_tokens=150-300  # 您可以根據需要調整生成回覆的長度
    )
    
    official_response = response.choices[0].text.strip()
    return official_response

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text
    feedback = "一個國家級博物館，北邊等車排隊的地方用小石子鋪路，請問是沒有經費了嗎?!"
    initial_response = "(1)現為碎石子鋪面之排隊動線處(3m*12m)，將更換為透水磚地坪。"
    chatgpt_response = generate_chatgpt_response(feedback, initial_response)
    reply_message = TextSendMessage(text=chatgpt_response)
    line_bot_api.reply_message(event.reply_token, reply_message)

def generate_chatgpt_response(feedback, initial_response):
    prompt = f"觀眾反應：{feedback}\n業管單位的初步回應：{initial_response}\n正式回覆："
    
    response = openai.Completion.create(
        engine="text-davinci-003",  # 或其他您喜歡的模型
        prompt=prompt,
        max_tokens=150  # 您可以根據需要調整生成回覆的長度
    )
    
    official_response = response.choices[0].text.strip()
    return official_response
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


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
