import requests
from tkinter import Tk, Button,Label, Text, END
from tkinter import filedialog
import re
import tkinter.messagebox as msgbox
import xmltodict
import base64
import hashlib

dir_path = ''
pattern = re.compile(
    r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
)

def is_valid_domain(domain):
    """ 
    Return whether or not given value is a valid domain.
    If the value is valid domain name this function returns ``True``, otherwise False
    :param value: domain string to validate
    """
    return True if pattern.match(domain) else False

class Application(object):
    def __init__(self):
        self.window = Tk()
        self.window.title(u'点猫云文件下载')
        # 设置窗口大小和位置
        self.window.geometry('310x370+500+300')
        self.window.minsize(310, 370)
        self.window.maxsize(310, 370)
        # 创建一个文本框
        #self.entry = Entry(self.window)
        # self.entry.place(x=10,y=10,width=200,height=25)
        # self.entry.bind("<Key-Return>",self.submit1)
        self.result_text1 = Text(self.window)
        # 喜欢什么背景色就在这里面找哦，但是有色差，得多试试：http://www.science.smith.edu/dftwiki/index.php/Color_Charts_for_TKinter
        self.title_label1 = Label(self.window, text=u'链接:')
        self.title_label1.place(x=10, y=5)

        self.result_text1.place(x=10, y=25, width=285, height=50)
        # self.result_text1.bind("<Key-Return>",self.submit1)

        self.title_label = Label(self.window, text=u'密码(如果没有填写null):')
        self.title_label.place(x=10, y=75)

        self.result_text2 = Text(self.window)
        self.result_text2.place(x=10, y=95, width=285, height=50)
       # self.result_text1.bind("<Key-Return>",self.submit1)
        # 创建一个按钮
        # 为按钮添加事件
        self.submit_btn = Button(
            self.window, text=u'开始下载并编码', command=self.submit)
        self.submit_btn.place(x=10, y=165, width=110, height=35)
        self.submit_btn2 = Button(
            self.window, text=u'选择下载目录', command=self.clean)
        self.submit_btn2.place(x=150, y=165, width=105, height=35)

        self.title_label2 = Label(self.window, text=u'下载目标目录:(请在按钮选取，此处填写无效')
        self.title_label2.place(x=10, y=210)

        self.result_text3 = Text(self.window)
        self.result_text3.place(x=10, y=235, width=285, height=50)

        self.title_label4 = Label(self.window, text=u'注：请填写完整链接')
        self.title_label4.place(x=10, y=300)
        # 翻译结果标题
        '''self.title_label = Label(self.window,text=u'下载结果:')
        self.title_label.place(x=10,y=165)'''

    def clean(self):
        global dir_path
        dir_path = filedialog.askdirectory(title='选择文件存放的位置！')
        # self.result_text3.set(where)
        self.result_text3.delete(0.0, END)
        self.result_text3.insert('end', dir_path)

    def run(self):
        self.window.mainloop()

    def submit(self):
        domain = self.result_text1.get(0.0,END).strip().replace("\n"," ")
        print(domain)
        if is_valid_domain(domain):
            mima = self.result_text2.get(0.0,END).strip().replace("\n"," ")
            print(mima)
            if dir_path == '':
                msgbox.showerror('错误提示','请输入路径')
            else:
                if mima == '':
                    msgbox.showerror('错误提示','请输入密码，无密码请输入null')
                    self.result_text2.delete(0.0, END)
                else:
                    a = requests.get(domain).text
                    if '<?xml version="1.0" encoding="utf-8"?>' in a:
                        xml = xmltodict.parse(a)
                        if(xml['file']['generator']!='Codemao Cloud'):
                            msgbox.showerror('错误提示','您输入的并不是使用点猫云XML上传的云盘链接')
                            self.result_text1.delete(0.0, END)
                        else:
                            name = xml['file']['name']
                            print(name)
                            passwordsha = xml['file']['password']
                            print(passwordsha)
                            contentb = xml['file']['content']
                            contenta = contentb.encode()
                            strDecode = base64.b64decode(contenta)
                            try:
                                shuju = strDecode.decode()
                                rb = False
                            except UnicodeDecodeError:
                                shuju = strDecode
                                rb = True
                            lujing = dir_path+'/'+name
                            print(lujing)
                            if passwordsha=='null':
                                if rb :
                                    f = open(lujing, "wb")
                                    f.write(shuju)
                                    f.close()
                                else:
                                    f = open(lujing, "w")
                                    f.write(shuju)
                                    f.close()
                                msgbox.showinfo(message='已在您选定目录生成文件')
                                self.result_text3.delete(0.0, END)
                                self.result_text1.delete(0.0, END)
                                self.result_text2.delete(0.0, END)
                            else:
                                mimsha = hashlib.sha1(mima.encode())
                                mimasha = mimsha.hexdigest()
                                print(mimasha)
                                if mimasha == passwordsha:
                                    if rb :
                                        f = open(lujing, "wb")
                                        f.write(shuju)
                                        f.close()
                                    else:
                                        f = open(lujing, "w")
                                        f.write(shuju)
                                        f.close()
                                    msgbox.showinfo(message='已在您选定目录生成文件')
                                    self.result_text3.delete(0.0, END)
                                    self.result_text1.delete(0.0, END)
                                    self.result_text2.delete(0.0, END)
                                else:
                                    msgbox.showerror('错误提示','密码错误')
                                    self.result_text2.delete(0.0, END)
                    else:
                        msgbox.showerror('错误提示','您输入的并不是使用点猫云XML上传的云盘链接')
                        self.result_text1.delete(0.0, END)
        else:
            msgbox.showerror('错误提示','请输入正确链接！')
            self.result_text1.delete(0.0, END)


