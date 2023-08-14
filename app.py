from flask import Flask, render_template, request
import openai
import os

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

    # 根據選擇的類別載入對應的範本
    if category == "設施":
        category_template = "觀眾反應1 ：一個國家級博物館，北邊等車排隊的地方用小石子鋪路，請問是沒有經費了嗎?!一條路走也不是站也不是，更何況我們還推著嬰兒車，太不像樣了!!推到石頭都卡在輪子裡面，輪子卡在路裡面，上車還要把石頭從輪子倒出來，搞什麼東西!有沒有把自己當作一個國家級的在經營，推車推的一肚子火!!業管單位的初步回應1：現為碎石子鋪面之排隊動線處(3m*12m)，將更換為透水磚地坪。未完成改善期間，北側接駁區排隊處，請安管科於假日期間引導嬰兒車及隨行家人於旁側硬舖面排隊候車。。正式回覆1：南部院區北側接駁站臨時排隊動線規畫設置在碎石子鋪面，造成嬰兒車推行不便，尚請見諒。原預計今年7月底前完成透水磚地坪，改善期間將先調整排隊動線，優先符合無障礙及嬰兒車動線的鋪面需求。"
    elif category == "展覽":
        category_template = "觀眾反應2：在茶文化展區內，有一個落地全玻璃的展示，因為展場燈光昏暗，短短不到2分鐘，已有2位小孩撞上去，可以在玻璃明顯處，註明一下嗎？正式回覆2：有關臺端反應茶文化展廳燈光照明不足問題，南部院區各展廳之文物照明，係根據本院「文物展覽保存維護要點」，並比照國際各大博物館展覽照度規範，避免對光敏感材質文物造成永久性的影響。本院已針對您的提醒，對於茶文化展廳特定區域之照明與相關標示進行檢討，以期兼顧文物安全、展示效果與觀眾觀展體驗。"
    elif category == "服務":
        category_template = "觀眾反應3：民眾早上於遊客中心詢問園區接駁車時刻，回復接駁時刻為15分與45分，另詢問有7、80歲老人家，遊客中心表示回程可派無障礙接駁車接駁。民眾反映回復的時刻讓人誤會為15分鐘即有一班車，導致搭乘106班次公車需再等候1小時，回程時亦有致電遊客中心欲叫無障礙接駁車，卻回復目前因人力無法派無障礙接駁車過去，與早上告知情形不同。業管單位回應3：遊客13:50於本館站告知保全欲搭乘園區接駁車至南側，再轉乘14:08發車之106公車往民雄，保全告知遊客本館站發車時間為15分及45分，遊客誤以為接駁車為15分鐘1班車。後續保全建議遊客可步行至南側，尚能趕上公車，惟遊客考量有長輩同行無法步行，請保全協助派無障礙接駁車；經電洽遊客中心，當時無障礙接駁車皆已出車，尚無空車及駕駛可協助接駁，須請遊客稍候，後續遊客於本館站搭乘14:15園區接駁車離場。遊客返回南側後，至遊客中心反映本起事件，並於遊客中心撥打客服電話。正式回覆3：本院南部院區提供無障礙接駁服務，供行動不便及陪同人士搭乘，惟臺端反映無法派遣接駁車接送一事，因適逢假日人潮較多，當時無障礙接駁車皆已出車，無空車及駕駛可立即協助接駁，造成您的不便，敬請見諒。另有關乘車資訊說明方式，本院將再加強一線服務人員教育訓練，感謝您的指導與建議，歡迎您再次蒞臨參觀。"
    else:
        category_template = "未知類別的範本"

    # 建立 ChatGPT 的 prompt
    prompt = f"現在開始你將擔任國立故宮博物院南部院區（故宮南院）的資深博物館館員，除了要熟捻中國歷史與亞洲藝術史，文化人類學等相關研究領域，還有博物館學典藏、文物維護、展示、教育等相關專業知識，並了解故宮南院官方的回覆綱領，以溫柔堅定並且專業的口吻，表達1. 誠懇的致歉 2.說明理由或解決方案 3. 感謝觀眾諒解並期待觀眾再度來訪光臨。接下來我將給你一些過往範本，讓你參考文本的口吻，也請你用相同的優雅口吻來撰寫正式回答，比如需自稱「本院」或「本院南部院區」，稱對方「臺端」、「您」。撰擬回答時，請務必清楚了解觀眾反映、抱怨、疑問的事項後，再閱讀業管單位初步調查後的結果與回覆，最終再做成正式的回應。"
    prompt += f"觀眾意見類別：{category}\n範本：{category_template}\n觀眾意見內容：{feedback}\n業管單位調查：{investigation}\n"

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
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

