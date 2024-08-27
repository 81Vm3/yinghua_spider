import json
import os
import requests
from bs4 import BeautifulSoup

from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import base64

import site_info
from anime import Anime

def unpad_pkcs7(data):
    # Unpad Pkcs7 padding manually
    padding_len = data[-1]
    return data[:-padding_len]

class VideoDownloader():
    __save_folder = 'saved_video'
    def __init__(self, link):
        self.link = link
        self.name = 'unknown'

    # 从视频播放器的链接中获取客户端的key，然后向api.php请求加密后的url
    def get_encrypted_url(self, link):
        r = requests.get(site_info.video_player + link, headers=site_info.header)
        r.raise_for_status()
        r.encoding = 'utf-8'
        soup = BeautifulSoup(r.text, "html.parser")
        script = soup.find('script', {'type': 'text/javascript'})

        time_str = '\"time\":\"'
        key_str = '\"key\":\"'

        time = ''
        key = ''
        sec = 0

        text = script.text

        loc = text.find(time_str)
        if loc != -1:
            sec = text.find('\",',loc)
            if sec != -1:
                time = text[loc + len(time_str):sec]

        loc = text.find(key_str)
        if loc != -1:
            sec = text.find('\",', loc)
            if sec != -1:
                key = text[loc + len(key_str):sec]

        if len(time) == 0 or len(key) == 0:
            return ''

        try:
            rep = requests.post(site_info.video_url_api, headers=site_info.header, data={
                'url': link,
                'time': time,
                'key': key
            })
            rep.raise_for_status()
            j = json.loads(rep.text)
            return j['url']
        except Exception as e:
            print(e)

    def unpad(self, ct):
        return ct[:-ct[-1]]
    def decrypt_url(self, url_encrypted):
        # 要先解开base64，因为在js的crypto库中加密后的数据通常也是经过base64编码的
        encrypted_data = base64.b64decode(url_encrypted)

        #  iv用的和key一样
        cipher = AES.new(site_info.AESKey, AES.MODE_CBC, site_info.AESIV)
        decrypted_data = cipher.decrypt(encrypted_data)
        decrypted_data = unpad_pkcs7(decrypted_data)
        return decrypted_data.decode('utf-8')

    def get_true_video_link(self):
        pass

    # 获取视频播放器的链接
    def get_video_player_link(self):
        url = f'{site_info.url}{self.link}'

        r = requests.get(url, headers=site_info.header)
        r.raise_for_status()
        r.encoding = 'utf-8'
        soup = BeautifulSoup(r.text, "html.parser")

        # 找播放器
        player = soup.find('div', class_=lambda c: c and 'hl-player-wrap' in c.split())
        if player:

            # 获取播放器的时候顺便获取动漫的名字
            self.name = soup.find('span', class_='hl-mob-name hl-text-site hl-lc-1').text

            script_blocks = player.find_all('script', {'type': 'text/javascript'})
            special_code = ''
            for s in script_blocks:
                script = s.text

                # 脚本中挖出这部动漫在后端中的 "url"
                target = '\"url\":\"'
                loc = script.find(target, 0)
                if loc != -1:
                    e = script.find('\",', loc)
                    if e != -1:
                        video_url = script[loc+len(target):e]
                        return video_url
        return ''

    def download(self):
        os.makedirs(VideoDownloader.__save_folder, exist_ok=True)

        path = f'{Anime}/{self.name}.mp4'