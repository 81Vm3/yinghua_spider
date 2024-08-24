import sys
from PyQt5.QtCore import Qt, QVariant
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLineEdit,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox
)

from anime_search import AnimeSearcher, SearchException

class SpiderApp:
    def __init__(self):
        self.__app = QApplication(sys.argv)
        self.window = QWidget()
        self.window.setWindowTitle('樱花动漫爬虫')
        self.window.setGeometry(100, 100, 600, 500)  # Adjusted for better visibility

        split_view = QHBoxLayout()

        # Create left and right layouts
        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()

        # Add widgets to the left layout
        self.search_input = QLineEdit('')
        left_layout.addWidget(self.search_input)
        self.search_button = QPushButton('搜索')
        self.search_button.setStatusTip("搜索动漫")
        self.search_button.clicked.connect(self.search_anime)
        left_layout.addWidget(self.search_button)

        # Add widgets to the right layout
        right_layout.addWidget(QLabel('动漫详情 (双击获取详细信息)'), alignment=Qt.AlignTop | Qt.AlignLeft)

        self.anime_list = QListWidget()
        self.anime_list.itemDoubleClicked.connect(self.on_anime_item_clicked)

        right_layout.addWidget(self.anime_list)
        right_layout.addStretch(3)

        # Add the left and right layouts to the split view
        left_layout.addStretch(3)
        split_view.addLayout(left_layout)
        split_view.addLayout(right_layout)

        # Set stretch factors to make both layouts take equal space (50% each)
        split_view.setStretch(0, 1)  # Left layout stretch factor
        split_view.setStretch(1, 1)  # Right layout stretch factor

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
                        # Create a list item with the anime name
                        list_item = QListWidgetItem(it.name)
                        # Store the anime object in the item's user data
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

    def on_anime_item_clicked(self, item):
        selected_anime = item.data(Qt.UserRole)
        if selected_anime:
            print(selected_anime.name)

if __name__ == '__main__':
    app = SpiderApp()
    app.getApp().exec_()
