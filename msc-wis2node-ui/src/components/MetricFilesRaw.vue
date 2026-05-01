<script setup>
// Vue
import { computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useDataDistributionMetrics } from '../stores/useDataDistributionMetrics'
import { useDarkTheme } from '@/stores/useDarkTheme'

import '../../node_modules/pretty-print-json/dist/css/pretty-print-json.css'
import { prettyPrintJson } from 'pretty-print-json'

// Naive UI
import { NCard, NSpace, NButton, NTag, NText, NScrollbar } from 'naive-ui'

// vue-echarts / echarts
import { use } from 'echarts/core'
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

// Metrics store
const metricsStore = useDataDistributionMetrics()
const { files, selectedFile, rawJson, loadingList, loadingFile, error, selectedFileData } =
  storeToRefs(metricsStore)
const { fetchFile } = metricsStore

const darkThemeStore = useDarkTheme()
const { isDark } = storeToRefs(darkThemeStore)

const selectedFileLabel = computed(() =>
  selectedFile.value ? `Selected file: ${selectedFile.value}` : 'No file selected',
)

function addColour(json) {
  return prettyPrintJson.toHtml(json)
}
const highlightedJson = computed(() => addColour(selectedFileData.value))
</script>

<template>
  <!-- Metrics / files panel -->
  <n-card size="large" class="metrics-card" title="Metric Files">
    <!-- Header row -->
    <n-space justify="space-between" align="center" class="metrics-header">
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
            <n-tag v-if="file === selectedFile" size="tiny" type="success"> selected </n-tag>
          </n-space>
        </n-button>
      </n-space>
    </div>
    <n-text v-else-if="!loadingList && !error" depth="3"> No metric files found. </n-text>

    <!-- Raw JSON view -->
    <div v-if="rawJson" class="metrics-raw-json">
      <n-text strong>Raw JSON</n-text>
      <n-scrollbar style="max-height: 240px; margin-top: 8px; white-space: pre-wrap">
        <pre
          :class="{ 'dark-mode': isDark }"
          style="white-space: pre-wrap"
          v-html="highlightedJson"
        ></pre>
      </n-scrollbar>
    </div>
  </n-card>
</template>

<style scoped>
/* Metrics panel */
.metrics-card {
  margin-top: 8px;
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
  font-size: 0.8em;
  white-space: pre-wrap;
}
</style>
