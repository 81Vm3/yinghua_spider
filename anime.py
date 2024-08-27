import io

import requests
import sys
import os
import json

from bs4 import BeautifulSoup
from PIL import Image

import site_info


class Anime:
    __save_folder = 'save'
    __folder_checked = False

    def __init__(self, day, name, url, img):
        self.status = ''
        self.director = ''
        self.director_main = ''
        self.year = ''
        self.country = ''
        self.language = ''
        self.type = ''
        self.duration = ''
        self.time = ''
        self.update = ''
        self.has_info = False
        self.has_cover = False
        self.image_data = io.BytesIO()

        self.day = day
        self.name = name
        self.url = url
        self.img = img

        self.video_links = []

    def get_info(self):
        if self.has_info:
            return

        response = requests.get(site_info.url + self.url)
        response.encoding = 'utf-8'

        soup = BeautifulSoup(response.text, "html.parser")
        info = soup.find('div', class_='hl-full-box clearfix')

        li = info.find_all('li', class_='hl-col-xs-12')
        m = {}
        for it in li:
            s = it.text.split('：')
            m[s[0]] = s[1]

        self.status = m['状态']
        self.director = m['主演']
        self.director_main = m['导演']
        self.year = m['年份']
        self.country = m['地区']
        self.type = m['类型']
        self.duration = m['时长']
        self.time = m['上映']
        self.language = m['语言']
        self.update = m['更新']
        self.has_info = True

    def show(self):
        print('作品:' + self.name)
        print('主演:' + self.director)
        print('导演:' + self.director_main)
        print('类型:' + self.type)
        print('语言:' + self.language)
        print('状态:' + self.status)
        print('更新:' + self.update)

    def to_json(self):
        j = {
            'url': {
                'video': self.url,
                'image': self.img
            },
            'info': {
                'name': self.name,
                'director': self.director,
                'director_main': self.director_main,
                'type': self.type,
                'language': self.language,
                'year': self.year,
                'duration': self.duration,
                'time': self.time,
                'status': self.status,
                'update': self.update
            }
        }
        return json.dumps(j, indent=4)

    def save_to_json(self):
        d = self.to_json()
        os.makedirs(Anime.__save_folder, exist_ok=True)

        with open(f'{Anime.__save_folder}/{self.name}.json', 'w') as f:
            f.write(d)

    def get_cover(self):
        if self.has_cover:
            return self.image_data

        r = requests.get(self.img, stream=True)
        r.raise_for_status()  # Check for any errors in the response

        # Write the image data directly to memory
        for chunk in r.iter_content(chunk_size=16 * 1024):
            self.image_data.write(chunk)

        self.image_data.seek(0)  # Reset the buffer position to the start
        self.has_cover = True
        return self.image_data  # Return the in-memory image data

    def save_cover(self):
        os.makedirs(Anime.__save_folder, exist_ok=True)
        raw = self.get_cover()  # io.ByteIO

        image = Image.open(raw).convert("RGB")
        image.save(f'{Anime.__save_folder}/{self.name}.jpg', 'jpeg')

    # 目前仅支持获取单线路的视频
    def get_video_links(self):
        r = requests.get(f'{site_info.url}/{self.url}')
        r.raise_for_status()

        r.encoding = 'utf-8'
        soup = BeautifulSoup(r.text, "html.parser")
        videos = soup.find_all('li', class_='hl-col-xs-4 hl-col-sm-2')

        self.video_links.clear()
        for it in videos:
            if it.text.find('集') != -1:
                a = it.find('a')
                self.video_links.append(a['href'])

    def save(self):
        os.makedirs(Anime.__save_folder, exist_ok=True)
        if not Anime.__folder_checked:
            for i in range(1, 8):
                os.makedirs(Anime.__save_folder + '/' + str(i), exist_ok=True)
            __folder_checked = True

        t = f"{Anime.__save_folder}/{str(self.day)}/"

        try:
            raw = self.get_cover()
            image = f'{t}{self.name}.webp'

            if not os.path.exists(image):
                with open(image, 'wb') as f:
                    f.write(raw.getvalue())

            n = f'{t}{self.name}.txt'
            with open(n, 'w') as f:
                f.writelines([
                    '主演:' + self.director + '\n',
                    '导演:' + self.director_main + '\n',
                    '类型:' + self.type + '\n',
                    '语言:' + self.language + '\n',
                    '年份:' + self.year + '\n',
                    '时长:' + self.duration + '\n',
                    '上映:' + self.time + '\n',
                    '状态:' + self.status + '\n',
                    '更新:' + self.update
                ])
        except Exception as e:
            print(e)
