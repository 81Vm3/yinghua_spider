import io

import requests
import sys
import os
import json

from bs4 import BeautifulSoup
import site_info


class Anime:
    __save_folder = 'save'
    __folder_checked = False

    status = ''
    director = ''
    director_main = ''
    year = ''
    country = ''
    language = ''
    type = ''
    duration = ''
    time = ''
    update = ''

    def __init__(self, day, name, url, img):
        self.day = day
        self.name = name
        self.url = url
        self.img = img

    def get_info(self):
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

    def get_cover(self):
        r = requests.get(self.img, stream=True)
        r.raise_for_status()  # Check for any errors in the response
        image_data = io.BytesIO()  # Create an in-memory bytes buffer

        # Write the image data directly to memory
        for chunk in r.iter_content(chunk_size=16 * 1024):
            image_data.write(chunk)

        image_data.seek(0)  # Reset the buffer position to the start
        return image_data  # Return the in-memory image data

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
