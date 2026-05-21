<script setup>
// Naive UI
import { NLayoutContent } from 'naive-ui'
import { NGrid, NGridItem, NText, NCard } from 'naive-ui'

import { storeToRefs } from 'pinia'

// Vue
import { useNotifMsg } from '../stores/useNotifMsg'
import { useErrorMsg } from '../stores/useErrorMsg'

// Local components
import ActivityCharts from '../components/ActivityCharts.vue'
import MetricFilesData from '@/components/MetricFilesData.vue'

const notifsStore = useNotifMsg()
const { avgMessages, timeUntilUpdate, totalNumMsg } = storeToRefs(notifsStore)

const errorsStore = useErrorMsg()
const { totalNumErrors, totalElapsedTime } = storeToRefs(errorsStore)

const brokerTopic = import.meta.env.VITE_TOPIC_NOTIFICATION
</script>

<template>
  <!-- CONTENT -->
  <n-layout-content class="app-content">
    <!-- Top metrics -->
    <n-grid cols="1 600:2 1000:4" x-gap="8" y-gap="16">
      <!-- Topic name -->
      <n-grid-item>
        <n-card>
          <n-text depth="3">MQTT Topic</n-text>
          <div class="stat-value">{{ brokerTopic }}</div>
          <n-text depth="3">Current subscription</n-text>
        </n-card>
      </n-grid-item>

      <n-grid-item>
        <n-card>
          <n-text depth="3">Total messages</n-text>
          <div class="stat-value">{{ totalNumMsg }}</div>
          <n-text depth="3">in the last {{ totalElapsedTime }} minutes</n-text>
        </n-card>
      </n-grid-item>

      <!-- Messages per second -->
      <n-grid-item>
        <n-card>
          <n-text depth="3">Messages / Second</n-text>
          <div class="stat-value">{{ avgMessages }}</div>
          <n-text depth="3">Averaged over last 60s. Update in {{ timeUntilUpdate }}s</n-text>
        </n-card>
      </n-grid-item>

      <!-- Errors / drops -->
      <n-grid-item>
        <n-card>
          <n-text depth="3">Dropped / Error Messages</n-text>
          <div class="stat-value">{{ totalNumErrors }}</div>
          <n-text type="error">in the last {{ totalElapsedTime }} minutes</n-text>
        </n-card>
      </n-grid-item>
    </n-grid>
    <!-- Activity / charts -->
    <div class="activity-card data-container">
      <n-card title="Activity" size="large">
        <ActivityCharts />
      </n-card>
      <MetricFilesData />
    </div>
  </n-layout-content>
</template>

<style scoped>
.data-container {
  margin-top: 8px;
}
</style>
