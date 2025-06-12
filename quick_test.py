#!/usr/bin/env python3

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_basic_functionality():
    print("=== 基本功能測試 ===")

    # 測試系統資訊收集
    from src.monitor.system_info import SystemInfoCollector

    collector = SystemInfoCollector()
    cpu = collector.get_cpu_usage()
    print(f"CPU 使用率測試: {cpu}%")

    # 測試檔案掃描
    from src.monitor.file_scanner import FileScanner

    scanner = FileScanner(max_depth=1, max_files_per_dir=5)
    result = scanner.scan_directory(".")
    print(f"檔案掃描測試: {result['total_files']} 檔案")

    # 測試設定
    from src.config.settings import Settings

    settings = Settings()
    print(f"設定測試: 間隔 {settings.interval_minutes} 分鐘")

    print("所有基本功能測試通過!")


if __name__ == "__main__":
    test_basic_functionality()
