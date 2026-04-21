from flask import Flask, request, render_template
import requests

app = Flask(__name__)

# 韓文題庫保留
zh_ko_dict = {
    "你好": "안녕하세요",

    "안녕하세요" : "你好",

    "謝謝": "감사합니다",

    "對不起": "죄송합니다",

    "早安": "좋은 아침",

    "晚安": "안녕히 주무세요",

    "老師": "선생님",

    "學生": "학생",

    "朋友": "친구",

    "Pikmin": "皮克敏",

    "家人": "가족",
    
    "愛": "사랑"    
}

@app.route('/')
def index():
    return render_template('index.html')

# 韓文查詢
@app.route('/ask', methods=['GET', 'POST'])
def ask():
    question = ""
    answer = ""
    if request.method == 'POST':
        question = request.form.get('question', '').strip()
        answer = zh_ko_dict.get(question, "抱歉，我目前沒有這個詞的韓文對應。")
    return render_template('ask.html', question=question, answer=answer)

# 股票查詢 - 使用 TWSE OpenAPI
@app.route('/stock', methods=['GET', 'POST'])
def stock():
    question = ""
    answer = ""
    if request.method == 'POST':
        question = request.form.get('question', '').strip()  # 使用者輸入的代號，如 2330
        
        try:
            # 1. 向證交所 API 發送請求
            # 取得所有股票當日的收盤資訊
            api_url = "https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_AVG_ALL"
            response = requests.get(api_url)
            
            if response.status_code == 200:
                data = response.json()  # API 回傳的是一個清單 (List)
                
                # 2. 在清單中搜尋符合的股票代號
                # 資料格式範例：[{"Code":"2330","Name":"台積電","ClosingPrice":"780.00"}, ...]
                stock_item = next((item for item in data if item["Code"] == question), None)
                
                if stock_item:
                    name = stock_item["Name"]
                    price = stock_item["ClosingPrice"]
                    answer = f"股票：{name} ({question})，最新收盤價：{price} 元"
                else:
                    answer = f"在證交所資料中找不到代號 {question}。請確認輸入是否正確。"
            else:
                answer = "暫時無法連線至證交所 API，請稍後再試。"
                
        except Exception as e:
            print(f"Error: {e}")
            answer = "程式執行發生錯誤，請檢查網路連線。"
            
    return render_template('stock.html', question=question, answer=answer)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
