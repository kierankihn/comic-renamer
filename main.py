#!/usr/bin/env python3

import os
import logging
import requests
import argparse
from typing import Dict, Optional

def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.
    """
    parser = argparse.ArgumentParser(description = 'Automatically rename your comics')
    parser.add_argument('path', help = 'Path to the directory containing comics')
    parser.add_argument('-f', '--format', default = '{namecn} {author}', help = 'Format for renaming')
    parser.add_argument('-v', '--verbose', action = 'store_true', help = 'Enable verbose logging')
    return parser.parse_args()

def setup_logging(verbose: bool) -> None:
    """
    Set up logging level based on verbosity.
    """
    logging.basicConfig(format='%(asctime)s %(filename)s %(levelname)s - %(message)s', level = logging.INFO if verbose else logging.WARN)

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
    response = requests.get(url, headers = headers)
    response.encoding = 'utf-8'
    if response.status_code != 200:
        raise Exception(f'Failed to fetch data from {url} due to api error.')
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

def rename_comics(path: str, format_str: str) -> None:
    """
    Rename comics in the specified directory.
    """
    for old_name in os.listdir(path):
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

def main() -> None:
    """
    Main function to execute the comic renaming process.
    """
    args = parse_arguments()
    setup_logging(args.verbose)
    rename_comics(args.path, args.format)

if __name__ == '__main__':
    main()
