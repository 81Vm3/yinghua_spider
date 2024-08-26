import requests
from bs4 import BeautifulSoup

import site_info
from anime import Anime
from anime_search import AnimeSearcher

from type_counter import TypeCounter


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

    a = AnimeSearcher()
    table = a.search_week()

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
