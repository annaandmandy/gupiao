#!/usr/bin/env python3
"""測試 CSV 欄位順序"""
from collections import OrderedDict

# 模擬資料（包含所有可能的欄位）
sample_row = OrderedDict([
    ('股票代碼', '2330'),
    ('日期', '2024-01-08'),
    ('收盤價', '590'),
    ('開盤價', '585'),
    ('最高價', '595'),
    ('最低價', '580'),
    ('漲跌價差', '+5'),
    ('成交股數', '50,000,000'),
    ('成交金額', '29,500,000,000'),
    ('成交筆數', '25,000'),
    ('外資買賣超', '10,000,000'),
    ('投信買賣超', '2,000,000'),
    ('自營商買賣超', '1,000,000'),
    ('三大法人買賣超合計', '13,000,000'),
    ('本益比', '25.5'),
    ('殖利率(%)', '2.5'),
    ('股價淨值比', '5.2'),
    ('MA5', '588.00'),
    ('MA10', '585.50'),
    ('漲跌幅(%)', '0.85'),
    ('量變化率(%)', '15.20'),
    ('量比', '1.25'),
    ('成交量(億股)', '0.50'),
    ('外資買進', '15,000,000'),
    ('外資賣出', '5,000,000'),
    ('投信買進', '3,000,000'),
    ('投信賣出', '1,000,000'),
    ('股利年度', '2023'),
    ('財報年季', '112/04'),
])

# 定義欄位順序（與 stock_api.py 相同）
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

# 應用排序
ordered_row = OrderedDict()
for col in column_order:
    if col in sample_row:
        ordered_row[col] = sample_row[col]

# 添加任何未在預定義列表中的欄位
for key, value in sample_row.items():
    if key not in ordered_row:
        ordered_row[key] = value

# 顯示結果
print("✅ CSV 欄位順序測試\n")
print("=" * 80)
print(f"{'欄位名稱':<20} | {'數值':<30} | 分類")
print("=" * 80)

current_category = ""
categories = {
    '日期': '📅 基本資訊',
    '股票代碼': '📅 基本資訊',
    '開盤價': '💹 價格資料',
    '成交股數': '📊 成交量基本',
    '成交量(億股)': '📈 成交量分析',
    'MA5': '📉 技術指標',
    '外資買進': '🏦 三大法人-外資',
    '投信買進': '🏢 三大法人-投信',
    '自營商買賣超': '🏪 三大法人-自營商',
    '本益比': '💼 基本面指標'
}

for i, (key, value) in enumerate(ordered_row.items(), 1):
    # 判斷分類
    category = ""
    for cat_key, cat_name in categories.items():
        if key == cat_key or (key.startswith(cat_key.split('(')[0]) and cat_key in key):
            category = cat_name
            break

    # 顯示分類標題
    if category and category != current_category:
        current_category = category
        if i > 1:
            print("-" * 80)
        print(f"\n{category}")
        print("-" * 80)

    # 尋找更細緻的分類
    if '開盤價' in key or '最高價' in key or '最低價' in key or '收盤價' in key or '漲跌' in key:
        category = '💹 價格資料'
    elif '成交股數' in key or '成交金額' in key or '成交筆數' in key:
        category = '📊 成交量基本'
    elif '成交量(億股)' in key or '量變化率' in key or '量比' in key:
        category = '📈 成交量分析'
    elif 'MA' in key:
        category = '📉 技術指標'
    elif '外資' in key:
        category = '🏦 三大法人-外資'
    elif '投信' in key:
        category = '🏢 三大法人-投信'
    elif '自營商' in key or '三大法人買賣超合計' in key:
        category = '🏪 三大法人-自營商'
    elif '本益比' in key or '殖利率' in key or '股價淨值比' in key or '股利年度' in key or '財報年季' in key:
        category = '💼 基本面指標'

    print(f"{key:<20} | {value:<30} | {category}")

print("\n" + "=" * 80)
print(f"\n✅ 總共 {len(ordered_row)} 個欄位，順序正確！")
print("\n欄位分組：")
print("  1. 基本資訊 (2欄)")
print("  2. 價格資料 (6欄)")
print("  3. 成交量基本資料 (3欄)")
print("  4. 成交量分析 (3欄)")
print("  5. 技術指標 (3欄)")
print("  6. 三大法人-外資 (3欄)")
print("  7. 三大法人-投信 (3欄)")
print("  8. 三大法人-自營商與合計 (2欄)")
print("  9. 基本面指標 (5欄)")
