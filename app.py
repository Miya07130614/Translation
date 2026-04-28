from flask import Flask, request, render_template
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
app = Flask(__name__)

# 韓文題庫
zh_ko_dict = {"你好": "안녕하세요", "謝謝": "감사합니다", "老師": "선생님", "學生": "학생"}


def fetch_tw_stock_quote(symbol):
    base_url = "https://query1.finance.yahoo.com/v7/finance/quote"
    candidates = [f"{symbol}.TW", f"{symbol}.TWO"]

    for yahoo_symbol in candidates:
        res = requests.get(
            base_url,
            params={"symbols": yahoo_symbol},
            verify=False,
            timeout=5,
        )
        res.raise_for_status()

        result = res.json().get("quoteResponse", {}).get("result", [])
        if result:
            return result[0]

    return None


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/ask", methods=["GET", "POST"])
def ask():
    question = ""
    answer = ""
    if request.method == "POST":
        question = request.form.get("question", "").strip()
        answer = zh_ko_dict.get(question, "抱歉，目前沒有這個詞。")
    return render_template("ask.html", question=question, answer=answer)


@app.route("/stock", methods=["GET", "POST"])
def stock():
    question = ""
    answer = ""

    if request.method == "POST":
        question = request.form.get("question", "").strip()

        try:
            idx_url = "https://openapi.twse.com.tw/v1/indices/TWT48U"
            res_idx = requests.get(idx_url, verify=False, timeout=5)

            found = False

            if res_idx.status_code == 200:
                data_idx = res_idx.json()
                item = next((i for i in data_idx if i.get("指數") == question), None)
                if item:
                    answer = (
                        f"日期：{item.get('日期')} | {item.get('指數')} | "
                        f"收盤：{item.get('收盤指數')} | "
                        f"漲跌：{item.get('漲跌點數')} ({item.get('漲跌百分比')}%)"
                    )
                    found = True

            if not found and question.isdigit():
                stock_item = fetch_tw_stock_quote(question)
                if stock_item:
                    market_price = stock_item.get("regularMarketPrice", "無資料")
                    previous_close = stock_item.get("regularMarketPreviousClose", "無資料")
                    stock_name = stock_item.get("longName") or stock_item.get("shortName") or question
                    stock_code = stock_item.get("symbol", "").split(".")[0] or question
                    answer = (
                        f"股票：{stock_name} ({stock_code}) | "
                        f"現價：{market_price} | 昨收：{previous_close}"
                    )
                    found = True

            if not found:
                answer = f"找不到「{question}」的資料。請輸入 2330 或 發行量加權股價指數"

        except Exception as e:
            print(f"Error: {e}")
            answer = "資料讀取失敗，請確認網路連線或代號是否正確。"

    return render_template("stock.html", question=question, answer=answer)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
