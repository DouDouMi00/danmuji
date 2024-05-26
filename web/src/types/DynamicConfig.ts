export type DynamicConfig = {
    "system": {
        "alertWhenMessagesQueueLonger": {
            "enable": boolean,
            "threshold": number,
            "interval": number
        }
    },
    "tts": {
        "readSymbolEnable": boolean,
        "blacklistSymbol": string[],
        "speaker": string,
        "volume": number,
        "voice": string,
        "rate": number,
        "history": {
            "voice": string,
            "rate": number,
            "volume": number
        },
        "japanese": {
            "enable": boolean,
            "voice": string,
            "rate": number,
            "volume": number
        }
    },
    "filter": {
        "danmu": {
            "enable": boolean,
            "symbolEnable": boolean,
            "emojiEnable": boolean,
            "deduplicate": boolean,
            "readfansMedalName" : boolean,
            "readfansMedalGuardLevel" : boolean,
            "isFansMedalBelongToLive": boolean,
            "fansMedalLevelBigger": number,
            "fansMedalGuardLevelBigger": number,
            "lengthShorter": number,
            "blacklistKeywords": string[],
            "blacklistUsers": string[],
            "whitelistUsers": string[],
            "whitelistKeywords": string[]
        },
        "gift": {
            "enable": boolean,
            "freeGiftEnable": boolean,
            "deduplicateTime": number,
            "freeGiftCountBigger": number,
            "moneyGiftPriceBigger": number,
        },
        "welcome": {
            "enable": boolean,
            "isFansMedalBelongToLive": boolean,
            "fansMedalLevelBigger": number,
            "fansMedalGuardLevelBigger": number,
        },
        "guardBuy": {
            "enable": boolean,
        },
        "like": {
            "enable": boolean,
            "deduplicate": boolean,
        },
        "subscribe": {
            "enable": boolean,
        },
        "superChat": {
            "enable": boolean,
        },
        "warning": {
            "enable": boolean,
        },
    }
};