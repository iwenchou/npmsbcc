from flask import Flask, render_template, request, jsonify
import openai
import os
import threading

app = Flask(__name__)

openai.api_key = os.environ.get("OPENAI_API_KEY")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate_response", methods=["GET", "POST"])
def generate_response():
    try:
        if request.method == "POST":
            category = request.json["category"]
            feedback = request.json["feedback"]
            investigation = request.json["investigation"]

            assistant_response, chat_history = generate_openai_response(category, feedback, investigation)

            # 將整個聊天歷史轉換成 JSON 格式回傳給前端
            return jsonify({"chat_history": chat_history})

        elif request.method == "GET":
            # 这里是处理 GET 请求的代码
            # 您可以返回一些测试数据或者一个简单的页面
            return "This is a GET request response"

    except Exception as e:
        app.logger.error("Error encountered: ", exc_info=True)
        return jsonify({"error": str(e)}), 500

def generate_openai_response(category, feedback, investigation):
    system_message = "現在開始你將擔任國立故宮博物院南部院區（故宮南院）的資深博物館館員，除了要熟捻中國歷史與亞洲藝術史，文化人類學等相關研究領域，還有博物館學典藏、文物維護、展示、教育等相關專業知識，並了解故宮南院官方的回覆綱領，以溫柔堅定並且專業的口吻，表達1. 誠懇的致歉 2.說明理由或解決方案 3. 感謝觀眾諒解並期待觀眾再度來訪光臨。請留意以『本院』、『本院南部院區』自稱，稱呼觀眾為『臺端』、『您』，請務必瞭解觀眾反映的具體事項，並斟酌參考業務單位的調查，用最簡潔俐落的方式回覆觀眾，切勿鉅細彌遺描述過程，整個回覆內容請勿超過350繁體中文字，在350繁體中文字以內把整個回覆講完。"
    user_message = f"觀眾意見類別：{category}\n觀眾意見內容：{feedback}\n業管單位調查：{investigation}\n"

    chat_history = [{"role": "system", "content": system_message}]
    chat_history.append({"role": "user", "content": user_message})

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=chat_history,
        temperature=0.38,
        max_tokens=800  # 調整此值以控制回應的長度
    )

    assistant_response = response.choices[0].message["content"]
    chat_history.append({"role": "assistant", "content": assistant_response})

    return assistant_response, chat_history
    
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

