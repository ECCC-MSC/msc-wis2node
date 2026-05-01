<script setup>
// Vue
import { storeToRefs } from 'pinia'
import { useDataDistributionMetrics } from '../stores/useDataDistributionMetrics'

// Naive UI
import { NDataTable, NDatePicker } from 'naive-ui'

import { DateTime } from 'luxon'

// Metrics store
const metricsStore = useDataDistributionMetrics()
const { metricFileTableTotals, minDate, maxDate, startAndEndDates, metricFileTableData } =
  storeToRefs(metricsStore)
const { obtainTableResults } = metricsStore

// Column data for the Metric File Data table
const columns = [
  {
    title: 'Dataset',
    key: 'dataset',
    resizable: true,
  },
  {
    title: 'Gigabytes published',
    key: 'size',
    sorter: (row1, row2) => row1.size - row2.size,
    resizable: true,
  },
  {
    title: 'Files',
    key: 'files',
    sorter: (row1, row2) => row1.files - row2.files,
    resizable: true,
  },
]

function disableInvalidDates(ts) {
  // Need to ensure first that the date is not below the min allowed date
  // and not higher than the max date

  // Return True to disable date
  if (typeof ts === 'object') {
    // Default, not a problem
    return false
  }
  let newDate = DateTime.fromMillis(ts)
  if (newDate < minDate.value || newDate > maxDate.value) {
    return true
  }
  return false
}

async function updateData(newVal) {
  if (typeof newVal[0] === 'number') {
    // Convert the obtained milliseconds to DateTime
    let newStart = DateTime.fromMillis(newVal[0])
    let newEnd = DateTime.fromMillis(newVal[1])
    if (
      newStart.toFormat('yyyy-MM-dd') === minDate.value.toFormat('yyyy-MM-dd') &&
      newEnd.toFormat('yyyy-MM-dd') === maxDate.value.toFormat('yyyy-MM-dd')
    ) {
      // Have the table display all the data
      metricFileTableData.value = metricFileTableTotals.value
    } else {
      // Need to sum up values for individual dates of each dataset

      // Build an array of dates to check for data
      let diff = newEnd.diff(newStart, 'days').toObject()['days']
      let datesToCheck = []
      let datesToAdd = Array.from({ length: diff + 1 }, (v, i) => i)
      datesToAdd.forEach((elem) => {
        datesToCheck.push(newStart.plus({ days: elem }).toFormat('yyyy-MM-dd'))
      })

      // Next, need to use this list to fill in a list of results
      let result = await obtainTableResults(datesToCheck)
      metricFileTableData.value = result
    }
  }
}
</script>

<template>
  <div>
    <n-data-table
      :columns="columns"
      :data="metricFileTableData"
      :max-height="300"
      :bordered="false"
      class="dataset-table"
    />
    <span>Selected Date Range:</span>
    <n-date-picker
      v-model:value="startAndEndDates"
      type="daterange"
      :is-date-disabled="disableInvalidDates"
      @update:value="updateData"
      clearable
    />
  </div>
</template>

<style scoped>
.dataset-table {
  margin-bottom: 1em;
}
</style>
