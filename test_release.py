#!/usr/bin/env python3
"""
測試發布流程的 Python 腳本
用於驗證檔案創建、複製和打包等步驟
"""

import os
import sys
import shutil
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


def check_file_exists(file_path, description="檔案"):
    """檢查檔案是否存在"""
    if os.path.exists(file_path):
        size = os.path.getsize(file_path)
        log_info(f"✅ {description} 存在: {file_path} (大小: {size} bytes)")
        return True
    else:
        log_error(f"❌ {description} 不存在: {file_path}")
        return False


def test_dist_directory():
    """測試 dist 目錄和執行檔"""
    log_info("開始測試 dist 目錄...")

    dist_path = Path("dist")
    exe_path = dist_path / "SystemMonitor.exe"

    # 檢查 dist 目錄
    if not dist_path.exists():
        log_error("dist 目錄不存在")
        return False

    log_info(f"✅ dist 目錄存在: {dist_path.absolute()}")

    # 檢查執行檔
    if not check_file_exists(exe_path, "SystemMonitor.exe"):
        return False

    # 讀取並顯示假執行檔內容
    try:
        with open(exe_path, "r", encoding="utf-8") as f:
            content = f.read()
        log_info(f"假執行檔內容:\n{content}")
    except Exception as e:
        log_error(f"無法讀取假執行檔: {e}")
        return False

    return True


def test_required_files():
    """測試必要檔案是否存在"""
    log_info("檢查必要檔案...")

    required_files = [
        ("config.example.json", "設定檔範例"),
        ("README.md", "說明文件"),
    ]

    all_files_exist = True
    for file_path, description in required_files:
        if not check_file_exists(file_path, description):
            all_files_exist = False

    return all_files_exist


def simulate_file_operations():
    """模擬檔案操作過程"""
    log_info("模擬檔案複製和打包操作...")

    # 建立測試 release 目錄
    release_dir = Path("test_release")
    if release_dir.exists():
        shutil.rmtree(release_dir)

    release_dir.mkdir()
    log_info(f"✅ 建立測試目錄: {release_dir.absolute()}")

    # 模擬複製檔案
    files_to_copy = [
        ("dist/SystemMonitor.exe", "SystemMonitor.exe"),
        ("config.example.json", "config.example.json"),
        ("README.md", "README.md"),
    ]

    for src, dst in files_to_copy:
        src_path = Path(src)
        dst_path = release_dir / dst

        if src_path.exists():
            shutil.copy2(src_path, dst_path)
            log_info(f"✅ 複製檔案: {src} -> {dst_path}")
        else:
            log_error(f"❌ 來源檔案不存在: {src}")
            return False

    # 檢查複製結果
    log_info("檢查複製結果:")
    for item in release_dir.iterdir():
        size = item.stat().st_size if item.is_file() else 0
        log_info(f"  - {item.name} ({size} bytes)")

    # 清理測試目錄
    shutil.rmtree(release_dir)
    log_info(f"✅ 清理測試目錄: {release_dir}")

    return True


def test_environment():
    """測試環境資訊"""
    log_info("測試環境資訊:")
    log_info(f"  - Python 版本: {sys.version}")
    log_info(f"  - 作業系統: {os.name}")
    log_info(f"  - 當前工作目錄: {os.getcwd()}")
    log_info(f"  - 腳本路徑: {__file__}")


def main():
    """主函數"""
    log_info("=" * 50)
    log_info("開始測試發布流程")
    log_info("=" * 50)

    # 測試環境
    test_environment()

    # 執行各項測試
    tests = [
        ("測試 dist 目錄和執行檔", test_dist_directory),
        ("測試必要檔案", test_required_files),
        ("模擬檔案操作", simulate_file_operations),
    ]

    all_passed = True
    for test_name, test_func in tests:
        log_info(f"\n--- {test_name} ---")
        try:
            result = test_func()
            if result:
                log_info(f"✅ {test_name} 通過")
            else:
                log_error(f"❌ {test_name} 失敗")
                all_passed = False
        except Exception as e:
            log_error(f"❌ {test_name} 發生異常: {e}")
            all_passed = False

    # 總結
    log_info("\n" + "=" * 50)
    if all_passed:
        log_info("🎉 所有測試通過！發布流程準備就緒。")
        sys.exit(0)
    else:
        log_error("❌ 部分測試失敗，請檢查上述錯誤。")
        sys.exit(1)


if __name__ == "__main__":
    main()
