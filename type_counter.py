from wordcloud import WordCloud
import matplotlib.pyplot as plt
from anime import Anime


class TypeCounter:
    def __init__(self, anime: list):
        self.word_map = {}
        for it in anime:
            s = it.type.split('/')
            for t in s:
                if len(t) == 0:
                    continue

                if not self.word_map.get(t):
                    self.word_map[t] = []
                self.word_map[t].append(it)

    def show(self):
        for k, v in self.word_map.items():
            print(k)
            for it in v:
                print(it.name)

    def show_wordcloud(self):
        wordcloud_data = {k: len(v) for k, v in self.word_map.items()}
        font_path = 'SimHei.ttf'
        wordcloud = WordCloud(font_path=font_path, width=800, height=400,
                              background_color='white').generate_from_frequencies(wordcloud_data)
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.show()