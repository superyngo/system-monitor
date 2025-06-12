"""
Google Sheets API 整合模組
"""

import gspread
from google.oauth2.service_account import Credentials
from typing import List, Dict, Any, Optional
from datetime import datetime
import time
from superyngo_logger import init_logger

# 初始化日誌器
logger = init_logger(app_name="system_monitor")


class GoogleSheetsClient:
    """Google Sheets 客戶端"""

    # Google Sheets API 範圍
    SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]

    def __init__(
        self,
        credentials_file: str,
        spreadsheet_url: str,
        worksheet_name: str = "System Monitor",
    ):
        """
        初始化 Google Sheets 客戶端

        Args:
            credentials_file: 服務帳戶憑證檔案路徑
            spreadsheet_url: Google Sheets 表單 URL
            worksheet_name: 工作表名稱
        """
        self.credentials_file = credentials_file
        self.spreadsheet_url = spreadsheet_url
        self.worksheet_name = worksheet_name
        self.client = None
        self.spreadsheet = None
        self.worksheet = None
        self._last_connection_time = 0
        self._connection_timeout = 300  # 5分鐘重新連線

        logger.info(f"Google Sheets 客戶端初始化: {worksheet_name}")

    def connect(self) -> bool:
        """
        連線到 Google Sheets

        Returns:
            連線是否成功
        """
        try:
            # 檢查是否需要重新連線
            current_time = time.time()
            if (
                self.client is not None
                and current_time - self._last_connection_time < self._connection_timeout
            ):
                return True

            logger.info("正在連線到 Google Sheets...")

            # 建立憑證
            credentials = Credentials.from_service_account_file(
                self.credentials_file, scopes=self.SCOPES
            )

            # 建立客戶端
            self.client = gspread.authorize(credentials)

            # 開啟試算表
            self.spreadsheet = self.client.open_by_url(self.spreadsheet_url)

            # 取得或建立工作表
            try:
                self.worksheet = self.spreadsheet.worksheet(self.worksheet_name)
                logger.info(f"找到現有工作表: {self.worksheet_name}")
            except gspread.WorksheetNotFound:
                logger.info(f"建立新工作表: {self.worksheet_name}")
                self.worksheet = self.spreadsheet.add_worksheet(
                    title=self.worksheet_name, rows=1000, cols=20
                )
                self._setup_headers()

            self._last_connection_time = current_time
            logger.info("Google Sheets 連線成功")
            return True

        except FileNotFoundError:
            logger.error(f"憑證檔案不存在: {self.credentials_file}")
            return False
        except Exception as e:
            logger.error(f"連線到 Google Sheets 失敗: {e}")
            return False

    def _setup_headers(self) -> None:
        """設定表頭"""
        try:
            headers = [
                "時間戳記",
                "CPU使用率(%)",
                "RAM使用率(%)",
                "RAM使用量(GB)",
                "RAM總量(GB)",
                "網路上傳(MB/s)",
                "網路下載(MB/s)",
                "目錄內容",
                "電池電量(%)",
                "電池狀態",
                "系統運行時間(小時)",
                "磁碟使用率(%)",
                "磁碟可用空間(GB)",
            ]

            self.worksheet.append_row(headers)
            logger.info("已設定表頭")

        except Exception as e:
            logger.error(f"設定表頭失敗: {e}")

    def upload_system_data(
        self, system_info: Dict[str, Any], directory_contents: str = ""
    ) -> bool:
        """
        上傳系統資料到 Google Sheets

        Args:
            system_info: 系統資訊
            directory_contents: 目錄內容字串

        Returns:
            上傳是否成功
        """
        try:
            if not self.connect():
                return False

            # 準備資料列
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # 取得各項資訊
            cpu_usage = system_info.get("cpu_usage", 0)
            memory = system_info.get("memory", {})
            internet = system_info.get("internet", {})
            battery = system_info.get("battery", {})
            uptime = system_info.get("uptime", {})
            disk = system_info.get("disk", {})

            # 建立資料列
            row_data = [
                timestamp,
                cpu_usage,
                memory.get("usage_percent", 0),
                memory.get("used_gb", 0),
                memory.get("total_gb", 0),
                internet.get("mb_sent_per_sec", 0),
                internet.get("mb_recv_per_sec", 0),
                directory_contents,
                battery.get("percent", 0)
                if battery.get("has_battery", False)
                else "N/A",
                "充電中"
                if battery.get("power_plugged", False)
                else "使用電池"
                if battery.get("has_battery", False)
                else "無電池",
                uptime.get("uptime_hours", 0),
                disk.get("usage_percent", 0),
                disk.get("free_gb", 0),
            ]

            # 上傳資料
            self.worksheet.append_row(row_data)

            logger.info(
                f"成功上傳系統資料: CPU {cpu_usage}%, RAM {memory.get('usage_percent', 0)}%"
            )
            return True

        except Exception as e:
            logger.error(f"上傳系統資料失敗: {e}")
            return False

    def get_last_n_rows(self, n: int = 10) -> List[List[str]]:
        """
        取得最後 N 筆資料

        Args:
            n: 要取得的資料筆數

        Returns:
            資料列清單
        """
        try:
            if not self.connect():
                return []

            all_records = self.worksheet.get_all_values()
            if len(all_records) <= 1:  # 只有表頭或沒有資料
                return []

            # 回傳最後 N 筆資料（不包含表頭）
            return all_records[-n:] if len(all_records) > n else all_records[1:]

        except Exception as e:
            logger.error(f"取得資料失敗: {e}")
            return []

    def clear_old_data(self, keep_days: int = 30) -> bool:
        """
        清除舊資料

        Args:
            keep_days: 保留天數

        Returns:
            清除是否成功
        """
        try:
            if not self.connect():
                return False

            from datetime import datetime, timedelta

            all_records = self.worksheet.get_all_values()
            if len(all_records) <= 1:
                return True

            # 計算保留的日期界限
            cutoff_date = datetime.now() - timedelta(days=keep_days)

            # 找出要保留的資料
            headers = all_records[0]
            rows_to_keep = [headers]  # 保留表頭

            for row in all_records[1:]:
                if len(row) > 0:
                    try:
                        row_date = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
                        if row_date >= cutoff_date:
                            rows_to_keep.append(row)
                    except ValueError:
                        # 如果日期格式不正確，保留該列
                        rows_to_keep.append(row)

            # 清除工作表並重新寫入資料
            if len(rows_to_keep) < len(all_records):
                self.worksheet.clear()
                if rows_to_keep:
                    self.worksheet.update(rows_to_keep)

                deleted_count = len(all_records) - len(rows_to_keep)
                logger.info(f"已清除 {deleted_count} 筆舊資料")

            return True

        except Exception as e:
            logger.error(f"清除舊資料失敗: {e}")
            return False

    def test_connection(self) -> Dict[str, Any]:
        """
        測試連線

        Returns:
            測試結果
        """
        result = {
            "success": False,
            "message": "",
            "spreadsheet_title": "",
            "worksheet_title": "",
            "error": "",
        }

        try:
            if self.connect():
                result["success"] = True
                result["message"] = "連線成功"
                result["spreadsheet_title"] = self.spreadsheet.title
                result["worksheet_title"] = self.worksheet.title
                logger.info("Google Sheets 連線測試成功")
            else:
                result["message"] = "連線失敗"
                result["error"] = "無法建立連線"

        except Exception as e:
            result["message"] = "連線測試失敗"
            result["error"] = str(e)
            logger.error(f"Google Sheets 連線測試失敗: {e}")

        return result

    def get_spreadsheet_info(self) -> Dict[str, Any]:
        """
        取得試算表資訊

        Returns:
            試算表資訊
        """
        try:
            if not self.connect():
                return {}

            info = {
                "title": self.spreadsheet.title,
                "id": self.spreadsheet.id,
                "url": self.spreadsheet.url,
                "worksheet_count": len(self.spreadsheet.worksheets()),
                "current_worksheet": self.worksheet.title,
                "row_count": self.worksheet.row_count,
                "col_count": self.worksheet.col_count,
            }

            return info

        except Exception as e:
            logger.error(f"取得試算表資訊失敗: {e}")
            return {}
