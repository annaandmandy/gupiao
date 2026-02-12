#!/usr/bin/env python3
"""測試新增的指標計算功能"""
from collections import OrderedDict

def calculate_technical_indicators(collected_data):
    """計算技術指標（移動平均線、漲跌幅）"""
    if not collected_data:
        return collected_data

    # 需要有收盤價才能計算
    for i, row in enumerate(collected_data):
        # 計算漲跌幅百分比
        if '收盤價' in row and '漲跌價差' in row:
            try:
                close = float(row['收盤價'].replace(',', ''))
                change = float(row['漲跌價差'].replace(',', ''))
                if close - change != 0:
                    change_pct = (change / (close - change)) * 100
                    row['漲跌幅(%)'] = f"{change_pct:.2f}"
            except (ValueError, ZeroDivisionError):
                pass

        # 計算移動平均線（5日、10日、20日）
        if '收盤價' in row:
            for period in [5, 10, 20]:
                if i >= period - 1:
                    prices = []
                    for j in range(i - period + 1, i + 1):
                        if '收盤價' in collected_data[j]:
                            try:
                                price = float(collected_data[j]['收盤價'].replace(',', ''))
                                prices.append(price)
                            except ValueError:
                                pass

                    if len(prices) == period:
                        ma = sum(prices) / period
                        row[f'MA{period}'] = f"{ma:.2f}"

    return collected_data

# 測試資料
test_data = [
    OrderedDict([('日期', '2024-01-02'), ('股票代碼', '2330'), ('收盤價', '590'), ('漲跌價差', '+5')]),
    OrderedDict([('日期', '2024-01-03'), ('股票代碼', '2330'), ('收盤價', '595'), ('漲跌價差', '+5')]),
    OrderedDict([('日期', '2024-01-04'), ('股票代碼', '2330'), ('收盤價', '600'), ('漲跌價差', '+5')]),
    OrderedDict([('日期', '2024-01-05'), ('股票代碼', '2330'), ('收盤價', '605'), ('漲跌價差', '+5')]),
    OrderedDict([('日期', '2024-01-08'), ('股票代碼', '2330'), ('收盤價', '610'), ('漲跌價差', '+5')]),
]

print("測試技術指標計算...")
result = calculate_technical_indicators(test_data)

for row in result:
    print(f"\n日期: {row['日期']}")
    print(f"  收盤價: {row['收盤價']}")
    print(f"  漲跌價差: {row['漲跌價差']}")
    if '漲跌幅(%)' in row:
        print(f"  漲跌幅(%): {row['漲跌幅(%)']}")
    if 'MA5' in row:
        print(f"  MA5: {row['MA5']}")
    if 'MA10' in row:
        print(f"  MA10: {row['MA10']}")
    if 'MA20' in row:
        print(f"  MA20: {row['MA20']}")

print("\n✅ 技術指標計算測試完成！")
