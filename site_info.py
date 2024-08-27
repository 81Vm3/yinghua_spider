
url = 'https://yinghua.uk'
search = 'https://yinghua.uk/so'

header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"
}

# 该网站的视频播放器，流量通过cdn，如cdn更新，则需要更新此url..
video_player = 'https://play.yhcdn.top/?url='

# 从后端请求真视频URL的链接
video_url_api = 'https://play.yhcdn.top/api.php'

# 解密URL所用的密钥
AESKey = b'ARTPLAYERliUlanG'
AESIV = b'ArtplayerliUlanG'