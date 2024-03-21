<template>
  <chat-renderer style="height: 100%" ref="renderer" :maxNumber="config.maxNumber"
    :showGiftName="config.showGiftName"></chat-renderer>
</template>

<script lang="ts" setup>
import ChatRenderer from '@/components/ChatRenderer/index.vue'
import { watch } from 'vue';
import { ref } from 'vue'
import { getUuid4Hex, mergeConfig, toBool, toInt, toFloat } from '@/utils'
import * as chatConfig from '@/api/chatConfig'
import { useRoute } from 'vue-router';

const renderer = ref<InstanceType<typeof ChatRenderer> | null>(null) as any; // 定义ref变量

type Raw = {
  filterd?: boolean,
  type?: string,
  faceImg?: string,
  time?: number,
  uname?: string,
  unamePronunciation?: string,
  authorType?: number,
  msg?: string,
  richContent?: string,
  liveRoomGuardLevel?: number,
  repeated?: number,
  price?: number,
  giftName?: string,
  num?: number,
  title?: string,
}

const props = defineProps({
  data: {
    type: Array<Raw>,
    required: true
  },
  locked: {
    type: Boolean,
    default: true
  }
});


watch(props, (newValue, oldValue) => {
  functionName(newValue.data);
});

function functionName(Value: Array<Raw>) {
  try {
    for (const raw of Value) {
      let message = {};
      if (raw.filterd === false) {
        if (raw.type === 'danmu') {
          message = {
            id: getUuid4Hex(),
            type: 0,
            avatarUrl: raw.faceImg,
            time: new Date(raw.time! * 1000),
            authorName: raw.uname,
            authorType: raw.authorType,
            content: raw.msg,
            richContent: raw.richContent,
            privilegeType: raw.liveRoomGuardLevel,
            repeated: raw.repeated,
          }
        }
        else if (raw.type === 'gift') {
          message = {
            id: getUuid4Hex(),
            type: 1,
            avatarUrl: raw.faceImg,
            time: new Date(raw.time! * 1000),
            authorName: raw.uname,
            authorNamePronunciation: raw.unamePronunciation,
            price: raw.price,
            // freePrice: data.totalFreeCoin, // 暂时没用到
            giftName: raw.giftName,
            num: raw.num
          }
        }
        else if (raw.type === 'guardBuy') {
          message = {
            id: getUuid4Hex(),
            type: 2,
            avatarUrl: raw.faceImg,
            time: new Date(raw.time! * 1000),
            authorName: raw.uname,
            authorNamePronunciation: raw.unamePronunciation,
            privilegeType: raw.liveRoomGuardLevel,
            title: raw.title
          }
        }
        else if (raw.type === 'superChat') {
          let message = {
            id: getUuid4Hex(),
            type: 3,
            avatarUrl: raw.faceImg,
            authorName: raw.uname,
            // authorNamePronunciation: this.getPronunciation(data.authorName),
            authorNamePronunciation: raw.unamePronunciation,
            price: raw.price,
            time: new Date(raw.time! * 1000),
            content: raw.msg,
          }
        }
        renderer.value.addMessage(message);
      }
    }
  } catch (error) {
    console.error('添加消息时出错:', error);
  }
};

function toObjIfJson(str: string) {
  if (typeof str !== 'string') {
    return str
  }
  try {
    return JSON.parse(str)
  } catch {
    return {}
  }
};

let strConfig = useRoute().query
let cfg: any = {}

// 从查询参数中过滤出非空配置项
for (let i in strConfig) {
  if (strConfig[i] !== '') {
    cfg[i] = strConfig[i]
  }
}

// 合并默认配置和用户自定义配置
cfg = mergeConfig(cfg, chatConfig.deepCloneDefaultConfig())

// 对特定配置项进行类型转换和默认值设置
cfg.minGiftPrice = toFloat(cfg.minGiftPrice, chatConfig.DEFAULT_CONFIG.minGiftPrice)
cfg.showDanmaku = toBool(cfg.showDanmaku)
cfg.showGift = toBool(cfg.showGift)
cfg.showGiftName = toBool(cfg.showGiftName)
cfg.showGiftName = true
cfg.mergeSimilarDanmaku = toBool(cfg.mergeSimilarDanmaku)
cfg.mergeGift = toBool(cfg.mergeGift)
cfg.maxNumber = toInt(cfg.maxNumber, chatConfig.DEFAULT_CONFIG.maxNumber)

// 配置消息拦截和展示相关设置
cfg.blockGiftDanmaku = toBool(cfg.blockGiftDanmaku)
cfg.blockLevel = toInt(cfg.blockLevel, chatConfig.DEFAULT_CONFIG.blockLevel)
cfg.blockNewbie = toBool(cfg.blockNewbie)
cfg.blockNotMobileVerified = toBool(cfg.blockNotMobileVerified)
cfg.blockMedalLevel = toInt(cfg.blockMedalLevel, chatConfig.DEFAULT_CONFIG.blockMedalLevel)

// 配置消息转发和自动翻译
cfg.relayMessagesByServer = toBool(cfg.relayMessagesByServer)
cfg.autoTranslate = toBool(cfg.autoTranslate)
cfg.importPresetCss = toBool(cfg.importPresetCss)

// 如果emoticons是JSON字符串，则转换为对象
cfg.emoticons = toObjIfJson(cfg.emoticons)

// 对配置项进行安全性和有效性检查
chatConfig.sanitizeConfig(cfg)
let config = cfg
console.log(config)
</script>

<style scoped>
*,
::before,
::after {
  background-repeat: no-repeat;
  box-sizing: content-box;
}
</style>