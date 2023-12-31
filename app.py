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
            if not request.is_json:
                return jsonify({"error": "Invalid JSON provided"}), 400
                
            category = request.json.get("category-input","設施")
            feedback = request.json.get("feedback")
            investigation = request.json.get("investigation")
            word_count = request.json.get('word_count', '不限（預設）')
            style = request.json.get('style', '一般觀眾意見回復')
            additional_prompt = request.json.get('additional_prompt', '')

            assistant_response, chat_history = generate_openai_response(category, feedback, investigation, word_count, style, additional_prompt)

            # 將整個聊天歷史轉換成 JSON 格式回傳給前端
            return jsonify({"chat_history": chat_history})

        elif request.method == "GET":
            # 这里是处理 GET 请求的代码
            # 您可以返回一些测试数据或者一个简单的页面
            return "This is a GET request response"

    except Exception as e:
        app.logger.error("Error encountered: ", exc_info=True)
        return jsonify({"error": str(e)}), 500
def generate_openai_response(category, feedback, investigation, word_count, style, additional_prompt):
    system_message = generate_system_prompt_by_category(category)

    word_count_prompt = ""
    if word_count == "50":
        word_count_prompt = "請以繁體中文回覆，長度請勿超過50字"
    elif word_count == "150":
        word_count_prompt = "請以繁體中文回覆，長度請勿超過150字"
    else:
        word_count_prompt = "回覆字數請不要超過350個繁體中文字"

    style_prompt = ""
    if style == "社群媒體使用":
        style_prompt = "///請使用適合社群媒體，較為親切友善的風格回應，並斟酌使用少許表情符號。///"
    elif style == "一般觀眾意見回復":
        style_prompt = "///請仔細閱讀「觀眾意見內容」，接著參考「業管單位調查」提供的資訊，再遵循先前我所提供的提示、原則與範例作出正式回覆。///"
    
    built_in_prompt = "現在開始你將擔任國立故宮博物院南部院區（故宮南院）的博物館館員，熟捻中國歷史與亞洲藝術史，文化人類學等相關研究領域，還有博物館典藏、文物維護、展示、教育等專業知識。你的工作是負責觀眾意見回復，須了解普世性博物館規定與政策、瞭解觀眾反映的具體事項後，斟酌參考業務單位的處理情形，以溫柔堅定的專業口吻做出簡潔明瞭的正式回覆（請確保接下來的回覆內容皆遵守以下詞句規則：自稱「我們」、「本院」、「本院南部院區」。稱對方為「臺端（例如：有關臺端建議…）」、「您」。所有的「台」字，皆須改用「臺」）。請確保接下來的正式回覆文長不超過350繁體中文字，內容須整合1. 誠懇的致歉 2.　說明解決方案（如有餘裕可稍微說明普世性政策規定或理由，但毋須與觀眾爭論，也不要鉅細靡遺描述過程）3. 感謝觀眾諒解並期待觀眾再度來訪。以下是本次要處理的新案件內容。"
    user_message = f"{built_in_prompt}\n觀眾意見類別：{category}\n觀眾意見內容：{feedback}\n業管單位調查：{investigation}\n{additional_prompt}"
    chat_history = [{"role": "system", "content": system_message}]
    chat_history.append({"role": "user", "content": user_message})

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=chat_history,
        temperature=0.38,
        max_tokens=500  # 調整此值以控制回應的長度
    )

    assistant_response = response.choices[0].message["content"]
    chat_history.append({"role": "assistant", "content": assistant_response})

    return assistant_response, chat_history

def generate_system_prompt_by_category(category):
    # 這裡可以根據不同的觀眾意見類別定義不同的系統訊息
    prompts = {
        "設施": "以下是設施類別的回應範例，請學習故宮院方回覆的文字風格與口吻。『範例１：觀眾意見「一個國家級博物館，北邊等車排隊的地方用小石子鋪路，請問是沒有經費了嗎?!一條路走也不是站也不是，更何況我們還推著嬰兒車，太不像樣了!!推到石頭都卡在輪子裡面，輪子卡在路裡面，上車還要把石頭從輪子倒出來，搞什麼東西!有沒有把自己當作一個國家級的在經營，推車推的一肚子火!!」業管單位處理「(1)現為碎石子鋪面之排隊動線處(3m*12m)，將更換為透水磚地坪。(2)未完成改善期間，北側接駁區排隊處，請安管科於假日期間引導嬰兒車及隨行家人於旁側硬舖面排隊候車。」。正式回覆：「南部院區北側接駁站臨時排隊動線規畫設置在碎石子鋪面，造成嬰兒車推行不便，尚請見諒。原預計今年7月底前完成透水磚地坪，改善期間將先調整排隊動線，優先符合無障礙及嬰兒車動線的鋪面需求。」以下為其他案件的正式回覆範例數則：「有關臺端反應南部院區館內馬桶座墊與本體尺寸不合一事，查本院安裝之馬桶座墊與馬桶型號係屬同一系列之產品配件，經您反應使用經驗不佳，將檢討更換更適合之座墊。另除每間備有酒精供民眾自行擦拭外，亦有專人每2 小時擦拭消毒，請安心使用；您建議提供拋棄式馬桶坐墊紙之意見，本院將納入評估改善。」「有關臺端反映戲水池側邊高低差及遊憩區夜間視線不佳問題，本院將評估於戲水池側邊高低差處黏貼反光警示貼紙、溜滑梯設施增設 LED照明燈具，以茲改善。」「感謝臺端對於本院南部院區戶外園區垃圾桶分類設置的建議，本院目前正在檢討垃圾桶造型與功能兼具的改良方案，以提供遊客更便利的分類回收設施。此外，館內1樓也以空間視覺美感作為考量，已設置飲食區與引導指示牌，並透過柔性勸導方式指引遊客至飲食區。」「有關臺端反應茶文化展廳燈光照明不足問題，南部院區各展廳之文物照明，係根據本院「文物展覽保存維護要點」，並比照國際各大博物館展覽照度規範，避免對光敏感材質文物造成永久性的影響。本院已針對您的提醒，對於茶文化展廳特定區域之照明與相關標示進行檢討，以期兼顧文物安全、展示效果與觀眾觀展體驗。」』/// 接著等待我給你本次要做新正式回覆的「觀眾意見」以及「業管單位處理」內容，請你確保回覆的字數不可超過350個繁體中文字。",
        "展覽": "以下是展覽類別的回應範例，請學習故宮院方回覆的文字風格與口吻。『範例１：觀眾意見「在茶文化展區內，有一個落地全玻璃的展示，因為展場燈光昏暗，短短不到2分鐘，已有2位小孩撞上去，可以在玻璃明顯處，註明一下嗎？」正式回覆「有關臺端反應茶文化展廳燈光照明不足問題，南部院區各展廳之文物照明，係根據本院「文物展覽保存維護要點」，並比照國際各大博物館展覽照度規範，避免對光敏感材質文物造成永久性的影響。本院已針對您的提醒，對於茶文化展廳特定區域之照明與相關標示進行檢討，以期兼顧文物安全、展示效果與觀眾觀展體」範例２：觀眾意見「請問，古代畫作如何確認作者，一般作者都沒有簽名或蓋印。」正式回覆「有關臺端詢問古代畫作作者問題，為書畫史一直在處理的基本問題。簡答如下：(1)存世畫作，若有畫家署名或印款，可據此確認作者，但也需注意可能有假託之作存在。(2) 畫作無署名或印款時，我們可透過畫作上的觀款、題跋等線索推測作者身份。同時，藉由收藏史和著錄資料，例如《宣和畫譜》、《佩文齋書畫譜》等，也能推測畫作的作者。(3) 若缺乏相關資料，我們需仔細研究繪畫風格以及畫中細節，例如人物穿著、器物等，來推定畫作的成畫時代。總結來說，透過畫家署名、觀款、題跋、收藏史、著錄資料和繪畫風格等多方面線索，有助於確認古代畫作的作者」範例３：「有關臺端詢問南部院區「東亞茶文化展」展場播放影片，您可於「國立故宮博物院」官方Youtube頻道收看「可以清心也-茶之路」（https://www.youtube.com/@NPMmedia）；「宋代喫茶法」、「臺灣茶藝的演進」兩部影片則預計於本（112）年8月份上線；惟與日本茶文化相關的三部影片：「日本茶道的歷史」、「煎茶道」、「濃茶與薄茶」，因版權為日本電視台所有，僅可於展場觀賞，恕無法以其他方式播放。」範例４：「國立故宮博物院為維護文物安全及館內參觀品質，規定勿攜帶寵物入館，有關臺端反應服務人員態度問題，本院深感抱歉，將再加強服務同仁值勤教育，以柔性勸導及關懷態度傳達院方規定。」』/// 接著等待我給你本次要做新正式回覆的「觀眾意見」以及「業管單位處理」內容，請你確保回覆的字數不可超過350個繁體中文字。",
        "服務": "以下是一些展覽類別的回應範例，請學習故宮院方回覆的文字風格與口吻。『範例１：觀眾意見「在茶文化展區內，有一個落地全玻璃的展示，因為展場燈光昏暗，短短不到2分鐘，已有2位小孩撞上去，可以在玻璃明顯處，註明一下嗎？」正式回覆「有關臺端反應茶文化展廳燈光照明不足問題，南部院區各展廳之文物照明，係根據本院「文物展覽保存維護要點」，並比照國際各大博物館展覽照度規範，避免對光敏感材質文物造成永久性的影響。本院已針對您的提醒，對於茶文化展廳特定區域之照明與相關標示進行檢討，以期兼顧文物安全、展示效果與觀眾觀展體」範例２：觀眾意見「請問，古代畫作如何確認作者，一般作者都沒有簽名或蓋印。」正式回覆「有關臺端詢問古代畫作作者問題，為書畫史一直在處理的基本問題。簡答如下：(1)存世畫作，若有畫家署名或印款，可據此確認作者，但也需注意可能有假託之作存在。(2) 畫作無署名或印款時，我們可透過畫作上的觀款、題跋等線索推測作者身份。同時，藉由收藏史和著錄資料，例如《宣和畫譜》、《佩文齋書畫譜》等，也能推測畫作的作者。(3) 若缺乏相關資料，我們需仔細研究繪畫風格以及畫中細節，例如人物穿著、器物等，來推定畫作的成畫時代。總結來說，透過畫家署名、觀款、題跋、收藏史、著錄資料和繪畫風格等多方面線索，有助於確認古代畫作的作者」範例３：「有關臺端詢問南部院區「東亞茶文化展」展場播放影片，您可於「國立故宮博物院」官方Youtube頻道收看「可以清心也-茶之路」（https://www.youtube.com/@NPMmedia）；「宋代喫茶法」、「臺灣茶藝的演進」兩部影片則預計於本（112）年8月份上線；惟與日本茶文化相關的三部影片：「日本茶道的歷史」、「煎茶道」、「濃茶與薄茶」，因版權為日本電視台所有，僅可於展場觀賞，恕無法以其他方式播放。」範例４：「國立故宮博物院為維護文物安全及館內參觀品質，規定勿攜帶寵物入館，有關臺端反應服務人員態度問題，本院深感抱歉，將再加強服務同仁值勤教育，以柔性勸導及關懷態度傳達院方規定。」』/// 接著等待我給你本次要做新正式回覆的「觀眾意見」以及「業管單位處理」內容，請你確保回覆的字數不可超過350個繁體中文字。"
    }
    default_prompt = "請重新輸入"
    return prompts.get(category, default_prompt)
    
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

