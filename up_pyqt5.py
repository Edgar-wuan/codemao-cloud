# -*- coding: utf-8 -*-
import sys
from PyQt5.QtWidgets import QWidget, QPushButton, QComboBox, QLabel, QApplication, QFileDialog, QMessageBox, QLineEdit
import os
import multiprocessing
import requests
import webbrowser
import time
import base64
import hashlib
import xmltodict
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes
# ####################GUI########################
ysxml = '''
<?xml version="1.0" encoding="UTF-8"?>
<file>
    <generator>Codemao Cloud 2.0</generator>
    <name>文件名</name>
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
            if mode == "XML模式":
                with open(path, 'rb') as file:
                    data = file.read()
                namen = os.path.split(path)[1]
                basedata = aes_encrypt(data, password1)
                print(basedata)
                # 生成XML内容，直接处理编码，不生成临时文件
                info_dict = {
                        'file': {
                                'generator': 'Codemao Cloud 2.0',
                                'name': namen,
                                'content': basedata
                        }
                }
                # 生成XML字符串，强制编码为UTF-8，与XML声明保持一致
                xml_str = xmltodict.unparse(info_dict, pretty=True)
                xml_data = xml_str.encode('utf-8')
                # 直接发送XML数据，无需临时文件，同时声明charset=utf-8
                a = requests.post(
                    url='https://static.box3.codemao.cn/block/',
                    data=xml_data,
                    headers={'Content-Type': 'text/xml; charset=utf-8'}
                )
                b = a.json()
                print(b)
                if b == {'ErrorCode': 'EntityTooLarge', 'ErrorMessage': 'payload size exceeds maximum allowed size (16777216 bytes)'}:
                    self.show_error('您传输的文件超过16mb，无法使用传输')
                else:
                    self.show_info("传输成功，请等待链接生成")
                    keyurl = 'https://static.box3.codemao.cn/block/'+b['Key']
                    self.show_im("链接为："+keyurl+'请抓紧时间复制，密码为：'+password1+' 正在启动浏览器，请稍等')
                    time.sleep(5)
                    webbrowser.open(keyurl)
            elif mode == "Data模式":
                file = open(path,'rb')
                a = requests.post(url='https://static.box3.codemao.cn/block/',data=file.read(),headers={'Content-Type':'text/html'})
                b = a.json()
                print(b)
                if b == {'ErrorCode': 'EntityTooLarge', 'ErrorMessage': 'payload size exceeds maximum allowed size (16777216 bytes)'}:
                    self.show_error('您传输的文件超过16mb，无法使用Data传输')
                else:
                    self.show_info("传输成功，请等待链接生成")
                    keyurl = 'https://static.box3.codemao.cn/block/'+b['Key']
                    self.show_im("链接为："+keyurl+'请抓紧时间复制，正在启动浏览器，请稍等')
                    time.sleep(5)
                    webbrowser.open(keyurl)
    def show_info(self, text):
        QMessageBox.information(self, "提示", text)
    def show_im(self, text):
        QMessageBox.critical(self, "重要", text)
    def show_error(self, text):
        QMessageBox.warning(self, "错误", text)
def get_aes_key(password):
    """将自定义密码转为AES-256要求的32字节密钥（哈希固定长度）"""
    return hashlib.sha256(password.encode("utf-8")).digest()
def aes_encrypt(plain_text, password):
    """AES-256加密：支持字符串/二进制文件，返回Base64格式密文"""
    key = get_aes_key(password)
    iv = get_random_bytes(16)  # 随机生成16字节初始化向量（CBC模式必需）
    cipher = AES.new(key, AES.MODE_CBC, iv)
    if isinstance(plain_text, str):
        plain_bytes = plain_text.encode("utf-8")
    else:
        plain_bytes = plain_text
    padded_data = pad(plain_bytes, AES.block_size)
    encrypted = cipher.encrypt(padded_data)
    return base64.b64encode(iv + encrypted).decode("utf-8")
def main():
    # 打包时不加这一条pyinstaller会默认不支持多进程
    multiprocessing.freeze_support()
    app = QApplication(sys.argv)
    ex = MyUI()
    sys.exit(app.exec_())
if __name__ == "__main__":
    main()
