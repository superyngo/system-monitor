"""
設定視窗模組 - 修復版本
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from pathlib import Path
from typing import Callable, Optional
from superyngo_logger import init_logger

# 初始化日誌器
logger = init_logger(app_name="system_monitor")


class SettingsWindow:
    """設定視窗"""

    def __init__(
        self, settings, on_settings_changed: Optional[Callable] = None, parent=None
    ):
        """
        初始化設定視窗

        Args:
            settings: 設定物件
            on_settings_changed: 設定變更回調
            parent: 父視窗
        """
        self.settings = settings
        self.on_settings_changed = on_settings_changed
        self.parent = parent

        self.window = None
        self.is_open = False

        # 變數（延遲初始化）
        self.credentials_file_var = None
        self.spreadsheet_url_var = None
        self.worksheet_name_var = None
        self.interval_var = None
        self.directories_listbox = None

        logger.info("設定視窗初始化完成")

    def _init_variables(self):
        """初始化 tkinter 變數"""
        if self.credentials_file_var is None:
            self.credentials_file_var = tk.StringVar()
            self.spreadsheet_url_var = tk.StringVar()
            self.worksheet_name_var = tk.StringVar()
            self.interval_var = tk.IntVar()

    def show(self):
        """顯示設定視窗"""
        if self.is_open:
            if self.window:
                self.window.lift()
                self.window.focus_force()
            return

        try:
            self._create_window()
            self._load_current_settings()
            self.is_open = True
            logger.info("設定視窗已開啟")
        except Exception as e:
            logger.error(f"開啟設定視窗失敗: {e}")
            if tk._default_root:
                messagebox.showerror("錯誤", f"開啟設定視窗失敗: {e}")

    def _create_window(self):
        """建立視窗"""
        # 確保有根視窗
        if not tk._default_root:
            root = tk.Tk()
            root.withdraw()  # 隱藏根視窗

        self.window = tk.Toplevel(self.parent) if self.parent else tk.Tk()

        # 初始化 tkinter 變數
        self._init_variables()

        self.window.title("System Monitor - 設定")
        self.window.geometry("600x500")
        self.window.resizable(True, True)

        # 設定視窗圖示（如果有的話）
        try:
            icon_path = Path("assets/icon.ico")
            if icon_path.exists():
                self.window.iconbitmap(str(icon_path))
        except Exception:
            pass  # 忽略圖示載入錯誤

        # 設定關閉事件
        self.window.protocol("WM_DELETE_WINDOW", self._on_close)

        # 建立內容
        self._create_widgets()

    def _create_widgets(self):
        """建立介面元件"""
        # 主框架
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")

        # 設定 grid 權重
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # 標籤頁
        notebook = ttk.Notebook(main_frame)
        notebook.grid(row=0, column=0, columnspan=2, sticky="nsew", pady=(0, 10))
        main_frame.rowconfigure(0, weight=1)

        # Google Sheets 設定頁
        self._create_sheets_tab(notebook)

        # 監控設定頁
        self._create_monitoring_tab(notebook)

        # 按鈕框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, columnspan=2, sticky="ew")

        # 按鈕
        ttk.Button(button_frame, text="測試連線", command=self._test_connection).pack(
            side=tk.LEFT, padx=(0, 5)
        )
        ttk.Button(button_frame, text="套用", command=self._apply_settings).pack(
            side=tk.RIGHT, padx=(5, 0)
        )
        ttk.Button(button_frame, text="確定", command=self._ok_clicked).pack(
            side=tk.RIGHT, padx=(5, 0)
        )
        ttk.Button(button_frame, text="取消", command=self._cancel_clicked).pack(
            side=tk.RIGHT, padx=(5, 0)
        )

    def _create_sheets_tab(self, notebook):
        """建立 Google Sheets 設定頁"""
        frame = ttk.Frame(notebook, padding="10")
        notebook.add(frame, text="Google Sheets")

        # 憑證檔案
        ttk.Label(frame, text="憑證檔案:").grid(
            row=0, column=0, sticky=tk.W, pady=(0, 5)
        )

        cred_frame = ttk.Frame(frame)
        cred_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        cred_frame.columnconfigure(0, weight=1)

        ttk.Entry(cred_frame, textvariable=self.credentials_file_var, width=50).grid(
            row=0, column=0, sticky="ew", padx=(0, 5)
        )
        ttk.Button(cred_frame, text="瀏覽", command=self._browse_credentials_file).grid(
            row=0, column=1
        )

        # 試算表 URL
        ttk.Label(frame, text="試算表 URL:").grid(
            row=2, column=0, sticky=tk.W, pady=(0, 5)
        )
        ttk.Entry(frame, textvariable=self.spreadsheet_url_var, width=70).grid(
            row=3, column=0, sticky="ew", pady=(0, 10)
        )

        # 工作表名稱
        ttk.Label(frame, text="工作表名稱:").grid(
            row=4, column=0, sticky=tk.W, pady=(0, 5)
        )
        ttk.Entry(frame, textvariable=self.worksheet_name_var, width=30).grid(
            row=5, column=0, sticky=tk.W, pady=(0, 10)
        )

        # 說明
        info_text = """設定說明：
1. 憑證檔案：從 Google Cloud Console 下載的服務帳戶金鑰（JSON 格式）
2. 試算表 URL：Google Sheets 的完整 URL
3. 工作表名稱：要寫入資料的工作表名稱（如果不存在會自動建立）

安全提醒：請妥善保管憑證檔案，不要洩露給他人"""

        info_label = ttk.Label(frame, text=info_text, font=("TkDefaultFont", 8))
        info_label.grid(row=6, column=0, sticky="ew", pady=(10, 0))

        frame.columnconfigure(0, weight=1)

    def _create_monitoring_tab(self, notebook):
        """建立監控設定頁"""
        frame = ttk.Frame(notebook, padding="10")
        notebook.add(frame, text="監控設定")

        # 監控間隔
        ttk.Label(frame, text="監控間隔（分鐘）:").grid(
            row=0, column=0, sticky=tk.W, pady=(0, 5)
        )

        interval_frame = ttk.Frame(frame)
        interval_frame.grid(row=1, column=0, sticky=tk.W, pady=(0, 10))

        interval_spinbox = ttk.Spinbox(
            interval_frame, from_=1, to=60, textvariable=self.interval_var, width=10
        )
        interval_spinbox.grid(row=0, column=0)
        ttk.Label(interval_frame, text="（建議 5-10 分鐘）").grid(
            row=0, column=1, padx=(5, 0)
        )

        # 監控目錄
        ttk.Label(frame, text="監控目錄:").grid(
            row=2, column=0, sticky=tk.W, pady=(10, 5)
        )

        dir_frame = ttk.Frame(frame)
        dir_frame.grid(row=3, column=0, sticky="nsew", pady=(0, 10))
        dir_frame.columnconfigure(0, weight=1)
        dir_frame.rowconfigure(0, weight=1)

        # 目錄清單
        list_frame = ttk.Frame(dir_frame)
        list_frame.grid(row=0, column=0, sticky="nsew")
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        self.directories_listbox = tk.Listbox(list_frame, height=8)
        self.directories_listbox.grid(row=0, column=0, sticky="nsew")

        # 捲軸
        scrollbar = ttk.Scrollbar(
            list_frame, orient=tk.VERTICAL, command=self.directories_listbox.yview
        )
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.directories_listbox.configure(yscrollcommand=scrollbar.set)

        # 目錄按鈕
        dir_button_frame = ttk.Frame(dir_frame)
        dir_button_frame.grid(row=0, column=1, sticky="ns", padx=(10, 0))

        ttk.Button(dir_button_frame, text="新增", command=self._add_directory).pack(
            pady=(0, 5), fill=tk.X
        )
        ttk.Button(dir_button_frame, text="移除", command=self._remove_directory).pack(
            pady=(0, 5), fill=tk.X
        )

        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(3, weight=1)

    def _browse_credentials_file(self):
        """瀏覽憑證檔案"""
        try:
            filename = filedialog.askopenfilename(
                title="選擇 Google Sheets 憑證檔案",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            )
            if filename:
                self.credentials_file_var.set(filename)
        except Exception as e:
            logger.error(f"瀏覽憑證檔案失敗: {e}")
            messagebox.showerror("錯誤", f"瀏覽檔案失敗: {e}")

    def _add_directory(self):
        """新增監控目錄"""
        try:
            directory = filedialog.askdirectory(title="選擇要監控的目錄")
            if directory:
                self.directories_listbox.insert(tk.END, directory)
        except Exception as e:
            logger.error(f"新增目錄失敗: {e}")
            messagebox.showerror("錯誤", f"新增目錄失敗: {e}")

    def _remove_directory(self):
        """移除監控目錄"""
        try:
            selection = self.directories_listbox.curselection()
            if selection:
                self.directories_listbox.delete(selection[0])
            else:
                messagebox.showinfo("提示", "請先選擇要移除的目錄")
        except Exception as e:
            logger.error(f"移除目錄失敗: {e}")
            messagebox.showerror("錯誤", f"移除目錄失敗: {e}")

    def _load_current_settings(self):
        """載入目前設定"""
        try:
            self.credentials_file_var.set(self.settings.credentials_file)
            self.spreadsheet_url_var.set(self.settings.spreadsheet_url)
            self.worksheet_name_var.set(self.settings.worksheet_name)
            self.interval_var.set(self.settings.interval_minutes)

            # 載入監控目錄
            self.directories_listbox.delete(0, tk.END)
            for directory in self.settings.monitor_directories:
                self.directories_listbox.insert(tk.END, directory)

        except Exception as e:
            logger.error(f"載入設定失敗: {e}")

    def _apply_settings(self):
        """套用設定"""
        try:
            # 驗證輸入
            if not self.credentials_file_var.get().strip():
                messagebox.showerror("錯誤", "請選擇憑證檔案")
                return

            if not self.spreadsheet_url_var.get().strip():
                messagebox.showerror("錯誤", "請輸入試算表 URL")
                return

            if self.interval_var.get() < 1:
                messagebox.showerror("錯誤", "監控間隔不能小於 1 分鐘")
                return

            # 儲存設定
            self.settings.credentials_file = self.credentials_file_var.get().strip()
            self.settings.spreadsheet_url = self.spreadsheet_url_var.get().strip()
            self.settings.worksheet_name = (
                self.worksheet_name_var.get().strip() or "System Monitor"
            )
            self.settings.interval_minutes = self.interval_var.get()

            # 儲存監控目錄
            directories = []
            for i in range(self.directories_listbox.size()):
                directories.append(self.directories_listbox.get(i))
            self.settings.monitor_directories = directories

            # 通知設定變更
            if self.on_settings_changed:
                self.on_settings_changed()

            messagebox.showinfo("成功", "設定已儲存")
            logger.info("設定已套用")

        except Exception as e:
            logger.error(f"套用設定失敗: {e}")
            messagebox.showerror("錯誤", f"套用設定失敗: {e}")

    def _test_connection(self):
        """測試 Google Sheets 連線"""

        def test_in_thread():
            try:
                # 先套用設定
                self._apply_settings()

                # 測試連線
                from ..api import GoogleSheetsClient

                client = GoogleSheetsClient(
                    self.settings.credentials_file,
                    self.settings.spreadsheet_url,
                    self.settings.worksheet_name,
                )

                result = client.test_connection()

                # 在主執行緒中顯示結果
                def show_result():
                    if result["success"]:
                        message = f"連線成功！\n\n試算表: {result['spreadsheet_title']}\n工作表: {result['worksheet_title']}"
                        messagebox.showinfo("連線測試", message)
                    else:
                        message = f"連線失敗\n\n錯誤: {result['error']}"
                        messagebox.showerror("連線測試", message)

                self.window.after(0, show_result)

            except Exception as e:
                logger.error(f"測試連線失敗: {e}")

                def show_error():
                    messagebox.showerror("連線測試", f"測試失敗: {e}")

                self.window.after(0, show_error)

        # 在背景執行緒中執行測試
        test_thread = threading.Thread(target=test_in_thread, daemon=True)
        test_thread.start()

    def _ok_clicked(self):
        """確定按鈕點擊"""
        self._apply_settings()
        self._close()

    def _cancel_clicked(self):
        """取消按鈕點擊"""
        self._close()

    def _on_close(self):
        """視窗關閉事件"""
        self._close()

    def _close(self):
        """關閉視窗"""
        try:
            if self.window:
                self.window.destroy()
                self.window = None
            self.is_open = False
            logger.info("設定視窗已關閉")
        except Exception as e:
            logger.error(f"關閉設定視窗失敗: {e}")


def show_settings_window(settings, on_settings_changed=None):
    """
    顯示設定視窗的便利函數

    Args:
        settings: 設定物件
        on_settings_changed: 設定變更回調
    """
    window = SettingsWindow(settings, on_settings_changed)
    window.show()
    return window
