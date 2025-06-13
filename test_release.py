#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試發布流程的 Python 腳本
用於驗證檔案創建、複製和打包等步驟
"""

import os
import sys
import shutil
from pathlib import Path
from datetime import datetime

# 設置標準輸出編碼為 UTF-8，解決 GitHub Actions Windows 環境編碼問題
if sys.platform == "win32":
    os.environ["PYTHONIOENCODING"] = "utf-8"


def log_info(message):
    """輸出信息日誌"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        print(f"[INFO] {timestamp} - {message}")
    except UnicodeEncodeError:
        # 如果仍有編碼問題，使用英文替代
        print(
            f"[INFO] {timestamp} - {message.encode('ascii', 'replace').decode('ascii')}"
        )


def log_error(message):
    """輸出錯誤日誌"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        print(f"[ERROR] {timestamp} - {message}")
    except UnicodeEncodeError:
        # 如果仍有編碼問題，使用英文替代
        print(
            f"[ERROR] {timestamp} - {message.encode('ascii', 'replace').decode('ascii')}"
        )


def check_file_exists(file_path, description="File"):
    """檢查檔案是否存在"""
    if os.path.exists(file_path):
        size = os.path.getsize(file_path)
        log_info(f"✅ {description} exists: {file_path} (size: {size} bytes)")
        return True
    else:
        log_error(f"❌ {description} not found: {file_path}")
        return False


def test_dist_directory():
    """Test dist directory and executable"""
    log_info("Starting dist directory test...")

    dist_path = Path("dist")
    exe_path = dist_path / "SystemMonitor.exe"

    # Check dist directory
    if not dist_path.exists():
        log_error("dist directory does not exist")
        return False

    log_info(f"✅ dist directory exists: {dist_path.absolute()}")

    # Check executable
    if not check_file_exists(exe_path, "SystemMonitor.exe"):
        return False

    # Read and display fake executable content
    try:
        with open(exe_path, "r", encoding="utf-8") as f:
            content = f.read()
        log_info(f"Fake executable content:\n{content}")
    except Exception as e:
        log_error(f"Cannot read fake executable: {e}")
        return False

    return True


def test_required_files():
    """Test if required files exist"""
    log_info("Checking required files...")

    required_files = [
        ("config.example.json", "Config example"),
        ("README.md", "Documentation"),
    ]

    all_files_exist = True
    for file_path, description in required_files:
        if not check_file_exists(file_path, description):
            all_files_exist = False

    return all_files_exist


def simulate_file_operations():
    """Simulate file operations process"""
    log_info("Simulating file copy and packaging operations...")

    # Create test release directory
    release_dir = Path("test_release")
    if release_dir.exists():
        shutil.rmtree(release_dir)

    release_dir.mkdir()
    log_info(f"✅ Created test directory: {release_dir.absolute()}")

    # Simulate file copying
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
            log_info(f"✅ Copied file: {src} -> {dst_path}")
        else:
            log_error(f"❌ Source file not found: {src}")
            return False

    # Check copy results
    log_info("Checking copy results:")
    for item in release_dir.iterdir():
        size = item.stat().st_size if item.is_file() else 0
        log_info(f"  - {item.name} ({size} bytes)")

    # Clean up test directory
    shutil.rmtree(release_dir)
    log_info(f"✅ Cleaned up test directory: {release_dir}")

    return True


def test_environment():
    """Test environment information"""
    log_info("Test environment information:")
    log_info(f"  - Python version: {sys.version}")
    log_info(f"  - Operating system: {os.name}")
    log_info(f"  - Current working directory: {os.getcwd()}")
    log_info(f"  - Script path: {__file__}")


def main():
    """Main function"""
    log_info("=" * 50)
    log_info("Starting release process test")
    log_info("=" * 50)

    # Test environment
    test_environment()

    # Execute tests
    tests = [
        ("Test dist directory and executable", test_dist_directory),
        ("Test required files", test_required_files),
        ("Simulate file operations", simulate_file_operations),
    ]

    all_passed = True
    for test_name, test_func in tests:
        log_info(f"\n--- {test_name} ---")
        try:
            result = test_func()
            if result:
                log_info(f"✅ {test_name} passed")
            else:
                log_error(f"❌ {test_name} failed")
                all_passed = False
        except Exception as e:
            log_error(f"❌ {test_name} exception: {e}")
            all_passed = False  # Summary
    log_info("\n" + "=" * 50)
    if all_passed:
        log_info("🎉 All tests passed! Release process is ready.")
        sys.exit(0)
    else:
        log_error("❌ Some tests failed, please check the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
