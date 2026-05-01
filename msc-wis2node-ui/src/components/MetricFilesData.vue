<script setup>
// Vue
import { storeToRefs } from 'pinia'
import { useDataDistributionMetrics } from '../stores/useDataDistributionMetrics'
import MetricFilesGraph from './MetricFilesGraph.vue'
import MetricFilesTable from './MetricFilesTable.vue'
import MetricFilesRaw from './MetricFilesRaw.vue'

import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { faChartLine, faTable, faArrowRotateRight } from '@fortawesome/free-solid-svg-icons'

// Naive UI
import { NCard, NTabPane, NTabs, NSpace, NButton } from 'naive-ui'

// Metrics store
const metricsStore = useDataDistributionMetrics()
const { selectedTab, lastLoad } = storeToRefs(metricsStore)
const { refresh } = metricsStore

function updateSelectedTab(newVal) {
  selectedTab.value = newVal
}

async function handleUpdate() {
  await refresh()
}
</script>

<template>
  <div>
    <n-card title="Metric Files Data" size="large" class="card-container">
      <n-button @click="handleUpdate">
        <n-space align="center" size="small">
          Reload Metric Files Data
          <FontAwesomeIcon :icon="faArrowRotateRight" />
        </n-space>
      </n-button>
      <span> Last load: {{ lastLoad }}</span>
      <n-tabs :value="selectedTab" v-on:update-value="updateSelectedTab" class="tab-container">
        <n-tab-pane name="graph" tab="Graph">
          <template #tab>
            <n-space align="center" size="small">
              <span>Graph</span>
              <FontAwesomeIcon :icon="faChartLine" />
            </n-space>
          </template>

          <MetricFilesGraph />
        </n-tab-pane>
        <n-tab-pane name="table" tab="Table">
          <template #tab>
            <n-space align="center" size="small">
              <span>Table</span>
              <FontAwesomeIcon :icon="faTable" />
            </n-space>
          </template>

          <MetricFilesTable />
        </n-tab-pane>
      </n-tabs>
    </n-card>
  </div>

  <MetricFilesRaw />
</template>

<style scoped>
.card-container {
  margin-top: 8px;
}
.reload-button {
  margin-right: 2px;
}
.tab-container {
  margin-top: 1em;
}
</style>
