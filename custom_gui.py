import io
import sys
from PyQt5.QtCore import Qt, QVariant
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,
    QLineEdit, QHBoxLayout, QLabel, QListWidget,
    QListWidgetItem, QMessageBox, QComboBox
)
from PIL import Image
from anime_search import AnimeSearcher, SearchException


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
        info_left.addWidget(self.info_cover)
        info_right.addWidget(self.info_director)
        info_right.addWidget(self.info_director_main)
        info_right.addWidget(self.info_type)
        info_right.addWidget(self.info_language)
        info_right.addWidget(self.info_year)
        info_right.addWidget(self.info_duration)
        info_right.addWidget(self.info_time)
        info_right.addWidget(self.info_status)
        info_right.addWidget(self.info_update)

        info_layout.addLayout(info_right)
        info_layout.addLayout(info_left)
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
        self.window.show()

    def getApp(self):
        return self.__app

    def search_anime(self):
        text = self.search_input.text()
        if len(text) > 0:
            a = AnimeSearcher()
            try:
                r = a.search(text)
                if len(r) > 0:
                    self.anime_list.clear()
                    for it in r:
                        list_item = QListWidgetItem(it.name)
                        list_item.setData(Qt.UserRole, QVariant(it))
                        self.anime_list.addItem(list_item)
                else:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Information)
                    msg.setText("没有搜索到内容捏~ 再试一次咯")
                    msg.setWindowTitle("搜索")
                    msg.setStandardButtons(QMessageBox.Ok)
                    msg.exec_()
            except SearchException:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("你急什么！等下再搜索")
                msg.setWindowTitle("错误")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()

    def week_search_anime_clicked(self):
        a = AnimeSearcher()
        table = a.search_week()
        self.anime_list.clear()

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
            except Exception as e:
                print(f"Error loading image: {e}")
                self.info_cover.setText("无法加载图片")


if __name__ == '__main__':
    app = SpiderApp()
    app.getApp().exec_()
