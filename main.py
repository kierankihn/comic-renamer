#!/usr/bin/env python3

import os
import json
import logging
import requests
import argparse

parser = argparse.ArgumentParser(description = 'Automaticly rename your comics')

parser.add_argument('path')
parser.add_argument('-f', '--format', default = '{namecn} - {author} - {press}')
parser.add_argument('-v', '--verbose', action = 'store_true')

args = parser.parse_args()

path = args.path
format = args.format
if args.verbose == True:
    logging.basicConfig(format = '%(asctime)s %(filename)s %(levelname)s - %(message)s', level = logging.DEBUG)
else:
    logging.basicConfig(format = '%(asctime)s %(filename)s %(levelname)s - %(message)s', level = logging.INFO)

userAgent = 'kierankihn/comic-renamer/0.0.1 (https://github.com/kierankihn/comic-renamer)'
httpHeaders = { 'User-agent': userAgent, 'Content-Type': 'application/json', 'accept': 'application/json' }

apiEndpoint = 'https://api.bgm.tv'
searchApi = '/search/subject/'
subjectApi = '/v0/subjects/'

def postBangumiApi(path: str, data):
    return json.loads(requests.post(url = apiEndpoint + path, data = data, headers = httpHeaders).content.decode())

def getBangumiApi(path: str):
    response = requests.get(url = apiEndpoint + path, headers = httpHeaders)
    if response.status_code != 200 or response.content.decode().find('对不起，您在  秒内只能进行一次搜索，请返回。') != -1:
        return {}
    return json.loads(response.content.decode())

def getComicInfo(name: str):
    response = getBangumiApi(path = searchApi + name + '?type=1&responseGroup=small&max_results=1')
    if response.get('results') == None or response.get('results') < 1:
        return {}
    return getBangumiApi(subjectApi + str(response['list'][0]['id']))

def getComicName(name: str, format: str):
    comicInfo = getComicInfo(name)
    comicName = comicInfo.get('name')
    comicNameCn = comicInfo.get('name_cn')
    comicAuthor = None
    comicPress = None

    if comicInfo.get('infobox') != None:
        for i in comicInfo['infobox']:
            if i['key'] == '作者' and comicAuthor == None:
                comicAuthor = i['value']
        for i in comicInfo['infobox']:
            if i['key'] == '作画' and comicAuthor == None:
                comicAuthor = i['value']
        for i in comicInfo['infobox']:
            if i['key'] == '原作' and comicAuthor == None:
                comicAuthor = i['value']
        for i in comicInfo['infobox']:
            if i['key'] == '出版社' and comicPress == None:
                comicPress = i['value']
    
    if (comicName == None and format.find('{name}') != -1) or \
       (comicNameCn == None and format.find('{namecn}') != -1) or \
       (comicAuthor == None and format.find('{author}') != -1) or \
       (comicPress == None and format.find('{press}') != -1):
        return None

    format = format.replace('{name}', comicName) \
                   .replace('{namecn}', comicNameCn) \
                   .replace('{author}', comicAuthor) \
                   .replace('{press}', comicPress)

    return format

for oldPath in os.listdir(path):
    try:
        newPath = getComicName(oldPath, format)
        if newPath != None:
            logging.info(f'Renamed {oldPath} into {newPath}')
            os.rename(os.path.join(path, oldPath), os.path.join(path, newPath))
    except BaseException as e:
        logging.error(e)