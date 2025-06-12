#!/usr/bin/env python3
"""
System Monitor - Windows 系統監控工具

功能：
- 即時監控 CPU、RAM、網路使用率
- 監控指定資料夾內容
- 自動上傳數據到 Google Sheets
- 系統托盤常駐程式
- 簡易設定介面

作者：System Monitor Team
版本：1.0.0
"""

from typing import Optional

import sys
import os
import time
import schedule
import threading
import tkinter as tk
from pathlib import Path

# 新增 src 目錄到 Python 路徑
# sys.path.insert(0, str(Path(__file__).parent / "src"))

from superyngo_logger import init_logger
from src.config import settings
from src.monitor import SystemInfoCollector, FileScanner
from src.api import GoogleSheetsClient
from src.ui import SystemTrayIcon, show_settings_window

# 初始化日誌器
logger = init_logger(app_name="system_monitor")
os.environ["PYTHONUTF8"] = "1"


class SystemMonitor:
    """系統監控主程式"""

    def __init__(self):
        """初始化系統監控器"""
        self.is_running = False
        self.is_monitoring = False
        self.monitoring_thread = None
        self.schedule_lock = threading.Lock()  # 新增鎖用於保護 schedule

        # 初始化元件
        self.system_collector = SystemInfoCollector()
        self.file_scanner = FileScanner()
        self.sheets_client = None
        self.tray_icon = None

        # 設定視窗
        self.settings_window = None

        # 創建隱藏的 tkinter 根視窗用於主執行緒操作
        self.root = tk.Tk()
        self.root.withdraw()  # 隱藏根視窗

        # 設定根視窗屬性
        self.root.protocol("WM_DELETE_WINDOW", self.shutdown)

        logger.info("System Monitor 初始化完成")

    def _initialize_sheets_client(self) -> bool:
        """初始化 Google Sheets 客戶端"""
        try:
            if not settings.credentials_file or not settings.spreadsheet_url:
                logger.warning("Google Sheets 設定不完整")
                return False

            self.sheets_client = GoogleSheetsClient(
                settings.credentials_file,
                settings.spreadsheet_url,
                settings.worksheet_name,
            )

            # 測試連線
            test_result = self.sheets_client.test_connection()
            if test_result["success"]:
                logger.info("Google Sheets 連線成功")
                return True
            else:
                logger.error(f"Google Sheets 連線失敗: {test_result['error']}")
                return False

        except Exception as e:
            logger.error(f"初始化 Google Sheets 客戶端失敗: {e}")
            return False

    def _collect_and_upload_data(self):
        """收集並上傳系統資料"""
        try:
            # 檢查是否應該繼續監控
            if not self.is_monitoring or not self.is_running:
                return

            logger.info("開始收集系統資料...")

            # 收集系統資訊
            system_info = self.system_collector.get_all_system_info()

            # 再次檢查狀態
            if not self.is_monitoring or not self.is_running:
                return

            # 收集目錄資訊
            directory_contents = ""
            if settings.monitor_directories:
                scan_results = self.file_scanner.scan_multiple_directories(
                    settings.monitor_directories
                )
                directory_contents = self.file_scanner.format_scan_results_for_sheets(
                    scan_results
                )

            # 最後檢查狀態
            if not self.is_monitoring or not self.is_running:
                return

            # 上傳到 Google Sheets
            if self.sheets_client:
                success = self.sheets_client.upload_system_data(
                    system_info, directory_contents
                )
                if success:
                    logger.info("系統資料上傳成功")
                    self._update_tray_status("資料上傳成功")

                    # 顯示通知（如果啟用）
                    if settings.get("ui.show_notifications", True) and self.tray_icon:
                        cpu_usage = system_info.get("cpu_usage", 0)
                        ram_usage = system_info.get("memory", {}).get(
                            "usage_percent", 0
                        )
                        self.tray_icon.show_notification(
                            "系統監控",
                            f"資料已上傳 - CPU: {cpu_usage}%, RAM: {ram_usage}%",
                        )
                else:
                    logger.error("系統資料上傳失敗")
                    self._update_tray_status("資料上傳失敗")
            else:
                logger.warning("Google Sheets 客戶端未初始化")
                self._update_tray_status("未設定 Google Sheets")

        except Exception as e:
            logger.error(f"收集並上傳資料失敗: {e}")
            self._update_tray_status(f"錯誤: {str(e)[:20]}...")

    def _update_tray_status(self, status: str):
        """更新托盤狀態"""
        try:
            if self.tray_icon:
                self.tray_icon.update_status(status, self.is_monitoring)
        except Exception as e:
            logger.error(f"更新托盤狀態失敗: {e}")

    def _monitoring_loop(self):
        """監控循環"""
        logger.info("監控循環啟動")

        while self.is_running:
            try:
                # 安全地執行排程檢查
                if self.is_monitoring:
                    with self.schedule_lock:
                        schedule.run_pending()
                time.sleep(1)  # 每秒檢查一次
            except Exception as e:
                logger.error(f"監控循環錯誤: {e}")
                # 發生錯誤時等待更長時間再繼續
                for _ in range(5):
                    if not self.is_running:
                        break
                    time.sleep(1)

        logger.info("監控循環結束")

    def start_monitoring(self):
        """開始監控"""
        try:
            if self.is_monitoring:
                logger.warning("監控已在運行中")
                return

            # 驗證設定
            validation_errors = settings.validate()
            if validation_errors:
                error_msg = "設定驗證失敗:\n" + "\n".join(validation_errors)
                logger.error(error_msg)
                if self.tray_icon:
                    self.tray_icon.show_notification(
                        "設定錯誤", "請檢查 Google Sheets 設定"
                    )
                self._update_tray_status("設定錯誤")
                return

            # 初始化 Google Sheets 客戶端
            if not self._initialize_sheets_client():
                logger.error("無法初始化 Google Sheets 客戶端")
                if self.tray_icon:
                    self.tray_icon.show_notification(
                        "連線失敗", "無法連線到 Google Sheets"
                    )
                self._update_tray_status("連線失敗")
                return

            # 設定排程
            with self.schedule_lock:
                schedule.clear()  # 清除現有排程
                schedule.every(settings.interval_minutes).minutes.do(
                    self._collect_and_upload_data
                )

            self.is_monitoring = True
            self._update_tray_status("監控中...")

            # 立即執行一次
            self._collect_and_upload_data()

            logger.info(f"監控已啟動，間隔: {settings.interval_minutes} 分鐘")

            if self.tray_icon:
                self.tray_icon.show_notification(
                    "監控啟動", f"每 {settings.interval_minutes} 分鐘收集一次資料"
                )

        except Exception as e:
            logger.error(f"啟動監控失敗: {e}")
            self._update_tray_status("啟動失敗")
            if self.tray_icon:
                self.tray_icon.show_notification("錯誤", f"啟動失敗: {e}")

    def stop_monitoring(self):
        """停止監控"""
        try:
            if not self.is_monitoring:
                logger.warning("監控未在運行中")
                return

            self.is_monitoring = False
            with self.schedule_lock:
                schedule.clear()
            self._update_tray_status("已停止")

            logger.info("監控已停止")

            if self.tray_icon:
                self.tray_icon.show_notification("監控停止", "資料收集已停止")

        except Exception as e:
            logger.error(f"停止監控失敗: {e}")

    def toggle_monitoring(self, start: Optional[bool] = None):
        """切換監控狀態"""
        if start is None:
            start = not self.is_monitoring

        if start:
            self.start_monitoring()
        else:
            self.stop_monitoring()

    def show_settings(self):
        """顯示設定視窗"""
        try:
            # 檢查是否在主執行緒
            if threading.current_thread() == threading.main_thread():
                # 在主執行緒中，直接執行
                self._show_settings_main_thread()
            else:
                # 在其他執行緒中，排程到主執行緒執行
                logger.info("從背景執行緒呼叫設定視窗，排程到主執行緒")
                self.root.after(0, self._show_settings_main_thread)

        except Exception as e:
            logger.error(f"顯示設定視窗失敗: {e}")

    def _show_settings_main_thread(self):
        """在主執行緒中顯示設定視窗"""
        try:
            if self.settings_window and self.settings_window.is_open:
                # 如果視窗已開啟，則將其帶到前景
                if self.settings_window.window:
                    self.settings_window.window.lift()
                    self.settings_window.window.focus_force()
                return

            logger.info("在主執行緒中創建設定視窗")
            self.settings_window = show_settings_window(
                settings, on_settings_changed=self._on_settings_changed
            )

        except Exception as e:
            logger.error(f"在主執行緒中顯示設定視窗失敗: {e}")

    def _check_tray_status(self):
        """定期檢查托盤圖示狀態"""
        try:
            if self.is_running and self.tray_icon and self.tray_icon.is_running:
                # 如果程式和托盤圖示都在運行，繼續檢查
                self.root.after(1000, self._check_tray_status)  # 每秒檢查一次
            else:
                # 如果托盤圖示已停止，退出主循環
                logger.info("托盤圖示已停止，退出主循環")
                self.root.quit()
        except Exception as e:
            logger.error(f"檢查托盤狀態失敗: {e}")
            self.root.quit()

    def _on_settings_changed(self):
        """設定變更回調"""
        try:
            logger.info("設定已變更，重新初始化...")

            # 如果正在監控，重新啟動
            if self.is_monitoring:
                self.stop_monitoring()
                # 稍等一下再啟動，確保資源被正確釋放
                threading.Timer(1.0, self.start_monitoring).start()

            self._update_tray_status("設定已更新")

        except Exception as e:
            logger.error(f"處理設定變更失敗: {e}")

    def run(self):
        """執行主程式"""
        try:
            self.is_running = True

            # 建立托盤圖示
            self.tray_icon = SystemTrayIcon(
                title="System Monitor",
                icon_path="assets/icon.ico",
                on_settings_click=self.show_settings,
                on_toggle_monitoring=self.toggle_monitoring,
                on_exit_click=self.shutdown,
            )

            # 啟動托盤圖示
            self.tray_icon.start()

            # 啟動監控執行緒
            self.monitoring_thread = threading.Thread(
                target=self._monitoring_loop, daemon=False
            )
            self.monitoring_thread.start()

            # 初始狀態
            self._update_tray_status("就緒")

            # 如果設定完整，自動啟動監控
            if settings.is_valid():
                logger.info("設定有效，自動啟動監控")
                self.start_monitoring()
            else:
                logger.info("設定不完整，請開啟設定視窗進行設定")
                self._update_tray_status("請設定")

            logger.info("System Monitor 已啟動")

            # 設定定期檢查托盤圖示狀態
            self._check_tray_status()

            # 執行 tkinter 主循環（用於處理設定視窗等 GUI 操作）
            try:
                self.root.mainloop()
            except tk.TclError:
                # 如果 tkinter 已經結束，忽略錯誤
                pass

        except KeyboardInterrupt:
            logger.info("接收到鍵盤中斷信號")
        except Exception as e:
            logger.error(f"執行主程式失敗: {e}")
        finally:
            self.shutdown()

    def shutdown(self):
        """關閉程式"""
        try:
            logger.info("正在關閉 System Monitor...")

            self.is_running = False
            self.stop_monitoring()

            # 等待監控執行緒結束
            if self.monitoring_thread and self.monitoring_thread.is_alive():
                logger.info("等待監控執行緒結束...")
                self.monitoring_thread.join(timeout=5.0)

            # 關閉托盤圖示
            if self.tray_icon:
                self.tray_icon.stop()

            # 關閉設定視窗
            if self.settings_window and self.settings_window.is_open:
                self.settings_window._close()

            # 關閉 tkinter 根視窗
            try:
                if self.root:
                    self.root.quit()
                    self.root.destroy()
            except tk.TclError:
                # 如果 tkinter 已經關閉，忽略錯誤
                pass

            logger.info("System Monitor 已關閉")

        except Exception as e:
            logger.error(f"關閉程式失敗: {e}")


def main():
    """主函數"""
    try:
        # 設定日誌
        logger.info("=== System Monitor 啟動 ===")
        logger.info(f"Python 版本: {sys.version}")
        logger.info(f"工作目錄: {os.getcwd()}")

        # 檢查必要檔案
        required_dirs = ["src", "assets"]
        for dir_name in required_dirs:
            if not Path(dir_name).exists():
                logger.error(f"必要目錄不存在: {dir_name}")
                sys.exit(1)

        # 建立並執行監控器
        monitor = SystemMonitor()
        monitor.run()

    except Exception as e:
        logger.error(f"程式啟動失敗: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
