<script setup>
// Vue
import { computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useNotifMsg } from '../stores/useNotifMsg'
import { useErrorMsg } from '../stores/useErrorMsg'

// vue-echarts / echarts
import { use } from 'echarts/core'
import VChart from 'vue-echarts'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, TitleComponent } from 'echarts/components'

// Register only what we need
use([CanvasRenderer, LineChart, GridComponent, TooltipComponent, TitleComponent])

const notifsStore = useNotifMsg()
const { avgMsgChartData } = storeToRefs(notifsStore)

const errorsStore = useErrorMsg()
const { receivedErrorsChartData } = storeToRefs(errorsStore)

// Line chart: MQTT messages per second for a topic over the last 7 minutes
const mqttMessagesLineOptions = computed(() => ({
  title: {
    text: 'MQTT Notifications / Second (last 7 minutes)',
    left: 'center',
    textStyle: { fontSize: 14 },
  },
  tooltip: { trigger: 'axis' },
  grid: { top: 40, left: 40, right: 20, bottom: 40 },
  xAxis: {
    type: 'category',
    data: ['-7m', '-6m', '-5m', '-4m', '-3m', '-2m', '-1m'],
    boundaryGap: false,
  },
  yAxis: {
    type: 'value',
    name: 'msg/s',
  },
  series: [
    {
      name: 'msg/s',
      type: 'line',
      smooth: true,
      symbol: 'circle',
      symbolSize: 6,
      data: avgMsgChartData.value,
      areaStyle: {},
    },
  ],
}))

// Line chart: MQTT error messages in the last 5 minutes
const mqttErrorsLineOptions = computed(() => ({
  title: {
    text: 'Error messages received (last 5 minutes)',
    left: 'center',
    textStyle: { fontSize: 14 },
  },
  tooltip: { trigger: 'axis' },
  grid: { top: 40, left: 40, right: 20, bottom: 40 },
  xAxis: {
    type: 'category',
    data: ['-5m', '-4m', '-3m', '-2m', '-1m'],
    boundaryGap: false,
  },
  yAxis: {
    type: 'value',
    name: 'Messages',
  },
  series: [
    {
      name: 'Number of messages',
      type: 'line',
      smooth: true,
      symbol: 'circle',
      symbolSize: 6,
      data: receivedErrorsChartData.value,
      areaStyle: {},
    },
  ],
  color: '#f87979',
}))
</script>

<template>
  <!-- Charts -->
  <div>
    <div class="chart-wrapper">
      <v-chart :option="mqttMessagesLineOptions" autoresize />
    </div>
    <div class="chart-wrapper">
      <v-chart :option="mqttErrorsLineOptions" autoresize />
    </div>
  </div>
</template>

<style scoped>
.charts-row {
  display: grid;
  grid-template-columns: 1fr 2fr;
  justify-content: center;
}

.chart-wrapper {
  display: inline-block;
  width: 50%;
  height: 260px;
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
