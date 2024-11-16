#!/usr/bin/env python3

import os
import logging
import requests
from typing import Dict, Optional
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import threading

def setup_logging(verbose: bool, log_text: tk.Text) -> None:
    """
    Set up logging level based on verbosity.
    """
    class TextHandler(logging.Handler):
        def __init__(self, text):
            logging.Handler.__init__(self)
            self.text = text

        def emit(self, record):
            msg = self.format(record)
            self.text.insert(tk.END, msg + '\n')
            self.text.yview(tk.END)  # Auto-scroll to the bottom

    logging.basicConfig(format='%(asctime)s %(filename)s %(levelname)s - %(message)s', level=logging.INFO if verbose else logging.WARN, handlers = [TextHandler(log_text)])

def get_bangumi_api(path: str) -> Dict:
    """
    Fetch data from the Bangumi API.
    """
    url = f'https://api.bgm.tv{path}'
    headers = {
        'User-agent': 'kierankihn/comic-renamer/1.0.0 (https://github.com/kierankihn/comic-renamer)',
        'Content-Type': 'application/json',
        'accept': 'application/json'
    }

    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'
    response.raise_for_status()

    if '对不起，您在  秒内只能进行一次搜索，请返回。' in response.text:
        raise Exception(f'Failed to fetch data from {url} due to api rate limit.')

    return response.json()

def get_comic_info(name: str) -> Optional[Dict]:
    """
    Get comic information from the Bangumi API.
    """
    search_response = get_bangumi_api(f'/search/subject/{name}?type=1&responseGroup=small&max_results=1')
    if not search_response or search_response.get('results', 0) < 1:
        return None
    subject_id = search_response['list'][0]['id']
    return get_bangumi_api(f'/v0/subjects/{subject_id}')

def get_comic_name(name: str, format_str: str) -> Optional[str]:
    """
    Generate the new comic name based on the provided format.
    """
    comic_info = get_comic_info(name)

    if not comic_info:
        return None

    base_info = {
        'name': comic_info.get('name'),
        'namecn': comic_info.get('name_cn'),
        'author': None,
        'press': None
    }
    comic_infobox = comic_info.get('infobox', [])

    for item in comic_infobox:
        if item['key'] == '作者':
            base_info['author'] = item['value']
        if item['key'] == '出版社':
            base_info['press'] = item['value']

    if any(value is None and key in format_str for key, value in base_info.items()):
        return None

    return format_str.format(**base_info)

def rename_comics(path: str, format_str: str, progress_var: tk.DoubleVar, progress_bar: ttk.Progressbar, callback) -> None:
    """
    Rename comics in the specified directory.
    """
    files = os.listdir(path)

    for i, old_name in enumerate(files):
        try:
            new_name = get_comic_name(old_name, format_str)
            if new_name:
                old_path = os.path.join(path, old_name)
                new_path = os.path.join(path, new_name)

                if not os.path.exists(os.path.dirname(new_path)):
                    os.makedirs(os.path.dirname(new_path))
                os.rename(old_path, new_path)

                logging.info(f'Renamed {old_name} into {new_name}')
            else:
                logging.warning(f'Failed to rename {old_name} due to not found')
        except Exception as e:
            logging.error(f'Failed to rename {old_name}: {e}')

        # Update progress bar
        progress_var.set((i + 1) / len(files) * 100)
        progress_bar.update()

    callback()

def main_gui():
    """
    Main function to execute the comic renaming process with GUI.
    """
    def browse_directory():
        folder_selected = filedialog.askdirectory()
        folder_path.set(folder_selected)

    def start_renaming():
        path = folder_path.get()
        format_str = format_entry.get()
        if not path:
            messagebox.showerror("Error", "Please select a directory.")
            return
        if not format_str:
            messagebox.showerror("Error", "Please enter a format.")
            return

        # Disable the start button to prevent multiple threads
        start_button.config(state=tk.DISABLED)

        # Start the renaming process in a separate thread
        threading.Thread(target=lambda: rename_comics(path, format_str, progress_var, progress_bar, enable_start_button)).start()

    def enable_start_button():
        start_button.config(state=tk.NORMAL)

    root = tk.Tk()
    root.title("Comic Renamer")
    root.geometry("600x400")  # Set initial window size

    folder_path = tk.StringVar()
    format_str = tk.StringVar(value='{namecn} {author}')
    progress_var = tk.DoubleVar()

    tk.Label(root, text="Directory:").grid(row=0, column=0, padx=10, pady=10, sticky='w')
    tk.Entry(root, textvariable=folder_path, width=50).grid(row=0, column=1, padx=10, pady=10, sticky='ew')
    tk.Button(root, text="Browse", command=browse_directory).grid(row=0, column=2, padx=10, pady=10, sticky='e')

    tk.Label(root, text="Format:").grid(row=1, column=0, padx=10, pady=10, sticky='w')
    format_entry = tk.Entry(root, textvariable=format_str, width=50)
    format_entry.grid(row=1, column=1, padx=10, pady=10, sticky='ew')

    start_button = tk.Button(root, text="Start Renaming", command=start_renaming, width=15, height=1)
    start_button.grid(row=2, column=1, padx=10, pady=10, sticky='')

    progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100)
    progress_bar.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky='ew')

    log_text = tk.Text(root, height=10, width=60)
    log_text.grid(row=4, column=0, columnspan=3, padx=10, pady=10, sticky='nsew')
    
    setup_logging(False, log_text)

    # Make columns and rows expandable
    root.columnconfigure(1, weight=1)
    root.rowconfigure(4, weight=1)

    root.mainloop()

if __name__ == '__main__':
    main_gui()