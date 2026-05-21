import { createRouter, createWebHistory } from 'vue-router'
import wis2NodeOverview from '@/views/wis2NodeOverview.vue'
import wis2NodeMonitoring from '@/views/wis2NodeMonitoring.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: wis2NodeOverview },
    { path: '/monitoring', component: wis2NodeMonitoring },
  ],
})

export default router
