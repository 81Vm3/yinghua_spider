import io
import sys
from PyQt5.QtCore import Qt, QVariant
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,
    QLineEdit, QHBoxLayout, QLabel, QListWidget,
    QListWidgetItem, QMessageBox, QComboBox,
    QProgressBar
)

from PIL import Image
from anime_search import AnimeSearcher, SearchException
from type_counter import TypeCounter

class SpiderApp:
    def __init__(self):
        self.__app = QApplication(sys.argv)
        self.window = QWidget()
        self.window.setWindowTitle('樱花动漫爬虫')
        self.window.setGeometry(100, 100, 600, 500)

        split_view = QHBoxLayout()

        # Left layout
        left_layout = QVBoxLayout()
        self.search_input = QLineEdit('')
        left_layout.addWidget(self.search_input)
        self.search_button = QPushButton('搜索')
        self.search_button.clicked.connect(self.search_anime)
        left_layout.addWidget(self.search_button)

        week_layout = QHBoxLayout()
        self.week_search_button = QPushButton('查看每周更新')
        self.week_search_button.clicked.connect(self.week_search_anime_clicked)
        self.week_search_list = QComboBox()
        self.week_search_list.addItems([
            "全部",
            "周一",
            "周二",
            "周三",
            "周四",
            "周五",
            "周六",
            "周日"
        ])
        week_layout.addWidget(self.week_search_button)
        week_layout.addWidget(self.week_search_list)
        week_layout.setStretch(0, 1)
        week_layout.setStretch(1, 1)
        left_layout.addLayout(week_layout)

        self.save_json_button = QPushButton('保存右侧所有动漫信息到json')
        self.save_json_button.clicked.connect(self.save_json_button_clicked)
        left_layout.addWidget(self.save_json_button)

        self.wordcloud_button = QPushButton('导出右侧所有动漫类型的词云')
        self.wordcloud_button.clicked.connect(self.wordcloud_button_clicked)
        left_layout.addWidget(self.wordcloud_button)

        # left_layout.addWidget(QLabel('进度'))
        # self.progress_bar = QProgressBar()
        # left_layout.addWidget(self.progress_bar)

        # Right layout
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel('动漫详情 (双击获取详细信息)'), alignment=Qt.AlignTop | Qt.AlignLeft)

        # List layout (40% of the vertical space)
        list_layout = QVBoxLayout()
        self.anime_list = QListWidget()
        self.anime_list.itemDoubleClicked.connect(self.on_anime_item_clicked)
        list_layout.addWidget(self.anime_list)

        # Info layout
        info_layout = QHBoxLayout()
        # info下分两层，一层封面一层信息
        info_left = QVBoxLayout()
        info_right = QVBoxLayout()

        self.info_cover = QLabel()
        self.info_director = QLabel()
        self.info_director_main = QLabel()
        self.info_type = QLabel()
        self.info_language = QLabel()
        self.info_year = QLabel()
        self.info_duration = QLabel()
        self.info_time = QLabel()
        self.info_status = QLabel()
        self.info_update = QLabel()
        self.info_director.setWordWrap(True)
        self.info_director_main.setWordWrap(True)
        self.info_type.setWordWrap(True)
        info_right.addWidget(self.info_cover)
        info_left.addWidget(self.info_director)
        info_left.addWidget(self.info_director_main)
        info_left.addWidget(self.info_type)
        info_left.addWidget(self.info_language)
        info_left.addWidget(self.info_year)
        info_left.addWidget(self.info_duration)
        info_left.addWidget(self.info_time)
        info_left.addWidget(self.info_status)
        info_left.addWidget(self.info_update)

        self.save_json_button_single = QPushButton('保存JSON')
        info_right.addWidget(self.save_json_button_single)
        self.save_json_button_single.clicked.connect(self.save_json_button_single_clicked)

        self.save_cover_button = QPushButton('保存封面')
        info_right.addWidget(self.save_cover_button)
        self.save_cover_button.clicked.connect(self.save_cover_button_clicked)

        self.save_video_button = QPushButton('下载选集')
        info_right.addWidget(self.save_video_button)
        self.save_video_button.clicked.connect(self.save_video_button_clicked)

        info_layout.addLayout(info_left)
        info_layout.addLayout(info_right)
        info_layout.setStretch(0, 1)
        info_layout.setStretch(1, 1)
        # info_layout.addStretch(1)

        right_layout.addLayout(list_layout)
        right_layout.addLayout(info_layout)

        right_layout.setStretch(1, 2)
        right_layout.setStretch(2, 3)

        left_layout.addStretch(1)
        split_view.addLayout(left_layout)
        split_view.addLayout(right_layout)

        split_view.setStretch(0, 1)
        split_view.setStretch(1, 1)

        self.window.setLayout(split_view)
        self.hide_buttons()
        self.window.show()

    def getApp(self):
        return self.__app

    def show_message_box(self, type, text):
        msg = QMessageBox()
        msg.setIcon(type)
        msg.setText(text)
        msg.setWindowTitle("提示")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def clear_anime_view(self):
        self.info_director.clear()
        self.info_director_main.clear()
        self.info_type.clear()
        self.info_language.clear()
        self.info_year.clear()
        self.info_duration.clear()
        self.info_time.clear()
        self.info_status.clear()
        self.info_update.clear()
        self.info_cover.clear()
        self.hide_buttons()

    def hide_buttons(self):
        self.save_cover_button.hide()
        self.save_json_button_single.hide()
        self.save_video_button.hide()

    def show_buttons(self):
        self.save_cover_button.show()
        self.save_json_button_single.show()
        self.save_video_button.show()

    def search_anime(self):
        text = self.search_input.text()
        if len(text) > 0:
            a = AnimeSearcher()
            try:
                r = a.search(text)
                if len(r) > 0:
                    self.anime_list.clear()
                    self.clear_anime_view()
                    for it in r:
                        list_item = QListWidgetItem(it.name)
                        list_item.setData(Qt.UserRole, QVariant(it))
                        self.anime_list.addItem(list_item)
                else:
                    self.show_message_box(QMessageBox.Information, '没有搜索到内容捏~ 再试一次咯')

            except SearchException:
                self.show_message_box(QMessageBox.Critical, '你急什么！等下再搜索')

    def week_search_anime_clicked(self):
        a = AnimeSearcher()
        table = a.search_week()
        self.anime_list.clear()
        self.clear_anime_view()

        index = self.week_search_list.currentIndex()
        if index == 0:
            for i in range(0, 7):
                for y in table[i]:
                    list_item = QListWidgetItem(y.name)
                    list_item.setData(Qt.UserRole, QVariant(y))
                    self.anime_list.addItem(list_item)
        else:
            index -= 1
            for y in table[index]:
                list_item = QListWidgetItem(y.name)
                list_item.setData(Qt.UserRole, QVariant(y))
                self.anime_list.addItem(list_item)

    def on_anime_item_clicked(self, item):
        selected_anime = item.data(Qt.UserRole)
        if selected_anime:
            selected_anime.get_info()
            raw = selected_anime.get_cover()
            self.info_director.setText('主演:' + selected_anime.director)
            self.info_director_main.setText('导演:' + selected_anime.director_main)
            self.info_type.setText('类型:' + selected_anime.type)
            self.info_language.setText('语言:' + selected_anime.language)
            self.info_year.setText('年份:' + selected_anime.year)
            self.info_duration.setText('时长:' + selected_anime.duration)
            self.info_time.setText('上映:' + selected_anime.time)
            self.info_status.setText('状态:' + selected_anime.status)
            self.info_update.setText('更新:' + selected_anime.update)

            try:
                image = Image.open(raw)
                image = image.convert("RGBA")  # Convert to RGBA format for compatibility with Qt

                # Convert the Pillow image to a QImage
                qim = QImage(image.tobytes(), image.width, image.height, QImage.Format_RGBA8888)

                pixmap = QPixmap.fromImage(qim)
                scaled_pixmap = pixmap.scaled(
                    self.anime_list.width(),
                    self.anime_list.height(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.info_cover.setPixmap(scaled_pixmap)
                self.info_cover.setAlignment(Qt.AlignCenter)
                self.show_buttons()

            except Exception as e:
                print(f"Error loading image: {e}")
                self.info_cover.setText("无法加载图片")

    def dump_anime_list(self):
        return [self.anime_list.item(x).data(Qt.UserRole) for x in range(self.anime_list.count())]

    def save_json_button_clicked(self):
        a = self.dump_anime_list()
        if len(a) > 0:
            for it in a:
                it.get_info()
                it.save_to_json()

    def wordcloud_button_clicked(self):
        a = self.dump_anime_list()
        if len(a) > 0:
            for it in a:
                it.get_info()

            t = TypeCounter(a)
            t.show_wordcloud()

    def save_cover_button_clicked(self):
        d = self.anime_list.selectedItems()[0]
        if d:
            a = d.data(Qt.UserRole)
            a.save_cover()
            self.show_message_box(QMessageBox.Information, '封面已保存到 save 文件夹下')

    def save_json_button_single_clicked(self):
        d = self.anime_list.selectedItems()[0]
        if d:
            a = d.data(Qt.UserRole)
            a.save_to_json()
            self.show_message_box(QMessageBox.Information, 'json 已保存到 save 文件夹下')

    def save_video_button_clicked(self):
        pass

