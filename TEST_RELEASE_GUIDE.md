# 測試發布流程指引

## 檔案說明

### 1. `.github/workflows/test_release.yml`

這是 GitHub Actions 的測試工作流程檔案，主要特點：

- **觸發條件**：

  - 手動觸發 (workflow_dispatch)
  - 推送 `test-*` 開頭的標籤時觸發

- **主要改動**：
  - 將 Nuitka 編譯步驟替換為建立假檔案
  - 在 `dist` 目錄建立假的 `SystemMonitor.exe`
  - 增加檔案驗證步驟
  - 標記為 prerelease (測試版本)

### 2. `test_release.py`

Python 測試腳本，用於驗證發布流程的各個步驟：

- 檢查 dist 目錄和執行檔
- 驗證必要檔案存在
- 模擬檔案複製和打包操作
- 提供詳細的測試報告

## 使用方法

### 方法一：本地測試

```powershell
# 在項目根目錄執行
uv run python test_release.py
```

### 方法二：GitHub Actions 測試

#### 手動觸發：

1. 進入 GitHub 倉庫
2. 點擊 "Actions" 標籤
3. 選擇 "Test Build and Release" workflow
4. 點擊 "Run workflow"
5. 輸入測試版本號 (例如：test-v0.1.0)
6. 點擊 "Run workflow" 按鈕

#### 標籤觸發：

```bash
# 建立並推送測試標籤
git tag test-v0.1.0
git push origin test-v0.1.0
```

## 測試項目

✅ **檔案建立測試**

- 在 dist 目錄建立假執行檔
- 驗證檔案大小和內容

✅ **檔案複製測試**

- 複製執行檔到 release 目錄
- 複製設定檔和說明文件

✅ **打包測試**

- 建立 ZIP 壓縮檔
- 驗證壓縮檔內容

✅ **發布測試**

- 建立 GitHub Release
- 上傳附件檔案
- 標記為測試版本

## 注意事項

1. **測試版本標記**：所有測試版本都會標記為 `prerelease`
2. **假執行檔**：測試版本包含的是文字檔案，非實際可執行檔案
3. **標籤命名**：建議使用 `test-` 前綴來區分測試版本
4. **清理**：測試完成後可以刪除測試標籤和 Release

## 故障排除

如果測試失敗，請檢查：

1. 必要檔案是否存在 (`config.example.json`, `README.md`)
2. Python 環境是否正確設定
3. GitHub token 權限是否足夠 (適用於 Actions)

## 從測試到正式發布

測試通過後，可以使用原始的 `release.yml` 進行正式發布：

1. 確保所有測試通過
2. 使用 `v*` 格式的標籤觸發正式發布
3. 正式版本會使用 Nuitka 進行實際編譯
