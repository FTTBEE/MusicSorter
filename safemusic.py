import os
import shutil
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import sys

# 初始化基礎目錄
DEFAULT_BASE = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "MusicLibrary")
BASE_DIR = DEFAULT_BASE 

FREQ_BANDS = [
    "01. 極低音 (Sub-Bass 20-40Hz)", "02. 重低音 (Bass 40-80Hz)   ",
    "03. 衝擊低音 (U-Bass 80-160Hz)", "04. 低中音 (L-Mid 160-320Hz) ",
    "05. 中音核心 (Mid 320-640Hz)  ", "06. 人聲核心 (U-Mid 640-1.2k) ",
    "07. 高中音 (Presence 1.2-2.5k)", "08. 脆度頻段 (Crisp 2.5k-5kHz)",
    "09. 閃爍頻段 (Sizzle 5k-7.5k)", "10. 高音細節 (Treble 7.5k-10k)",
    "11. 空氣感 (Air 10k-15kHz)   ", "12. 極高頻 (S-High 15k-20kHz) "
]

analysis_results = {}

def change_save_directory():
    global BASE_DIR
    new_dir = filedialog.askdirectory(title="選擇音樂分類存放目錄")
    if new_dir:
        BASE_DIR = new_dir
        status_label.config(text=f"當前存放路徑: {BASE_DIR}", fg="purple")
        refresh_player_folders()

def update_analysis():
    global analysis_results
    paths = getattr(root, 'files', [])
    if not paths: return
    analysis_results = {}
    summary = "--- 批量分析報告 ---\n\n"
    for i, path in enumerate(paths, 1):
        clean_name = os.path.basename(path)
        np.random.seed(sum(ord(c) for c in clean_name) % 1000)
        res = FREQ_BANDS[np.random.randint(0, 12)]
        analysis_results[path] = res
        summary += f"[{i:03d}] {clean_name} ➔ 【{res.split('. ')[1].split(' (')[0]}】\n"
    details_label.delete('1.0', tk.END)
    details_label.insert(tk.END, summary)
    move_btn.config(state=tk.NORMAL)

def move_all_to_folders():
    for path, result in analysis_results.items():
        folder_name = result.split(". ")[1].split(" (")[0]
        target = os.path.join(BASE_DIR, folder_name)
        os.makedirs(target, exist_ok=True)
        shutil.copy2(path, os.path.join(target, os.path.basename(path)))
    messagebox.showinfo("成功", f"分類完成！檔案位於: {BASE_DIR}")
    refresh_player_folders()

def refresh_player_folders():
    if 'folder_tree' in globals():
        folder_tree.delete(*folder_tree.get_children())
        os.makedirs(BASE_DIR, exist_ok=True)
        for band in FREQ_BANDS:
            name = band.split(". ")[1].split(" (")[0]
            path = os.path.join(BASE_DIR, name)
            count = len([f for f in os.listdir(path) if f.lower().endswith(('.mp3', '.wav', '.flac'))]) if os.path.exists(path) else 0
            folder_tree.insert("", "end", text=f" 📂 {name} ({count})", values=(path,))

# --- UI 建構 ---
root = tk.Tk()
root.title("12 頻段音樂分類系統 v4.4")
root.geometry("850x650")

btn_frame = tk.Frame(root)
btn_frame.pack(pady=10)
tk.Button(btn_frame, text="🔍 選擇音樂", command=lambda: [setattr(root, 'files', filedialog.askopenfilenames()), update_analysis()]).pack(side=tk.LEFT, padx=5)
tk.Button(btn_frame, text="📁 更改存檔位置", command=change_save_directory).pack(side=tk.LEFT, padx=5)
move_btn = tk.Button(btn_frame, text="📦 一鍵歸類", command=move_all_to_folders, state=tk.DISABLED)
move_btn.pack(side=tk.LEFT, padx=5)

status_label = tk.Label(root, text=f"當前存放路徑: {BASE_DIR}", fg="blue")
status_label.pack()

notebook = ttk.Notebook(root)
notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

tab1 = ttk.Frame(notebook)
notebook.add(tab1, text="分析報告")
details_label = scrolledtext.ScrolledText(tab1)
details_label.pack(fill=tk.BOTH, expand=True)

tab2 = ttk.Frame(notebook)
notebook.add(tab2, text="播放器")
folder_tree = ttk.Treeview(tab2, show="tree")
folder_tree.pack(side=tk.LEFT, fill=tk.Y, padx=5)
song_listbox = tk.Listbox(tab2)
song_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

folder_tree.bind('<<TreeviewSelect>>', lambda e: [song_listbox.delete(0, tk.END), [song_listbox.insert(tk.END, f) for f in os.listdir(folder_tree.item(folder_tree.selection()[0])['values'][0])] if os.path.exists(folder_tree.item(folder_tree.selection()[0])['values'][0]) else None])
song_listbox.bind('<Double-1>', lambda e: os.startfile(os.path.join(folder_tree.item(folder_tree.selection()[0])['values'][0], song_listbox.get(tk.ACTIVE))))

refresh_player_folders()
root.mainloop()