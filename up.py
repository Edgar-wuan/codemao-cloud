# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
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
# 保留原XML模板常量
ysxml = '''
<?xml version="1.0" encoding="UTF-8"?>
<file>
    <generator>Codemao Cloud 2.0</generator>
    <name>文件名</name>
    <content>文件内容->UTF-8->base64</content>
</file>'''
class MyUI:
    def __init__(self, root):
        self.root = root
        self.root.title("点猫云文件上传")
        self.root.geometry("600x200+500+500")  # 尺寸+初始位置（与原程序一致）
        self.root.resizable(False, False)  # 固定窗口大小
        self.initUI()
    def initUI(self):
        # 1. 选择文件按钮
        self.btn1 = tk.Button(self.root, text='选择文件', command=self.choose_file)
        self.btn1.place(x=20, y=20, width=100, height=30)  # 位置/尺寸与原程序对齐
        # 2. 文件路径输入框（带placeholder）
        self.le = tk.Entry(self.root, font=("Arial", 9))
        self.le.place(x=130, y=20, width=350, height=30)
        self.le_placeholder = "输入文件完整路径或在左边选择文件"
        self.le.insert(0, self.le_placeholder)
        # 绑定焦点事件实现placeholder效果
        self.le.bind("<FocusIn>", self.on_le_focus_in)
        self.le.bind("<FocusOut>", self.on_le_focus_out)
        # 3. 模式标签
        self.info = tk.Label(self.root, text="模式：", font=("Arial", 14,"bold"))
        self.info.place(x=60, y=157)
        self.info = tk.Label(self.root, text="请输入密码：", font=("Arial", 14,"bold"))
        self.info.place(x=30, y=72.5)
        self.info = tk.Label(self.root, text="请确认密码：", font=("Arial", 14,"bold"))
        self.info.place(x=30, y=112.5)
        # 4. 模式下拉框
        self.box = ttk.Combobox(self.root, values=("XML模式", "Data模式"), state="readonly")
        self.box.current(0)  # 默认选中第一个
        self.box.place(x=130, y=155, width=100, height=30)
        self.box.bind("<<ComboboxSelected>>", self.change_mode)
        # 5. 密码输入框（带密码隐藏）
        self.le1 = tk.Entry(self.root, show="*", font=("Arial", 10))
        self.le1.place(x=130, y=70, width=200, height=30)
        self.le1_placeholder = "输入密码"
        self.le1.insert(0, self.le1_placeholder)
        self.le1.bind("<FocusIn>", self.on_le1_focus_in)
        self.le1.bind("<FocusOut>", self.on_le1_focus_out)
        # 6. 确认密码输入框
        self.le2 = tk.Entry(self.root, show="*", font=("Arial", 10))
        self.le2.place(x=130, y=110, width=200, height=30)
        self.le2_placeholder = "确认密码"
        self.le2.insert(0, self.le2_placeholder)
        self.le2.bind("<FocusIn>", self.on_le2_focus_in)
        self.le2.bind("<FocusOut>", self.on_le2_focus_out)
        # 7. 确认传输按钮
        self.btn2 = tk.Button(self.root, text="确认传输(XML)", command=self.check_file)
        self.btn2.place(x=340, y=70, width=140, height=70)
    # --------------------- placeholder 事件处理 ---------------------
    def on_le_focus_in(self, e):
        if self.le.get() == self.le_placeholder:
            self.le.delete(0, tk.END)
    def on_le_focus_out(self, e):
        if not self.le.get():
            self.le.insert(0, self.le_placeholder)
    def on_le1_focus_in(self, e):
        if self.le1.get() == self.le1_placeholder:
            self.le1.delete(0, tk.END)
    def on_le1_focus_out(self, e):
        if not self.le1.get():
            self.le1.insert(0, self.le1_placeholder)
    def on_le2_focus_in(self, e):
        if self.le2.get() == self.le2_placeholder:
            self.le2.delete(0, tk.END)
    def on_le2_focus_out(self, e):
        if not self.le2.get():
            self.le2.insert(0, self.le2_placeholder)
    def choose_file(self):
        """选择文件并填充到输入框"""
        fname = filedialog.askopenfilename(title="选择文件", initialdir="/home")
        if fname:
            self.le.delete(0, tk.END)
            self.le.insert(0, fname)
    def change_mode(self, e):
        """切换模式时更新按钮文字"""
        text = self.box.get()
        if text == "XML模式":
            self.btn2.config(text="确认传输(XML)")
        elif text == "Data模式":
            self.btn2.config(text="确认传输(Data)")
    def check_file(self):
        """校验文件并执行上传逻辑（完全复用原逻辑）"""
        mode = self.box.get()
        path = self.le.get().strip()
        password1 = self.le1.get().strip()
        password2 = self.le2.get().strip()
        # 过滤placeholder值
        if password1 == self.le1_placeholder:
            password1 = ""
        if password2 == self.le2_placeholder:
            password2 = ""
        if path == self.le_placeholder:
            path = ""
        # 密码校验
        if password1 != password2:
            self.show_error("两次输入密码不一致")
        # 路径校验
        elif len(path) == 0:
            self.show_error("请输入路径")
        # 文件合法性校验
        elif not os.path.isfile(path):
            self.show_error("路径不合法")
        # 文件大小校验（≤1GB）
        elif os.path.getsize(path) > 1024 * 1024 * 1024:
            self.show_error("当前只支持小于1GB文件")
            self.le.delete(0, tk.END)
            self.le.insert(0, self.le_placeholder)
        else:
            # XML模式逻辑
            if mode == "XML模式":
                try:
                    with open(path, 'rb') as file:
                        data = file.read()
                    namen = os.path.split(path)[1]
                    basedata = aes_encrypt(data, password1)
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
                    # 大小超限判断
                    if b == {'ErrorCode': 'EntityTooLarge', 'ErrorMessage': 'payload size exceeds maximum allowed size (16777216 bytes)'}:
                        self.show_error('您传输的文件超过16mb，无法使用传输')
                    else:
                        self.show_info("传输成功，请等待链接生成")
                        keyurl = 'https://static.box3.codemao.cn/block/' + b['Key']
                        if password1:
                            self.show_im(f"链接为：{keyurl}请抓紧时间复制，密码为：{password1} 正在启动浏览器，请稍等")
                        else:
                            self.show_im(f"链接为：{keyurl}请抓紧时间复制，无密码，正在启动浏览器，请稍等")
                        time.sleep(5)
                        webbrowser.open(keyurl)
                except Exception as e:
                    self.show_error(f"XML模式上传失败：{str(e)}")
            # Data模式逻辑
            elif mode == "Data模式":
                try:
                    with open(path, 'rb') as file:
                        a = requests.post(
                            url='https://static.box3.codemao.cn/block/',
                            data=file.read(),
                            headers={'Content-Type': 'text/html'}
                        )
                    b = a.json()
                    print(b)
                    if b == {'ErrorCode': 'EntityTooLarge', 'ErrorMessage': 'payload size exceeds maximum allowed size (16777216 bytes)'}:
                        self.show_error('您传输的文件超过16mb，无法使用Data传输')
                    else:
                        self.show_info("传输成功，请等待链接生成")
                        keyurl = 'https://static.box3.codemao.cn/block/' + b['Key']
                        self.show_im(f"链接为：{keyurl}请抓紧时间复制，正在启动浏览器，请稍等")
                        time.sleep(5)
                        webbrowser.open(keyurl)
                except Exception as e:
                    self.show_error(f"Data模式上传失败：{str(e)}")
    # --------------------- 弹窗方法（对应原程序的QMessageBox） ---------------------
    def show_info(self, text):
        messagebox.showinfo("提示", text)
    def show_im(self, text):
        # Tkinter无critical级别，用showerror替代（视觉上更醒目，与原逻辑一致）
        messagebox.showerror("重要", text)
    def show_error(self, text):
        messagebox.showwarning("错误", text)
# --------------------- 加密相关函数（完全复用原程序） ---------------------
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
# --------------------- 主函数 ---------------------
def main():
    # 打包时不加这一条pyinstaller会默认不支持多进程
    multiprocessing.freeze_support()
    root = tk.Tk()
    ex = MyUI(root)
    root.mainloop()
if __name__ == "__main__":
    main()
