from flask import Flask, request, render_template
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
app = Flask(__name__)

# 韓文題庫
zh_ko_dict = {"你好": "안녕하세요", "謝謝": "감사합니다", "老師": "선생님", "學生": "학생"}


def fetch_tw_stock_quote(symbol):
    res = requests.get(
        "https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL",
        verify=False,
        timeout=10,
    )
    res.raise_for_status()

    if "json" not in res.headers.get("Content-Type", "").lower():
        return None

    data = res.json()
    return next((item for item in data if item.get("Code") == symbol), None)


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
            found = False

            if question.isdigit():
                stock_item = fetch_tw_stock_quote(question)
                if stock_item:
                    stock_name = stock_item.get("Name", question)
                    stock_code = stock_item.get("Code", question)
                    closing_price = stock_item.get("ClosingPrice", "無資料")
                    change = stock_item.get("Change", "無資料")
                    trade_date = stock_item.get("Date", "無資料")
                    answer = (
                        f"股票：{stock_name} ({stock_code}) | "
                        f"日期：{trade_date} | 收盤價：{closing_price} | 漲跌價差：{change}"
                    )
                    found = True
            else:
                idx_url = "https://openapi.twse.com.tw/v1/exchangeReport/MI_INDEX"
                res_idx = requests.get(idx_url, verify=False, timeout=5)

                if res_idx.status_code == 200 and "json" in res_idx.headers.get("Content-Type", "").lower():
                    data_idx = res_idx.json()
                    item = next((i for i in data_idx if i.get("指數") == question), None)
                    if item:
                        answer = (
                            f"日期：{item.get('日期')} | {item.get('指數')} | "
                            f"收盤：{item.get('收盤指數')} | "
                            f"漲跌：{item.get('漲跌點數')} ({item.get('漲跌百分比')}%)"
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
