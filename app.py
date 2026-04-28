def fetch_tw_stock_quote(symbol):
    base_url = "https://query1.finance.yahoo.com/v8/finance/chart"
    candidates = [f"{symbol}.TW", f"{symbol}.TWO"]
    res = requests.get(
        "https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL",
        verify=False,
        timeout=10,
    )
    res.raise_for_status()

    for yahoo_symbol in candidates:
        res = requests.get(
            f"{base_url}/{yahoo_symbol}",
            params={"interval": "1d", "range": "2d"},
            verify=False,
            timeout=5,
        )
        res.raise_for_status()
    if "json" not in res.headers.get("Content-Type", "").lower():
        return None

        result = res.json().get("chart", {}).get("result", [])
        if result:
            meta = result[0].get("meta", {})
            if meta.get("regularMarketPrice") is not None:
                return meta
    data = res.json()
    return next((item for item in data if item.get("Code") == symbol), None)

    return None


@app.route("/")
def index():
            if question.isdigit():
                stock_item = fetch_tw_stock_quote(question)
                if stock_item:
                    market_price = stock_item.get("regularMarketPrice", "無資料")
                    previous_close = stock_item.get("previousClose", "無資料")
                    stock_name = stock_item.get("longName") or stock_item.get("shortName") or question
                    stock_code = stock_item.get("symbol", "").split(".")[0] or question
                    stock_name = stock_item.get("Name", question)
                    stock_code = stock_item.get("Code", question)
                    closing_price = stock_item.get("ClosingPrice", "無資料")
                    change = stock_item.get("Change", "無資料")
                    trade_date = stock_item.get("Date", "無資料")
                    answer = (
                        f"股票：{stock_name} ({stock_code}) | "
                        f"現價：{market_price} | 昨收：{previous_close}"
                        f"日期：{trade_date} | 收盤價：{closing_price} | 漲跌價差：{change}"
                    )
                    found = True
            else:
                idx_url = "https://openapi.twse.com.tw/v1/indices/TWT48U"
                idx_url = "https://openapi.twse.com.tw/v1/exchangeReport/MI_INDEX"
                res_idx = requests.get(idx_url, verify=False, timeout=5)

                if res_idx.status_code == 200 and "json" in res_idx.headers.get("Content-Type", "").lower():
