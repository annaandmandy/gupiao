#!/usr/bin/env python3
"""測試三大法人資料抓取"""
import requests
from datetime import datetime

# 測試參數
stock_code = "2330"
date_str = "20240102"

# 呼叫 API
url = f"https://www.twse.com.tw/rwd/zh/fund/T86?date={date_str}&selectType=ALLBUT0999&response=json"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

print(f"測試日期: {date_str}")
print(f"股票代碼: {stock_code}")
print(f"API URL: {url}\n")

try:
    response = requests.get(url, headers=headers, timeout=10)
    result = response.json()

    print(f"API 狀態: {result.get('stat')}")
    print(f"資料筆數: {len(result.get('data', []))}\n")

    if result.get('stat') == 'OK' and result.get('data'):
        # 找到對應股票
        stock_data = next((row for row in result['data'] if row[0] == stock_code), None)

        if stock_data:
            print(f"找到 {stock_code} 的資料!")
            print(f"原始資料長度: {len(stock_data)}")
            print(f"\n欄位對應:")
            print(f"[0] 股票代碼: {stock_data[0]}")
            print(f"[1] 股票名稱: {stock_data[1]}")
            print(f"[2] 外資買進: {stock_data[2]}")
            print(f"[3] 外資賣出: {stock_data[3]}")
            print(f"[4] 外資買賣超: {stock_data[4]}")
            print(f"[8] 投信買進: {stock_data[8]}")
            print(f"[9] 投信賣出: {stock_data[9]}")
            print(f"[10] 投信買賣超: {stock_data[10]}")
            print(f"[11] 自營商買賣超: {stock_data[11]}")

            # 檢查索引 18 是否存在
            if len(stock_data) > 18:
                print(f"[18] 三大法人買賣超合計: {stock_data[18]}")
            else:
                print(f"\n❌ 錯誤：資料只有 {len(stock_data)} 個欄位，沒有索引 [18]！")
                print(f"完整資料: {stock_data}")
        else:
            print(f"❌ 找不到股票代碼 {stock_code}")
    else:
        print(f"❌ API 回傳錯誤: {result}")

except Exception as e:
    print(f"❌ 發生錯誤: {e}")
    import traceback
    traceback.print_exc()
