<template>
    <v-toolbar>
        <template v-for="(route, index) in router.options.routes" :key="index">
            <a class="text-white link" :href="getLink(route.path)" :class="{ selected: router.currentRoute.value.path == route.path }" tabindex="0"><p>{{ route.meta?.name }}</p></a>
        </template>
        <v-spacer></v-spacer>
        <div class="text-white link"><p tabindex="0">{{ websocketStatus }}</p></div>
    </v-toolbar>
</template>

<style scoped lang="scss">
@import "../styles/settings.scss";

.v-toolbar {
    background-color: #67a3be;
}
.link {
    height: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
    text-decoration: none;
}
.link > p {
    padding-left: 32px;
    padding-right: 32px;
}
.link:hover {
    background-color: rgba($color: (#000000), $alpha: 0.1);
}
.selected {
    background-color: rgba($color: (#000000), $alpha: 0.2);
}
</style>

<script lang="ts" setup>
import { useRouter } from 'vue-router';
import { onWSState } from '@/services/Database';
import { ref } from 'vue';

const router = useRouter();
const websocketStatus = ref('未连接');
const functionURL = window.location.hostname === 'localhost' ? 'localhost:8080' : window.location.host;


function getLink(path: string) {
    return `${window.location.protocol}//${functionURL}${path}?token=${new URL(document.URL).searchParams.get("token")as string}`;
}

onWSState.subscribe(data => {
    if (data == 'connected') {
        websocketStatus.value = '已连接';
    } else {
        websocketStatus.value = '未连接';
    }
});
</script>