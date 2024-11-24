from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QListWidget, QListWidgetItem, QCheckBox, QFileDialog
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
        self.phone_input.setPlaceholderText("电话")
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("邮箱")
        self.address_input = QLineEdit()
        self.address_input.setPlaceholderText("地址")
        self.bookmark_checkbox = QCheckBox("收藏")
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

    def loadContacts(self):
        response = requests.get(self.api_url)
        if response.status_code == 200:
            self.contact_list.clear()
            contacts = sorted(response.json(), key=lambda x: not x.get("bookmarked", False))  # Sort by bookmark status
            for contact in contacts:
                item_text = f'{contact["name"]} - {contact["phone"]} - {contact["email"]} - {contact["address"]}'
                item = QListWidgetItem(item_text)
                item.setData(1, contact["id"])
                self.contact_list.addItem(item)

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
        if name:
            response = requests.get(f'{self.api_url}/search', params={'name': name})
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
                requests.post(self.api_url, json=row.to_dict())
            self.loadContacts()

    def export_contacts(self):
        file_path, _ = QFileDialog.getSaveFileName(self, '导出联系人', '', 'Excel Files (*.xlsx)')
        if file_path:
            response = requests.get(self.api_url)
            if response.status_code == 200:
                contacts = response.json()
                df = pd.DataFrame(contacts)
                df.to_excel(file_path, index=False)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ContactBook()
    ex.show()
    sys.exit(app.exec_())
