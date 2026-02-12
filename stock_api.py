from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import requests
from datetime import datetime, timedelta
from collections import OrderedDict
import csv
import io
import time
import os

app = Flask(__name__)
# 允許所有來源的 CORS 請求（生產環境建議限制特定網域）
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"],
        "expose_headers": ["Content-Type"],
        "supports_credentials": False
    }
})

def parse_roc_date(roc_date_str):
    """轉換民國日期為西元日期"""
    parts = roc_date_str.split('/')
    year = int(parts[0]) + 1911
    month = int(parts[1])
    day = int(parts[2])
    return datetime(year, month, day)

def format_date(date):
    """格式化日期為 YYYY-MM-DD"""
    return date.strftime('%Y-%m-%d')

@app.route('/api/stock-data', methods=['POST'])
def get_stock_data():
    try:
        data = request.json
        stock_code = data.get('stockCode')
        start_date = datetime.strptime(data.get('startDate'), '%Y-%m-%d')
        end_date = datetime.strptime(data.get('endDate'), '%Y-%m-%d')
        data_types = data.get('dataTypes', [])

        # 計算日期範圍，避免請求過大
        days_diff = (end_date - start_date).days

        # 如果包含三大法人資料，限制更嚴格（因為需要逐日請求）
        if 'institutional' in data_types and days_diff > 30:
            return jsonify({
                'success': False,
                'error': '查詢三大法人資料時，日期範圍不能超過 30 天（建議 7-14 天）'
            }), 400
        elif days_diff > 90:
            return jsonify({
                'success': False,
                'error': '日期範圍不能超過 90 天，請縮短查詢區間'
            }), 400
        
        collected_data = []
        
        # 獲取股價資料
        if 'price' in data_types:
            collected_data = fetch_price_data(stock_code, start_date, end_date, collected_data)
        
        # 獲取三大法人資料
        if 'institutional' in data_types:
            collected_data = fetch_institutional_data(stock_code, start_date, end_date, collected_data)

        # 獲取基本面指標
        if 'fundamental' in data_types:
            collected_data = fetch_fundamental_data(stock_code, start_date, end_date, collected_data)

        # 按日期排序
        collected_data.sort(key=lambda x: x['日期'])

        # 計算技術指標
        if 'technical' in data_types:
            collected_data = calculate_technical_indicators(collected_data)

        # 計算成交量分析
        if 'volume' in data_types:
            collected_data = calculate_volume_analysis(collected_data)

        # 重新排序欄位，按類別組織（日期最左邊）
        ordered_data = []

        # 定義欄位順序（按類別分組）
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

        for row in collected_data:
            ordered_row = OrderedDict()

            # 按照定義的順序添加欄位（如果存在）
            for col in column_order:
                if col in row:
                    ordered_row[col] = row[col]

            # 添加任何未在預定義列表中的欄位（以防萬一）
            for key, value in row.items():
                if key not in ordered_row:
                    ordered_row[key] = value

            ordered_data.append(ordered_row)

        return jsonify({
            'success': True,
            'data': ordered_data,
            'count': len(ordered_data)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def fetch_price_data(stock_code, start_date, end_date, collected_data):
    """獲取每日股價資料"""
    current = start_date
    
    while current <= end_date:
        year = current.year
        month = current.month
        date_param = f"{year}{month:02d}01"
        
        url = f"https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date={date_param}&stockNo={stock_code}"
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            result = response.json()
            
            if result.get('stat') == 'OK' and result.get('data'):
                for row in result['data']:
                    row_date = parse_roc_date(row[0])
                    
                    if start_date <= row_date <= end_date:
                        date_str = format_date(row_date)
                        
                        # 找到或建立該日期的資料
                        existing_row = next((d for d in collected_data if d['日期'] == date_str), None)
                        if not existing_row:
                            existing_row = OrderedDict()
                            existing_row['日期'] = date_str
                            existing_row['股票代碼'] = stock_code
                            collected_data.append(existing_row)
                        
                        existing_row.update({
                            '成交股數': row[1],
                            '成交金額': row[2],
                            '開盤價': row[3],
                            '最高價': row[4],
                            '最低價': row[5],
                            '收盤價': row[6],
                            '漲跌價差': row[7],
                            '成交筆數': row[8]
                        })
            
            # 移除延遲，提升速度
            
        except Exception as e:
            print(f"Error fetching price data for {year}-{month:02d}: {e}")
        
        # 移到下個月
        if current.month == 12:
            current = datetime(current.year + 1, 1, 1)
        else:
            current = datetime(current.year, current.month + 1, 1)
    
    return collected_data

def fetch_institutional_data(stock_code, start_date, end_date, collected_data):
    """獲取三大法人買賣超資料"""
    current = start_date
    
    while current <= end_date:
        # 跳過週末
        if current.weekday() < 5:  # 0-4 是週一到週五
            date_param = current.strftime('%Y%m%d')
            url = f"https://www.twse.com.tw/rwd/zh/fund/T86?date={date_param}&selectType=ALLBUT0999&response=json"
            
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                response = requests.get(url, headers=headers, timeout=10)
                result = response.json()
                
                if result.get('stat') == 'OK' and result.get('data'):
                    # 找到對應股票的資料
                    stock_data = next((row for row in result['data'] if row[0] == stock_code), None)
                    
                    if stock_data:
                        date_str = format_date(current)
                        
                        existing_row = next((d for d in collected_data if d['日期'] == date_str), None)
                        if not existing_row:
                            existing_row = OrderedDict()
                            existing_row['日期'] = date_str
                            existing_row['股票代碼'] = stock_code
                            collected_data.append(existing_row)
                        
                        existing_row.update({
                            '外資買進': stock_data[2],   # 外陸資買進股數(不含外資自營商)
                            '外資賣出': stock_data[3],   # 外陸資賣出股數(不含外資自營商)
                            '外資買賣超': stock_data[4], # 外陸資買賣超股數(不含外資自營商)
                            '投信買進': stock_data[8],   # 投信買進股數
                            '投信賣出': stock_data[9],   # 投信賣出股數
                            '投信買賣超': stock_data[10], # 投信買賣超股數
                            '自營商買賣超': stock_data[11], # 自營商買賣超股數
                            '三大法人買賣超合計': stock_data[18] # 三大法人買賣超股數
                        })

                # 移除延遲，提升速度
                
            except Exception as e:
                print(f"Error fetching institutional data for {date_param}: {e}")
        
        current += timedelta(days=1)
    
    return collected_data

def fetch_fundamental_data(stock_code, start_date, end_date, collected_data):
    """獲取基本面指標（本益比、殖利率、股價淨值比）"""
    current = start_date

    while current <= end_date:
        date_param = current.strftime('%Y%m%d')
        url = f"https://www.twse.com.tw/rwd/zh/afterTrading/BWIBBU_d?date={date_param}&selectType=ALL&response=json"

        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            result = response.json()

            if result.get('stat') == 'OK' and result.get('data'):
                # 找到對應股票的資料
                stock_data = next((row for row in result['data'] if row[0] == stock_code), None)

                if stock_data:
                    date_str = format_date(current)

                    existing_row = next((d for d in collected_data if d['日期'] == date_str), None)
                    if not existing_row:
                        existing_row = OrderedDict()
                        existing_row['日期'] = date_str
                        existing_row['股票代碼'] = stock_code
                        collected_data.append(existing_row)

                    existing_row.update({
                        '殖利率(%)': stock_data[2],      # 殖利率(%)
                        '股利年度': stock_data[3],        # 股利年度
                        '本益比': stock_data[4],          # 本益比
                        '股價淨值比': stock_data[5],      # 股價淨值比
                        '財報年季': stock_data[6]         # 財報年/季
                    })

        except Exception as e:
            print(f"Error fetching fundamental data for {date_param}: {e}")

        current += timedelta(days=1)

    return collected_data

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

def calculate_volume_analysis(collected_data):
    """計算成交量分析（量變化率、量比）"""
    if not collected_data:
        return collected_data

    for i, row in enumerate(collected_data):
        # 計算量變化率（與前一日比較）
        if i > 0 and '成交股數' in row and '成交股數' in collected_data[i-1]:
            try:
                current_vol = float(row['成交股數'].replace(',', ''))
                prev_vol = float(collected_data[i-1]['成交股數'].replace(',', ''))
                if prev_vol != 0:
                    vol_change = ((current_vol - prev_vol) / prev_vol) * 100
                    row['量變化率(%)'] = f"{vol_change:.2f}"
            except (ValueError, ZeroDivisionError):
                pass

        # 計算量比（5日平均量）
        if '成交股數' in row and i >= 4:
            volumes = []
            for j in range(i - 4, i + 1):
                if '成交股數' in collected_data[j]:
                    try:
                        vol = float(collected_data[j]['成交股數'].replace(',', ''))
                        volumes.append(vol)
                    except ValueError:
                        pass

            if len(volumes) == 5:
                avg_vol = sum(volumes) / 5
                try:
                    current_vol = float(row['成交股數'].replace(',', ''))
                    if avg_vol != 0:
                        vol_ratio = current_vol / avg_vol
                        row['量比'] = f"{vol_ratio:.2f}"
                except (ValueError, ZeroDivisionError):
                    pass

        # 計算換手率（需要流通股數，這裡暫時使用成交股數/10億作為簡化）
        # 注意：真實換手率需要從其他API獲取實際流通股數
        if '成交股數' in row:
            try:
                volume = float(row['成交股數'].replace(',', ''))
                # 這是簡化計算，實際應該用實際流通股數
                row['成交量(億股)'] = f"{volume / 100000000:.2f}"
            except ValueError:
                pass

    return collected_data

@app.route('/')
def home():
    return jsonify({
        'message': '台股資料抓取 API',
        'version': '2.0',
        'endpoints': {
            '/api/stock-data': 'POST - 獲取股票資料'
        }
    })

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    # 從環境變數讀取 PORT，Railway 會自動設定
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'

    print("🚀 台股資料抓取 API 伺服器啟動中...")
    print(f"📍 伺服器位址: http://0.0.0.0:{port}")
    print("💡 請在瀏覽器開啟 taiwan-stock-scraper-v2.html")

    app.run(debug=debug, host='0.0.0.0', port=port)
