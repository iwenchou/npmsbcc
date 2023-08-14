from flask import Flask, render_template, request
import openai

app = Flask(__name__)

openai.api_key = "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"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate_response", methods=["POST"])
def generate_response():
    category = request.form.get("category")
    feedback = request.form.get("feedback")
    investigation = request.form.get("investigation")

    # 建立 ChatGPT 的 prompt
    prompt = f"現在開始你將擔任國立故宮博物院南部院區（故宮南院）的資深博物館館員，除了要熟捻中國歷史與亞洲藝術史，文化人類學等相關研究領域，還有博物館學典藏、文物維護、展示、教育等相關專業知識，並了解故宮南院官方的回覆綱領，以溫柔堅定並且專業的口吻，表達1. 誠懇的致歉 2.說明理由或解決方案 3. 感謝觀眾諒解並期待觀眾再度來訪光臨。"
    
    # 構建 ChatGPT 輸入
    chatgpt_input = f"觀眾意見類別：{category}\n觀眾意見內容：{feedback}\n業管單位調查：{investigation}\n"
    prompt += chatgpt_input
    
    # 使用 ChatGPT 生成回應
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        max_tokens=350
    )
    
    official_response = response.choices[0].text.strip()
    return render_template("index.html", response=official_response)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

