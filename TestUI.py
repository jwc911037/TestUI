#!/usr/bin/python
# -*- coding: UTF-8 -*-
# import Pecker
from Tkinter import *
import tkFileDialog
import ttk
from PIL import ImageTk, Image
import sys
import os
import serial
import serial.tools.list_ports
import time
import threading
import  Queue as queue
import tkMessageBox
import signal
#==========主畫面==========#
class GUI(Frame): 
    def __init__(self,master):
        self.master = master
        self.queue = queue.Queue()
        self.step = serial.Serial()
        self.serv = serial.Serial()
        window= Frame(self.master)
        window.pack()
        window.configure(background='#344253')
    
        self.COM=[]
        self.port_list = list(serial.tools.list_ports.comports())
        for port in self.port_list:
            port_serial = port[0]
            self.COM.append(port_serial)
        #==========下拉步進馬達COM==========#
        self.lab1=Label(window,text='步進馬達COM :',fg='#FFFFFF',bg='#344253',font=('Calibri,微軟正黑',12,'bold'))
        self.lab1.grid(column=16, row=6,rowspan=2,pady=10)
        # self.lab1_ttp = CreateToolTip(self.lab1, "請選擇步進馬達連接埠")

        self.box_value1 = StringVar()
        self.box1 = ttk.Combobox(window, textvariable=self.box_value1,state='readonly',width=10)
        self.box1['values'] = (self.COM) 
        self.box1.bind('<<ComboboxSelected>>',self.Choice1)
        self.box1.grid(column=17, row=6,columnspan=2,rowspan=2,padx=10,pady=10)
        #==========下拉步進馬達COM==========#
        #==========下拉伺服馬達COM==========#
        self.lab2=Label(window,text='伺服馬達COM :',fg='#FFFFFF',bg='#344253',font=('Calibri,微軟正黑',12,'bold'))
        self.lab2.grid(column=16,row=8,rowspan=2,pady=10)
        # self.lab2_ttp = CreateToolTip(self.lab2, "請選擇伺服馬達連接埠")
        
        self.box_value2 = StringVar()
        self.box2 = ttk.Combobox(window, textvariable=self.box_value2,state='readonly',width=10)
        self.box2['values'] = (self.COM) 
        self.box2.bind('<<ComboboxSelected>>',self.Choice2)
        self.box2.grid(column=17, row=8,columnspan=2,rowspan=2,padx=10,pady=10)
        #==========下拉伺服馬達COM==========#
       
        #==========Send按鈕==========#
        self.img8=ImageTk.PhotoImage(Image.open("img/send.png"))
        self.send=Button(window, image=self.img8, bg='#344253',command=self.spawnthread)
        self.send.grid(column=16,row=15,columnspan=3)
        # self.button6_ttp = CreateToolTip(self.send, "傳送")
        self.pause_img=ImageTk.PhotoImage(Image.open("img/pause.png"))
        self.pause=Button(window, image=self.pause_img, bg='#344253',command=self.pauseEvent)
        self.pause.grid(column=14,row=12,columnspan=3,rowspan=2,padx=10,pady=10)
        self.pause.config(state=DISABLED)
        # self.pause_ttp = CreateToolTip(self.pause, '暫停')

        self.moveon_img=ImageTk.PhotoImage(Image.open("img/move_on.png"))
        self.moveon=Button(window, image=self.moveon_img, bg='#344253',command=self.resumeEvent)
        self.moveon.grid(column=17,row=12,columnspan=3,rowspan=2,padx=10,pady=10)
        self.moveon.config(state=DISABLED)
        # self.moveon_ttp = CreateToolTip(self.pause, '繼續')
        #==========Send按鈕==========#
        #==========訊息框==========#
        self.frame2=Frame(window,width=25,height=15)
        self.frame2.grid(column=16,row=16,columnspan=3,rowspan=3,pady=10)
        self.t=Text(self.frame2,height=15,width=25, bg='#477979',fg='white',font=('Calibri',12),padx=10,pady=5)
        self.t.grid(column=16,row=16,columnspan=3,rowspan=3,pady=10)
        self.t.config(state=DISABLED)
        self.vbar=ttk.Scrollbar(self.frame2,orient=VERTICAL)
        self.vbar.pack(side=RIGHT,fill=Y)
        self.vbar.config(command=self.t.yview)
        self.t.config(yscrollcommand=self.vbar.set)
        self.t.pack(side=LEFT,expand=True,fill=BOTH)
        # self.t_ttp = CreateToolTip(self.t, "port連接訊息框")
        #==========訊息框==========#
        #==========進度條==========#
        self.progress = ttk.Progressbar(window, orient="horizontal",length=280, mode="determinate")
        self.progress.grid(column=16,row=20,columnspan=10,rowspan=2,pady=22)
        self.progress['value'] = 0
        self.nowstep = 0
        #決定進度條長度(計算行數)
        gcode = open('gcode/cathy.gcode','r')
        total_line=-1
        for (total_line, line) in enumerate(gcode):
            pass
        total_line += 1
        nowstep = 0
        self.progress["maximum"] = total_line
        gcode.close()
        #==========進度條==========#
    

    def Choice1(self,event):
        step_port = self.box_value1.get()
        list = self.COM
        if step_port in list:  
            self.port1 = step_port
            return self.port1
    def Choice2(self,event):
        serv_port = self.box_value2.get()
        list = self.COM
        if serv_port in list:  
            self.port2 = serv_port
            return self.port2

    def spawnthread(self):
        #預先清空訊息框舊訊息
        self.t.config(state=NORMAL)
        self.t.delete('1.0',END)
        self.send.config(state=DISABLED)
        self.pause.config(state=ACTIVE)
        #開啟步進馬達COM
        try:
            self.step = serial.Serial(self.port1,115200)
        except Exception:
            self.t.config(state=NORMAL)
            self.t.insert(INSERT,'無法連接該步進馬達COM，請檢查後再重新連接一次...\n')
            self.t.config(state=DISABLED)
            self.send.config(state=ACTIVE)
            return
        #開啟伺服馬達COM
        # try:
        #     self.serv = serial.Serial(self.port2,9600)
        # except Exception:
        #     self.step.close() #如果伺服馬達沒開成功步進馬達要先關掉
        #     self.t.config(state=NORMAL)
        #     self.t.insert('insert','無法連接該伺服馬達COM，請檢查後再重新連接一次...\n')
        #     self.t.config(state=DISABLED)
        #     self.send.config(state = "active")
        #     return
        # 啟動grbl
        self.step.write("\r\n\r\n")
        time.sleep(2)
        self.step.flushInput()
        self.t.config(state=NORMAL)
        self.t.insert('insert','Initialize grbl...\n')
        self.t.config(state=DISABLED)
        #建立子執行緒執行繪圖
        
        self.thread = ThreadedClient(self.queue,self.step,self.serv)
        self.thread.start()
        self.periodiccall()

    def periodiccall(self):
        self.checkqueue()
        if self.thread.is_alive():
            self.master.after(100,self.periodiccall)
        else:
            self.t.config(state=NORMAL)
            self.t.insert('insert','Finished...\n')
            self.t.config(state=DISABLED)
            tkMessageBox.showinfo("Pecker", "Sending Completed!")
            #回復Send按鈕
            self.send.config(state=ACTIVE)
            #清空訊息框
            self.t.config(state=NORMAL)
            self.t.delete('1.0',END)
            self.t.config(state=DISABLED)
            #進度條歸零
            self.progress["value"] = 0
            self.nowstep = 0

    def checkqueue(self):
        while self.queue.qsize():
            try:
                #將指令印在訊息框上
                msg = self.queue.get(0)
                self.t.config(state=NORMAL)
                self.t.insert(END, msg+'\n')
                self.t.config(state=DISABLED)
                self.t.see(END)
                #進度條更新
                self.nowstep += 1
                self.progress["value"] = self.nowstep
            except queue.Empty:
                pass
    def pauseEvent(self):
        # self.thread.pause()
        # self.pauseflag = True
        self.event.set()
        self.pause.config(state=DISABLED)
        self.moveon.config(state=ACTIVE)

    def resumeEvent(self):
        # self.thread.resume()
        # self.pauseflag = False
        self.event.wait()
        self.pause.config(state=ACTIVE)
        self.moveon.config(state=DISABLED)

class ThreadedClient(threading.Thread):

    def __init__(self, queue, step, serv):
        threading.Thread.__init__(self)
        self.queue = queue
        self.step = step
    def run(self):
        gcode = open('gcode/cathy.gcode','r')
        if self.step.isOpen():
           
            for line in gcode:
                l = line.strip()
                if l.startswith('Z'):
                    continue
                    # pen = l.split('Z')[1]
                    # self.step.write('G4 P1\n')
                    # grbl_out = self.step.readline()
                    # msg = l + ':' + grbl_out.strip()
                    # self.queue.put(msg)
                    # # print l + ':' + grbl_out.strip()
                            
                    # self.serv.write(pen+'\n')
                    # self.step.write('G4 P1\n')
                    # grbl_out = self.step.readline()
                    # msg = l + ':' + grbl_out.strip()
                    # self.queue.put(msg)
                    # # print l + ':' + grbl_out.strip()
                else:
                    self.step.write(l+'\n')
                    grbl_out = self.step.readline()
                    # print l + ':' + grbl_out.strip()
                    msg = l + ':' + grbl_out.strip()
                    self.queue.put(msg)
            gcode.close()
            self.step.close()
            # self.serv.close()
#==========主畫面==========#
if __name__ == '__main__':  
    #==========開啟使用者介面==========#
    def on_closing():
        if tkMessageBox.askokcancel("Pecker", "你確定要離開Pecker嗎?"):
            if app.step.isOpen():
                app.step.close()
            if app.serv.isOpen():
                app.serv.close()
            root.destroy()
    root = Tk()
    app = GUI(root)
    root.title('Pecker')
    # root.resizable(0,0)
    root.geometry('500x650+20+10')
    root.configure(background='#344253')
    root.iconbitmap(default='img/icon.ico')
    root.protocol("WM_DELETE_WINDOW", on_closing)  
    root.mainloop()
    #==========開啟使用者介面==========#