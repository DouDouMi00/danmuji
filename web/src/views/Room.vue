<template>
  <v-container fluid class="pa-0">
    <v-row no-gutters>
      <v-col cols="12" md="12">
        <v-sheet class="pa-2 bg-transparent" style="height: 90vh">
          <LogChatPanel style="height: 100%;" :data="logEvent_room" />
        </v-sheet>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts" setup>
import LogChatPanel from '@/components/LogChatPanel.vue';
import { StatsEvent } from '@/types/WebsocketBroadcastMessage';
import { onWSMessages } from '@/services/Database';
import { ref, Ref } from 'vue';

const logEvent_room: Ref<StatsEvent['events']> = ref([]);

onWSMessages.subscribe((rawData) => {
  if (rawData.type !== "stats") {
    return;
  }
  const data = rawData.data;
  logEvent_room.value = data.events;
});
</script>

<style scoped>
html {
  font-family: "Helvetica Neue", Helvetica, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "\5FAE \8F6F \96C5 \9ED1 ", "微软雅黑", Arial, sans-serif;
}

html,
body,
#app {
  height: 100%;
}

body {
  margin: 0;
  background-color: #f6f8fa;
}

a,
a:focus,
a:hover {
  text-decoration: none;
}

yt-live-chat-renderer {
  background-color: transparent !important;
}
</style>
