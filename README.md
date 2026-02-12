# 📊 台股資料抓取工具

URL: https://annaandmandy.github.io/gupiao/taiwan-stock-scraper-v2.html

一個功能完整的台股資料抓取工具，可以下載每日股價、三大法人買賣超、基本面指標、技術指標等資料為 CSV 檔案。

## ✨ 功能特色

### 資料類型
- ✅ **每日股價資料**：開盤價、最高價、最低價、收盤價、成交量、成交金額、成交筆數、漲跌價差
- ✅ **三大法人買賣超**：外資、投信、自營商的買進、賣出、買賣超資料
- ✅ **基本面指標** ⭐ 新增：本益比（PE）、殖利率（%）、股價淨值比（PB）
- ✅ **技術指標** ⭐ 新增：MA5/MA10/MA20 移動平均線、漲跌幅百分比
- ✅ **成交量分析** ⭐ 新增：量變化率、量比、成交量億股
- ✅ **CSV 下載**：一鍵下載所有資料

### 技術特色
- 🚀 前後端分離架構
- ☁️ 後端可部署至 Railway
- 🌐 前端可部署至 GitHub Pages
- 📱 響應式設計，支援手機和桌面
- ⚡ 自動批次抓取，提升效率

## 🏗️ 架構

```
前端（GitHub Pages）
    ↓ HTTP Request
後端（Railway - Flask API）
    ↓ HTTP Request
台灣證券交易所 API
```

## 🚀 快速開始

### 本地使用

1. **安裝 Python 套件**
   ```bash
   pip install -r requirements.txt
   ```

2. **啟動後端伺服器**
   ```bash
   python stock_api.py
   ```

3. **開啟前端網頁**
   在瀏覽器開啟 `taiwan-stock-scraper-v2.html`

### 雲端部署

詳細部署步驟請參考 [部署說明.md](部署說明.md)

## 📖 使用說明

詳細使用方式請參考 [使用說明.md](使用說明.md)

## 📁 檔案結構

```
gupiao/
├── stock_api.py                    # Flask 後端 API
├── taiwan-stock-scraper-v2.html    # 前端網頁
├── requirements.txt                # Python 依賴套件
├── Procfile                        # Railway 部署設定
├── runtime.txt                     # Python 版本
├── .env.example                    # 環境變數範例
├── .gitignore                      # Git 忽略檔案
├── README.md                       # 本檔案
├── 使用說明.md                     # 使用者說明
└── 部署說明.md                     # 部署指南
```

## 🛠️ 技術棧

### 後端
- Python 3.11
- Flask - Web 框架
- Flask-CORS - 跨域請求處理
- Requests - HTTP 請求
- Gunicorn - WSGI 伺服器

### 前端
- HTML5
- CSS3
- Vanilla JavaScript
- 無需任何框架或建置工具

## 📊 資料來源

所有資料來自台灣證券交易所公開 API：
- 每日股價：`https://www.twse.com.tw/exchangeReport/STOCK_DAY`
- 三大法人：`https://www.twse.com.tw/rwd/zh/fund/T86`
- 基本面指標：`https://www.twse.com.tw/rwd/zh/afterTrading/BWIBBU_d`

## ⚠️ 注意事項

1. **資料範圍限制**：
   - 三大法人資料：建議不超過 14 天（系統限制 30 天）
   - 其他資料：建議不超過 3 個月（系統限制 90 天）
2. **股票代碼**：僅支援上市股票（證交所），不支援櫃買股票
3. **交易日**：僅能抓取已交易日的資料，週末和假日無資料
4. **技術指標計算**：
   - 移動平均線需要足夠的歷史資料（MA5需5天、MA10需10天、MA20需20天）
   - 量比需要至少5天的成交量資料
5. **基本面資料**：部分股票可能沒有完整的基本面資料

## 📝 常用股票代碼

- 2330：台積電
- 2454：聯發科
- 2317：鴻海
- 2412：中華電
- 2308：台達電
- 2882：國泰金
- 2303：聯電
- 6505：台塑化

## 🤝 貢獻

歡迎提交 Issue 和 Pull Request！

## 📄 授權

MIT License

## 🙏 致謝

感謝台灣證券交易所提供公開 API。
