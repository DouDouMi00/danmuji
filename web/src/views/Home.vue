<template>
    <v-container fluid class="pa-0">
        <v-row no-gutters>
            <v-col cols="12" md="3">
                <v-sheet class="pa-2 bg-transparent" :style="{ 'height': showEngineConfig ? '60vh' : '90vh' }">
                    <ConfigPanel style="height: 100%;"/>
                </v-sheet>
                <v-sheet class="pa-2 bg-transparent" style="height: 30vh;" v-if="showEngineConfig">
                    <EngineConfigPanel style="height: 100%;"/>
                </v-sheet>
            </v-col>
            <v-col cols="12" md="9">
                <v-sheet class="pa-2 bg-transparent" style="height: 90vh;">
                    <LogPanel style="height: 100%;" :data="logEvent" @toggle="toggleLock" :locked="locked"/>
                </v-sheet>
            </v-col>
        </v-row>
    </v-container>
    <v-container fluid class="pa-1">
        <v-row no-gutters>
            <v-col cols="12" md="8" class="graph-container">
                <v-sheet class="pa-2 bg-transparent" style="height: 45vh;">
                    <GraphPanel style="height: 100%;" name="原始数据" :columes="['弹幕', '礼物', '入场', '其他']" :data="rawGraphData" :locked="locked"/>
                </v-sheet>
                <v-sheet class="pa-2 bg-transparent" style="height: 45vh;">
                    <GraphPanel style="height: 100%;" name="过滤后数据" :columes="['弹幕', '礼物', '入场', '其他']" :data="filteredGraphData" :locked="locked"/>
                </v-sheet>
            </v-col>
            <v-col cols="12" md="4">
                <v-sheet class="pa-2 bg-transparent" style="height: 30vh;">
                    <GraphPanel style="height: 100%;" name="CPU占用率" :columes="['百分比']" :data="cpuUsage" :locked="locked"/>
                </v-sheet>
                <v-sheet class="pa-2 bg-transparent" style="height: 30vh;">
                    <GraphPanel style="height: 100%;" name="输出队列高度" :columes="['高度']" :data="messagesQueueLegnth" :locked="locked"/>
                </v-sheet>
                <v-sheet class="pa-2 bg-transparent" style="height: 30vh;">
                    <GraphPanel style="height: 100%;" name="平均延迟" :columes="['秒']" :data="delay" :locked="locked"/>
                </v-sheet>
            </v-col>
        </v-row>
    </v-container>
</template>

<style scoped>
</style>

<script lang="ts" setup>
import ConfigPanel from '@/components/ConfigPanel.vue'
import LogPanel from '@/components/LogPanel.vue';
import GraphPanel from '@/components/GraphPanel.vue';
import { onWSMessages, getRunningMode } from '@/services/Database';
import { ref, Ref } from 'vue';
import { StatsEvent } from '@/types/WebsocketBroadcastMessage';
import EngineConfigPanel from '@/components/EngineConfigPanel.vue';

const rawGraphData: Ref<number[][]> = ref([[], [], [], []]);
const filteredGraphData: Ref<number[][]> = ref([[], [], [], []]);
const messagesQueueLegnth: Ref<number[][]> = ref([[]]);
const logEvent: Ref<StatsEvent['events']> = ref([]);
const cpuUsage: Ref<number[][]> = ref([[]]);
const delay: Ref<number[][]> = ref([[]]);
const showEngineConfig: Ref<boolean> = ref(false);
const locked: Ref<boolean> = ref(true);

getRunningMode().then(data => {
    showEngineConfig.value = !data.remote;
});

onWSMessages.subscribe((rawData) => {
    if (rawData.type !== "stats") {
        return;
    }
    const data = rawData.data;
    logEvent.value = logEvent.value.concat(data.events);
    rawGraphData.value[0].push(data.stats.rawDanmu);
    rawGraphData.value[1].push(data.stats.rawGift);
    rawGraphData.value[2].push(data.stats.rawWelcome);
    rawGraphData.value[3].push(data.stats.rawGuardBuy + data.stats.rawLike + data.stats.rawSubscribe + data.stats.rawSuperChat);

    filteredGraphData.value[0].push(data.stats.rawDanmu - data.stats.filteredDanmu);
    filteredGraphData.value[1].push(data.stats.rawGift - data.stats.filteredGift);
    filteredGraphData.value[2].push(data.stats.rawWelcome - data.stats.filteredWelcome);
    filteredGraphData.value[3].push(data.stats.rawGuardBuy + data.stats.rawLike + data.stats.rawSubscribe + data.stats.rawSuperChat - (data.stats.filteredGuardBuy + data.stats.filteredLike + data.stats.filteredSubscribe + data.stats.filteredSuperChat));

    messagesQueueLegnth.value[0].push(data.stats.messagesQueueLength);

    cpuUsage.value[0].push(data.stats.cpuUsage);

    delay.value[0].push(data.stats.delay);
});

function toggleLock() {
    locked.value = !locked.value;
}

</script>
