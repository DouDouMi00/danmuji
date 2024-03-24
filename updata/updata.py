# -*- coding: utf-8 -*-
import wx
from pathlib import Path
from os import system, mkdir
from requests import get
from hashlib import md5
from base64 import b64encode
from json import loads, load
from packaging.version import parse
from send2trash import send2trash
from winreg import OpenKey, HKEY_LOCAL_MACHINE, QueryValueEx
from threading import Thread


def update_ui(TextCtrl, text):
    TextCtrl.SetValue(text)
    TextCtrl.SetName("文本框")
    TextCtrl.SetToolTip(wx.ToolTip(text))
    TextCtrl.SetFocus()


class AccessibleFrame(wx.Frame):
    def __init__(self, parent, title):
        super(AccessibleFrame, self).__init__(parent, title=title)
        # 获取屏幕宽高
        self.screen_width, self.screen_height = wx.GetDisplaySize()
        self.SetSize(self.screen_width // 2, self.screen_height // 2)
        self.Centre()
        # 创建一个面板
        panel = wx.Panel(self)

        # 文本框字体大小
        self.TextCtrl = wx.TextCtrl(
            panel,
            value="弹幕机更新程序",
            style=wx.TE_READONLY | wx.TE_MULTILINE,
            id=wx.ID_ANY,
        )
        self.TextCtrl.SetFont(wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.NORMAL))
        self.TextCtrl.SetName("文本框")
        self.TextCtrl.SetToolTip(wx.ToolTip("弹幕机更新程序"))
        self.TextCtrl.SetFocus()

        # 创建并设置第一个按钮的标签和访问键
        self.button1 = wx.Button(panel, label="检查更新", id=wx.ID_ANY)
        self.button1.SetName("按钮")  # 设置按钮的名称以增强可访问性
        self.button1.SetToolTip(wx.ToolTip("检查更新"))

        # 将按钮布局到面板上
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.TextCtrl, 1, wx.ALL | wx.EXPAND, 10)
        sizer.Add(self.button1, 0, wx.ALL | wx.CENTER, 10)

        panel.SetSizer(sizer)

        self.Bind(wx.EVT_BUTTON, self.on_start_async, self.button1)

    def get_updata_config(self, event):
        self.button1.Enable(False)
        with open("config.updata.json", "r", encoding="utf-8") as file:
            updata_config = load(file)
        return updata_config

    # 检测弹幕机安装状态
    def DMJ_InstStatCheck(self, event):
        self.button1.Enable(False)
        try:
            with OpenKey(
                HKEY_LOCAL_MACHINE,
                r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\企鹅弹幕机",
            ) as reg:
                DDM_VERSION = QueryValueEx(reg, "DisplayVersion")
                wx.CallAfter(update_ui, self.TextCtrl, f"当前版本：{DDM_VERSION[0]}")
            return DDM_VERSION
        except:
            raise Exception("弹幕机未安装")

    def get_latest_tag(self, event, updata_url: str, headers: dict = None) -> tuple:
        self.button1.Enable(False)
        try:
            data = loads(get(updata_url, headers=headers).text)
            latest_tag = data["name"]
            latest_tag_body = data["body"]
            return latest_tag, latest_tag_body
        except:
            raise Exception("获取最新版本信息失败！")

    def get_download_info(self, event, url: str, headers: dict = None) -> list:
        self.button1.Enable(False)
        try:
            response = get(url, headers=headers, stream=True)
            file_size = int(response.headers.get("content-length", 0))
            dl_content_md5 = str(response.headers.get("content-md5", ""))
            return file_size, dl_content_md5
        except Exception as e:
            raise Exception(f"获取下载信息失败：{e}")

    def content_md5(self, event, path: str) -> bool:
        try:
            with open(Path(path), "rb") as f:
                return b64encode(md5(f.read()).digest()).decode("utf-8")
        except Exception as e:
            wx.CallAfter(update_ui, self.TextCtrl, f"打开文件失败：{str(e)}")
            return False

    def download_file(
        self, event, url: str, install_exe_path: str, headers: dict = None
    ) -> bool:
        self.button1.Enable(False)
        try:
            wx.CallAfter(update_ui, self.TextCtrl, "正在下载...")
            response = get(url, headers=headers, stream=True)
            if response.status_code == 200:
                file_size = int(response.headers.get("content-length", 0))
                chunk_size = 0
                with open(install_exe_path, "wb") as file:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            file.write(chunk)
                            chunk_size += len(chunk)
                        downloaded_percentage = (chunk_size / file_size) * 100
                        total_size_mb = file_size / (1024 * 1024)
                        text = f"已下载：{downloaded_percentage:.2f}%，总大小：{total_size_mb:.2f}MB"
                        wx.CallAfter(self.SetTitle, f"弹幕机更新{text}")
                        wx.CallAfter(update_ui, self.TextCtrl, text)
                wx.CallAfter(
                    update_ui, self.TextCtrl, f"下载完成！文件在{install_exe_path}"
                )
        except Exception as e:
            wx.CallAfter(update_ui, self.TextCtrl, f"下载失败：{e}")
            return False

    def run_update(self, event, InstallExePath: str):
        self.button1.Enable(False)
        wx.CallAfter(update_ui, self.TextCtrl, f"安装文件：{InstallExePath}")
        safe_path = Path(InstallExePath).resolve(strict=True)
        if system(safe_path) == 0:
            wx.CallAfter(update_ui, self.TextCtrl, "更新完成！")
            send2trash(InstallExePath)
        else:
            raise Exception("更新失败")

    def handleUpdateFailure(self, e):
        wx.CallAfter(update_ui, self.TextCtrl, f"更新失败：{e}")
        self.button1.SetLabel("重新下载")
        wx.CallAfter(self.SetTitle, "弹幕机更新程序")
        self.button1.SetName("按钮，更新失败点击按钮重新下载")
        self.button1.SetToolTip(wx.ToolTip("更新失败点击重新下载"))
        self.button1.Enable(True)

    def on_start_async(self, event):
        self.button1.Enable(False)
        thread = Thread(target=self.mian)
        thread.start()

    def on_start_async2(self, event):
        self.button1.Enable(False)
        thread2 = Thread(target=self.mian2)
        thread2.start()

    def mian2(self):
        try:
            if Path.exists(self.install_exe_path):
                file_size, dl_content_md5 = self.get_download_info(
                    self, self.download_url, self.headers
                )
                if self.content_md5(self, self.install_exe_path) == dl_content_md5:
                    wx.CallAfter(update_ui, self.TextCtrl, "文件MD5值一致,开始更新")
                    self.run_update(self, self.install_exe_path)
                else:
                    wx.CallAfter(update_ui, self.TextCtrl, "文件已损坏，重新下载！")
                    send2trash(self.install_exe_path)
                    self.download_file(
                        self, self.download_url, self.install_exe_path, self.headers
                    )
            else:
                wx.CallAfter(update_ui, self.TextCtrl, "文件不存在，重新下载！")
                self.download_file(
                    self, self.download_url, self.install_exe_path, self.headers
                )
        except Exception as e:
            self.handleUpdateFailure(e)

    def mian(self):
        try:
            updata_config = self.get_updata_config(self)
            DDM_VERSION = self.DMJ_InstStatCheck(self)

            self.headers = updata_config["Upgrade"]["headers"]
            updata_url = updata_config["Upgrade"]["updata_url"]
            latest_tag, latest_tag_body = self.get_latest_tag(
                self, updata_url, self.headers
            )

            download_Temp_path = (
                Path.expanduser("~") + "\\AppData\\Local\\Temp\\qedmj\\"
            )
            download_name = updata_config["Upgrade"]["download_name"] % latest_tag
            self.install_exe_path = download_Temp_path + download_name
            self.download_url = updata_config["Upgrade"]["download_url"] % download_name

            if not Path.exists(download_Temp_path):
                mkdir(download_Temp_path)

            if parse(DDM_VERSION[0]) < parse(latest_tag) and not ("beta" in latest_tag):
                wx.CallAfter(
                    update_ui,
                    self.TextCtrl,
                    f"有最新版本：{latest_tag}\n更新内容：{latest_tag_body}\n下载地址：{self.download_url}\n",
                )
                # 设置按钮名称确认更新
                self.button1.SetLabel("确认下载")
                self.Bind(wx.EVT_BUTTON, self.on_start_async2, self.button1)
                self.button1.Enable(True)
            else:
                wx.CallAfter(update_ui, self.TextCtrl, "当前版本为最新版本，无需更新！")
        except Exception as e:
            self.handleUpdateFailure(e)


if __name__ == "__main__":
    app = wx.App()
    frame = AccessibleFrame(None, "弹幕机更新程序")
    frame.Show(True)
    app.MainLoop()
