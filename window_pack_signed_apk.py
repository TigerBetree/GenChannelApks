# coding=UTF-8
__author__ = 'tiger'

try:
    # for Python2
    from Tkinter import *  ## notice capitalized T in Tkinter
    from FileDialog import *
    from tkFileDialog import askopenfilename
    import tkMessageBox
except ImportError:
    # for Python3
    from tkinter import *  ## notice here too
    from tkinter.filedialog import *
    import tkinter.messagebox

import shutil
import os

from pack_signed_apk_script import *

root = Tk()
root.title('Android渠道打包工具')
root.resizable(True, True)


class MyWindows:

    def __init__(self, window):
        self.setupdir = os.path.abspath(os.path.curdir)
        print('[init] setup dir : %s' % self.setupdir)

        Label(window, text='  选择keystore文件: ').grid(sticky=E)
        self.keystore_file_name = StringVar()
        self.keystore_file_name.set('  选择keystore  ')
        self.keystorefile = Button(window, textvariable=self.keystore_file_name, command=self.keystore_select_dialog)
        self.keystorefile.grid(row=0, column=1, sticky=W)

        Label(window, text='  keystore密码: ').grid(sticky=E)
        self.keystore_pass = Entry(window)
        self.keystore_pass.grid(row=1, column=1, sticky=EW)

        Label(window, text='  keystore Alia 名称: ').grid(sticky=E)
        self.keystore_alia = Entry(window)
        self.keystore_alia.grid(row=2, column=1, sticky=EW)

        Label(window, text='  选择apk文件: ').grid(sticky=E)
        self.apk_file_name = StringVar()
        self.apk_file_name.set('  选择apk  ')
        self.targetfile = Button(window, textvariable=self.apk_file_name, command=self.apk_select_dialog)
        self.targetfile.grid(row=3, column=1, sticky=W)

        Label(window, text='渠道号: ').grid(sticky=E)
        self.newchannelname = Entry(window)
        self.newchannelname.grid(row=4, column=1, sticky=EW)
        btn = Button(window, text='  +  ', command=self.insert)
        btn.grid(row=4, column=2, sticky=W)

        Label(window, text='渠道列表: ').grid(sticky=NE)
        self.channel_list_box = Listbox(window)
        self.channel_list_box.grid(row=5, column=1, sticky=EW)

        btn = Button(window, text='  开始打包  ', command=self.start)
        btn.grid(row=6, column=1)

    def keystore_select_dialog(self):
        targetfilepath = askopenfilename()
        targetfilepath = os.path.abspath(targetfilepath)
        print('[KeystoreSelect] FilePath : %s' % targetfilepath)

        print('[KeystoreSelect] os.sep : %s' % os.sep)
        pathlist = targetfilepath.split(os.sep)
        print('[KeystoreSelect] pathlist : ')
        print(pathlist)

        self.keystorefilename = pathlist[len(pathlist) - 1]

        print('[KeystoreSelect] FileName : %s' % self.keystorefilename)

        self.keysotefiledir = targetfilepath.replace(self.keystorefilename, '')

        print('[KeystoreSelect] FileDir : %s' % self.keysotefiledir)

        self.keystore_file_name.set(self.keystorefilename)

        if os.path.isfile('%s\%s' % (self.setupdir, self.keystorefilename)):
            os.remove('%s\%s' % (self.setupdir, self.keystorefilename))
            print('[KeystoreSelect] remove existed file.')
        else:
            print('[KeystoreSelect] no existed file.')

        targetfile = r'%s' % targetfilepath
        print('[KeystoreSelect] TargetFile : %s' % targetfile)
        shutil.copy(targetfile, '%s\%s' % (self.setupdir, self.keystorefilename))

    def apk_select_dialog(self):
        targetfilepath = askopenfilename()
        if not targetfilepath.endswith(r'.apk'):
            tkMessageBox.showinfo("Error", "请选择apk文件！")
            return

        targetfilepath = os.path.abspath(targetfilepath)
        print('[ApkSelect] FilePath : %s' % targetfilepath)

        print('[ApkSelect] os.sep : %s' % os.sep)
        pathlist = targetfilepath.split(os.sep)
        print('[ApkSelect] pathlist : ')
        print(pathlist)

        self.apkfilename = pathlist[len(pathlist) - 1]

        print('[ApkSelect] FileName : %s' % self.apkfilename)

        self.apkfiledir = targetfilepath.replace(self.apkfilename, '')

        print('[ApkSelect] FileDir : %s' % self.apkfiledir)

        self.apk_file_name.set(self.apkfilename)

        if os.path.isfile('%s\%s' % (self.setupdir, self.apkfilename)):
            os.remove('%s\%s' % (self.setupdir, self.apkfilename))
            print('[FileSelect] remove existed file.')
        else:
            print('[FileSelect] no existed file.')

        targetfile = r'%s' % targetfilepath
        print('[FileSelect] TargetFile : %s' % targetfile)
        shutil.copy(targetfile, '%s\%s' % (self.setupdir, self.apkfilename))

    def insert(self):
        channelid = self.newchannelname.get().rstrip()
        if len(channelid) == 0:
            return
        self.channel_list_box.insert(0, channelid)
        self.newchannelname.delete(0, 'end')
        self.newchannelname.focus()

    def start(self):
        keystorepass = self.keystore_pass.get().rstrip()
        keystorealia = self.keystore_alia.get().rstrip()

        if len(self.keystorefilename) == 0:
            tkMessageBox.showinfo("Error", "请选择keystore文件！")
            return

        if len(keystorepass) == 0:
            tkMessageBox.showinfo("Error", "请填写keystore密码！")
            return

        if len(keystorealia) == 0:
            tkMessageBox.showinfo("Error", "请选择keystore Alia名称！")
            return

        if len(self.apkfilename) == 0:
            tkMessageBox.showinfo("Error", "请选择apk文件！")
            return

        channellist = []
        for idx in range(self.channel_list_box.size()):
            channellist.insert(idx, self.channel_list_box.get(idx))

        if len(channellist) == 0:
            tkMessageBox.showinfo("Error", "请填写渠道号！")
            return

        s = set(channellist)
        channellist = [i for i in s]
        print("[Channel List] : ")
        print(channellist)

        bca = PackChannelApk(self.setupdir, self.keystorefilename, keystorepass, keystorealia,
                             self.apkfilename, self.apkfiledir, channellist)
        bca.start()


window = MyWindows(root)

root.update()  # update window ,must do
curWidth = root.winfo_reqwidth() + 200  # get current width
curHeight = root.winfo_height() + 5  # get current height
scnWidth, scnHeight = root.maxsize()  # get screen width and height
# now generate configuration information
tmpcnf = '%dx%d+%d+%d' % (curWidth, curHeight, (scnWidth - curWidth) / 2, (scnHeight - curHeight) / 2)
root.geometry(tmpcnf)
root.mainloop()
