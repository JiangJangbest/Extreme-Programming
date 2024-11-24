from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, \
    QListWidget, QListWidgetItem, QCheckBox, QFileDialog, QMenu, QAction, QMessageBox
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import requests
import sys
import pandas as pd  # For Excel import/export


class ContactBook(QWidget):
    def __init__(self):
        super().__init__()
        self.api_url = 'http://127.0.0.1:5000/contacts'  # Backend API URL
        self.initUI()
        self.loadContacts()

    def initUI(self):
        self.setWindowTitle('通讯录')
        self.setGeometry(100, 100, 500, 500)
        layout = QVBoxLayout()

        # Contact List
        self.contact_list = QListWidget()
        layout.addWidget(self.contact_list)

        # 创建上下文菜单（右键菜单）
        self.context_menu = QMenu(self)
        favorite_action = QAction('收藏', self)
        favorite_action.triggered.connect(self.on_favorite)
        self.context_menu.addAction(favorite_action)

        # 连接 contextMenuEvent 到显示菜单的方法
        self.contact_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.contact_list.customContextMenuRequested.connect(self.show_context_menu)

        # Search Layout
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入姓名查找...")
        search_button = QPushButton('查找')
        search_button.clicked.connect(self.search_contact)
        search_layout.addWidget(QLabel('查找姓名:'))
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_button)
        layout.addLayout(search_layout)

        # Add Contact Layout
        add_layout = QVBoxLayout()

        # Input fields for multiple contact methods
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("姓名")
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("电话(多个用逗号隔开)")
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("邮箱")
        self.address_input = QLineEdit()
        self.address_input.setPlaceholderText("地址")
        self.bookmark_checkbox = QCheckBox("收藏")
        # 连接 QCheckBox 的 stateChanged 信号到槽函数
        self.bookmark_checkbox.stateChanged.connect(self.on_state_changed)

        add_button = QPushButton('添加')
        add_button.clicked.connect(self.add_contact)

        add_layout.addWidget(QLabel('姓名:'))
        add_layout.addWidget(self.name_input)
        add_layout.addWidget(QLabel('电话:'))
        add_layout.addWidget(self.phone_input)
        add_layout.addWidget(QLabel('邮箱:'))
        add_layout.addWidget(self.email_input)
        add_layout.addWidget(QLabel('地址:'))
        add_layout.addWidget(self.address_input)
        add_layout.addWidget(self.bookmark_checkbox)
        add_layout.addWidget(add_button)
        layout.addLayout(add_layout)

        # Import/Export Layout
        file_layout = QHBoxLayout()
        import_button = QPushButton('导入')
        import_button.clicked.connect(self.import_contacts)
        export_button = QPushButton('导出')
        export_button.clicked.connect(self.export_contacts)
        file_layout.addWidget(import_button)
        file_layout.addWidget(export_button)
        layout.addLayout(file_layout)

        self.setLayout(layout)
        self.setFont(QFont("仿宋", 10))

    def show_context_menu(self, position):
        # 在指定的位置显示上下文菜单
        self.context_menu.exec_(self.contact_list.viewport().mapToGlobal(position))

    def on_favorite(self):
        # 获取当前选中的项目
        current_item = self.contact_list.currentItem()
        contact_id = current_item.data(1)
        if not current_item:
            return
        temp_arr = str(current_item.text()).split(" - ")
        # 执行收藏操作（这里仅打印示例）
        print(f'收藏了: {current_item.text()}')
        response = requests.get(f'{self.api_url}/collect', params={'id': contact_id})
        if response.status_code == 200:
            QMessageBox.information(self, '收藏成功', f'您已成功收藏了联系人：{temp_arr[0]}')

    # 定义一个槽函数来处理 stateChanged 信号
    def on_state_changed(self, state):
        if state == Qt.Checked:
            bookmarked = 1
            print("收藏已选中")
        else:
            bookmarked = 0
            print("收藏已取消")
        self.search_contact_collect(bookmarked)

    def loadContacts(self):
        response = requests.get(self.api_url)
        if response.status_code == 200:
            self.contact_list.clear()
            contacts = sorted(response.json(), key=lambda x: not x.get("bookmarked", False))  # Sort by bookmark status
            print(contacts)
            for contact in contacts:
                item_text = f'{contact["name"]} - {contact["phone"]} - {contact["email"]} - {contact["address"]}'
                item = QListWidgetItem(item_text)
                item.setData(1, contact["id"])
                self.contact_list.addItem(item)

    # 添加联系人
    def add_contact(self):
        name = self.name_input.text()
        phone = self.phone_input.text()
        email = self.email_input.text()
        address = self.address_input.text()
        bookmarked = self.bookmark_checkbox.isChecked()
        if name and phone:
            response = requests.post(self.api_url, json={
                'name': name,
                'phone': phone,
                'email': email,
                'address': address,
                'bookmarked': bookmarked
            })
            if response.status_code == 200:
                self.loadContacts()
                self.name_input.clear()
                self.phone_input.clear()
                self.email_input.clear()
                self.address_input.clear()
                self.bookmark_checkbox.setChecked(False)

    def search_contact(self):
        name = self.search_input.text()
        response = requests.get(f'{self.api_url}/search', params={'name': name})
        if response.status_code == 200:
            self.contact_list.clear()
            for contact in response.json():
                item_text = f'{contact["name"]} - {contact["phone"]} - {contact["email"]} - {contact["address"]}'
                item = QListWidgetItem(item_text)
                item.setData(1, contact["id"])
                self.contact_list.addItem(item)

    def search_contact_collect(self, bookmarked):
        response = requests.get(f'{self.api_url}/search/collect', params={'bookmarked': bookmarked})
        if response.status_code == 200:
            self.contact_list.clear()
            for contact in response.json():
                item_text = f'{contact["name"]} - {contact["phone"]} - {contact["email"]} - {contact["address"]}'
                item = QListWidgetItem(item_text)
                item.setData(1, contact["id"])
                self.contact_list.addItem(item)

    def import_contacts(self):
        file_path, _ = QFileDialog.getOpenFileName(self, '导入联系人', '', 'Excel Files (*.xlsx)')
        if file_path:
            data = pd.read_excel(file_path)
            for _, row in data.iterrows():
                temp_dic = row.to_dict()
                add_dic = {
                    'name': temp_dic['姓名'],
                    'phone': temp_dic['电话'],
                    'email': temp_dic['邮箱'],
                    'address': temp_dic['地址'],
                    'bookmarked': 0
                }
                requests.post(f'{self.api_url}', json=add_dic)
            self.loadContacts()

    def export_contacts(self):
        file_path, _ = QFileDialog.getSaveFileName(self, '导出联系人', '', 'Excel Files (*.xlsx)')
        try:
            if file_path:
                response = requests.get(self.api_url)
                if response.status_code == 200:
                    contacts = response.json()
                    # df = pd.DataFrame(contacts)
                    # df.to_excel(file_path, index=False)
                    # 准备要导出到 Excel 的数据
                    data_to_export = []
                    for contact in contacts:
                        # 只包含 address, name, phone, 并且重命名 address 为 地址, name 为 名字, phone 为 电话
                        # 注意：如果 email 在原始数据中，也应该包含它并重命名为 邮箱
                        row = {
                            '姓名': contact.get('name'),
                            '电话': contact.get('phone'),
                            '邮箱': contact.get('email', ''),  # 如果 email 可能不存在，使用 get 方法并提供默认值
                            '地址': contact.get('address'),
                        }
                        data_to_export.append(row)
                    # 创建 DataFrame
                    df = pd.DataFrame(data_to_export)
                    # 导出到 Excel
                    df.to_excel(file_path, index=False)
                    QMessageBox.information(self, '导出成功', )

        except Exception as ex:
            print(ex)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ContactBook()
    ex.show()
    sys.exit(app.exec_())
