# coding=utf-8
import os
import shutil
import re
import time
import tkMessageBox

__author__ = 'tiger'

#AndroidManifest.xml中配置频道的meta-data名称
channel_meta_data_name = 'UMENG_CHANNEL'


def genTime():
    return 'apks_%s' % time.strftime('%Y%m%d%H%M', time.localtime(time.time()))


class PackChannelApk:
    def __init__(self, setupdir, ks, kspass, ksalia, filename, outputfiledir, clist):
        self.keystore = './' + ks
        self.storepass = kspass
        self.alianame = ksalia
        self.setupdir = setupdir
        self.filename = filename
        self.channellist = clist
        self.basename = filename.split('.apk')[0]
        self.apkdir = '%s%s' % (outputfiledir, genTime())
        print('[Pack] PackChannelApk __init__')
        print('[Pack] keystore_name : %s' % self.keystore)
        print('[Pack] keystore_pass : %s' % self.storepass)
        print('[Pack] keystore_alia : %s' % self.alianame)
        print('[Pack] apk_name : %s' % self.filename)
        print('[Pack] setupdir : %s' % self.setupdir)
        print('[Pack] apkdir : %s' % self.apkdir)


    def start(self):
        print('--------------Start Gen Apk-------------------')

        # 删除旧文件
        # if os.path.exists(apks_dir):
        #     shutil.rmtree(apks_dir)

        # 解压apk到temp目录
        cmd_extract = r'java -jar %s\apktool\apktool_2.0.2.jar d -f -s %s\%s -o %s\temp' % (self.setupdir, self.setupdir, self.filename, self.setupdir)
        os.system(cmd_extract)

        # 备份AndroidManifest.xml
        if os.path.exists('%s\AndroidManifest.xml' % self.setupdir):
            os.remove('%s\AndroidManifest.xml' % self.setupdir)
        manifest_path = r'%s\temp\AndroidManifest.xml' % self.setupdir
        shutil.copyfile(manifest_path, '%s\AndroidManifest.xml' % self.setupdir)

        # 生成渠道包
        for channel in self.channellist:
            print('[Gen Apk] channel : %s' % channel)
            self.modify_channel(channel)

        # 删除无用文件
        if os.path.exists('%s\temp' % self.setupdir):
            shutil.rmtree('%s\temp' % self.setupdir)
        if os.path.exists('%s\AndroidManifest.xml' % self.setupdir):
            os.remove('%s\AndroidManifest.xml' % self.setupdir)

        flag = tkMessageBox.askokcancel("成功", "打包成功!")
        if flag:
            os.system("explorer.exe %s" % self.apkdir)
        print('--------------Done-------------------')


    # 生成渠道包
    def modify_channel(self, channel):
        # 修改渠道
        tempxml = ''
        f = open('%s\AndroidManifest.xml' % self.setupdir)
        for line in f:
            if line.find(channel_meta_data_name) > 0:
                find = re.search(r'android:value=".*"', line, re.M | re.I)
                if find:
                    line = re.sub(r'android:value=".*"', r'android:value="%s"' % channel, line)
                    print('[Gen Apk] modify channel id to %s' % channel)
                else:
                    print('[Gen Apk] modify channel id failed, stop pack!')
                    f.close()
                    return
            tempxml += line
        f.close()

        # 将修改渠道号后的数据写入manifest
        output = open('./temp/AndroidManifest.xml', mode='w+')
        output.write(tempxml)
        output.close()

        # 生成目标渠道的未压缩未签名apk
        print('[Gen Apk] Start gen unsigned apk.')
        unsign_apk = r'%s/%s_%s_unsigned.apk' % (self.apkdir, self.basename, channel)
        cmd_path = r'java -jar apktool/apktool_2.0.2.jar b temp -o %s' % unsign_apk
        os.system(cmd_path)

        # 生成目标渠道的未压缩的签名apk
        unaligned_signed_apk = r'%s/%s_%s_signed_unaligned.apk' % (self.apkdir, self.basename, channel)

        # 此签名方法在一些机型上面会报错：
        # http://stackoverflow.com/questions/2914105/android-what-is-install-parse-failed-no-certificates-error
        # cmd_sign = r'jarsigner -verbose -keystore %s -storepass %s -signedjar %s %s %s' \
        #            % (keystore, storepass, unaligned_signed_apk, unsign_apk, alianame)

        print('[Gen Apk] Start gen signed apk.')
        cmd_sign = r'jarsigner -digestalg SHA1 -sigalg MD5withRSA -verbose -keystore %s -storepass %s -signedjar %s %s %s' \
                   % (self.keystore, self.storepass, unaligned_signed_apk, unsign_apk, self.alianame)
        print('[Gen Apk] cmd_sign : ' + cmd_sign)
        os.system(cmd_sign)

        # 生成目标渠道签名并压缩后的apk
        print('[Gen Apk] Start gen aligned apk.')
        aligned_signed_apk = r'%s/%s_%s.apk' % (self.apkdir, self.basename, channel)
        cmd_align = r'%s\zipalign -f -v 4 %s %s' % (self.setupdir, unaligned_signed_apk, aligned_signed_apk)
        print('[Gen Apk] cmd_align : ' + cmd_align)
        os.system(cmd_align)

        # 删除无用的临时文件
        os.remove(unsign_apk)
        os.remove(unaligned_signed_apk)
        # 删除copy的原apk文件
        os.remove(this.filename)
