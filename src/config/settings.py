"""
配置管理模組
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any
from superyngo_logger import init_logger

# 初始化日誌器
logger = init_logger(app_name="system_monitor")


class Settings:
    """系統監控設定管理"""

    def __init__(self, config_file: str = "config.json"):
        self.config_file = Path(config_file)
        self.config = self._load_default_config()
        self.load()

    def _load_default_config(self) -> Dict[str, Any]:
        """載入預設設定"""
        return {
            "google_sheets": {
                "credentials_file": "",
                "spreadsheet_url": "",
                "worksheet_name": "System Monitor",
            },
            "monitoring": {
                "interval_minutes": 5,
                "monitor_directories": [],
                "enable_cpu_monitoring": True,
                "enable_ram_monitoring": True,
                "enable_internet_monitoring": True,
                "enable_directory_monitoring": True,
            },
            "ui": {
                "show_notifications": True,
                "minimize_to_tray": True,
                "start_minimized": False,
            },
            "logging": {
                "log_level": "INFO",
                "log_file": "system_monitor.log",
                "max_log_size_mb": 10,
                "backup_count": 5,
            },
        }

    def load(self) -> None:
        """從檔案載入設定"""
        try:
            if self.config_file.exists():
                with open(self.config_file, "r", encoding="utf-8") as f:
                    loaded_config = json.load(f)
                    # 合併設定，保留預設值
                    self._merge_config(self.config, loaded_config)
                logger.info(f"設定已從 {self.config_file} 載入")
            else:
                logger.info("設定檔案不存在，使用預設設定")
                self.save()  # 儲存預設設定
        except Exception as e:
            logger.error(f"載入設定失敗: {e}")
            logger.info("使用預設設定")

    def _merge_config(self, default: Dict, loaded: Dict) -> None:
        """遞迴合併設定"""
        for key, value in loaded.items():
            if key in default:
                if isinstance(default[key], dict) and isinstance(value, dict):
                    self._merge_config(default[key], value)
                else:
                    default[key] = value

    def save(self) -> None:
        """儲存設定到檔案"""
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            logger.info(f"設定已儲存到 {self.config_file}")
        except Exception as e:
            logger.error(f"儲存設定失敗: {e}")

    def get(self, key_path: str, default: Any = None) -> Any:
        """取得設定值（支援點記法路徑）"""
        keys = key_path.split(".")
        value = self.config

        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, key_path: str, value: Any) -> None:
        """設定值（支援點記法路徑）"""
        keys = key_path.split(".")
        config = self.config

        # 建立巢狀字典結構
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]

        config[keys[-1]] = value
        self.save()

    # 便利方法
    @property
    def credentials_file(self) -> str:
        return self.get("google_sheets.credentials_file", "")

    @credentials_file.setter
    def credentials_file(self, value: str) -> None:
        self.set("google_sheets.credentials_file", value)

    @property
    def spreadsheet_url(self) -> str:
        return self.get("google_sheets.spreadsheet_url", "")

    @spreadsheet_url.setter
    def spreadsheet_url(self, value: str) -> None:
        self.set("google_sheets.spreadsheet_url", value)

    @property
    def worksheet_name(self) -> str:
        return self.get("google_sheets.worksheet_name", "System Monitor")

    @worksheet_name.setter
    def worksheet_name(self, value: str) -> None:
        self.set("google_sheets.worksheet_name", value)

    @property
    def interval_minutes(self) -> int:
        return self.get("monitoring.interval_minutes", 5)

    @interval_minutes.setter
    def interval_minutes(self, value: int) -> None:
        self.set("monitoring.interval_minutes", max(1, value))

    @property
    def monitor_directories(self) -> List[str]:
        return self.get("monitoring.monitor_directories", [])

    @monitor_directories.setter
    def monitor_directories(self, value: List[str]) -> None:
        self.set("monitoring.monitor_directories", value)

    def add_monitor_directory(self, directory: str) -> None:
        """新增監控目錄"""
        dirs = self.monitor_directories
        if directory not in dirs:
            dirs.append(directory)
            self.monitor_directories = dirs

    def remove_monitor_directory(self, directory: str) -> None:
        """移除監控目錄"""
        dirs = self.monitor_directories
        if directory in dirs:
            dirs.remove(directory)
            self.monitor_directories = dirs

    def validate(self) -> List[str]:
        """驗證設定，回傳錯誤清單"""
        errors = []

        # 檢查 Google Sheets 設定
        if not self.credentials_file:
            errors.append("未設定 Google Sheets 憑證檔案")
        elif not os.path.exists(self.credentials_file):
            errors.append(f"Google Sheets 憑證檔案不存在: {self.credentials_file}")

        if not self.spreadsheet_url:
            errors.append("未設定 Google Sheets 表單 URL")

        # 檢查監控目錄
        for directory in self.monitor_directories:
            if not os.path.exists(directory):
                errors.append(f"監控目錄不存在: {directory}")

        # 檢查監控間隔
        if self.interval_minutes < 1:
            errors.append("監控間隔不能小於 1 分鐘")

        return errors

    def is_valid(self) -> bool:
        """檢查設定是否有效"""
        return len(self.validate()) == 0


# 全域設定實例
settings = Settings()
