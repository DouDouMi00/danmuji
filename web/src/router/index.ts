// Composables
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
    {
        path: '/',
        component: () => import('@/views/Home.vue'),
        meta: {
            name: "配置",
        }
    },
    {
        path: '/StyleGenerator',
        component: () => import('@/views/StyleGenerator.vue'),
        meta: {
            name: "样式生成器",
        }
    },
    {
        path: '/Room',
        component: () => import('@/views/Room.vue'),
        meta: {
            name: "直播间",
        }
    }
]


const router = createRouter({
    history: createWebHistory(process.env.BASE_URL),
    routes,
})

export default router
