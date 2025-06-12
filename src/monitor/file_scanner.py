"""
檔案掃描模組
"""

from pathlib import Path
from typing import List, Dict, Union, Optional, Any
from datetime import datetime
from superyngo_logger import init_logger

# 初始化日誌器
logger = init_logger(app_name="system_monitor")


class FileScanner:
    """檔案掃描器"""

    def __init__(self, max_depth: int = 3, max_files_per_dir: int = 100):
        """
        初始化檔案掃描器

        Args:
            max_depth: 最大掃描深度
            max_files_per_dir: 每個目錄最大檔案數量
        """
        self.max_depth = max_depth
        self.max_files_per_dir = max_files_per_dir
        logger.info(
            f"檔案掃描器初始化完成 (深度: {max_depth}, 每目錄最大檔案數: {max_files_per_dir})"
        )

    def scan_directory(self, directory_path: str) -> Dict[str, Any]:
        """
        掃描指定目錄

        Args:
            directory_path: 目錄路徑

        Returns:
            目錄資訊字典
        """
        try:
            path = Path(directory_path)
            if not path.exists():
                logger.warning(f"目錄不存在: {directory_path}")
                return {
                    "path": directory_path,
                    "exists": False,
                    "error": "目錄不存在",
                    "scan_time": datetime.now().isoformat(),
                }

            if not path.is_dir():
                logger.warning(f"路徑不是目錄: {directory_path}")
                return {
                    "path": directory_path,
                    "exists": True,
                    "is_directory": False,
                    "error": "路徑不是目錄",
                    "scan_time": datetime.now().isoformat(),
                }

            # 掃描目錄內容
            directory_info = {
                "path": directory_path,
                "exists": True,
                "is_directory": True,
                "scan_time": datetime.now().isoformat(),
                "total_files": 0,
                "total_directories": 0,
                "total_size_bytes": 0,
                "files": [],
                "subdirectories": [],
            }

            # 遞迴掃描
            self._scan_recursive(path, directory_info, 0)

            # 格式化大小
            directory_info["total_size_mb"] = round(
                directory_info["total_size_bytes"] / (1024 * 1024), 2
            )
            directory_info["total_size_gb"] = round(
                directory_info["total_size_bytes"] / (1024 * 1024 * 1024), 4
            )

            logger.info(
                f"掃描完成: {directory_path} (檔案: {directory_info['total_files']}, 目錄: {directory_info['total_directories']})"
            )
            return directory_info

        except PermissionError:
            logger.warning(f"沒有權限存取目錄: {directory_path}")
            return {
                "path": directory_path,
                "exists": True,
                "error": "沒有存取權限",
                "scan_time": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"掃描目錄失敗 {directory_path}: {e}")
            return {
                "path": directory_path,
                "error": str(e),
                "scan_time": datetime.now().isoformat(),
            }

    def _scan_recursive(
        self, path: Path, info: Dict[str, Any], current_depth: int
    ) -> None:
        """
        遞迴掃描目錄

        Args:
            path: 當前路徑
            info: 資訊字典
            current_depth: 當前深度
        """
        if current_depth >= self.max_depth:
            return

        try:
            items = list(path.iterdir())
            files_count = 0

            for item in items:
                if files_count >= self.max_files_per_dir:
                    logger.debug(f"達到檔案數量限制，跳過剩餘項目: {path}")
                    break

                try:
                    if item.is_file():
                        file_info = self._get_file_info(item)
                        if file_info:
                            info["files"].append(file_info)
                            info["total_files"] += 1
                            info["total_size_bytes"] += file_info.get("size_bytes", 0)
                            files_count += 1

                    elif item.is_dir():
                        dir_info = self._get_directory_info(item)
                        if dir_info:
                            info["subdirectories"].append(dir_info)
                            info["total_directories"] += 1

                            # 遞迴掃描子目錄
                            if current_depth < self.max_depth - 1:
                                subdir_info = {
                                    "total_files": 0,
                                    "total_directories": 0,
                                    "total_size_bytes": 0,
                                    "files": [],
                                    "subdirectories": [],
                                }
                                self._scan_recursive(
                                    item, subdir_info, current_depth + 1
                                )

                                # 合併統計
                                info["total_files"] += subdir_info["total_files"]
                                info["total_directories"] += subdir_info[
                                    "total_directories"
                                ]
                                info["total_size_bytes"] += subdir_info[
                                    "total_size_bytes"
                                ]

                except (PermissionError, OSError) as e:
                    logger.debug(f"跳過無法存取的項目 {item}: {e}")
                    continue

        except (PermissionError, OSError) as e:
            logger.debug(f"無法列出目錄內容 {path}: {e}")

    def _get_file_info(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """取得檔案資訊"""
        try:
            stat = file_path.stat()
            file_info = {
                "name": file_path.name,
                "path": str(file_path),
                "size_bytes": stat.st_size,
                "size_kb": round(stat.st_size / 1024, 2),
                "size_mb": round(stat.st_size / (1024 * 1024), 4),
                "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "created_time": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "extension": file_path.suffix.lower(),
            }
            return file_info
        except (PermissionError, OSError) as e:
            logger.debug(f"無法取得檔案資訊 {file_path}: {e}")
            return None

    def _get_directory_info(self, dir_path: Path) -> Optional[Dict[str, Any]]:
        """取得目錄資訊"""
        try:
            stat = dir_path.stat()
            dir_info = {
                "name": dir_path.name,
                "path": str(dir_path),
                "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "created_time": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            }
            return dir_info
        except (PermissionError, OSError) as e:
            logger.debug(f"無法取得目錄資訊 {dir_path}: {e}")
            return None

    def scan_multiple_directories(
        self, directories: List[str]
    ) -> Dict[str, Dict[str, Any]]:
        """
        掃描多個目錄

        Args:
            directories: 目錄路徑清單

        Returns:
            每個目錄的掃描結果
        """
        results = {}

        for directory in directories:
            try:
                logger.info(f"開始掃描目錄: {directory}")
                results[directory] = self.scan_directory(directory)
            except Exception as e:
                logger.error(f"掃描目錄失敗 {directory}: {e}")
                results[directory] = {
                    "path": directory,
                    "error": str(e),
                    "scan_time": datetime.now().isoformat(),
                }

        return results

    def get_summary(
        self, scan_results: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Union[int, float]]:
        """
        取得掃描結果摘要

        Args:
            scan_results: 掃描結果

        Returns:
            摘要統計
        """
        summary: Dict[str, Union[int, float]] = {
            "total_directories_scanned": len(scan_results),
            "total_files_found": 0,
            "total_subdirectories_found": 0,
            "total_size_bytes": 0,
            "total_size_mb": 0.0,
            "total_size_gb": 0.0,
            "successful_scans": 0,
            "failed_scans": 0,
        }

        for path, result in scan_results.items():
            if "error" in result:
                summary["failed_scans"] += 1
            else:
                summary["successful_scans"] += 1
                summary["total_files_found"] += int(result.get("total_files", 0))
                summary["total_subdirectories_found"] += int(
                    result.get("total_directories", 0)
                )
                summary["total_size_bytes"] += int(result.get("total_size_bytes", 0))

        # 計算大小轉換
        total_bytes = int(summary["total_size_bytes"])
        summary["total_size_mb"] = round(total_bytes / (1024 * 1024), 2)
        summary["total_size_gb"] = round(total_bytes / (1024 * 1024 * 1024), 4)

        return summary

    def format_scan_results_for_sheets(
        self, scan_results: Dict[str, Dict[str, Any]]
    ) -> str:
        """
        格式化掃描結果以供 Google Sheets 使用

        Args:
            scan_results: 掃描結果

        Returns:
            格式化的字串
        """
        try:
            summary = self.get_summary(scan_results)

            # 建立簡潔的摘要字串
            parts = []

            for path, result in scan_results.items():
                if "error" in result:
                    parts.append(f"{path}: 錯誤 - {result['error']}")
                else:
                    files = result.get("total_files", 0)
                    dirs = result.get("total_directories", 0)
                    size_mb = result.get("total_size_mb", 0)
                    parts.append(f"{path}: {files}檔案, {dirs}目錄, {size_mb}MB")

            # 加入總摘要
            total_files = summary["total_files_found"]
            total_dirs = summary["total_subdirectories_found"]
            total_size_mb = summary["total_size_mb"]

            result_str = " | ".join(parts)
            result_str += (
                f" | 總計: {total_files}檔案, {total_dirs}目錄, {total_size_mb}MB"
            )

            return result_str

        except Exception as e:
            logger.error(f"格式化掃描結果失敗: {e}")
            return f"格式化失敗: {str(e)}"
