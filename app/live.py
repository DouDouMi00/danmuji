from pyee import AsyncIOEventEmitter
from .config import getJsonConfig, updateJsonConfig
from .logger import timeLog
from .tool import isAllCharactersEmoji
from blivedm.blivedm import BLiveClient, BaseHandler
from blivedm.blivedm.models.web import HeartbeatMessage
import aiohttp, concurrent.futures, asyncio, sys
from bilibili_api import Credential, user, sync, login_func
from .patch_bilibili_api_python import patch_check_qrcode_events
import tkinter as tk
import json
from pypinyin import pinyin


def get_richContent(data, isEmoji):

    richContent = []
    if isEmoji:
        richContent.append({"type": 1, "url": data["info"][0][13]["url"]})
        return richContent

    dict_index = 0
    startPos = 0
    pos = 0
    data_json = json.loads(data["info"][0][15]["extra"])
    content_msg_text:str = data_json["content"]
    while pos <= len(content_msg_text):
        if content_msg_text.find("[", pos, pos + 1) != -1 and pos != startPos:
            richContent.append({"type": 0, "text": content_msg_text[startPos:pos]})
            startPos = pos
            dict_index += 1
        if content_msg_text.find("]", pos, pos + 1) != -1 and pos > 0:
            richContent.append(
                {
                    "type": 1,
                    "text": content_msg_text[startPos : pos + 1],
                    "url": data_json["emots"][content_msg_text[startPos : pos + 1]][
                        "url"
                    ],
                    "width": data_json["emots"][content_msg_text[startPos : pos + 1]][
                        "width"
                    ],
                    "height": data_json["emots"][content_msg_text[startPos : pos + 1]][
                        "height"
                    ],
                }
            )
            startPos = pos + 1
            dict_index += 1
        # 遍历到结尾
        if pos == len(content_msg_text):
            richContent.append(
                {"type": 0, "text": content_msg_text[startPos : len(content_msg_text)]}
            )
            break
        pos += 1
    return richContent


liveEvent = AsyncIOEventEmitter()
room = None
firstHeartBeat = True

# 0为普通用户，1为总督，2位提督，3为舰长
guardLevelMap = {0: 0, 1: 3, 2: 2, 3: 1}

guardLevelMap_name = {0: "", 3: "总督", 2: "提督", 1: "舰长"}
guardLevelMap_name_raw = {0: "", 1: "总督", 2: "提督", 3: "舰长"}
author_type_map = {
    0: "",
    1: "member",  # 舰队
    2: "moderator",  # 房管
    3: "owner",  # 主播
}


class LiveMsgHandler(BaseHandler):
    def _on_heartbeat(self, client: BLiveClient, message: HeartbeatMessage):
        global firstHeartBeat
        if firstHeartBeat:
            liveEvent.emit("connected")
            firstHeartBeat = False

    def onDanmuCallback(self, client: BLiveClient, command: dict):
        uid = command["info"][2][0]
        faceImg = command["info"][0][15]["user"]["base"]["face"]
        msg = command["info"][1]
        uname = command["info"][2][1]
        isadmin = command["info"][2][2] == 1
        liveRoomGuardLevel = command["info"][7]
        liveRoomGuardLevelName = guardLevelMap_name_raw[liveRoomGuardLevel]
        if len(command["info"][3]) != 0:
            isFansMedalBelongToLive = (
                command["info"][3][3] == getJsonConfig()["engine"]["bili"]["liveID"]
            )
            fansMedalLevel = command["info"][3][0]
            fansMedalName = command["info"][3][1]
            fansMedalGuardLevel = guardLevelMap[command["info"][3][10]]
            fansMedalGuardLevelName = guardLevelMap_name[fansMedalGuardLevel]
            if uid == client.room_owner_uid:
                authorType = 3  # 主播
            elif isadmin:
                authorType = 2  # 房管
            elif liveRoomGuardLevel != 0:  # 3总督，2提督，1舰长
                authorType = 1  # 舰队
            else:
                authorType = 0
            authorTypeText = author_type_map[authorType]
        else:
            isFansMedalBelongToLive = False
            fansMedalLevel = 0
            fansMedalName = ""
            fansMedalGuardLevel = 0
            fansMedalGuardLevelName = ""
            authorType = 0
            authorTypeText = ""
        isEmoji = command["info"][0][12] == 1 or isAllCharactersEmoji(msg)
        isEmojiRaw = command["info"][0][12] == 1
        richContent = get_richContent(command, isEmojiRaw)
        timeLog(
            f"[Danmu] [{authorTypeText}] [{liveRoomGuardLevelName}] [[{fansMedalGuardLevelName}]{fansMedalName}:{fansMedalLevel}] {uname}: {msg}"
        )
        liveEvent.emit(
            "danmu",
            uid,
            uname,
            isFansMedalBelongToLive,
            authorType,
            authorTypeText,
            fansMedalName,
            fansMedalLevel,
            fansMedalGuardLevelName,
            fansMedalGuardLevel,
            liveRoomGuardLevelName,
            liveRoomGuardLevel,
            msg,
            richContent,
            faceImg,
            isEmoji,
        )

    def onGuardBuyCallback(self, client: BLiveClient, command: dict):
        if "role_name" not in command["data"] or command["data"]["role_name"] not in [
            "总督",
            "提督",
            "舰长",
        ]:
            return
        uid = command["data"]["uid"]
        num = command["data"]["num"]
        uname = command["data"]["username"]
        unamePronunciation = (" ".join(y for x in pinyin(uname) for y in x),)
        giftName = command["data"]["role_name"]
        liveRoomGuardLevel = command["data"]["guard_level"]
        newGuard = "第1天" == command["data"]["toast_msg"][-3:]
        title = f" {uname} 购买 {num} 个月的 {giftName} "
        try:
            faceImg = sync(
                user.User(
                    command["data"]["uid"],
                    Credential(
                        None,
                        None,
                        None,
                    ),
                ).get_user_info()
            )["face"]
        except:
            faceImg = "static.hdslb.com/images/member/noface.gif"

        timeLog(
            f"[GuardBuy] {uname} bought {'New ' if newGuard else ''}{giftName} x {num}."
        )
        liveEvent.emit(
            "guardBuy",
            uid,
            uname,
            unamePronunciation,
            liveRoomGuardLevel,
            newGuard,
            faceImg,
            giftName,
            num,
            title,
        )

    def onSCCallback(self, client: BLiveClient, command: dict):
        uid = command["data"]["uid"]
        uname = command["data"]["user_info"]["uname"]
        unamePronunciation = (" ".join(y for x in pinyin(uname) for y in x),)
        price = command["data"]["price"]
        msg = command["data"]["message"]
        faceImg = command["data"]["user_info"]["face"]
        timeLog(f"[SuperChat] {uname} bought {price}元的SC: {msg}")
        liveEvent.emit("superChat", uid, faceImg, uname, unamePronunciation, price, msg)

    def onGiftCallback(self, client: BLiveClient, command: dict):
        uid = command["data"]["uid"]
        uname = command["data"]["uname"]
        unamePronunciation = (" ".join(y for x in pinyin(uname) for y in x),)
        giftName = command["data"]["giftName"]
        num = command["data"]["num"]
        price = command["data"]["price"] / 1000
        price = price if command["data"]["coin_type"] == "gold" else 0
        faceImg = command["data"]["face"]
        timeLog(f"[Gift] {uname} bought {price:.1f}元的{giftName} x {num}.")
        liveEvent.emit(
            "gift", uid, uname, unamePronunciation, price, faceImg, giftName, num
        )

    def onInteractWordCallback(self, client: BLiveClient, command: dict):
        if command["data"]["roomid"] != getJsonConfig()["engine"]["bili"]["liveID"]:
            return
        uid = command["data"]["uid"]
        uname = command["data"]["uname"]
        if command["data"]["fans_medal"] != None:
            isFansMedalBelongToLive = (
                command["data"]["fans_medal"]["anchor_roomid"]
                == getJsonConfig()["engine"]["bili"]["liveID"]
            )
            fansMedalLevel = command["data"]["fans_medal"]["medal_level"]
            fansMedalGuardLevel = guardLevelMap[
                command["data"]["fans_medal"]["guard_level"]
            ]
        else:
            isFansMedalBelongToLive = False
            fansMedalLevel = 0
            fansMedalGuardLevel = 0
        isSubscribe = command["data"]["msg_type"] == 2
        timeLog(
            f"[Interact] {uname} {'subscribe' if isSubscribe else 'enter'} the stream."
        )
        if isSubscribe:
            liveEvent.emit(
                "subscribe",
                uid,
                uname,
                isFansMedalBelongToLive,
                fansMedalLevel,
                fansMedalGuardLevel,
            )
        else:
            liveEvent.emit(
                "welcome",
                uid,
                uname,
                isFansMedalBelongToLive,
                fansMedalLevel,
                fansMedalGuardLevel,
            )

    def onLikeCallback(self, client: BLiveClient, command: dict):
        uid = command["data"]["uid"]
        uname = command["data"]["uname"]
        timeLog(f"[Like] {uname} liked the stream.")
        liveEvent.emit("like", uid, uname)

    def onWarning(self, client: BLiveClient, command: dict):
        msg = command['msg']
        timeLog(f"[Warning] {msg}")
        liveEvent.emit("warning", msg, False)

    def onCutOff(self, client: BLiveClient, command: dict):
        print(command)
        msg = command['msg']
        timeLog(f"[Warning] Cut Off, {msg}")
        liveEvent.emit("warning", msg, True)

    _CMD_CALLBACK_DICT = {
        **BaseHandler._CMD_CALLBACK_DICT,
        "DANMU_MSG": onDanmuCallback,
        "SEND_GIFT": onGiftCallback,
        "USER_TOAST_MSG": onGuardBuyCallback,
        "SUPER_CHAT_MESSAGE": onSCCallback,
        "INTERACT_WORD": onInteractWordCallback,
        "LIKE_INFO_V3_CLICK": onLikeCallback,
        "WARNING": onWarning,
        "CUT_OFF": onCutOff,
    }


async def getSelfInfo():
    # 检查B站凭证是否有效
    try:
        config = getJsonConfig()
        return await user.get_self_info(
            Credential(
                config["kvdb"]["bili"]["sessdata"],
                config["kvdb"]["bili"]["jct"],
                config["kvdb"]["bili"]["buvid3"],
            )
        )
    except:
        return None


async def getSelfLiveID():
    # 获取自己直播间ID
    try:
        config = getJsonConfig()
        return (
            await user.User(
                config["kvdb"]["bili"]["uid"],
                Credential(
                    config["kvdb"]["bili"]["sessdata"],
                    config["kvdb"]["bili"]["jct"],
                    config["kvdb"]["bili"]["buvid3"],
                ),
            ).get_live_info()
        )["live_room"]["roomid"]
    except:
        return None


def loginBili():
    img, token = login_func.get_qrcode()
    window = tk.Tk()
    window.resizable(0, 0)
    window.title("企鹅弹幕机 - 扫码登陆B站")
    image = tk.PhotoImage(file=img.url.replace("file://", ""))
    widget = tk.Label(window, compound="top", image=image)
    widget.pack()
    window.eval("tk::PlaceWindow . center")
    outputCred = None
    count = 0

    def update():
        nonlocal img, token, count
        if count == 60:
            img, token = login_func.get_qrcode()
            image.configure(file=img.url.replace("file://", ""))
            count = 0
            timeLog(f"[Live] 刷新二维码")
        count += 1
        event, cred = patch_check_qrcode_events(token)
        nonlocal outputCred
        outputCred = cred
        if event != login_func.QrCodeLoginEvents.DONE:
            timeLog(f"[Live] 等待二维码登录中...")
            window.after(1000, update)
        else:
            window.destroy()

    window.after(1000, update)
    window.protocol("WM_DELETE_WINDOW", lambda: sys.exit(0))
    window.mainloop()
    del image, widget
    config = getJsonConfig()
    config["kvdb"]["bili"]["uid"] = int(outputCred.dedeuserid)
    config["kvdb"]["bili"]["sessdata"] = outputCred.sessdata
    config["kvdb"]["bili"]["buvid3"] = outputCred.buvid3
    config["kvdb"]["bili"]["jct"] = outputCred.bili_jct
    sync(updateJsonConfig(config))
    timeLog(
        f'[Live] 二维码登录完成，uid: {config["kvdb"]["bili"]["uid"]}，sessdata: {config["kvdb"]["bili"]["sessdata"]}，buvid3: {config["kvdb"]["bili"]["buvid3"]}, jct: {config["kvdb"]["bili"]["jct"]}'
    )


async def connectLive():
    room.start()


async def disconnectLive():
    await room.close()


async def initalizeLive():
    global room
    # 检查B站凭证是否有效
    data = await getSelfInfo()
    if data == None:
        timeLog(f"[Live] B站凭证无效，使用扫码重新登录B站...")
        liveEvent.emit("login")
        loop = asyncio.get_running_loop()
        with concurrent.futures.ThreadPoolExecutor() as pool:
            await loop.run_in_executor(pool, loginBili)
        config = getJsonConfig()
        if config["kvdb"]["isFirstTimeToLogin"]:
            liveID = await getSelfLiveID()
            if liveID != None:
                timeLog(
                    f"[Live] 第一次使用账号登陆，将默认直播间号修改为登陆的账号直播间号{liveID}"
                )
                config["engine"]["bili"]["liveID"] = liveID
                await updateJsonConfig(config)
            else:
                timeLog(
                    f"[Live] 第一次使用账号登陆，但该账号未开通直播间，忽略直播间号自动设置"
                )
    config = getJsonConfig()
    config["kvdb"]["isFirstTimeToLogin"] = False
    await updateJsonConfig(config)
    session = aiohttp.ClientSession(
        headers={
            "Cookie": f'buvid3={config["kvdb"]["bili"]["buvid3"]}; SESSDATA={config["kvdb"]["bili"]["sessdata"]}; bili_jct={config["kvdb"]["bili"]["jct"]};'
        }
    )
    room = BLiveClient(
        config["engine"]["bili"]["liveID"],
        uid=config["kvdb"]["bili"]["uid"],
        session=session,
    )
    room.set_handler(LiveMsgHandler())
    await connectLive()
