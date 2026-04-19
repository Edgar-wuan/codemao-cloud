import requests
from tkinter import Tk, Button, Label, Text, END
from tkinter import filedialog
import re
import tkinter.messagebox as msgbox
import xmltodict
import base64
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
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
        self.title_label = Label(self.window, text=u'密码(如果没有不必填写):')
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
        domain = self.result_text1.get(0.0, END).strip().replace("\n", " ")
        print(domain)
        if is_valid_domain(domain):
            mima = self.result_text2.get(0.0, END).strip().replace("\n", " ")
            print(mima)
            if dir_path == '':
                msgbox.showerror('错误提示', '请输入路径')
            else:
                # 获取响应原始字节数据，避免requests自动编码猜测导致的错误
                response = requests.get(domain)
                xml_data = response.content
                # 检查是否为XML格式（使用字节判断，避免编码问题）
                if b'<?xml version="1.0" encoding="utf-8"?>' in xml_data:
                    # 使用原始字节解析XML，让xmltodict自动根据XML声明处理编码
                    xml = xmltodict.parse(xml_data)
                    if(xml['file']['generator'] != 'Codemao Cloud 2.0'):
                        msgbox.showerror('错误提示', '您输入的并不是使用点猫云XML上传的云盘链接，或上传版本过低')
                        self.result_text1.delete(0.0, END)
                    else:
                        name = xml['file']['name']
                        print(name)
                        contentb = xml['file']['content']
                        # 关键修改1：删除原错误的rb判断（原判断的是密文的编码，无意义）
                        shuju = contentb  # XML里的content本身是Base64字符串，直接传给解密函数即可
                        lujing = dir_path+'/'+name
                        print(lujing)
                        try:
                            result = aes_decrypt(shuju, mima)
                            # 关键修改2：根据解密结果的类型判断写入模式
                            if isinstance(result, bytes):
                                # 二进制数据（图片/视频）→ 用wb模式写入
                                with open(lujing, "wb") as f:
                                    f.write(result)
                            else:
                                # 文本数据 → 用w模式写入
                                with open(lujing, "w", encoding="utf-8") as f:
                                    f.write(result)
                            msgbox.showinfo(message='已在您选定目录生成文件')
                            self.result_text3.delete(0.0, END)
                            self.result_text1.delete(0.0, END)
                            self.result_text2.delete(0.0, END)
                        except ValueError:
                            # 捕获密码错误/解密失败的异常
                            msgbox.showerror('错误提示', '密码错误或解密失败')
                            self.result_text2.delete(0.0, END)
                else:
                    msgbox.showerror('错误提示', '您输入的并不是使用点猫云XML上传的云盘链接')
                    self.result_text1.delete(0.0, END)
        else:
            msgbox.showerror('错误提示', '请输入正确链接！')
            self.result_text1.delete(0.0, END)
def get_aes_key(password):
    """将自定义密码转为AES-256要求的32字节密钥（哈希固定长度）"""
    return hashlib.sha256(password.encode("utf-8")).digest()
def aes_decrypt(encrypted_b64, password):
    """AES-256解密：Base64密文 → 明文（自动兼容文本/二进制）"""
    key = get_aes_key(password)
    encrypted_bytes = base64.b64decode(encrypted_b64)
    # 拆分IV（前16字节）和密文
    iv = encrypted_bytes[:16]
    ciphertext = encrypted_bytes[16:]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_padded = cipher.decrypt(ciphertext)
    decrypted = unpad(decrypted_padded, AES.block_size)
    # 关键修改：先尝试转UTF-8文本，失败则返回二进制bytes
    try:
        return decrypted.decode("utf-8")
    except UnicodeDecodeError:
        return decrypted
if __name__ == "__main__":
    app = Application()
    app.run()
