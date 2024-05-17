from .logger import timeLog
import json, os, appdirs
from pyee import AsyncIOEventEmitter
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from uuid import getnode
from base64 import b64encode
from copy import deepcopy

configEvent = AsyncIOEventEmitter()

def get_machine_code()->str:
    """获取MAC地址"""
    mac_num = ''.join(['{:02x}'.format((getnode() >> ele) & 0xff)
                        for ele in range(0,8*6,8)][::-1])
    return mac_num

# 使用PBKDF2从密码生成密钥，增加安全性
kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,  # AES-256密钥长度
    salt=b'\x85\x06\\E\xbfz\x9f\x92\xf2\x95\xb2FR\xdf\x82\xd5',
    iterations=100000,
    backend=default_backend()
)
derived_key = b64encode(kdf.derive(get_machine_code().encode())).decode()
 
# 创建Fernet对象
fernet = Fernet(derived_key)

# 加密/解密函数，使用Fernet对象
def encrypt_value(value: str):
    return fernet.encrypt(value.encode()).decode()

def decrypt_value(encrypted_value: str):
    return fernet.decrypt(encrypted_value.encode()).decode()

def mergeConfigRecursively(template, raw):
    for key in template:
        if key not in raw:
            raw[key] = template[key]
        elif type(template[key]) == dict:
            mergeConfigRecursively(template[key], raw[key])

configPath = os.path.join(appdirs.user_config_dir('danmuji', 'xqe2011'), './config.json')
os.makedirs(appdirs.user_config_dir('danmuji', 'xqe2011'), exist_ok=True)
# 合并配置文件
jsonConfig = json.load(open(configPath, encoding='utf-8')) if os.path.isfile(configPath) else {}
templateConfig = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../config.template.json'), encoding='utf-8', mode='r'))
mergeConfigRecursively(templateConfig, jsonConfig)
with open(configPath, encoding='utf-8', mode='w') as f:
        json.dump(jsonConfig, f, ensure_ascii=False, indent=4)
# 读取配置后解密特定字段
if jsonConfig["kvdb"]["bili"]["sessdata"]  != "" and len(jsonConfig["kvdb"]["bili"]["sessdata"]) != 222:
    jsonConfig["kvdb"]["bili"]["sessdata"]=decrypt_value(jsonConfig["kvdb"]["bili"]["sessdata"])
if jsonConfig["kvdb"]["bili"]["jct"]  != "" and len(jsonConfig["kvdb"]["bili"]["jct"]) != 32:
    jsonConfig["kvdb"]["bili"]["jct"]=decrypt_value(jsonConfig["kvdb"]["bili"]["jct"])
timeLog(f'[Config] Loaded json config: {json.dumps(jsonConfig, ensure_ascii=False)}')

async def updateJsonConfig(config):
    global jsonConfig
    oldConfig = jsonConfig
    jsonConfig = config
    with open(configPath, encoding='utf-8', mode='w') as f:
        jsonConfigSave = deepcopy(jsonConfig)
        if len(jsonConfigSave["kvdb"]["bili"]["sessdata"]) == 222:
            jsonConfigSave["kvdb"]["bili"]["sessdata"]=encrypt_value(jsonConfigSave["kvdb"]["bili"]["sessdata"])
        if len(jsonConfigSave["kvdb"]["bili"]["jct"]) == 32:
            jsonConfigSave["kvdb"]["bili"]["jct"]=encrypt_value(jsonConfigSave["kvdb"]["bili"]["jct"])
        json.dump(jsonConfigSave, f, ensure_ascii=False, indent=4)
    timeLog(f'[Config] Updated json config: {json.dumps(jsonConfig, ensure_ascii=False)}')
    configEvent.emit('update', oldConfig, jsonConfig)

# 获取并解密配置
def getJsonConfig():
    global jsonConfig
    return jsonConfig