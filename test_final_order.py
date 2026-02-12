#!/usr/bin/env python3
"""測試最終的欄位順序邏輯"""
from collections import OrderedDict
import json

# 模擬後端收集的資料（順序可能是混亂的）
collected_data = [
    {
        '三大法人買賣超合計': '13000000',
        '外資買賣超': '10000000',
        '外資買進': '15000000',
        '外資賣出': '5000000',
        '成交筆數': '25000',
        '成交股數': '50000000',
        '成交金額': '29500000000',
        '投信買賣超': '2000000',
        '投信買進': '3000000',
        '投信賣出': '1000000',
        '收盤價': '590',
        '日期': '2024-01-08',
        '最低價': '580',
        '最高價': '595',
        '漲跌價差': '+5',
        '股票代碼': '2330',
        '自營商買賣超': '1000000',
        '開盤價': '585',
        '本益比': '25.5',
        '殖利率(%)': '2.5',
        'MA5': '588.00',
        '量變化率(%)': '15.20'
    }
]

# 定義正確的欄位順序（與 stock_api.py 相同）
column_order = [
    # 基本資訊
    '日期', '股票代碼',

    # 價格資料
    '開盤價', '最高價', '最低價', '收盤價', '漲跌價差', '漲跌幅(%)',

    # 成交量基本資料
    '成交股數', '成交金額', '成交筆數',

    # 成交量分析
    '成交量(億股)', '量變化率(%)', '量比',

    # 技術指標
    'MA5', 'MA10', 'MA20',

    # 三大法人 - 外資
    '外資買進', '外資賣出', '外資買賣超',

    # 三大法人 - 投信
    '投信買進', '投信賣出', '投信買賣超',

    # 三大法人 - 自營商與合計
    '自營商買賣超', '三大法人買賣超合計',

    # 基本面指標
    '本益比', '殖利率(%)', '股價淨值比', '股利年度', '財報年季'
]

# 重新排序
ordered_data = []
for row in collected_data:
    ordered_row = OrderedDict()

    # 嚴格按照定義的順序添加欄位（如果存在）
    for col in column_order:
        if col in row:
            ordered_row[col] = row[col]

    # 注意：不添加未定義的欄位
    ordered_data.append(ordered_row)

# 輸出結果
print("✅ 排序後的欄位順序：\n")
for i, key in enumerate(ordered_data[0].keys(), 1):
    print(f"{i:2d}. {key}")

print(f"\n總共 {len(ordered_data[0])} 個欄位")

# 測試 JSON 序列化
json_str = json.dumps(ordered_data[0], ensure_ascii=False)
parsed = json.loads(json_str)

print("\n✅ JSON 序列化後的順序：\n")
for i, key in enumerate(parsed.keys(), 1):
    print(f"{i:2d}. {key}")

# 驗證順序是否一致
original_keys = list(ordered_data[0].keys())
parsed_keys = list(parsed.keys())

if original_keys == parsed_keys:
    print("\n✅ 順序完全一致！")
else:
    print("\n❌ 順序不一致！")
    print(f"原始: {original_keys[:5]}...")
    print(f"解析: {parsed_keys[:5]}...")
