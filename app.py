from flask import Flask, request, render_template
import requests
import urllib3

# 停用 SSL 警告訊息
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

# 韓文題庫
zh_ko_dict = {
    "你好": "안녕하세요",
    "謝謝": "감사합니다",
    "老師": "선생님",
    "學生": "학생",
    "愛": "사랑"
}

@app.route('/')
def index():
    return render_template('index.html')

# 韓文翻譯路由
@app.route('/ask', methods=['GET', 'POST'])
def ask():
    question = ""
    answer = ""
    if request.method == 'POST':
        question = request.form.get('question', '').strip()
        answer = zh_ko_dict.get(question, "抱歉，我目前沒有這個詞的韓文對應。")
    return render_template('ask.html', question=question, answer=answer)

# 股票/指數查詢路由
@app.route('/stock', methods=['GET', 'POST'])
def stock():
    question = ""
    answer = ""
    if request.method == 'POST':
        question = request.form.get('question', '').strip() # 使用者輸入，例如「發行量加權股價指數」
        
        try:
            # 這是大盤指數的 API 網址
            api_url = "https://openapi.twse.com.tw/v1/indices/TWT48U"
            response = requests.get(api_url, timeout=10, verify=False)
            
            if response.status_code == 200:
                data = response.json()
                
                # 在列表中尋找符合的指數名稱
                # 你提供的格式包含：日期, 指數, 收盤指數, 漲跌, 漲跌點數, 漲跌百分比
                item = next((i for i in data if i.get("指數") == question or question in i.get("指數", "")), None)
                
                if item:
                    date = item.get("日期")
                    idx_name = item.get("指數")
                    close = item.get("收盤指數")
                    change_sign = item.get("漲跌") # 可能是 + 或 -
                    change_point = item.get("漲跌點數")
                    change_percent = item.get("漲跌百分比")
                    
                    answer = f"日期：{date} | 指數：{idx_name} | 收盤：{close} | 漲跌：{change_sign}{change_point} ({change_percent}%)"
                else:
                    answer = f"找不到「{question}」的資料。請試著輸入「發行量加權股價指數」。"
            else:
                answer = "證交所 API 連線失敗。"
                
        except Exception as e:
            print(f"DEBUG: {e}")
            answer = f"系統錯誤：{str(e)}"
            
    return render_template('stock.html', question=question, answer=answer)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
