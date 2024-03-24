# -*- coding: utf-8 -*-  
from requests import get
import hashlib, base64
from json import loads
from packaging.version import parse
import os
import send2trash

#计算机\HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\企鹅弹幕机
# try:  
#     reg=winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\企鹅弹幕机")
#     Version=winreg.QueryValueEx(reg,'DisplayVersion')
# finally:  
#     reg.Close()

headers = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}
updata_url= 'https://api.github.com/repos/DouDouMi00/danmuji/releases/latest'
download_Temp_path = './temp/'
data = loads(get(updata_url,headers=headers).text)
latest_tag = data['name']
latest_tag_body = data['body']
download_name = f'qedanmuji_Installer_{latest_tag}.exe'
install_exe_path = download_Temp_path + download_name
download_url = f"https://github.com/DouDouMi00/danmuji/releases/download/latest/{download_name}"

def run_update(InstallExePath):
    print(f"安装文件：{InstallExePath}")
    os.system(os.path.abspath(InstallExePath))
    print("安装完成！")

if parse('v1.4.0') < parse(latest_tag):
    print(f"有最新版本：{latest_tag}\n更新内容：{latest_tag_body}\n下载地址：{download_url}")
    try:
        response = get(download_url,headers=headers, stream=True)
        file_size = int(response.headers.get('content-length', 0))
        dl_content_md5 = str(response.headers.get('content-md5', ''))
    except Exception as e:
        print(f"获取文件信息失败：{e}")
        exit()
    print(f"最新版本文件大小：{file_size / 1024 / 1024}MB\n最新版本文件md5:{dl_content_md5}")
    if os.path.exists(install_exe_path):
        with open(install_exe_path, 'rb') as f:
            if base64.b64encode(hashlib.md5(f.read()).digest()).decode("utf-8")==dl_content_md5:
                print("文件MD5值一致,开始更新")
                run_update(install_exe_path)
            else:
                print("文件已损坏，重新下载！")
        send2trash.send2trash(install_exe_path)
    if response.status_code == 200:
        print("正在下载...")
        with open(install_exe_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)
        print(f'下载完成！文件在{install_exe_path}')
    else:
        print("下载失败！")