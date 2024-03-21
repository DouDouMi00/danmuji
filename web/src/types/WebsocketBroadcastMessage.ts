import { DynamicConfig } from "./DynamicConfig";

export type DanmuEvent = {
    'type': 'danmu',
    'filterd': boolean,
    'uid': number,
    'uname': string,
    'faceImg': string,
    'msg': string,
    'time': number,
    'authorType': number,
    'richContent':string,
    'liveRoomGuardLevel': number,
    'repeated': number
};

export type GiftEvent = {
    'type': 'gift',
    'filterd': boolean,
    'uid': number,
    'uname': string,
    'faceImg': string,
    'giftName': string,
    'num': number,
    'time': number,
    'unamePronunciation': string,
    'price' :number,
};

export type GuardBuyEvent = {
    'type': 'guardBuy',
    'filterd': boolean,
    'uid': number,
    'uname': string,
    'newGuard': number,
    'giftName': string,
    'num': number,
    'faceImg': string,
    'time': number,
    'unamePronunciation': string,
    'liveRoomGuardLevel': number,
    'title' :string,
};

export type LikeEvent = {
    'type': 'like',
    'filterd': boolean,
    'uid': number,
    'uname': string
};

export type SubscribeEvent = {
    'type': 'subscribe',
    'filterd': boolean,
    'uid': number,
    'uname': string
};

export type WelcomeEvent = {
    'type': 'welcome',
    'filterd': boolean,
    'uid': number,
    'uname': string
};

export type SuperChatEvent = {
    "type": "superChat",
    "filterd": boolean,
    "uid": number,
    "uname": string,
    "price": number,
    "msg": string,
    'faceImg': string,
    'unamePronunciation': string,
    'title' :string,
};

export type ConfigEvent = DynamicConfig;

export type StatsEvent = {
    "events": (DanmuEvent | GiftEvent | GuardBuyEvent | LikeEvent | SubscribeEvent | WelcomeEvent | SuperChatEvent)[],
    "stats": {
        'filteredDanmu': number,
        'rawDanmu': number,
        'filteredGift': number,
        'rawGift': number,
        'filteredWelcome': number,
        'rawWelcome': number,
        'filteredLike': number,
        'rawLike': number,
        'filteredGuardBuy': number,
        'rawGuardBuy': number,
        'filteredSubscribe': number,
        'rawSubscribe': number,
        'filteredSuperChat': number,
        'rawSuperChat': number,
        'cpuUsage': number,
        'messagesQueueLength': number,
        'delay': number
    }
};

export type WebsocketBroadcastMessage = {
    "type": "stats",
    "data": StatsEvent
} | {
    "type": "config",
    "data": ConfigEvent
};