"""
系統資訊收集模組
"""

import psutil
import time
from typing import Dict, Union, Any
from superyngo_logger import init_logger

# 初始化日誌器
logger = init_logger(app_name="system_monitor")


class SystemInfoCollector:
    """系統資訊收集器"""

    def __init__(self):
        self._last_net_io = None
        self._last_net_time = None
        self._net_interface = self._get_primary_interface()
        logger.info("系統資訊收集器初始化完成")

    def _get_primary_interface(self) -> str:
        """取得主要網路介面"""
        try:
            # 取得預設路由的網路介面
            for interface, addrs in psutil.net_if_addrs().items():
                for addr in addrs:
                    if addr.family == 2 and not addr.address.startswith(
                        "127."
                    ):  # IPv4, not localhost
                        stats = psutil.net_if_stats().get(interface)
                        if stats and stats.isup:
                            return interface
            return (
                list(psutil.net_if_addrs().keys())[0] if psutil.net_if_addrs() else ""
            )
        except Exception as e:
            logger.warning(f"無法偵測主要網路介面: {e}")
            return ""

    def get_cpu_usage(self) -> float:
        """取得 CPU 使用率（百分比）"""
        try:
            # 第一次呼叫會回傳 0.0，所以我們呼叫兩次
            psutil.cpu_percent(interval=None)  # 非阻塞呼叫初始化
            cpu_usage = psutil.cpu_percent(interval=1.0)  # 1秒間隔測量
            logger.debug(f"CPU 使用率: {cpu_usage}%")
            return round(cpu_usage, 2)
        except Exception as e:
            logger.error(f"取得 CPU 使用率失敗: {e}")
            return 0.0

    def get_memory_usage(self) -> Dict[str, Union[float, int]]:
        """取得記憶體使用情況"""
        try:
            memory = psutil.virtual_memory()
            memory_info = {
                "total_gb": round(memory.total / (1024**3), 2),
                "used_gb": round(memory.used / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
                "usage_percent": round(memory.percent, 2),
            }
            logger.debug(f"記憶體使用情況: {memory_info}")
            return memory_info
        except Exception as e:
            logger.error(f"取得記憶體使用情況失敗: {e}")
            return {"total_gb": 0, "used_gb": 0, "available_gb": 0, "usage_percent": 0}

    def get_internet_usage(self) -> Dict[str, Union[float, str]]:
        """取得網路使用情況"""
        try:
            current_time = time.time()
            net_io = psutil.net_io_counters()

            if self._last_net_io is None or self._last_net_time is None:
                # 第一次呼叫，儲存初始值
                self._last_net_io = net_io
                self._last_net_time = current_time
                return {
                    "bytes_sent_per_sec": 0.0,
                    "bytes_recv_per_sec": 0.0,
                    "mb_sent_per_sec": 0.0,
                    "mb_recv_per_sec": 0.0,
                    "interface": self._net_interface,
                }

            # 計算時間差和流量差
            time_diff = current_time - self._last_net_time
            bytes_sent_diff = net_io.bytes_sent - self._last_net_io.bytes_sent
            bytes_recv_diff = net_io.bytes_recv - self._last_net_io.bytes_recv

            # 計算每秒流量
            bytes_sent_per_sec = bytes_sent_diff / time_diff if time_diff > 0 else 0
            bytes_recv_per_sec = bytes_recv_diff / time_diff if time_diff > 0 else 0

            # 更新上次記錄
            self._last_net_io = net_io
            self._last_net_time = current_time

            internet_usage = {
                "bytes_sent_per_sec": round(bytes_sent_per_sec, 2),
                "bytes_recv_per_sec": round(bytes_recv_per_sec, 2),
                "mb_sent_per_sec": round(bytes_sent_per_sec / (1024 * 1024), 4),
                "mb_recv_per_sec": round(bytes_recv_per_sec / (1024 * 1024), 4),
                "interface": self._net_interface,
            }

            logger.debug(f"網路使用情況: {internet_usage}")
            return internet_usage

        except Exception as e:
            logger.error(f"取得網路使用情況失敗: {e}")
            return {
                "bytes_sent_per_sec": 0.0,
                "bytes_recv_per_sec": 0.0,
                "mb_sent_per_sec": 0.0,
                "mb_recv_per_sec": 0.0,
                "interface": "unknown",
            }

    def get_disk_usage(self, path: str = "C:\\") -> Dict[str, Union[float, int, str]]:
        """取得磁碟使用情況"""
        try:
            disk = psutil.disk_usage(path)
            disk_info = {
                "total_gb": round(disk.total / (1024**3), 2),
                "used_gb": round(disk.used / (1024**3), 2),
                "free_gb": round(disk.free / (1024**3), 2),
                "usage_percent": round((disk.used / disk.total) * 100, 2),
                "path": path,
            }
            logger.debug(f"磁碟使用情況 ({path}): {disk_info}")
            return disk_info
        except Exception as e:
            logger.error(f"取得磁碟使用情況失敗 ({path}): {e}")
            return {
                "total_gb": 0,
                "used_gb": 0,
                "free_gb": 0,
                "usage_percent": 0,
                "path": path,
            }

    def get_system_uptime(self) -> Dict[str, Union[int, float]]:
        """取得系統運行時間"""
        try:
            boot_time = psutil.boot_time()
            uptime_seconds = time.time() - boot_time

            uptime_info = {
                "uptime_seconds": round(uptime_seconds, 2),
                "uptime_minutes": round(uptime_seconds / 60, 2),
                "uptime_hours": round(uptime_seconds / 3600, 2),
                "uptime_days": round(uptime_seconds / 86400, 2),
                "boot_time": boot_time,
            }

            logger.debug(f"系統運行時間: {uptime_info}")
            return uptime_info

        except Exception as e:
            logger.error(f"取得系統運行時間失敗: {e}")
            return {
                "uptime_seconds": 0,
                "uptime_minutes": 0,
                "uptime_hours": 0,
                "uptime_days": 0,
                "boot_time": 0,
            }

    def get_battery_info(self) -> Dict[str, Union[float, bool, str]]:
        """取得電池資訊（如果有的話）"""
        try:
            battery = psutil.sensors_battery()
            if battery is None:
                return {
                    "has_battery": False,
                    "percent": 0.0,
                    "power_plugged": False,
                    "time_left": "N/A",
                }

            time_left = (
                "無限"
                if battery.power_plugged
                else f"{battery.secsleft // 3600}h {(battery.secsleft % 3600) // 60}m"
            )
            if battery.secsleft == psutil.POWER_TIME_UNLIMITED:
                time_left = "無限"
            elif battery.secsleft == psutil.POWER_TIME_UNKNOWN:
                time_left = "未知"

            battery_info = {
                "has_battery": True,
                "percent": round(battery.percent, 2),
                "power_plugged": battery.power_plugged,
                "time_left": time_left,
            }

            logger.debug(f"電池資訊: {battery_info}")
            return battery_info

        except Exception as e:
            logger.error(f"取得電池資訊失敗: {e}")
            return {
                "has_battery": False,
                "percent": 0.0,
                "power_plugged": False,
                "time_left": "N/A",
            }

    def get_all_system_info(self) -> Dict[str, Any]:
        """取得所有系統資訊"""
        try:
            system_info = {
                "timestamp": time.time(),
                "cpu_usage": self.get_cpu_usage(),
                "memory": self.get_memory_usage(),
                "internet": self.get_internet_usage(),
                "disk": self.get_disk_usage(),
                "uptime": self.get_system_uptime(),
                "battery": self.get_battery_info(),
            }

            logger.info("已收集完整系統資訊")
            return system_info

        except Exception as e:
            logger.error(f"收集系統資訊失敗: {e}")
            return {}
