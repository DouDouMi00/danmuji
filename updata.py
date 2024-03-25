# -*- coding: utf-8 -*-  
from os import path,system
from requests import get
from hashlib import md5
from base64 import b64encode
from json import loads
from packaging.version import parse
from send2trash import send2trash
'''
垃圾回收--未完成
安装异常处理--未完成
版本号判断--未完成
配置文件--未完成
'''
#计算机\HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\企鹅弹幕机
# try:  
#     reg=winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\企鹅弹幕机")
#     Version=winreg.QueryValueEx(reg,'DisplayVersion')
# finally:  
#     reg.Close()

headers = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}
dmj_version = 'v1.4.1'
updata_url= 'https://api.github.com/repos/DouDouMi00/danmuji/releases/latest'
download_Temp_path = './temp/'
data = loads(get(updata_url,headers=headers).text)
latest_tag = data['name']
latest_tag_body = data['body']
download_name = f'qedanmuji_Installer_{latest_tag}.exe'
install_exe_path = download_Temp_path + download_name
download_url = f"https://github.com/DouDouMi00/danmuji/releases/download/latest/{download_name}"

def get_download_info(url:str,headers:dict=None)->list:
    try:
        response = get(url,headers=headers, stream=True)
        file_size = int(response.headers.get('content-length', 0))
        dl_content_md5 = str(response.headers.get('content-md5', ''))
        print(f"最新版本文件大小：{file_size / 1024 / 1024}MB\n最新版本文件md5:{dl_content_md5}")
        response.close()
        return [file_size,dl_content_md5]
    except Exception as e:
        print(f"获取下载文件信息失败：{e}")
        exit()

def content_md5(path:str)->bool:
    with open(path, 'rb') as f:
        return b64encode(md5(f.read()).digest()).decode("utf-8")

def download_file(url:str,path:str,headers:dict=None)->bool:
    try:
        print("正在下载...")
        response = get(url,headers=headers, stream=True)
        if response.status_code == 200:
            with open(path, "wb") as file:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        file.write(chunk)
            response.close()
            print(f'下载完成！文件在{install_exe_path}')
            print("下载完成！将在下次弹幕机重启时弹出更新窗口！")
            return True
    except Exception as e:
        print(f"下载失败：{e}")
        return False

def run_update(InstallExePath:str):
    print(f"安装文件：{InstallExePath}")
    system(path.abspath(InstallExePath))

if parse(dmj_version) < parse(latest_tag) and not ('beta' in latest_tag):
    print(f"有最新版本：{latest_tag}\n更新内容：{latest_tag_body}\n下载地址：{download_url}")
    if path.exists(install_exe_path):
        if content_md5(install_exe_path)==get_download_info(download_url,headers)[1]:
            print("文件MD5值一致,开始更新")
            run_update(install_exe_path)
        else:
            print("文件已损坏，重新下载！")
            send2trash(install_exe_path)
            download_file(download_url,install_exe_path,headers)
    else:
        print("文件不存在，重新下载！")
        download_file(download_url,install_exe_path,headers)
else:
    print("当前版本为最新版本，无需更新！")