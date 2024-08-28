import io
import os
import sys
from PyQt5.QtCore import Qt, QVariant
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,
    QLineEdit, QHBoxLayout, QLabel, QListWidget,
    QListWidgetItem, QMessageBox, QComboBox,
    QProgressBar,
    QTextEdit
)

from PIL import Image
import codecs

import site_info
from anime import Anime
from anime_search import AnimeSearcher, SearchException
from type_counter import TypeCounter
from video_downloader import VideoDownloader, DownloaderWorker


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

        info_layout.addLayout(info_left)
        info_layout.addLayout(info_right)
        info_layout.setStretch(0, 1)
        info_layout.setStretch(1, 1)
        # info_layout.addStretch(1)

        right_layout.addLayout(list_layout)
        right_layout.addLayout(info_layout)

        self.downloader_window = DownloaderWindow()
        right_layout.addWidget(self.downloader_window)

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

    @staticmethod
    def show_message_box(icon_type, text):
        msg = QMessageBox()
        msg.setIcon(icon_type)
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
        self.downloader_window.clear_combo()

    def hide_buttons(self):
        self.save_cover_button.hide()
        self.save_json_button_single.hide()
        self.downloader_window.hide()

    def show_buttons(self):
        self.save_cover_button.show()
        self.save_json_button_single.show()
        self.downloader_window.show()

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

            self.downloader_window.clear_combo()
            self.downloader_window.update_combo(selected_anime.video_links, selected_anime.video_strs)

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
                try:
                    it.get_info()
                    it.save_to_json()
                except Exception as e:
                    print(e)

    def wordcloud_button_clicked(self):
        a = self.dump_anime_list()
        if len(a) > 0:
            for it in a:
                it.get_info()

            t = TypeCounter(a)
            t.show_wordcloud()

    def get_selected_anime(self):
        d = self.anime_list.selectedItems()[0]
        if d:
            return d.data(Qt.UserRole)
        return None

    def save_cover_button_clicked(self):
        a = self.get_selected_anime()
        if a:
            a.save_cover()
            self.show_message_box(QMessageBox.Information, '封面已保存到 save 文件夹下')

    def save_json_button_single_clicked(self):
        a = self.get_selected_anime()
        if a:
            a.save_to_json()
            self.show_message_box(QMessageBox.Information, 'json 已保存到 save 文件夹下')


class DownloaderWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.link_info = []

        # -------------- 下载选集的窗口 ---------------
        layout = QHBoxLayout()
        self.download_video_button = QPushButton('下载')
        self.download_video_button.clicked.connect(self.download_video_button_clicked)
        layout.addWidget(self.download_video_button)

        self.combo = QComboBox()
        layout.addWidget(self.combo)

        self.status_window = DownloaderStatusWindow()

        super().setLayout(layout)

    def clear_combo(self):
        self.combo.clear()

    def download_video_button_clicked(self):
        if self.combo.count() == 0:
            pass
        else:
            try:
                index = self.combo.currentIndex()
                link = self.link_info[index]
                d = VideoDownloader(link)
                player = d.get_video_player_link()
                if len(player) > 0:
                    print('get player success')
                    if player.find('yinghua-') != -1:
                        encrypted_url = d.get_encrypted_url(player)
                        if len(encrypted_url) > 0:
                            print('encrypted_url = ' + encrypted_url)
                            # 线路1，需要解密
                            decrypted_url = d.decrypt_url(encrypted_url)
                            print('decrypted_url = ' + decrypted_url)
                            self.status_window.update_text(decrypted_url)
                            self.status_window.tmp_name = f'{d.name} {self.combo.currentText()}.mp4'
                            self.status_window.show()
                    # 线路2，不需要解密
                    else:
                        url = codecs.decode(player, 'unicode_escape').replace('\\/', '/')
                        self.status_window.update_text(url)
                        self.status_window.tmp_name = f'{d.name} {self.combo.currentText()}.mp4'
                        self.status_window.show()

            except Exception as e:
                SpiderApp.show_message_box(QMessageBox.Critical, "无法下载视频: " + str(e))

    def update_combo(self, links: list, strs: list):
        self.link_info = links

        self.combo.clear()
        for it in strs:
            self.combo.addItem(it)


class DownloaderStatusWindow(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        self.info_label = QLabel(
            '解密完成，你可以复制下面的url到浏览器下载\n 或者点下面的按钮，用爬虫单线下载并保存到本地(可能会造成卡顿)')
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.download_button = QPushButton('单线下载')
        self.download_button.clicked.connect(self.download_button_clicked)

        self.progress_bar = QProgressBar()

        layout.addWidget(self.info_label)
        layout.addWidget(self.text_edit)
        horizon_layout = QHBoxLayout()
        horizon_layout.addWidget(self.download_button)
        horizon_layout.addWidget(self.progress_bar)
        horizon_layout.setStretch(0, 1)
        horizon_layout.setStretch(1, 3)
        layout.addLayout(horizon_layout)
        super().setLayout(layout)

    def update_text(self, text):
        self.text_edit.setText(text)

    def download_button_clicked(self):
        try:
            url = self.text_edit.toPlainText()
            if len(url) != 0:
                self.download_button.setEnabled(False)

                os.makedirs(VideoDownloader.save_folder, exist_ok=True)
                path = f'{VideoDownloader.save_folder}/{self.tmp_name}'
                # Run the download in a new thread.
                self.downloader = DownloaderWorker(
                    url,
                    path
                )
                # Connect the signals which send information about the download
                # progress with the proper methods of the progress bar.
                self.downloader.setTotalProgress.connect(self.progress_bar.setMaximum)
                self.downloader.setCurrentProgress.connect(self.progress_bar.setValue)
                # Qt will invoke the `succeeded()` method when the file has been
                # downloaded successfully and `downloadFinished()` when the
                # child thread finishes.
                self.downloader.succeeded.connect(self.downloadSucceeded)
                self.downloader.finished.connect(self.downloadFinished)
                self.downloader.start()
        except Exception as e:
            print(e)

    def downloadSucceeded(self):
        self.progress_bar.setValue(self.progress_bar.maximum())

    def downloadFinished(self):
        try:
            # Restore the button.
            self.download_button.setEnabled(True)
            SpiderApp.show_message_box(QMessageBox.Information, '视频已保存到 ' + self.downloader.get_filename())

            # Delete the thread when no longer needed.
            del self.downloader
        except Exception as e:
            print(e)
