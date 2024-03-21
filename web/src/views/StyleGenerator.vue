<template>
  <v-container fluid class="pa-0">
    <v-row no-gutters>
      <v-col cols="12" md="6">
        <v-sheet class="pa-2 bg-transparent" style="height: 90vh;">
          <v-textarea v-model="textareaValue" no-resize rows="20" variant="outlined" bg-color="grey-lighten-2" color="black"
            label="css 样式"></v-textarea>
        </v-sheet>
      </v-col>
      <v-col cols="12" md="6">
        <v-sheet class="pa-2 bg-transparent" style="height: 90vh">
          <div v-html="`<style> ${textareaValue} </style>`"></div>
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
import { ref, Ref, watch, onMounted } from 'vue';


const logEvent_room: Ref<StatsEvent['events']> = ref([]);
let textareaValue = ref('')

function saveToLocalStorage() {
  localStorage.setItem('textareaValue', textareaValue.value);
}

function loadFromLocalStorage() {
  const storedValue = localStorage.getItem('textareaValue');
  if (storedValue) {
    textareaValue.value = storedValue;
  }
}

onWSMessages.subscribe((rawData) => {
  if (rawData.type !== "stats") {
    return;
  }
  const data = rawData.data;
  logEvent_room.value = data.events;
});

onMounted(() => {
  loadFromLocalStorage();
});

watch(textareaValue, () => {
  saveToLocalStorage();
}, {
  deep: true
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


</style>
