"""
系統托盤圖示模組
"""

import pystray
from PIL import Image
import threading
import time
from pathlib import Path
from typing import Callable, Optional
from superyngo_logger import init_logger

# 初始化日誌器
logger = init_logger(app_name="system_monitor")


class SystemTrayIcon:
    """系統托盤圖示"""

    def __init__(
        self,
        title: str = "System Monitor",
        icon_path: str = "assets/icon.ico",
        on_settings_click: Optional[Callable] = None,
        on_toggle_monitoring: Optional[Callable] = None,
        on_exit_click: Optional[Callable] = None,
    ):
        """
        初始化系統托盤圖示

        Args:
            title: 托盤圖示標題
            icon_path: 圖示檔案路徑
            on_settings_click: 設定按鈕點擊回調
            on_toggle_monitoring: 切換監控狀態回調
            on_exit_click: 退出按鈕點擊回調
        """
        self.title = title
        self.icon_path = Path(icon_path)
        self.on_settings_click = on_settings_click
        self.on_toggle_monitoring = on_toggle_monitoring
        self.on_exit_click = on_exit_click

        self.icon = None
        self.is_running = False
        self.is_monitoring = False
        self.last_status = "就緒"

        logger.info(f"系統托盤圖示初始化: {title}")

    def _load_icon_image(self) -> Image.Image:
        """載入圖示圖片"""
        try:
            if self.icon_path.exists():
                return Image.open(self.icon_path)
            else:
                # 如果找不到圖示，建立一個簡單的預設圖示
                logger.warning(f"圖示檔案不存在: {self.icon_path}，使用預設圖示")
                return self._create_default_icon()
        except Exception as e:
            logger.error(f"載入圖示失敗: {e}，使用預設圖示")
            return self._create_default_icon()

    def _create_default_icon(self) -> Image.Image:
        """建立預設圖示"""
        try:
            # 建立一個簡單的 16x16 圖示
            img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
            # 畫一個簡單的矩形
            for x in range(2, 14):
                for y in range(2, 14):
                    if x == 2 or x == 13 or y == 2 or y == 13:
                        img.putpixel((x, y), (64, 128, 255, 255))
                    elif 4 <= x <= 11 and 4 <= y <= 11:
                        img.putpixel((x, y), (32, 32, 32, 255))
            return img
        except Exception as e:
            logger.error(f"建立預設圖示失敗: {e}")
            # 最後手段：建立純色圖示
            return Image.new("RGBA", (16, 16), (64, 128, 255, 255))

    def _on_settings_clicked(self, icon, item):
        """設定按鈕點擊處理"""
        try:
            if self.on_settings_click:
                logger.info("開啟設定視窗")
                self.on_settings_click()
        except Exception as e:
            logger.error(f"開啟設定失敗: {e}")

    def _on_toggle_monitoring_clicked(self, icon, item):
        """切換監控狀態處理"""
        try:
            if self.on_toggle_monitoring:
                self.is_monitoring = not self.is_monitoring
                logger.info(f"切換監控狀態: {'啟動' if self.is_monitoring else '停止'}")
                self.on_toggle_monitoring(self.is_monitoring)
                self._update_menu()
        except Exception as e:
            logger.error(f"切換監控狀態失敗: {e}")

    def _on_exit_clicked(self, icon, item):
        """退出按鈕點擊處理"""
        try:
            logger.info("準備退出應用程式")
            if self.on_exit_click:
                self.on_exit_click()
            self.stop()
        except Exception as e:
            logger.error(f"退出應用程式失敗: {e}")

    def _create_menu(self) -> pystray.Menu:
        """建立右鍵選單"""
        monitoring_text = "停止監控" if self.is_monitoring else "開始監控"

        menu_items = [
            pystray.MenuItem(
                f"狀態: {self.last_status}",
                lambda: None,  # 不可點擊的狀態項目
                enabled=False,
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(monitoring_text, self._on_toggle_monitoring_clicked),
            pystray.MenuItem("設定", self._on_settings_clicked),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("退出", self._on_exit_clicked),
        ]

        return pystray.Menu(*menu_items)

    def _update_menu(self):
        """更新選單"""
        try:
            if self.icon:
                self.icon.menu = self._create_menu()
                self.icon.update_menu()
        except Exception as e:
            logger.error(f"更新選單失敗: {e}")

    def start(self):
        """啟動托盤圖示"""
        try:
            if self.is_running:
                return

            image = self._load_icon_image()
            menu = self._create_menu()

            self.icon = pystray.Icon(self.title, image, menu=menu)

            self.is_running = True
            logger.info("系統托盤圖示已啟動")

            # 在新執行緒中運行
            def run_icon():
                try:
                    self.icon.run()
                except Exception as e:
                    logger.error(f"托盤圖示運行失敗: {e}")
                finally:
                    self.is_running = False

            icon_thread = threading.Thread(target=run_icon, daemon=True)
            icon_thread.start()

        except Exception as e:
            logger.error(f"啟動托盤圖示失敗: {e}")
            self.is_running = False

    def stop(self):
        """停止托盤圖示"""
        try:
            if self.icon and self.is_running:
                self.icon.stop()
                self.is_running = False
                logger.info("系統托盤圖示已停止")
        except Exception as e:
            logger.error(f"停止托盤圖示失敗: {e}")

    def update_status(self, status: str, monitoring: Optional[bool] = None):
        """
        更新狀態

        Args:
            status: 狀態文字
            monitoring: 監控狀態（可選）
        """
        try:
            self.last_status = status
            if monitoring is not None:
                self.is_monitoring = monitoring

            self._update_menu()

            # 更新托盤提示文字
            if self.icon:
                tooltip = f"{self.title}\n狀態: {status}\n監控: {'啟動' if self.is_monitoring else '停止'}"
                self.icon.title = tooltip

        except Exception as e:
            logger.error(f"更新狀態失敗: {e}")

    def show_notification(self, title: str, message: str):
        """
        顯示通知

        Args:
            title: 通知標題
            message: 通知訊息
        """
        try:
            if self.icon:
                self.icon.notify(message, title)
                logger.debug(f"顯示通知: {title} - {message}")
        except Exception as e:
            logger.error(f"顯示通知失敗: {e}")

    def wait_for_exit(self):
        """等待圖示退出"""
        try:
            while self.is_running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            logger.info("接收到鍵盤中斷信號")
            self.stop()

    @property
    def visible(self) -> bool:
        """檢查圖示是否可見"""
        return self.is_running and self.icon is not None
