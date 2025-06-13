#!/usr/bin/env python3
"""
本地模擬完整發布流程測試腳本
模擬 GitHub Actions 的完整流程，包括壓縮檔建立
"""

import sys
import shutil
import zipfile
from pathlib import Path
from datetime import datetime


def log_info(message):
    """輸出信息日誌"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[INFO] {timestamp} - {message}")


def log_error(message):
    """輸出錯誤日誌"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[ERROR] {timestamp} - {message}")


def simulate_full_release_process(version="test-v0.1.0"):
    """模擬完整的發布流程"""
    log_info("=" * 60)
    log_info(f"開始模擬完整發布流程 - 版本: {version}")
    log_info("=" * 60)

    try:
        # 步驟 1: 確保 dist 目錄存在並建立假執行檔
        log_info("步驟 1: 建立假執行檔...")
        dist_dir = Path("dist")
        dist_dir.mkdir(exist_ok=True)

        fake_exe_content = f"""This is a fake SystemMonitor.exe for testing purposes.
Build Date: {datetime.now()}
Version: {version}
Platform: Windows
Architecture: x64
Test Mode: ON
"""

        exe_path = dist_dir / "SystemMonitor.exe"
        with open(exe_path, "w", encoding="utf-8") as f:
            f.write(fake_exe_content)

        log_info(f"✅ 假執行檔已建立: {exe_path} ({exe_path.stat().st_size} bytes)")

        # 步驟 2: 建立 release 目錄
        log_info("步驟 2: 建立 release 目錄...")
        release_dir = Path("release")
        if release_dir.exists():
            shutil.rmtree(release_dir)
        release_dir.mkdir()
        log_info(f"✅ Release 目錄已建立: {release_dir}")

        # 步驟 3: 複製檔案到 release 目錄
        log_info("步驟 3: 複製檔案到 release 目錄...")
        files_to_copy = [
            (exe_path, "SystemMonitor.exe"),
            ("config.example.json", "config.example.json"),
            ("README.md", "README.md"),
        ]

        for src, dst in files_to_copy:
            src_path = Path(src)
            dst_path = release_dir / dst

            if src_path.exists():
                shutil.copy2(src_path, dst_path)
                log_info(f"✅ 複製: {src} -> {dst_path}")
            else:
                log_error(f"❌ 來源檔案不存在: {src}")
                return False

        # 步驟 4: 建立壓縮檔
        log_info("步驟 4: 建立壓縮檔...")
        zip_filename = f"SystemMonitor-{version}.zip"
        zip_path = Path(zip_filename)

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for file_path in release_dir.rglob("*"):
                if file_path.is_file():
                    # 在 ZIP 中使用相對路徑（不包含 release/ 前綴）
                    arcname = file_path.relative_to(release_dir)
                    zipf.write(file_path, arcname)
                    log_info(f"  添加到 ZIP: {arcname}")

        zip_size = zip_path.stat().st_size
        log_info(f"✅ 壓縮檔已建立: {zip_path} ({zip_size} bytes)")

        # 步驟 5: 驗證壓縮檔內容
        log_info("步驟 5: 驗證壓縮檔內容...")
        with zipfile.ZipFile(zip_path, "r") as zipf:
            file_list = zipf.namelist()
            log_info("壓縮檔內容:")
            for file_name in file_list:
                file_info = zipf.getinfo(file_name)
                log_info(f"  - {file_name} ({file_info.file_size} bytes)")

        # 步驟 6: 測試解壓縮
        log_info("步驟 6: 測試解壓縮...")
        extract_dir = Path("test_extract")
        if extract_dir.exists():
            shutil.rmtree(extract_dir)

        with zipfile.ZipFile(zip_path, "r") as zipf:
            zipf.extractall(extract_dir)

        log_info("解壓縮結果:")
        for item in extract_dir.rglob("*"):
            if item.is_file():
                log_info(
                    f"  - {item.relative_to(extract_dir)} ({item.stat().st_size} bytes)"
                )

        # 步驟 7: 清理
        log_info("步驟 7: 清理暫存檔案...")
        shutil.rmtree(release_dir)
        shutil.rmtree(extract_dir)
        log_info("✅ 暫存檔案已清理")

        # 成功總結
        log_info("=" * 60)
        log_info("🎉 完整發布流程模擬成功！")
        log_info(f"📦 產生的發布檔案: {zip_path}")
        log_info(f"📁 檔案大小: {zip_size} bytes")
        log_info(f"🏷️  版本標籤: {version}")
        log_info("=" * 60)

        return True

    except Exception as e:
        log_error(f"發布流程失敗: {e}")
        return False


def cleanup():
    """清理所有測試產生的檔案"""
    log_info("清理測試檔案...")

    cleanup_items = ["dist", "release", "test_extract", "SystemMonitor-*.zip"]

    for item in cleanup_items:
        if "*" in item:
            # 處理萬用字元
            for path in Path(".").glob(item):
                if path.exists():
                    if path.is_dir():
                        shutil.rmtree(path)
                    else:
                        path.unlink()
                    log_info(f"🗑️  已刪除: {path}")
        else:
            path = Path(item)
            if path.exists():
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink()
                log_info(f"🗑️  已刪除: {path}")


def main():
    """主函數"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "cleanup":
            cleanup()
            return
        elif sys.argv[1].startswith("test-"):
            version = sys.argv[1]
        else:
            version = f"test-{sys.argv[1]}"
    else:
        version = "test-v0.1.0"

    # 執行完整流程測試
    success = simulate_full_release_process(version)

    if success:
        log_info("\n💡 提示：")
        log_info("   - 檢查生成的 ZIP 檔案")
        log_info("   - 執行 'python local_test_full.py cleanup' 清理檔案")
        log_info("   - 可指定版本：'python local_test_full.py v1.2.3'")
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
