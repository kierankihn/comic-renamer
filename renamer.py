import os
import logging
import requests
from typing import Dict, Optional
import tkinter as tk
from tkinter import ttk

__VERSION__ = '1.2.0'

def get_bangumi_api(path: str) -> Dict:
    """
    Fetch data from the Bangumi API.
    """
    url = f'https://api.bgm.tv{path}'
    headers = {
        'User-agent': f'kierankihn/comic-renamer/{__VERSION__} (https://github.com/kierankihn/comic-renamer)',
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