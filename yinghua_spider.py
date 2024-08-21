import requests
from bs4 import BeautifulSoup

import site_info
from anime import Anime
from type_counter import TypeCounter

header = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "max-age=0",
    "Connectin": "keep-alive",
    "Host": "2.2.2.2",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36 Edg/95.0.1020.53",
}

day_chs = [
    "周一",
    "周二",
    "周三",
    "周四",
    "周五",
    "周六",
    "周日"
]

def show_info(day: int, table: list, save: bool):
    print('#########################################')
    print('以下是周' + str(day+1) + ' 的动漫')
    print('#########################################')

    for anime in table[day]:
        anime.get_info()
        print('----------------------')
        anime.show()

        if save:
            anime.save()

def main():
    try:
        opt = int(input("输入你要获取周几的动漫 (1-7, -1 则获取全部): "))

        if (opt < 1 or opt > 7) and opt != -1:
            print("输入错误")
            return
    except ValueError:
        print("输入错误")
        return

    save_to_disk = input("是否要将详细结果和预览图保存? (N/y): ")
    if save_to_disk != 'y':
        save_to_disk = 'N'

    print("爬取主页中...")

    response = requests.get(site_info.url, headers=header)
    response.encoding = 'utf-8'

    soup = BeautifulSoup(response.text, "html.parser")
    div_tag = soup.find('div', id='conch-content')

    rows = div_tag.find('div', class_='row')

    table = []
    cnt = 0

    print("正在分析主页数据...")

    for day in rows:
        items = day.find_all('a', class_='hl-item-thumb hl-lazy')
        table.append([])
        for it in items:
            table[cnt].append(
                Anime(
                    cnt+1,
                    it['title'],
                    it['href'],
                    it['data-original']
                )
            )
        cnt += 1

    if opt == -1:
        for i in range(0, 7):
            show_info(i, table, save_to_disk == 'y')
    else:
        show_info(opt-1, table, save_to_disk == 'y')

    l = []
    for x in table:
        for y in x:
            l.append(y)
    tc = TypeCounter(l)
    tc.show_wordcloud()

if __name__ == '__main__':
    main()
