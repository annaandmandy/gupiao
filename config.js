// 台股資料抓取工具 - 設定檔
// 部署到 GitHub Pages 時，請將 API_BASE_URL 改為你的 Railway 網址

const CONFIG = {
    // 後端 API 網址
    // 本地開發：保持此設定，會自動使用 localhost:5000
    // Railway 部署：請修改為你的 Railway URL（例如：'https://your-app.railway.app'）
    API_BASE_URL: 'https://web-production-ae345.up.railway.app',

    // 是否啟用手動設定功能（true = 允許用戶在網頁上修改 API URL）
    ALLOW_MANUAL_CONFIG: true,

    // API 版本
    API_VERSION: '2.0'
};

// 自動偵測環境：本地開發時使用 localhost
if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    CONFIG.API_BASE_URL = 'http://localhost:5000';
}
