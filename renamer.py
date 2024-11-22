import os
import json
import logging
import requests
from typing import  List, Dict, Optional
import tkinter as tk
from tkinter import ttk

__VERSION__ = '1.3.1'

def get_tw_press(path: str) -> Optional[List]:
    """
    Fetch data from the TW Press API.
    """
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

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
    
def get_comic_person_info(bangumi_id: int) -> Dict:
    """
    Get comic person information from the Bangumi API.
    """
    search_response = get_bangumi_api(f'/v0/subjects/{bangumi_id}/persons')
    return search_response

def get_comic_name(name: str, format_str: str, use_tw_press: bool) -> Optional[str]:
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

    if use_tw_press:
        tw_press = get_tw_press('data.json')
    comic_person_info = get_comic_person_info(comic_info['id'])

    for item in comic_person_info:
        if item['relation'] == '作者':
            base_info['author'] = item['name']
        if item['relation'] == '出版社' and (base_info['press'] is None or (use_tw_press and item['name'] in tw_press)):
            base_info['press'] = item['name']

    if any(value is None and key in format_str for key, value in base_info.items()):
        return None

    return format_str.format(**base_info)

def rename_comics(path: str, format_str: str, use_tw_press : bool, progress_var: tk.DoubleVar, progress_bar: ttk.Progressbar, callback) -> None:
    """
    Rename comics in the specified directory.
    """
    files = os.listdir(path)

    logging.info(f'Start renaming {len(files)} files in {path} with format {format_str}')

    for i, old_name in enumerate(files):
        try:
            new_name = get_comic_name(old_name, format_str, use_tw_press)
            if new_name:
                old_path = os.path.join(path, old_name)
                new_path = os.path.join(path, new_name)

                if not os.path.exists(os.path.dirname(new_path)):
                    os.makedirs(os.path.dirname(new_path))
                os.rename(old_path, new_path)

                logging.debug(f'Renamed {old_name} into {new_name}')
            else:
                logging.warning(f'Failed to rename {old_name} due to not found')
        except Exception as e:
            logging.error(f'Failed to rename {old_name}: {e}')

        # Update progress bar
        progress_var.set((i + 1) / len(files) * 100)
        progress_bar.update()

    logging.info('Done')

    callback()