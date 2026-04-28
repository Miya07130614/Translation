from flask import Flask, request, render_template
from datetime import date
import requests
import urllib3

zh_ko_dict = {"你好": "?????", "謝謝": "?????", "老師": "???", "學生": "??"}


def fetch_tw_stock_quote(symbol):
    res = requests.get(
        "https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL",
        verify=False,
        timeout=10,
    )
    res.raise_for_status()
def fetch_tw_stock_quotes(symbol, days=10):
    today = date.today()
    year = today.year
    month = today.month
    rows = []

    if "json" not in res.headers.get("Content-Type", "").lower():
        return None
    for _ in range(3):
        month_key = f"{year}{month:02d}01"
        res = requests.get(
            "https://www.twse.com.tw/rwd/zh/afterTrading/STOCK_DAY",
            params={"date": month_key, "stockNo": symbol, "response": "json"},
            verify=False,
            timeout=10,
        )
        res.raise_for_status()

    data = res.json()
    return next((item for item in data if item.get("Code") == symbol), None)
        if "json" not in res.headers.get("Content-Type", "").lower():
            break

        payload = res.json()
        month_rows = payload.get("data", [])
        if month_rows:
            rows = month_rows + rows
            if len(rows) >= days:
                stock_name = ""
                title = payload.get("title", "")
                parts = title.split()
                if len(parts) >= 3:
                    stock_name = parts[2]
                return {
                    "code": symbol,
                    "name": stock_name or symbol,
                    "rows": rows[-days:],
                }

        month -= 1
        if month == 0:
            month = 12
            year -= 1

    if rows:
        return {"code": symbol, "name": symbol, "rows": rows[-days:]}

    return None


@app.route("/")
def index():
            found = False

            if question.isdigit():
                stock_item = fetch_tw_stock_quote(question)
                stock_item = fetch_tw_stock_quotes(question, days=10)
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
                    lines = [f"股票：{stock_item['name']} ({stock_item['code']}) 近10個交易日"]
                    for row in stock_item["rows"]:
                        lines.append(
                            f"{row[0]} | 開盤：{row[3]} | 最高：{row[4]} | 最低：{row[5]} | 收盤：{row[6]} | 漲跌：{row[7]}"
                        )
                    answer = "\n".join(lines)
                    found = True
            else:
                idx_url = "https://openapi.twse.com.tw/v1/exchangeReport/MI_INDEX"
