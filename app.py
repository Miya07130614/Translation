from flask import Flask, request, render_template

app = Flask(__name__)

# 1. 建立韓文翻譯題庫
zh_ko_dict = {
    "你好": "안녕하세요",
    "謝謝": "감사합니다",
    "對不起": "죄송합니다",
    "老師": "선생님",
    "學生": "학생"
}

# 2. 建立股票價格資料庫 (範例資料)
stock_dict = {
    "2330": "台積電 - 780.0",
    "2317": "鴻海 - 150.5",
    "2454": "聯發科 - 1100.0",
    "0050": "元大台灣50 - 155.2"
}

@app.route('/')
def index():
    return render_template('index.html')

# 韓文查詢功能
@app.route('/ask', methods=['GET', 'POST'])
def ask():
    question = ""
    answer = ""
    if request.method == 'POST':
        question = request.form.get('question', '').strip()
        answer = zh_ko_dict.get(question, "抱歉，我目前沒有這個詞的韓文對應。")
    return render_template('ask.html', question=question, answer=answer)

# 股票查詢功能 (已修正)
@app.route('/stock', methods=['GET', 'POST'])
def stock():
    question = ""
    answer = ""
    if request.method == 'POST':
        # 讀取使用者輸入的股票號碼
        question = request.form.get('question', '').strip()
        # 從 stock_dict 查詢，而非 zh_ko_dict
        answer = stock_dict.get(question, f"抱歉，查不到代號 {question} 的收盤價。")
    
    return render_template('stock.html', question=question, answer=answer)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
