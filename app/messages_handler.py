from .live import liveEvent
from .filter import (
    filterDanmu,
    filterGift,
    filterGuardBuy,
    filterLike,
    filterSubscribe,
    filterWelcome,
    filterSuperChat,
    filterWarning,
)
from .stats import (
    setOutputMessagesLength,
    appendDanmuFilteredStats,
    appendGiftFilteredStats,
    appendWelcomeFilteredStats,
    appendLikeFilteredStats,
    appendGuardBuyFilteredStats,
    appendSubscribeFilteredStats,
    appendSuperChatFilteredStats,
    appendWarningFilteredStats,
)
import time

messagesQueue = []
haveReadMessages = []


def popMessagesQueue():
    global messagesQueue, haveReadMessages
    if len(messagesQueue) == 0:
        return None
    data = messagesQueue.pop(0)
    setOutputMessagesLength(len(messagesQueue))
    haveReadMessages.append(data)
    return data


def getHaveReadMessages():
    global haveReadMessages
    return haveReadMessages


def messagesQueueAppend(data):
    global messagesQueue
    messagesQueue.append(data)
    setOutputMessagesLength(len(messagesQueue))


def messagesQueueAppendAtStart(data):
    global messagesQueue
    messagesQueue.insert(0, data)
    setOutputMessagesLength(len(messagesQueue))


@liveEvent.on("danmu")
async def onDanmu(
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
):
    if filterDanmu(
        uid,
        uname,
        isFansMedalBelongToLive,
        fansMedalLevel,
        fansMedalGuardLevel,
        msg,
        isEmoji,
    ):
        appendDanmuFilteredStats(
            uid=uid,
            uname=uname,
            time=int(time.time()),
            msg=msg,
            richContent=richContent,
            isEmoji=isEmoji,
            authorType=authorType,
            authorTypeText=authorTypeText,
            fansMedalName=fansMedalName,
            fansMedalLevel=fansMedalLevel,
            fansMedalGuardLevelName=fansMedalGuardLevelName,
            fansMedalGuardLevel=fansMedalGuardLevel,
            liveRoomGuardLevelName=liveRoomGuardLevelName,
            liveRoomGuardLevel=liveRoomGuardLevel,
            faceImg=faceImg,
            filterd=False,
        )
        messagesQueueAppend(
            {
                "type": "danmu",
                "time": int(time.time()),
                "uid": uid,
                "uname": uname,
                "msg": msg,
                "richContent": richContent,
                "isEmoji": isEmoji,
                "fansMedalName": fansMedalName,
                "fansMedalLevel": fansMedalLevel,
                "fansMedalGuardLevelName": fansMedalGuardLevelName,
                "fansMedalGuardLevel": fansMedalGuardLevel,
                "liveRoomGuardLevelName": liveRoomGuardLevelName,
                "liveRoomGuardLevel": liveRoomGuardLevel,
                "faceImg": faceImg,
                "authorType": authorType,
                "authorTypeText": authorTypeText,
            }
        )

    else:
        appendDanmuFilteredStats(
            faceImg=faceImg,
            time=int(time.time()),
            uid=uid,
            uname=uname,
            msg=msg,
            isEmoji=isEmoji,
            filterd=True,
        )


@liveEvent.on("gift")
async def onGift(uid, uname, unamePronunciation, price, faceImg, giftName, num):
    def deduplicateCallback(userInfo, giftName):
        giftInfo = userInfo["gifts"][giftName]
        messagesQueueAppend(
            {
                "type": "gift",
                "time": time.time(),
                "uid": userInfo["uid"],
                "uname": userInfo["uname"],
                "giftName": giftName,
                "num": giftInfo["count"],
            }
        )

    result = filterGift(uid, uname, price, giftName, num, deduplicateCallback)
    if result == True:
        appendGiftFilteredStats(
            uid=uid,
            uname=uname,
            unamePronunciation=unamePronunciation,
            time=int(time.time()),
            price=price,
            faceImg=faceImg,
            giftName=giftName,
            num=num,
            filterd=False,
        )
        messagesQueueAppend(
            {
                "type": "gift",
                "time": time.time(),
                "uid": uid,
                "uname": uname,
                "giftName": giftName,
                "num": num,
            }
        )
    else:
        appendGiftFilteredStats(
            uid=uid,
            uname=uname,
            unamePronunciation=unamePronunciation,
            time=int(time.time()),
            price=price,
            faceImg=faceImg,
            giftName=giftName,
            num=num,
            filterd=(result != None),
        )


@liveEvent.on("guardBuy")
async def onGuardBuy(
    uid,
    uname,
    unamePronunciation,
    liveRoomGuardLevel,
    newGuard,
    faceImg,
    giftName,
    num,
    title,
):
    if filterGuardBuy(uid, uname, newGuard, giftName, num):
        appendGuardBuyFilteredStats(
            uid=uid,
            uname=uname,
            unamePronunciation=unamePronunciation,
            time=int(time.time()),
            liveRoomGuardLevel=liveRoomGuardLevel,
            newGuard=newGuard,
            faceImg=faceImg,
            giftName=giftName,
            num=num,
            title=title,
            filterd=False,
        )
        messagesQueueAppend(
            {
                "type": "guardBuy",
                "time": time.time(),
                "uid": uid,
                "uname": uname,
                "newGuard": newGuard,
                "giftName": giftName,
                "num": num,
            }
        )
    else:
        appendGuardBuyFilteredStats(
            uid=uid,
            uname=uname,
            unamePronunciation=unamePronunciation,
            time=int(time.time()),
            liveRoomGuardLevel=liveRoomGuardLevel,
            newGuard=newGuard,
            faceImg=faceImg,
            giftName=giftName,
            num=num,
            title=title,
            filterd=True,
        )


@liveEvent.on("like")
async def onLike(uid, uname):
    if filterLike(uid, uname):
        appendLikeFilteredStats(uid=uid, uname=uname, filterd=False)
        messagesQueueAppend(
            {"type": "like", "time": time.time(), "uid": uid, "uname": uname}
        )
    else:
        appendLikeFilteredStats(uid=uid, uname=uname, filterd=True)


@liveEvent.on("superChat")
async def onSuperChat(uid, faceImg, uname, unamePronunciation, price, msg):
    if filterSuperChat(uid, uname, price, msg):
        appendSuperChatFilteredStats(
            uid=uid,
            faceImg=faceImg,
            uname=uname,
            unamePronunciation=unamePronunciation,
            time=int(time.time()),
            price=price,
            msg=msg,
            filterd=False,
        )
        messagesQueueAppend(
            {
                "type": "superChat",
                "time": time.time(),
                "uid": uid,
                "uname": uname,
                "price": price,
                "msg": msg,
            }
        )
    else:
        appendSuperChatFilteredStats(
            uid=uid,
            faceImg=faceImg,
            uname=uname,
            unamePronunciation=unamePronunciation,
            time=int(time.time()),
            price=price,
            msg=msg,
            filterd=True,
        )


@liveEvent.on("subscribe")
async def onSubscribe(
    uid, uname, isFansMedalBelongToLive, fansMedalLevel, fansMedalGuardLevel
):
    if filterSubscribe(
        uid, uname, isFansMedalBelongToLive, fansMedalLevel, fansMedalGuardLevel
    ):
        appendSubscribeFilteredStats(uid=uid, uname=uname, filterd=False)
        messagesQueueAppend(
            {"type": "subscribe", "time": time.time(), "uid": uid, "uname": uname}
        )
    else:
        appendSubscribeFilteredStats(uid=uid, uname=uname, filterd=True)


@liveEvent.on("welcome")
async def onWelcome(
    uid, uname, isFansMedalBelongToLive, fansMedalLevel, fansMedalGuardLevel
):
    if filterWelcome(
        uid, uname, isFansMedalBelongToLive, fansMedalLevel, fansMedalGuardLevel
    ):
        appendWelcomeFilteredStats(uid=uid, uname=uname, filterd=False)
        messagesQueueAppend(
            {"type": "welcome", "time": time.time(), "uid": uid, "uname": uname}
        )
    else:
        appendWelcomeFilteredStats(uid=uid, uname=uname, filterd=True)


@liveEvent.on("warning")
async def onWarning(msg, isCutOff):
    if filterWarning(msg, isCutOff):
        appendWarningFilteredStats(msg=msg, isCutOff=isCutOff, filterd=False)
        messagesQueueAppend(
            {"type": "warning", "time": time.time(), "msg": msg, "isCutOff": isCutOff}
        )
    else:
        appendWarningFilteredStats(msg=msg, isCutOff=isCutOff, filterd=True)


async def markAllMessagesInvalid():
    global messagesQueue
    messagesQueue = [{"type": "system", "time": time.time(), "msg": "已清空弹幕列表"}]
    setOutputMessagesLength(len(messagesQueue))
