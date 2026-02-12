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
        
        collected_data = []
        
        # 獲取股價資料
        if 'price' in data_types:
            collected_data = fetch_price_data(stock_code, start_date, end_date, collected_data)
        
        # 獲取三大法人資料
        if 'institutional' in data_types:
            collected_data = fetch_institutional_data(stock_code, start_date, end_date, collected_data)
        
        # 按日期排序
        collected_data.sort(key=lambda x: x['日期'])

        # 重新排序欄位，確保日期在最前面
        ordered_data = []
        for row in collected_data:
            ordered_row = OrderedDict()
            ordered_row['日期'] = row['日期']
            ordered_row['股票代碼'] = row['股票代碼']
            # 添加其他欄位
            for key, value in row.items():
                if key not in ['日期', '股票代碼']:
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
            
            time.sleep(0.3)  # 避免請求過快
            
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

                time.sleep(0.3)  # 減少延遲，避免請求超時
                
            except Exception as e:
                print(f"Error fetching institutional data for {date_param}: {e}")
        
        current += timedelta(days=1)
    
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
