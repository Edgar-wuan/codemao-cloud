# -*- coding: utf-8 -*-
import sys
from PyQt5.QtWidgets import QWidget, QPushButton, QComboBox, QLabel, QApplication, QFileDialog, QMessageBox, QLineEdit
import os
import multiprocessing
import requests
import webbrowser
import time
import base64
from xml.etree import ElementTree as ET
import hashlib
import xmltodict

# from requests_toolbelt import MultipartEncoder

# ####################GUI########################

ysxml = '''
<?xml version="1.0" encoding="UTF-8"?>
<file>
    <generator>Codemao Cloud</generator>
    <name>文件名</name>
    <password>密码的sha1摘要</password>
    <content>文件内容->UTF-8->base64</content>
</file>'''


class MyUI(QWidget):

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.btn1 = QPushButton('选择文件', self)
        self.btn1.move(20, 20)
        self.btn1.clicked.connect(self.choose_file)

        self.le = QLineEdit(self, )
        self.le.move(130, 20)
        self.le.resize(350, 30)
        self.le.setPlaceholderText("输入文件完整路径或在左边选择文件")

        # 设置标签
        self.info = QLabel(self)
        self.info.move(60, 160)
        self.info.setText("<b>模式</b>")
        # 设置下拉选项框
        self.box = QComboBox(self)
        self.box.addItems(("XML模式", "Data模式")),
        self.box.move(130, 155)
        self.box.currentIndexChanged.connect(self.change_mode)
        '''        # 设置标签
        self.iinfo = QLabel(self)
        self.iinfo.move(35, 100)
        self.iinfo.setText("<b>生成链接:尚未生成</b>")'''
                # 输入密码框
        self.le1 = QLineEdit(self, )
        self.le1.move(130, 70)
        self.le1.resize(200, 30)
        self.le1.setPlaceholderText("请输入密码")
        self.le1.setEchoMode(self.le1.Password)

        self.le2 = QLineEdit(self, )
        self.le2.move(130, 110)
        self.le2.resize(200, 30)
        self.le2.setPlaceholderText("确认密码")
        self.le2.setEchoMode(self.le2.Password)
        # 确认按钮
        self.btn2 = QPushButton("确认传输(XML)", self)
        self.btn2.resize(150, 70)
        self.btn2.move(350, 80)
        self.btn2.clicked.connect(self.check_file)
        self.setGeometry(500, 500, 600, 200)
        self.setWindowTitle("点猫云文件上传")
        self.show()

    def choose_file(self):
        fname = QFileDialog.getOpenFileName(self, "选择文件", '/home')

        if fname[0]:

            self.le.setText(str(fname[0]))

    def change_mode(self):
        text = self.box.currentText()
        if text == "XML模式":
            self.btn2.setText("确认传输(XML)")
        elif text == "Data模式":
            self.btn2.setText("确认传输(Data)")

    def check_file(self):
        mode = self.box.currentText()
        path = self.le.text()
        password1 = self.le1.text().strip()
        password2 = self.le2.text().strip()

        if password1 != password2:
            self.show_error("两次输入密码不一致")

        elif len(path) == 0:
            self.show_error("请输入路径")

        elif not os.path.isfile(path):
            self.show_error("路径不合法")

        elif os.path.getsize(path) > 1024*1024*1024:
            self.show_error("当前只支持小于1GB文件")
            self.le.clear()
        else:
            if len(password1) == 0:
                password1 = 'null'
            if mode == "XML模式":
                file = open(path, 'rb')
                data = file.read()
                file.close()
                basedata = base64.b64encode(data).decode()
                print(basedata)
                namen = os.path.split(path)[1]
                if password1=='null':
                    mima = 'null'
                else:   
                    mim = hashlib.sha1(password1.encode())
                    mima = mim.hexdigest()
                with open('format.xml', 'w') as f:
                    info_dict = {
                            'file': {
                                    'generator': 'Codemao Cloud',
                                    'name': namen,
                                    'password': mima,
                                    'content': basedata
                            }
                    }
                    f.write(xmltodict.unparse(info_dict, pretty=True))
                file = open('format.xml','rb')
                a = requests.post(url='https://static.box3.codemao.cn/block/',data=file.read(),headers={'Content-Type':'text/xml'})
                b = a.json()
                print(b)
                if b == {'ErrorCode': 'EntityTooLarge', 'ErrorMessage': 'payload size exceeds maximum allowed size (16777216 bytes)'}:
                    self.show_error('您传输的文件超过16mb，无法使用传输')
                else:
                    self.show_info("传输成功，请等待链接生成")
                    # print(isinstance(b,(dict)))
                    keyurl = 'https://static.box3.codemao.cn/block/'+b['Key']
                    # print(keyurl)
                    # self.iinfo.setText("<b>生成链接:"+keyurl+"</b>")
                    self.show_im("链接为："+keyurl+'请抓紧时间复制，密码为：'+password1+' 正在启动浏览器，请稍等')
                    time.sleep(5)
                    webbrowser.open(keyurl)
            elif mode == "Data模式":
                file = open(path,'rb')
                a = requests.post(url='https://static.box3.codemao.cn/block/',data=file.read(),headers={'Content-Type':'text/xml'})
                b = a.json()
                print(b)
                if b == {'ErrorCode': 'EntityTooLarge', 'ErrorMessage': 'payload size exceeds maximum allowed size (16777216 bytes)'}:
                    self.show_error('您传输的文件超过16mb，无法使用Data传输')
                else:
                    self.show_info("传输成功，请等待链接生成")
                    # print(isinstance(b,(dict)))
                    keyurl = 'https://static.box3.codemao.cn/block/'+b['Key']
                    # print(keyurl)
                    # self.iinfo.setText("<b>生成链接:"+keyurl+"</b>")
                    self.show_im("链接为："+keyurl+'请抓紧时间复制，正在启动浏览器，请稍等')
                    time.sleep(5)
                    webbrowser.open(keyurl)

    def show_info(self, text):
        QMessageBox.information(self, "提示", text)

    def show_im(self, text):
        QMessageBox.critical(self, "重要", text)

    def show_error(self, text):
        QMessageBox.warning(self, "错误", text)


def main():
    # 打包时不加这一条pyinstaller会默认不支持多进程
    multiprocessing.freeze_support()
    app = QApplication(sys.argv)
    ex = MyUI()
    sys.exit(app.exec_())



