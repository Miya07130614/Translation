from flask import Flask, request, render_template
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
app = Flask(__name__)

# 韓文題庫
zh_ko_dict = {"你好": "안녕하세요", "謝謝": "감사합니다", "老師": "선생님", "學生": "학생"}

@app.route('/')
def index(): return render_template('index.html')

@app.route('/ask', methods=['GET', 'POST'])
def ask():
    question = ""; answer = ""
    if request.method == 'POST':
        question = request.form.get('question', '').strip()
        answer = zh_ko_dict.get(question, "抱歉，目前沒有這個詞。")
    return render_template('ask.html', question=question, answer=answer)

@app.route('/stock', methods=['GET', 'POST'])
def stock():
    question = ""; answer = ""
    if request.method == 'POST':
        question = request.form.get('question', '').strip()
        try:
            # 策略：先嘗試抓大盤指數 API，如果找不到，再嘗試抓個股 API
            # 1. 嘗試大盤 API
            idx_url = "https://openapi.twse.com.tw/v1/indices/TWT48U"
            res_idx = requests.get(idx_url, verify=False, timeout=5)
            
            # 2. 嘗試個股 API
            stock_url = "https://www.twse.com.tw/rwd/zh/afterTrading/STOCK_DAY"
            res_stock = requests.get(stock_url, verify=False, timeout=5)

            found = False
            # 先在大盤資料找
            if res_idx.status_code == 200:
                data_idx = res_idx.json()
                item = next((i for i in data_idx if i.get("指數") == question), None)
                if item:
                    answer = f"日期：{item.get('日期')} | {item.get('指數')} | 收盤：{item.get('收盤指數')} | 漲跌：{item.get('漲跌點數')} ({item.get('漲跌百分比')}%)"
                    found = True

            # 如果大盤沒找到，在個股資料找
            if not found and res_stock.status_code == 200:
                data_stock = res_stock.json()
                item = next((i for i in data_stock if i.get("Code") == question), None)
                if item:
                    answer = f"股票：{item.get('Name')} ({item.get('Code')}) | 收盤價：{item.get('ClosingPrice')} 元"
                    found = True

            if not found:
                answer = f"找不到「{question}」的資料。請輸入 2330 或 發行量加權股價指數"

        except Exception as e:
            print(f"Error: {e}")
            answer = "資料讀取失敗，請確認網路連線或代號是否正確。"
            
    return render_template('stock.html', question=question, answer=answer)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
