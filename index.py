# -*- coding: utf-8 -*-
import tkinter as tk
import up
import down
import tkinter.messagebox as msgbox
#创建窗口
window=tk.Tk()
window.title('欢迎使用点猫云')#窗口的标题
window.geometry('200x350')#窗口的大小

#按钮的函数
def hit_me1():
    up.main()
def hit_me2():
    down.app = down.Application()
    down.app.run()
  
def hit_me3():
    msgbox.showwarning(message='还在制作中……')
    #webbrowser.open('')
#按钮
b=tk.Button(window,text='上传文件',width=20,height=5,command=hit_me1)
b.pack()
c=tk.Button(window,text='下载文件',width=20,height=5,command=hit_me2)
c.pack()
b=tk.Button(window,text='网页版软件',width=20,height=5,command=hit_me3)
b.pack()
var=tk.StringVar()#定_')
var.set('made by Edgar_勿安')
l = tk.Label(window, 
    textvariable=var,    # 标签的文字
    #bg='yellowgreen',     # 标签背景颜色
    font=('Arial', 12),     # 字体和字体大小
    width=20, height=5  # 标签长宽
    )
l.pack()   
window.mainloop()
