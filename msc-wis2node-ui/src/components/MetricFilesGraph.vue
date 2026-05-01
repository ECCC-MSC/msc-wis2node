<script setup>
// Vue
import { computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useDataDistributionMetrics } from '../stores/useDataDistributionMetrics'

// Naive UI
import { NSelect } from 'naive-ui'

// vue-echarts / echarts
import { use } from 'echarts/core'
import VChart from 'vue-echarts'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, TitleComponent } from 'echarts/components'

// Register only what we need
use([CanvasRenderer, LineChart, GridComponent, TooltipComponent, TitleComponent])

// Metrics store
const metricsStore = useDataDistributionMetrics()
const {
  dropdownDatasetOptions,
  metricDataJson,
  fileTotals,
  sizeTotals,
  dataTypeOptions,
  selectedMetric,
  selectedDataset,
} = storeToRefs(metricsStore)
const { gigabyteCalc } = metricsStore

const metricFilesLineOptions = computed(() => ({
  title: {
    text: 'Metric Files Data',
    left: 'center',
    textStyle: { fontSize: 14 },
  },
  tooltip: { trigger: 'axis' },
  grid: { top: 40, left: 40, right: 20, bottom: 40 },
  xAxis: {
    type: 'category',
    data: Object.keys(metricDataJson.value),
    boundaryGap: false,
  },
  yAxis: {
    type: 'value',
    name: metricGraphValues.value['units'],
  },
  series: [
    {
      name: metricGraphValues.value['chartHoverDesc'],
      type: 'line',
      smooth: true,
      symbol: 'circle',
      symbolSize: 6,
      data: metricGraphValues.value['graphValues'],
      areaStyle: {},
    },
  ],
  color: '#008000',
}))

const metricGraphValues = computed(() => {
  let graphUnits = ''
  let hoverDesc = ''
  if (selectedMetric.value === 'Size') {
    graphUnits = 'Gigabytes published'
    hoverDesc = 'Gigabytes published'
  } else {
    graphUnits = 'Number of files'
    hoverDesc = 'Number of files'
  }

  if (selectedDataset.value === 'total') {
    if (selectedMetric.value === 'Size') {
      return {
        graphValues: sizeTotals.value,
        units: graphUnits,
        chartHoverDesc: hoverDesc,
      }
    } else {
      return {
        graphValues: fileTotals.value,
        units: graphUnits,
        chartHoverDesc: hoverDesc,
      }
    }
  }

  // Need to compute the values for the selected dataset
  let values = []
  for (let date of Object.keys(metricDataJson.value)) {
    if (selectedDataset.value in metricDataJson.value[date]) {
      if (selectedMetric.value === 'Size') {
        let foundSize = metricDataJson.value[date][selectedDataset.value].bytes.slice(0, -3)
        let foundUnits = metricDataJson.value[date][selectedDataset.value].bytes.slice(-2)
        values.push(gigabyteCalc(foundSize, foundUnits))
      } else {
        values.push(metricDataJson.value[date][selectedDataset.value].files)
      }
    } else {
      // Dataset does not have values for the specific date
      values.push(0)
    }
  }

  return {
    graphValues: values,
    units: graphUnits,
    chartHoverDesc: hoverDesc,
  }
})
</script>

<template>
  <div>
    <div class="chart-wrapper">
      <v-chart :option="metricFilesLineOptions" autoresize />
    </div>
    <div>
      <span>Metric: </span>
      <n-select
        v-model:value="selectedMetric"
        :options="dataTypeOptions"
        class="dropdown-content"
      />
      <span>Selected dataset: </span>
      <n-select v-model:value="selectedDataset" :options="dropdownDatasetOptions" />
    </div>
  </div>
</template>

<style scoped>
.chart-wrapper {
  height: 350px;
}

.dropdown-content {
  margin-bottom: 1em;
}
</style>
