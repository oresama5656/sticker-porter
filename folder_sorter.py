#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sticker Porter - フォルダ整理ツール

LINEスタンプ作成フローにおけるファイルの仕分け作業を自動化するツール。

【PyInstallerでEXE化する場合のコマンド】
pip install pyinstaller
pyinstaller --onefile --windowed --name "StickerPorter" folder_sorter.py
"""

import os
import sys
import json
import shutil
import tkinter as tk
from tkinter import scrolledtext, messagebox
from datetime import datetime
from pathlib import Path


class FolderSorterApp:
    """フォルダ整理ツールのメインアプリケーションクラス"""

    # デフォルトのフォルダ設定
    DEFAULT_CONFIG = {
        "workbench_folder": "00_WorkBench",
        "ready_to_upload_folder": "01_Ready_To_Upload",
        "uploaded_done_folder": "02_Uploaded_Done",
        "raw_archive_folder": "99_Raw_Archive"
    }

    def __init__(self):
        """アプリケーションの初期化"""
        # アプリケーションのベースディレクトリを取得
        # EXE化した場合も正しく動作するように対応
        if getattr(sys, 'frozen', False):
            self.base_dir = Path(sys.executable).parent
        else:
            self.base_dir = Path(__file__).parent

        # 設定の読み込み
        self.config_path = self.base_dir / "config.json"
        self.config = self.load_config()

        # フォルダの確保
        self.ensure_folders()

        # GUIの構築
        self.root = tk.Tk()
        self.setup_gui()

    def load_config(self) -> dict:
        """設定ファイルを読み込む。存在しない場合は作成する。"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                # デフォルト値で不足キーを補完
                for key, value in self.DEFAULT_CONFIG.items():
                    if key not in config:
                        config[key] = value
                return config
            except (json.JSONDecodeError, IOError) as e:
                # 読み込みエラー時はデフォルトを使用
                print(f"設定ファイル読み込みエラー: {e}")
                return self.DEFAULT_CONFIG.copy()
        else:
            # 設定ファイルを新規作成
            self.save_config(self.DEFAULT_CONFIG)
            return self.DEFAULT_CONFIG.copy()

    def save_config(self, config: dict):
        """設定ファイルを保存する"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"設定ファイル保存エラー: {e}")

    def ensure_folders(self):
        """必要なフォルダが存在することを確認し、なければ作成する"""
        for folder_key in ["workbench_folder", "ready_to_upload_folder", 
                          "uploaded_done_folder", "raw_archive_folder"]:
            folder_path = self.base_dir / self.config[folder_key]
            folder_path.mkdir(parents=True, exist_ok=True)

    def get_folder_path(self, key: str) -> Path:
        """設定キーからフォルダパスを取得"""
        return self.base_dir / self.config[key]

    def setup_gui(self):
        """GUIを構築する"""
        self.root.title("Sticker Porter - フォルダ整理ツール")
        self.root.geometry("450x350")
        self.root.resizable(False, False)

        # ウィンドウを画面中央に配置
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - 450) // 2
        y = (self.root.winfo_screenheight() - 350) // 2
        self.root.geometry(f"450x350+{x}+{y}")

        # メインフレーム
        main_frame = tk.Frame(self.root, padx=20, pady=15)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # ======== ステータス表示エリア ========
        status_frame = tk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(status_frame, text="状態:", font=("Yu Gothic UI", 10)).pack(side=tk.LEFT)
        self.status_label = tk.Label(
            status_frame, 
            text="待機中", 
            font=("Yu Gothic UI", 10, "bold"),
            fg="#2e7d32"  # 緑色
        )
        self.status_label.pack(side=tk.LEFT, padx=5)

        # ======== ボタンエリア ========
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)

        # ボタンA: 製造完了（仕分け）
        self.btn_manufacture = tk.Button(
            button_frame,
            text="📦 製造完了（仕分け）",
            font=("Yu Gothic UI", 12, "bold"),
            bg="#1976d2",
            fg="white",
            activebackground="#1565c0",
            activeforeground="white",
            width=18,
            height=2,
            command=self.process_manufacture_complete
        )
        self.btn_manufacture.pack(side=tk.LEFT, padx=(0, 10))

        # ボタンB: 投稿完了（片付け）
        self.btn_upload = tk.Button(
            button_frame,
            text="🚀 投稿完了（片付け）",
            font=("Yu Gothic UI", 12, "bold"),
            bg="#388e3c",
            fg="white",
            activebackground="#2e7d32",
            activeforeground="white",
            width=18,
            height=2,
            command=self.process_upload_complete
        )
        self.btn_upload.pack(side=tk.LEFT)

        # ======== ログ表示エリア ========
        log_frame = tk.Frame(main_frame)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        tk.Label(log_frame, text="処理ログ:", font=("Yu Gothic UI", 9)).pack(anchor=tk.W)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=8,
            font=("Consolas", 9),
            state=tk.DISABLED,
            wrap=tk.WORD
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

        # ログのタグ設定（色分け用）
        self.log_text.tag_configure("info", foreground="#1976d2")
        self.log_text.tag_configure("success", foreground="#2e7d32")
        self.log_text.tag_configure("error", foreground="#c62828")
        self.log_text.tag_configure("warning", foreground="#f57c00")

        # 初期ログ
        self.log_message("アプリ起動完了。ボタンを押して処理を開始してください。", "info")

    def log_message(self, message: str, tag: str = "info"):
        """ログエリアにメッセージを追加する"""
        self.log_text.configure(state=tk.NORMAL)
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n", tag)
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)
        self.root.update()

    def update_status(self, text: str, color: str = "#2e7d32"):
        """ステータスラベルを更新する"""
        self.status_label.config(text=text, fg=color)
        self.root.update()

    def move_file_safe(self, src: Path, dest_folder: Path) -> bool:
        """ファイルまたはフォルダを安全に移動する（重複時はタイムスタンプ付与）"""
        if not src.exists():
            return False

        dest = dest_folder / src.name

        # 同名が存在する場合はタイムスタンプを付与
        if dest.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if src.is_file():
                stem = src.stem
                suffix = src.suffix
                new_name = f"{stem}_{timestamp}{suffix}"
            else:
                new_name = f"{src.name}_{timestamp}"
            dest = dest_folder / new_name
            self.log_message(f"  → 重複のためリネーム: {new_name}", "warning")

        try:
            shutil.move(str(src), str(dest))
            return True
        except Exception as e:
            self.log_message(f"エラー: {src.name} の移動に失敗 - {e}", "error")
            return False

    def process_manufacture_complete(self):
        """製造完了（仕分け）処理: WorkBench → Ready_To_Upload / Raw_Archive"""
        self.update_status("処理中...", "#f57c00")
        self.log_message("=== 製造完了（仕分け）処理開始 ===", "info")

        workbench = self.get_folder_path("workbench_folder")
        ready_to_upload = self.get_folder_path("ready_to_upload_folder")
        raw_archive = self.get_folder_path("raw_archive_folder")

        zip_count = 0
        folder_count = 0

        try:
            for item in workbench.iterdir():
                if item.is_file() and item.suffix.lower() == ".zip":
                    # ZIPファイルは Ready_To_Upload へ
                    if self.move_file_safe(item, ready_to_upload):
                        self.log_message(f"ZIP移動: {item.name} → {self.config['ready_to_upload_folder']}", "success")
                        zip_count += 1
                elif item.is_dir():
                    # フォルダは Raw_Archive へ
                    if self.move_file_safe(item, raw_archive):
                        self.log_message(f"フォルダ移動: {item.name} → {self.config['raw_archive_folder']}", "success")
                        folder_count += 1

            self.log_message(f"完了: ZIP {zip_count}件, フォルダ {folder_count}件 を移動", "info")
            self.update_status("処理完了", "#2e7d32")

        except Exception as e:
            self.log_message(f"エラー: 処理中に問題が発生 - {e}", "error")
            self.update_status("エラー発生", "#c62828")

    def process_upload_complete(self):
        """投稿完了（片付け）処理: Ready_To_Upload → Uploaded_Done"""
        self.update_status("処理中...", "#f57c00")
        self.log_message("=== 投稿完了（片付け）処理開始 ===", "info")

        ready_to_upload = self.get_folder_path("ready_to_upload_folder")
        uploaded_done = self.get_folder_path("uploaded_done_folder")

        zip_count = 0

        try:
            for item in ready_to_upload.iterdir():
                if item.is_file() and item.suffix.lower() == ".zip":
                    if self.move_file_safe(item, uploaded_done):
                        self.log_message(f"ZIP移動: {item.name} → {self.config['uploaded_done_folder']}", "success")
                        zip_count += 1

            self.log_message(f"完了: ZIP {zip_count}件 を移動", "info")
            self.update_status("処理完了", "#2e7d32")

        except Exception as e:
            self.log_message(f"エラー: 処理中に問題が発生 - {e}", "error")
            self.update_status("エラー発生", "#c62828")

    def run(self):
        """アプリケーションを実行する"""
        self.root.mainloop()


def main():
    """エントリーポイント"""
    app = FolderSorterApp()
    app.run()


if __name__ == "__main__":
    main()
