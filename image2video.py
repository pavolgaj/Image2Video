#!/usr/bin/python
import sys,shutil,os
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog
from subprocess import Popen, PIPE

def get_codecs():
    process=Popen('ffmpeg -hide_banner -codecs', stderr=PIPE,stdout=PIPE, shell=True)
    (output, err)=process.communicate()
    output=str(output.decode())

    if len(output)==0:
        tk.messagebox.showerror(title='Error',message='ffmpeg not installed!')
        return

    codecs=[]
    for l in output.splitlines():
        if '=' in l: continue
        tmp=l.strip().split()
        if 'V' in tmp[0] and 'E' in tmp[0]: codecs.append(tmp[1])
    return sorted(codecs)

def get_formats():
    process=Popen('ffmpeg -hide_banner -formats', stderr=PIPE,stdout=PIPE, shell=True)
    (output, err)=process.communicate()
    output=str(output.decode())

    if len(output)==0:
        print('ffmpeg not installed!')
        return

    formats=[]
    formats1={}
    for l in output.splitlines():
        if '=' in l: continue
        tmp=l.strip().split()
        if 'E' in tmp[0]:
            process=Popen('ffmpeg -hide_banner -h muxer='+tmp[1], stderr=PIPE,stdout=PIPE, shell=True)
            (out, err)=process.communicate()
            out=str(out.decode()).splitlines()
            if len(out)<3: continue
            if 'Mime type: video' in out[2]:
                ext=out[1].strip().split()[-1].replace('.','')
                if not ext.split(',')[0] in formats:
                    formats.append(ext.split(',')[0])
                    formats1[out[0][out[0].find('[')+1:out[0].find(']')].strip()]=ext

    return formats1


def load():
    files = filedialog.askopenfilenames(parent=root, title='Load images',multiple=True,filetypes=[("JPG images", ".jpg .JPG .jpeg .JPEG"),("PNG images", ".png .PNG"),("TIFF images", ".tiff .TIFF .tif .TIFF"),("All files", "*.*")])
    if len(files)==0: return

    f=open('list.tmp','w')
    for name in sorted(files):
        f.write("file '"+name+"'\n")
    f.close()

    Button2.config(state=tk.NORMAL)
    Button3.config(state=tk.NORMAL)

def loadL():
    lst = filedialog.askopenfilename(parent=root, title='Load list',filetypes=[("Text files", ".txt .TXT .lst .LST"),("All files", "*.*")])
    if len(lst)==0: return

    shutil.copy(lst,'list.tmp')

    Button2.config(state=tk.NORMAL)
    Button3.config(state=tk.NORMAL)

def saveL():
    lst = filedialog.asksaveasfilename(parent=root, title='Save list',filetypes=[("Text files", ".txt .TXT .lst .LST"),("All files", "*.*")])
    if len(lst)==0: return

    shutil.copy('list.tmp',lst)


def save():
    #ffmpeg -f concat -i input.txt -r FPS -vcodec CODEC  -s WIDTHxHEIGHT  output.mp4
    if sys.platform == "win32":
        out = filedialog.asksaveasfilename(parent=root, title='Save video',filetypes=[("MP4 videos", ".mp4 .MP4"),("AVI videos", ".avi .AVI"),("MPEG videos", ".mpg .MPG .mpeg .MPEG"),("FLV videos", ".flv .FLV"),("All files", "*.*")],defaultextension='.mp4')
    else:
        out = filedialog.asksaveasfilename(parent=root, title='Save video',filetypes=[("MP4 videos", ".mp4 .MP4"),("AVI videos", ".avi .AVI"),("MPEG videos", ".mpg .MPG .mpeg .MPEG"),("FLV videos", ".flv .FLV"),("All files", "*.*")])

    if len(out)==0: return

    cmd='ffmpeg -reinit_filter 0 -hide_banner -y -f concat -safe 0 -r '+str(fpsVar.get())+' -i list.tmp -r '+str(fpsVar.get())+' -vcodec '+codecsVar.get()
    if 'width' in sizeVar.get(): cmd+=' -vf scale='+sizeVar.get().split()[1]+':-1:flags=lanczos'
    elif 'height' in sizeVar.get(): cmd+=' -vf scale=-1:'+sizeVar.get().split()[1]+':flags=lanczos'
    elif not sizeVar.get()=='original': cmd+=' -vf scale='+sizeVar.get()+':flags=lanczos'
    if codecsVar.get()=='h264': cmd+=' -crf 15'
    cmd+=' "'+out+'"'

    #print(cmd)
    process=Popen(cmd, shell=True)
    process.communicate()

    tk.messagebox.showinfo(title='Image2Video',message='Video creation finished!')

def close():
    global root
    if os.path.isfile('list.tmp'): os.remove('list.tmp')
    root.destroy()

process=Popen('ffmpeg -h', stderr=PIPE,stdout=PIPE, shell=True)
(output, err)=process.communicate()
output=str(output.decode())

if len(output)==0:
    tk.messagebox.showerror(title='Error',message='ffmpeg not installed!')
    sys.exit()

root = tk.Tk()
root.protocol( 'WM_DELETE_WINDOW', close)
# Creates a toplevel widget.

root.geometry("240x280")
root.resizable(0,0)
root.title("Image2Video")

fpsVar = tk.DoubleVar()
codecsVar = tk.StringVar()
sizeVar = tk.StringVar()

Button1 = tk.Button(root)
Button1.place(x=40, y=10, height=33, width=160)
Button1.configure(command=load)
Button1.configure(text='''Load Images''')

Button3 = tk.Button(root)
Button3.place(x=130, y=60, height=33, width=100)
Button3.configure(command=saveL)
Button3.configure(text='''Save List''')
Button3.config(state=tk.DISABLED)

Button4 = tk.Button(root)
Button4.place(x=20, y=60, height=33, width=100)
Button4.configure(command=loadL)
Button4.configure(text='''Load List''')

Label1 = tk.Label(root)
Label1.place(x=20, y=120, height=21, width=50)
Label1.configure(text='''FPS''')

Spinbox1 = tk.Spinbox(root, from_=1.0, to=100.0)
Spinbox1.place(x=90, y=120, height=23, width=120)
Spinbox1.configure(textvariable=fpsVar)
value_list = ['10','15','20','25','30','50']
Spinbox1.configure(values=value_list)
fpsVar.set(15)


Label2 = tk.Label(root)
Label2.place(x=20, y=160, height=21, width=50)
Label2.configure(text='''Codecs''')

TCombobox1 = ttk.Combobox(root)
TCombobox1.place(x=90, y=160, height=21, width=120)
#value_list = ['mpeg4','h264',]
TCombobox1.configure(state="readonly")
value_list=get_codecs()
TCombobox1.configure(values=value_list)
TCombobox1.configure(textvariable=codecsVar)
if 'h264' in value_list: codecsVar.set('h264')
elif 'mpeg4' in value_list: codecsVar.set('mpeg4')
else: codecsVar.set('rawvideo')

Label3 = tk.Label(root)
Label3.place(x=20, y=200, height=21, width=50)
Label3.configure(text='''Size''')

TCombobox2 = ttk.Combobox(root)
TCombobox2.place(x=90, y=200, height=21, width=120)
value_list = ['720x480','720x576','352x240','352x288','640x480','768x576','352x240','352x240','128x96','176x144','352x288','704x576','1408x1152','160x120','320x240','640x480','800x600','1024x768','1600x1200','2048x1536','1280x1024','2560x2048','5120x4096','852x480','1366x768','1600x1024','1920x1200','2560x1600','3200x2048','3840x2400','6400x4096','7680x4800','320x200','640x350','852x480','1280x720','1920x1080','2048x1080','1998x1080','2048x858','4096x2160','3996x2160','4096x1716','640x360','240x160','400x240','432x240','480x320','960x540','2048x1080','4096x2160','3840x2160','7680x4320','1920x1280','1280x854','1620x1080','1080x720']

TCombobox2.configure(state="readonly")
TCombobox2.configure(values=['original','height 720','height 1080','width 1280','width 1920']+sorted(value_list,key=lambda x: float(x.split('x')[0]+'.'+x.split('x')[1].rjust(4,'0'))))
TCombobox2.configure(textvariable=sizeVar)
sizeVar.set('original')

Button2 = tk.Button(root)
Button2.place(x=40, y=240, height=33, width=160)
Button2.configure(command=save)
Button2.configure(text='''Save Video''')
Button2.config(state=tk.DISABLED)

root.mainloop()
