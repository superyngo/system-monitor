# GitHub Repository 設定指南

## 1. 建立 Repository

1. 到 [GitHub](https://github.com) 建立新的 repository
2. Repository 名稱建議：`system-monitor`
3. 設為 **Public**（如果要讓其他人使用）或 **Private**
4. **不要** 初始化 README、.gitignore 或 LICENSE（因為本地已有）

## 2. 上傳專案到 GitHub

在專案根目錄執行以下命令：

```powershell
# 初始化 Git repository（如果還沒有的話）
git init

# 添加所有檔案
git add .

# 建立初始 commit
git commit -m "Initial commit: System Monitor v0.1.0"

# 添加遠端 repository（請替換成您的 GitHub username 和 repository 名稱）
git remote add origin https://github.com/YOUR_USERNAME/system-monitor.git

# 推送到 GitHub
git branch -M main
git push -u origin main
```

## 3. 設定 GitHub Actions 權限

1. 到您的 GitHub repository
2. 點選 **Settings** 標籤
3. 左側選單點選 **Actions** > **General**
4. 在 "Workflow permissions" 區域：
   - 選擇 "Read and write permissions"
   - 勾選 "Allow GitHub Actions to create and approve pull requests"
5. 點選 **Save**

## 4. 發布第一個版本

### 方法一：使用發布腳本（推薦）

```powershell
# 發布 0.1.0 版本
python release.py 0.1.0 "Initial release with basic monitoring features"
```

### 方法二：手動建立 tag

```powershell
# 提交所有變更
git add .
git commit -m "Release version 0.1.0"

# 建立 tag
git tag -a v0.1.0 -m "Release v0.1.0"

# 推送到 GitHub
git push origin main
git push origin v0.1.0
```

## 5. 監控建置狀態

1. 推送 tag 後，到 GitHub repository
2. 點選 **Actions** 標籤
3. 查看 "Build and Release" workflow 的執行狀態
4. 建置完成後，會自動建立 Release 並上傳編譯好的執行檔

## 6. 觸發條件說明

### 自動觸發：

- 當推送符合 `v*` 格式的 tag 時（如 v1.0.0, v0.1.0）

### 手動觸發：

1. 到 GitHub repository 的 **Actions** 標籤
2. 點選 "Build and Release" workflow
3. 點選 "Run workflow" 按鈕
4. 輸入版本號（如 v0.2.0）
5. 點選 "Run workflow"

## 7. 版本號命名建議

採用語義版本控制（Semantic Versioning）：

- **主版本號.次版本號.修補版本號** (如 1.0.0)
- **主版本號**：重大功能變更或不相容的 API 修改
- **次版本號**：新增功能但保持向後相容
- **修補版本號**：Bug 修復

範例：

- `v0.1.0` - 初始版本
- `v0.2.0` - 新增 Google Sheets 整合功能
- `v0.2.1` - 修復 CPU 監控的 Bug
- `v1.0.0` - 第一個穩定版本

## 8. 疑難排解

### 如果 Actions 執行失敗：

1. 檢查 repository 的 Actions 權限設定
2. 確認 `pyproject.toml` 中的依賴項目正確
3. 查看 Actions 的錯誤日誌

### 如果無法推送 tag：

```powershell
# 刪除本地 tag
git tag -d v0.1.0

# 刪除遠端 tag（如果已推送）
git push --delete origin v0.1.0

# 重新建立正確的 tag
git tag -a v0.1.0 -m "Release v0.1.0"
git push origin v0.1.0
```
