#!/usr/bin/env python3
"""測試 JSON 序列化是否保持 OrderedDict 順序"""
import json
from collections import OrderedDict

# 建立有序的資料
ordered_row = OrderedDict([
    ('日期', '2024-01-08'),
    ('股票代碼', '2330'),
    ('開盤價', '585'),
    ('最高價', '595'),
    ('收盤價', '590'),
    ('外資買賣超', '10000000'),
    ('本益比', '25.5')
])

print("原始 OrderedDict 順序：")
for key in ordered_row.keys():
    print(f"  {key}")

# 序列化為 JSON
json_str = json.dumps(ordered_row, ensure_ascii=False)
print(f"\n序列化後的 JSON：")
print(json_str)

# 反序列化
parsed = json.loads(json_str)
print(f"\n反序列化後的鍵順序：")
for key in parsed.keys():
    print(f"  {key}")

print("\n✅ 測試完成")
print("注意：Python 3.7+ 的 dict 和 json 都保持插入順序")
