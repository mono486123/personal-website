import json
import os
import re
import subprocess
import sys
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, ttk

# 設定 Windows 背景執行隱藏 Cmd 視窗
CREATE_NO_WINDOW = 0x08000000 if sys.platform == 'win32' else 0

CONFIG = {
    "01 / 技術實作": {"file": "systems.json", "key": "systems"},
    "02 / 末日小說": {"file": "novels.json", "key": "novels"},
    "03 / 生活與節奏": {"file": "micro_logs.json", "key": "micro_logs"}
}

class UniversalGardenManager:
    def __init__(self, root):
        self.root = root
        self.root.title("🌸 個人數位花園 - 萬能發布管理系統")
        self.root.geometry("680x780")
        self.root.resizable(False, False)

        self.style = ttk.Style()
        self.style.theme_use('clam')

        # 頂部分區選擇
        top_frame = ttk.LabelFrame(self.root, text="📌 選擇發布分區", padding=10)
        top_frame.pack(fill='x', padx=10, pady=10)

        ttk.Label(top_frame, text="目前管理類別:").pack(side='left', padx=5)
        self.cat_var = tk.StringVar(value="01 / 技術實作")
        self.cat_combo = ttk.Combobox(top_frame, textvariable=self.cat_var, values=list(CONFIG.keys()), state='readonly', width=20)
        self.cat_combo.pack(side='left', padx=5)
        self.cat_combo.bind("<<ComboboxSelected>>", self.on_category_change)

        # Tab 容器
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=(0, 5))

        self.tab_add = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_add, text=" ➕ 新增卡片 ")

        self.tab_manage = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_manage, text=" 🗑️ 檢視與刪除 ")

        # 底部 Git 設定
        self.setup_bottom_settings()

        # 初始化頁面
        self.setup_add_tab()
        self.setup_manage_tab()

        # 預設載入 01 類別
        self.on_category_change()

    def setup_bottom_settings(self):
        bottom_frame = ttk.LabelFrame(self.root, text="⚙️ Git 自動化推送設定", padding=10)
        bottom_frame.pack(fill='x', padx=10, pady=(0, 10))

        self.var_auto_push = tk.BooleanVar(value=True)
        self.var_only_json = tk.BooleanVar(value=True)

        ttk.Checkbutton(bottom_frame, text="✅ 執行動作後自動 Git Push 到 GitHub", variable=self.var_auto_push).pack(side='left', padx=10)
        ttk.Checkbutton(bottom_frame, text="🎯 僅推送目標 JSON 檔 (保護其他 HTML)", variable=self.var_only_json).pack(side='left', padx=10)

    def get_current_json_file(self):
        cat = self.cat_var.get()
        return CONFIG[cat]["file"]

    def load_data(self):
        json_file = self.get_current_json_file()
        if os.path.exists(json_file):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def save_data(self, data):
        json_file = self.get_current_json_file()
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def run_git_sync(self, commit_msg):
        json_file = self.get_current_json_file()
        target = json_file if self.var_only_json.get() else "."

        try:
            subprocess.run(["git", "add", target], check=True, creationflags=CREATE_NO_WINDOW)
            subprocess.run(["git", "commit", "-m", commit_msg], check=True, creationflags=CREATE_NO_WINDOW)
            subprocess.run(["git", "push", "origin", "main"], check=True, creationflags=CREATE_NO_WINDOW)
            messagebox.showinfo("成功", f"🎉 已更新並成功 Push 上 GitHub！\n\n目標: {target}\n訊息: {commit_msg}")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Git 錯誤", f"❌ Git 推送失敗 (可能沒有新變更):\n{e}")
        except Exception as e:
            messagebox.showerror("系統錯誤", f"❌ 未知錯誤:\n{e}")

    def on_category_change(self, event=None):
        cat = self.cat_var.get()
        for widget in self.form_frame.winfo_children():
            widget.destroy()

        if cat == "01 / 技術實作":
            self.build_systems_form()
        elif cat == "02 / 末日小說":
            self.build_novels_form()
        elif cat == "03 / 生活與節奏":
            self.build_micro_logs_form()

        self.refresh_treeview()

    # ==========================================
    # 動態表單建置
    # ==========================================
    def setup_add_tab(self):
        self.form_frame = ttk.LabelFrame(self.tab_add, text="卡片詳細內容", padding=15)
        self.form_frame.pack(fill='both', expand=True, padx=10, pady=10)

    # ---------------- 01 / 技術實作 ----------------
    def build_systems_form(self):
        f = self.form_frame

        # 抓取過往 systems.json 內的 Badge 作為選單歷史記憶
        existing_data = self.load_data()
        history_badges = list(dict.fromkeys([item.get('badge') for item in existing_data if item.get('badge')]))
        default_badges = ["C++17 / OpenCV", "Python / Edge AI", "DevOps / Optimization", "Python / Web"]
        badge_options = list(dict.fromkeys(default_badges + history_badges))

        ttk.Label(f, text="1. 專案名稱:").grid(row=0, column=0, sticky='w', pady=2)
        self.e_sys_title = ttk.Entry(f, width=55); self.e_sys_title.grid(row=1, column=0, pady=(0, 8))

        ttk.Label(f, text="2. Badge 分類 (可選擇歷史選單或自行輸入):").grid(row=2, column=0, sticky='w', pady=2)
        self.combo_sys_badge = ttk.Combobox(f, width=52, values=badge_options)
        self.combo_sys_badge.grid(row=3, column=0, pady=(0, 8))
        if badge_options: self.combo_sys_badge.set(badge_options[0])

        ttk.Label(f, text="3. 專案說明:").grid(row=4, column=0, sticky='w', pady=2)
        self.t_sys_desc = tk.Text(f, width=55, height=4, font=('Segoe UI', 9)); self.t_sys_desc.grid(row=5, column=0, pady=(0, 8))

        ttk.Label(f, text="4. Tags (支援全形/半形逗點、頓號、句號自動防呆切割):").grid(row=6, column=0, sticky='w', pady=2)
        self.e_sys_tags = ttk.Entry(f, width=55); self.e_sys_tags.grid(row=7, column=0, pady=(0, 8))

        ttk.Label(f, text="5. GitHub 網址 (選填):").grid(row=8, column=0, sticky='w', pady=2)
        self.e_sys_github = ttk.Entry(f, width=55); self.e_sys_github.grid(row=9, column=0, pady=(0, 8))

        ttk.Label(f, text="6. 展演/影片網址 (選填):").grid(row=10, column=0, sticky='w', pady=2)
        self.e_sys_post = ttk.Entry(f, width=55); self.e_sys_post.grid(row=11, column=0, pady=(0, 12))

        ttk.Button(f, text="🚀 發布至 01/技術實作", command=self.save_system).grid(row=12, column=0, ipady=4, sticky='we')

    def save_system(self):
        title = self.e_sys_title.get().strip()
        badge = self.combo_sys_badge.get().strip()
        desc = self.t_sys_desc.get("1.0", tk.END).strip()
        if not title or not badge or not desc: return messagebox.showwarning("提示", "請填寫完整資訊！")

        # 使用正則表達式自動相容 , ， 、 。 ； ; 拆分標籤
        raw_tags = self.e_sys_tags.get()
        tags = [t.strip() for t in re.split(r'[,，、。；;\s]+', raw_tags) if t.strip()]

        links = []
        if self.e_sys_github.get().strip(): links.append({"name": "💻 GitHub 專案庫", "url": self.e_sys_github.get().strip()})
        if self.e_sys_post.get().strip(): links.append({"name": "📹 實作展示 / 貼文", "url": self.e_sys_post.get().strip()})

        data = self.load_data()
        data.insert(0, {"id": len(data)+1, "badge": badge, "title": title, "description": desc, "tags": tags, "links": links})
        self.save_data(data); self.refresh_treeview()
        if self.var_auto_push.get(): self.run_git_sync(f"feat: 新增技術專案 {title}")

    # ---------------- 02 / 末日小說 ----------------
    def build_novels_form(self):
        f = self.form_frame
        ttk.Label(f, text="1. 小說書名/篇名:").grid(row=0, column=0, sticky='w', pady=2)
        self.e_nov_title = ttk.Entry(f, width=55); self.e_nov_title.grid(row=1, column=0, pady=(0, 8))

        ttk.Label(f, text="2. Badge 狀態 (例: 十萬字連載中):").grid(row=2, column=0, sticky='w', pady=2)
        self.e_nov_badge = ttk.Entry(f, width=55); self.e_nov_badge.grid(row=3, column=0, pady=(0, 8))

        ttk.Label(f, text="3. 簡介第一段:").grid(row=4, column=0, sticky='w', pady=2)
        self.t_nov_p1 = tk.Text(f, width=55, height=3, font=('Segoe UI', 9)); self.t_nov_p1.grid(row=5, column=0, pady=(0, 8))

        ttk.Label(f, text="4. 簡介第二段 (選填):").grid(row=6, column=0, sticky='w', pady=2)
        self.t_nov_p2 = tk.Text(f, width=55, height=3, font=('Segoe UI', 9)); self.t_nov_p2.grid(row=7, column=0, pady=(0, 8))

        ttk.Label(f, text="5. 風格調性 (例: 荒誕寫實 / 黑色幽默):").grid(row=8, column=0, sticky='w', pady=2)
        self.e_nov_style = ttk.Entry(f, width=55); self.e_nov_style.grid(row=9, column=0, pady=(0, 8))

        ttk.Label(f, text="6. 登場角色 (例: 森元、夕中):").grid(row=10, column=0, sticky='w', pady=2)
        self.e_nov_chars = ttk.Entry(f, width=55); self.e_nov_chars.grid(row=11, column=0, pady=(0, 8))

        ttk.Label(f, text="7. 閱讀網址:").grid(row=12, column=0, sticky='w', pady=2)
        self.e_nov_url = ttk.Entry(f, width=55); self.e_nov_url.grid(row=13, column=0, pady=(0, 12))

        ttk.Button(f, text="🚀 發布至 02/末日小說", command=self.save_novel).grid(row=14, column=0, ipady=4, sticky='we')

    def save_novel(self):
        title, badge = self.e_nov_title.get().strip(), self.e_nov_badge.get().strip()
        p1 = self.t_nov_p1.get("1.0", tk.END).strip()
        if not title or not p1: return messagebox.showwarning("提示", "書名與簡介為必填！")

        data = self.load_data()
        data.insert(0, {
            "id": len(data)+1, "badge": badge, "title": title, "intro1": p1,
            "intro2": self.t_nov_p2.get("1.0", tk.END).strip(),
            "style": self.e_nov_style.get().strip(), "characters": self.e_nov_chars.get().strip(),
            "url": self.e_nov_url.get().strip(), "btn_text": "前往連載頁面 ➔"
        })
        self.save_data(data); self.refresh_treeview()
        if self.var_auto_push.get(): self.run_git_sync(f"feat: 新增小說作品 {title}")

    # ---------------- 03 / 生活與節奏 ----------------
    def build_micro_logs_form(self):
        f = self.form_frame

        now = datetime.now()
        current_year = str(now.year)
        current_month = f"{now.month:02d}"

        years = [str(y) for y in range(2024, 2031)]
        months = [f"{m:02d}" for m in range(1, 13)]

        ttk.Label(f, text="1. 發表年月 (下拉選單點選):").grid(row=0, column=0, sticky='w', pady=2)
        date_frame = ttk.Frame(f)
        date_frame.grid(row=1, column=0, sticky='w', pady=(0, 8))

        self.combo_log_year = ttk.Combobox(date_frame, values=years, state='readonly', width=10)
        self.combo_log_year.set(current_year if current_year in years else "2026")
        self.combo_log_year.pack(side='left', padx=(0, 5))

        ttk.Label(date_frame, text="年").pack(side='left', padx=(0, 10))

        self.combo_log_month = ttk.Combobox(date_frame, values=months, state='readonly', width=8)
        self.combo_log_month.set(current_month)
        self.combo_log_month.pack(side='left', padx=(0, 5))

        ttk.Label(date_frame, text="月").pack(side='left')

        ttk.Label(f, text="2. 分類標籤:").grid(row=2, column=0, sticky='w', pady=2)
        categories = ["生活", "突發奇想", "興趣", "有感而發"]
        self.combo_log_cat = ttk.Combobox(f, values=categories, state='readonly', width=52)
        self.combo_log_cat.set("生活")
        self.combo_log_cat.grid(row=3, column=0, pady=(0, 8))

        ttk.Label(f, text="3. 動態標題:").grid(row=4, column=0, sticky='w', pady=2)
        self.e_log_title = ttk.Entry(f, width=55); self.e_log_title.grid(row=5, column=0, pady=(0, 8))

        ttk.Label(f, text="4. 內文隨筆內容:").grid(row=6, column=0, sticky='w', pady=2)
        self.t_log_desc = tk.Text(f, width=55, height=7, font=('Segoe UI', 9)); self.t_log_desc.grid(row=7, column=0, pady=(0, 12))

        ttk.Button(f, text="🚀 發布至 03/生活與節奏", command=self.save_micro_log).grid(row=8, column=0, ipady=4, sticky='we')

    def save_micro_log(self):
        year = self.combo_log_year.get()
        month = self.combo_log_month.get()
        date_str = f"{year}/{month}"

        cat = self.combo_log_cat.get().strip()
        title = self.e_log_title.get().strip()
        desc = self.t_log_desc.get("1.0", tk.END).strip()

        if not cat or not title or not desc:
            return messagebox.showwarning("提示", "請完整填寫標題與隨筆內容！")

        data = self.load_data()
        data.insert(0, {"id": len(data)+1, "date": date_str, "category": cat, "title": title, "desc": desc})
        self.save_data(data); self.refresh_treeview()
        if self.var_auto_push.get(): self.run_git_sync(f"feat: 新增生活隨筆 {title}")

    # ==========================================
    # 檢視與刪除頁面
    # ==========================================
    def setup_manage_tab(self):
        f = ttk.LabelFrame(self.tab_manage, text="當前類別內容清單", padding=10)
        f.pack(fill='both', expand=True, padx=10, pady=10)

        columns = ("id", "title")
        self.tree = ttk.Treeview(f, columns=columns, show='headings', height=18)
        self.tree.heading("id", text="編號")
        self.tree.heading("title", text="標題/名稱")
        self.tree.column("id", width=60, anchor='center')
        self.tree.column("title", width=460)
        self.tree.pack(fill='both', expand=True, pady=(0, 10))

        btn_f = ttk.Frame(f)
        btn_f.pack(fill='x')
        ttk.Button(btn_f, text="🗑️ 刪除選取項目", command=self.delete_selected).pack(side='left', padx=5)
        ttk.Button(btn_f, text="🔄 重新整理", command=self.refresh_treeview).pack(side='left', padx=5)

    def refresh_treeview(self):
        for r in self.tree.get_children(): self.tree.delete(r)
        data = self.load_data()
        for idx, item in enumerate(data):
            t = item.get('title') or item.get('name') or '未命名項目'
            self.tree.insert("", "end", iid=idx, values=(idx + 1, t))

    def delete_selected(self):
        sel = self.tree.selection()
        if not sel: return messagebox.showwarning("未選取", "請先點選項目！")
        idx = int(sel[0])
        data = self.load_data()
        title = data[idx].get('title', '項目')

        if messagebox.askyesno("確認", f"確定要刪除 [{title}] 嗎？"):
            data.pop(idx)
            self.save_data(data)
            self.refresh_treeview()
            if self.var_auto_push.get():
                self.run_git_sync(f"fix: 刪除項目 {title}")

if __name__ == '__main__':
    root = tk.Tk()
    app = UniversalGardenManager(root)
    root.mainloop()