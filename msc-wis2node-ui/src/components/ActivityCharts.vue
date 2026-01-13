<script setup>
// Vue
import { onMounted, computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useDataDistributionMetrics } from '../stores/useDataDistributionMetrics'

// Naive UI
import { NCard, NSpace, NButton, NTag, NText, NScrollbar } from 'naive-ui'

// vue-echarts / echarts
import { use } from 'echarts/core'
import VChart from 'vue-echarts'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, BarChart } from 'echarts/charts'
import {
  GridComponent,
  TooltipComponent,
  LegendComponent,
  TitleComponent,
} from 'echarts/components'

// Register only what we need
use([
  CanvasRenderer,
  LineChart,
  BarChart,
  GridComponent,
  TooltipComponent,
  LegendComponent,
  TitleComponent,
])

// Line chart: MQTT messages per second for a topic over the last 7 minutes
const mqttMessagesLineOptions = computed(() => ({
  title: {
    text: 'Example MQTT Messages / Second (last 7 minutes)',
    left: 'center',
    textStyle: { fontSize: 14 },
  },
  tooltip: { trigger: 'axis' },
  grid: { top: 40, left: 40, right: 20, bottom: 40 },
  xAxis: {
    type: 'category',
    data: ['-6m', '-5m', '-4m', '-3m', '-2m', '-1m', 'Now'],
    boundaryGap: false,
  },
  yAxis: {
    type: 'value',
    name: 'msg/s',
  },
  series: [
    {
      name: 'wis2/obs/temperature',
      type: 'line',
      smooth: true,
      symbol: 'circle',
      symbolSize: 6,
      data: [15, 22, 18, 25, 28, 30, 26],
      areaStyle: {},
    },
  ],
}))

// Bar chart: MQTT messages by QoS level in the last 5 minutes
const mqttQosBarOptions = computed(() => ({
  title: {
    text: 'Example MQTT Messages by QoS (last 5 minutes)',
    left: 'center',
    textStyle: { fontSize: 14 },
  },
  tooltip: { trigger: 'axis' },
  grid: { top: 40, left: 40, right: 20, bottom: 40 },
  xAxis: {
    type: 'category',
    data: ['QoS 0', 'QoS 1', 'QoS 2'],
  },
  yAxis: {
    type: 'value',
    name: 'messages',
  },
  series: [
    {
      name: 'Messages',
      type: 'bar',
      data: [420, 180, 35],
      barWidth: '50%',
    },
  ],
}))

// Metrics store
const metricsStore = useDataDistributionMetrics()
const { files, selectedFile, rawJson, loadingList, loadingFile, error } = storeToRefs(metricsStore)
const { fetchFileList, fetchFile } = metricsStore

onMounted(async () => {
  await fetchFileList()
  if (files.value.length > 0 && !selectedFile.value) {
    const latest = files.value[files.value.length - 1]
    await fetchFile(latest)
  }
})

const selectedFileLabel = computed(() =>
  selectedFile.value ? `Selected file: ${selectedFile.value}` : 'No file selected'
)
</script>

<template>
  <!-- Charts -->
  <div class="charts-row">
    <div class="chart-wrapper">
      <v-chart :option="mqttMessagesLineOptions" autoresize />
    </div>
    <div class="chart-wrapper">
      <v-chart :option="mqttQosBarOptions" autoresize />
    </div>
  </div>

  <!-- Metrics / files panel -->
  <n-card size="small" class="metrics-card">
    <!-- Header row -->
    <n-space justify="space-between" align="center" class="metrics-header">
      <n-text strong>Metrics files</n-text>

      <n-space size="small" align="center">
        <n-text depth="3">
          <span v-if="loadingList">Loading file list…</span>
          <span v-else-if="loadingFile">Loading file {{ selectedFile }}…</span>
          <span v-else>{{ selectedFileLabel }}</span>
        </n-text>
        <n-text v-if="error" type="error">Error: {{ error }}</n-text>
      </n-space>
    </n-space>

    <!-- Files list -->
    <div v-if="files.length" class="metrics-files">
      <n-space wrap size="small">
        <n-button
          v-for="file in files"
          :key="file"
          size="tiny"
          tertiary
          :type="file === selectedFile ? 'primary' : 'default'"
          :loading="loadingFile && file === selectedFile"
          @click="fetchFile(file)"
        >
          <n-space size="small" align="center">
            <span>{{ file }}</span>
            <n-tag v-if="file === selectedFile" size="tiny" type="success" bordered="{false}">
              selected
            </n-tag>
          </n-space>
        </n-button>
      </n-space>
    </div>
    <n-text v-else-if="!loadingList && !error" depth="3"> No metric files found. </n-text>

    <!-- Raw JSON view -->
    <div v-if="rawJson" class="metrics-raw-json">
      <n-text strong>Raw JSON</n-text>
      <n-scrollbar style="max-height: 240px; margin-top: 8px">
        <pre>{{ rawJson }}</pre>
      </n-scrollbar>
    </div>
  </n-card>
</template>

<style scoped>
.charts-row {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-top: 8px;
}

.chart-wrapper {
  flex: 1 1 300px;
  min-height: 260px;
}

/* Metrics panel */
.metrics-card {
  margin-top: 16px;
  font-size: 13px;
}

.metrics-header {
  margin-bottom: 8px;
}

.metrics-files {
  margin-bottom: 8px;
}

/* Raw JSON */
.metrics-raw-json pre {
  margin: 0;
  font-family: Menlo, Monaco, Consolas, 'Courier New', monospace;
  font-size: 12px;
  white-space: pre-wrap;
}
</style>
