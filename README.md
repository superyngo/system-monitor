# System Monitor

Windows 系統監控工具，支援 Google Sheets 整合

## 功能特色

- 📊 即時監控 CPU、RAM 使用率
- 🌐 網路使用量統計
- 📁 指定資料夾內容監控
- ☁️ 自動上傳數據到 Google Sheets
- 🎯 系統托盤常駐程式
- ⚙️ 簡易 GUI 設定介面

## 開發環境設定

### 前置需求

- Python 3.13+
- uv (Python 套件管理工具)

### 安裝步驟

1. 複製專案：

```bash
git clone <repository-url>
cd system-monitor
```

2. 創建虛擬環境並安裝依賴：

```bash
uv sync
```

3. 創建應用程式圖示：

```bash
uv run python create_icon.py
```

4. 執行程式：

```bash
uv run python main.py
```

## 編譯打包

本專案使用 Nuitka 編譯為獨立執行檔。

### 方法一：使用批次檔案（推薦）

```bash
build.bat
```

### 方法二：手動編譯

```bash
# 安裝編譯依賴
uv add --optional build nuitka ordered-set

# 執行編譯
uv run python build.py
```

### 方法三：直接使用 Nuitka

```bash
uv run python -m nuitka @nuitka.cfg main.py
```

編譯完成後會生成 `SystemMonitor.exe` 單一執行檔。

## 設定說明

### Google Sheets API 設定

1. 前往 [Google Cloud Console](https://console.cloud.google.com/)
2. 建立新專案或選擇現有專案
3. 啟用 Google Sheets API
4. 建立服務帳戶金鑰（JSON 格式）
5. 將金鑰檔案放置於專案目錄並在設定中指定路徑

### 安全性考量

- 服務帳戶金鑰檔案應妥善保管，不可公開
- 建議使用最小權限原則設定 Google Sheets 存取權限
- 定期輪換 API 金鑰

### 設定檔案格式

```json
{
  "google_sheets": {
    "credentials_file": "path/to/credentials.json",
    "spreadsheet_url": "https://docs.google.com/spreadsheets/d/your-sheet-id/edit",
    "worksheet_name": "System Monitor"
  },
  "monitoring": {
    "interval_minutes": 5,
    "monitor_directories": ["C:\\Users\\user\\Documents", "D:\\Projects"]
  }
}
```

## 專案結構

```
system-monitor/
├── main.py                 # 主程式入口
├── build.py                # 編譯腳本
├── build.bat               # Windows 編譯批次檔
├── create_icon.py          # 圖示生成腳本
├── nuitka.cfg              # Nuitka 設定檔
├── pyproject.toml          # 專案設定
├── assets/
│   └── icon.ico            # 應用程式圖示
└── src/
    ├── api/
    │   └── google_sheets.py # Google Sheets API 整合
    ├── config/
    │   └── settings.py      # 設定管理
    ├── monitor/
    │   ├── system_info.py   # 系統資訊收集
    │   └── file_scanner.py  # 檔案掃描
    └── ui/
        ├── tray_icon.py     # 系統托盤
        └── settings_window.py # 設定視窗
```

## 授權條款

MIT License
