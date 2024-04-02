# -*- coding: utf-8 -*-  
import wx
from os import path,system,mkdir
from requests import get
from hashlib import md5
from base64 import b64encode
from json import loads ,load
from packaging.version import parse
from send2trash import send2trash
from winreg import OpenKey,HKEY_LOCAL_MACHINE,QueryValueEx
import threading


class AccessibleFrame(wx.Frame):
    def __init__(self, parent, title):
        super(AccessibleFrame, self).__init__(parent, title=title, size=(800, 500))

        # 创建一个面板
        panel = wx.Panel(self)

        #文本框字体大小
        self.text_ctrl = wx.StaticText(panel, label="弹幕机正在检查更新")
        #设置字体大小
        self.text_ctrl.SetFont(wx.Font(20, wx.DEFAULT, wx.NORMAL, wx.NORMAL))
        self.text_ctrl.SetName("文本框")
        self.text_ctrl.SetToolTip(wx.ToolTip("这是一个文本框"))

        # 创建并设置第一个按钮的标签和访问键
        self.button1 = wx.Button(panel, label="检查更新", id=wx.ID_ANY)
        self.button1.SetName("按钮")  # 设置按钮的名称以增强可访问性
        self.button1.SetToolTip(wx.ToolTip("检查更新"))

        # 将按钮布局到面板上
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.text_ctrl, 0,  10)
        sizer.Add(self.button1, 0, wx.ALL | wx.CENTER, 10)

        panel.SetSizer(sizer)

        self.Bind(wx.EVT_BUTTON, self.mian, self.button1)

    def get_updata_config(self, event):
        self.button1.Enable(False)
        with open('config.updata.json', 'r', encoding='utf-8') as file:
            updata_config = load(file)
        return updata_config

    #检测弹幕机安装状态
    def DMJ_InstStatCheck(self, event):
        self.button1.Enable(False)
        try:  
            with OpenKey(HKEY_LOCAL_MACHINE,r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\企鹅弹幕机") as reg:
                DDM_VERSION=QueryValueEx(reg,'DisplayVersion')
                self.text_ctrl.SetLabel(f"当前版本：{DDM_VERSION[0]}")
                self.text_ctrl.SetFocus()
            return DDM_VERSION
        except:
            self.button1.Enable(True)  
            raise Exception("弹幕机未安装")
            
    def get_latest_tag(self, event,updata_url:str,headers:dict=None)->tuple:
        self.button1.Enable(False)
        try:
            data = loads(get(updata_url, headers=headers).text)
            latest_tag = data['name']
            latest_tag_body = data['body']
            return latest_tag,latest_tag_body
        except:
            self.button1.Enable(True)
            raise Exception("获取最新版本信息失败！")
 
    def get_download_info(self, event,url:str,headers:dict=None,Attempts:int=5)->list:
        self.button1.Enable(False)
        try:
            for i in range(Attempts):
                response = get(url,headers=headers, stream=True)
                file_size = int(response.headers.get('content-length', 0))
                dl_content_md5 = str(response.headers.get('content-md5', ''))
                self.text_ctrl.SetLabel(f"最新版本文件大小：{file_size / 1024 / 1024}MB\n最新版本文件md5:{dl_content_md5}")
                self.text_ctrl.SetFocus()
                response.close()
                break
            return [file_size,dl_content_md5]
        except Exception as e:
            self.button1.Enable(True)
            raise Exception("获取下载信息失败：{e}")

    def content_md5(self, event,path:str)->bool:
        self.button1.Enable(False)
        with open(path, 'rb') as f:
            return b64encode(md5(f.read()).digest()).decode("utf-8")

    def download_file(self, event,url:str,download_Temp_path:str,install_exe_path:str,headers:dict=None,Attempts:int=5)->bool:
        try:
            for i in range(Attempts):
                self.text_ctrl.SetLabel("正在下载...")
                self.text_ctrl.SetFocus()
                response = get(url,headers=headers, stream=True)
                if response.status_code == 200:
                    #创建文件夹
                    if not path.exists(download_Temp_path):
                        mkdir(download_Temp_path)
                    with open(install_exe_path, "wb") as file:
                        for chunk in response.iter_content(chunk_size=1024):
                            if chunk:
                                file.write(chunk)
                    response.close()
                    self.text_ctrl.SetLabel(f'下载完成！文件在{path}')
                    self.text_ctrl.SetFocus()
                    break
        except Exception as e:
            self.button1.Enable(True)
            raise Exception(f"下载失败：{e}")

    def run_update(self, event,InstallExePath:str):
        self.text_ctrl.SetLabel(f"安装文件：{InstallExePath}")
        self.text_ctrl.SetFocus()
        if system(path.abspath(InstallExePath)) == 0:
            self.text_ctrl.SetLabel("更新完成！")
            self.text_ctrl.SetFocus()
            send2trash(InstallExePath)
        else:
            self.button1.Enable(True)
            raise Exception("更新失败")

    def mian(self,event):
        try:
            updata_config = self.get_updata_config(self)
            DDM_VERSION = self.DMJ_InstStatCheck(self)
            
            headers = updata_config["Upgrade"]["headers"]
            updata_url = updata_config["Upgrade"]["updata_url"]
            latest_tag,latest_tag_body = self.get_latest_tag(self,updata_url,headers)
            

            download_Temp_path = path.expanduser('~') + '\\AppData\\Local\\Temp\\qedmj\\'
            download_name = updata_config["Upgrade"]["download_name"]%latest_tag
            install_exe_path = download_Temp_path + download_name
            download_url = updata_config["Upgrade"]["download_url"]%download_name

            if parse(DDM_VERSION[0]) < parse(latest_tag) and not ('beta' in latest_tag):
                self.text_ctrl.SetLabel(f"有最新版本：{latest_tag}\n更新内容：{latest_tag_body}\n下载地址：{download_url}")
                self.text_ctrl.SetFocus()
                if path.exists(install_exe_path):
                    if self.content_md5(self,install_exe_path)==self.get_download_info(self,download_url,headers)[1]:
                        self.text_ctrl.SetLabel("文件MD5值一致,开始更新")
                        self.text_ctrl.SetFocus()
                        self.run_update(self,install_exe_path)
                    else:
                        self.text_ctrl.SetLabel("文件已损坏，重新下载！")
                        self.text_ctrl.SetFocus()
                        send2trash(install_exe_path)
                        new_thread = threading.Thread(target=self.download_file,
                                                      args=(self,download_url, download_Temp_path,install_exe_path, headers))
                        new_thread.start()
                else:
                    self.text_ctrl.SetLabel("文件不存在，重新下载！")
                    self.text_ctrl.SetFocus()
                    new_thread = threading.Thread(target=self.download_file,
                                                  args=(self,download_url, download_Temp_path,install_exe_path, headers))
                    new_thread.start()
            else:
                self.text_ctrl.SetLabel("当前版本为最新版本，无需更新！")
                self.text_ctrl.SetFocus()
        except Exception as e:
            self.text_ctrl.SetLabel(f"更新失败：{e}")
            self.text_ctrl.SetFocus()
            self.button1.Enable(True)

if __name__ == "__main__":
    app = wx.App()
    frame = AccessibleFrame(None, "弹幕姬更新程序")
    frame.Show(True)
    app.MainLoop()