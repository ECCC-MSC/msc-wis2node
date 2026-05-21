// useDataDistributionMetrics.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { DateTime } from 'luxon'

const baseUrl = import.meta.env.VITE_DATA_DISTRIBUTION_METRICS_URL

export const useDataDistributionMetrics = defineStore('metrics', () => {
  // State
  const metricsBaseUrl = ref(baseUrl || '')
  const files = ref([]) // list of JSON file names or URLs
  const selectedFile = ref(null) // the currently selected file name
  const selectedFileData = ref(null) // parsed JSON of the selected file
  const loadingList = ref(false)
  const loadingFile = ref(false)
  const error = ref(null)

  const errorsList = ref([]) // Errors used in the Monitoring page

  // Getters
  const hasData = computed(() => !!selectedFileData.value)

  // Data and reference keys from metric files
  // Used for the Metric File Data graph and table

  // Json for storing all metric data in the form
  // {date_1: {title_1: {metric data}, ..., total: {metric data}, ...} }
  const metricDataJson = ref({})

  // List of total accumulated file sizes and number of files
  // for each dataset. Loaded on startup
  const metricFileTableTotals = ref([])

  // For checking if a dataset is found for the first
  // time, and if the data has been loaded in yet
  const availableDatasets = ref([])

  // Totals for initial graphs for all datasets across all dates

  // List recording file size totals. Each entry is a different data
  const sizeTotals = ref([])
  // List recording total number of files. Each entry is a different data
  const fileTotals = ref([])

  // For keeping track of selected and available dates for the metric files
  const startAndEndDates = ref([DateTime.now(), DateTime.now()])
  const minDate = ref(DateTime.now())
  const maxDate = ref(DateTime.now())
  const selectedStartDate = ref(false)

  // For storing selectable options of the Metrics File Data graph
  const dropdownDatasetOptions = ref([{ label: 'All Datasets', value: 'total' }])
  const dataTypeOptions = ref([
    {
      label: 'Number of files',
      value: 'Files',
    },
    {
      label: 'Gigabytes published',
      value: 'Size',
    },
  ])

  // For initialializing selected options of the
  // Metrics File Data graph on startup
  const selectedMetric = ref('Files')
  const selectedDataset = ref('total')

  const metricFileTableData = ref([])
  const selectedTab = ref('graph')
  const lastLoad = ref() // Visual indicator of when metric files data was retrieved

  // Actions

  // Fetch list of JSON files by scraping the HTML index
  async function fetchFileList() {
    lastLoad.value = new Date().toLocaleString()
    if (!metricsBaseUrl.value) {
      error.value = 'VITE_DATA_DISTRIBUTION_METRICS_URL is not configured.'
      return
    }

    loadingList.value = true
    error.value = null

    try {
      // Get the HTML directory listing
      const res = await fetch(metricsBaseUrl.value)

      if (!res.ok) {
        throw new Error(`Failed to fetch file list: ${res.status} ${res.statusText}`)
      }

      const html = await res.text()

      // Parse HTML and extract <a> tags pointing to *.json
      const parser = new DOMParser()
      const doc = parser.parseFromString(html, 'text/html')
      const anchors = Array.from(doc.querySelectorAll('a'))

      const jsonFiles = anchors
        .map((a) => a.getAttribute('href') || '')
        .filter((href) => href.endsWith('.json'))
        // normalize in case of full URLs or paths; keep just filename
        .map((href) => href.split('/').filter(Boolean).pop())
        .filter(Boolean)

      // Ensure files contain data. Each file represents 1 date
      let filesToUse = []
      for (const file of jsonFiles) {
        const url = `${metricsBaseUrl.value}/${file}`
        const datekey = file.slice(0, -5)
        const res = await fetch(url)
        const resContentLen = Number(res.headers.get('content-length'))

        if (res.ok && resContentLen > 0) {
          if (selectedStartDate.value === false) {
            minDate.value = DateTime.fromISO(datekey)
            selectedStartDate.value = true
          }

          // Update to keep track of the upper bound of dates
          maxDate.value = DateTime.fromISO(datekey)

          const data = await res.json()
          metricDataJson.value[datekey] = {}
          const keys = Object.keys(data)
          for (let key of keys) {
            const datasetName = data[key].title

            let size = data[key].bytes.slice(0, -3)
            let units = data[key].bytes.slice(-2)
            let gbUsed = gigabyteCalc(size, units)
            if (key !== 'total') {
              metricDataJson.value[datekey][datasetName] = data[key]

              if (!availableDatasets.value.includes(datasetName)) {
                availableDatasets.value.push(datasetName)
                dropdownDatasetOptions.value.push({
                  label: datasetName,
                  value: datasetName,
                })
                // We then add it to the overall dataset
                metricFileTableTotals.value.push({
                  dataset: datasetName,
                  size: gbUsed,
                  files: data[key].files,
                })
              } else {
                // Already added to metricFileTableTotals, get its index and update values accordingly
                const index = metricFileTableTotals.value.findIndex(
                  (dataset) => dataset.dataset === datasetName,
                )
                metricFileTableTotals.value[index].size += gbUsed
                metricFileTableTotals.value[index].files += data[key].files
              }
            } else {
              // For total values of the date
              metricDataJson.value[datekey]['total'] = data[key]
              fileTotals.value.push(data[key].files)
              sizeTotals.value.push(gbUsed)
            }
          }

          filesToUse.push(file)
        } else {
          console.warn(`Metric file missing data at ${url}`)
        }
      }

      // Sort files by data size
      metricFileTableTotals.value.sort((a, b) => b.size - a.size)
      metricFileTableData.value = metricFileTableTotals.value
      filesToUse.sort()
      files.value = filesToUse

      // Change the default values of the dates to the max range available
      startAndEndDates.value = [minDate.value, maxDate.value]
    } catch (e) {
      error.value = e instanceof Error ? e.message : String(e)
      files.value = []
    } finally {
      loadingList.value = false
    }
  }

  // Helper function for date selection option of
  // metric files table
  async function obtainTableResults(dates) {
    let results = []
    let addedDatasets = []
    for (let date of dates) {
      if (Object.keys(metricDataJson.value).includes(date)) {
        const url = `${metricsBaseUrl.value}/${date}.json`
        const res = await fetch(url)
        if (res.ok) {
          const data = await res.json()
          const keys = Object.keys(data)
          for (let key of keys) {
            let size = data[key].bytes.slice(0, -3)
            let units = data[key].bytes.slice(-2)
            let gbUsed = gigabyteCalc(size, units)

            const datasetName = data[key].title

            if (key !== 'total') {
              if (!addedDatasets.includes(datasetName)) {
                addedDatasets.push(datasetName)
                results.push({
                  dataset: datasetName,
                  size: gbUsed,
                  files: data[key].files,
                })
              } else {
                const index = results.findIndex((dataset) => dataset.dataset === datasetName)
                results[index].size = results[index].size + gbUsed
                results[index].files = results[index].files + data[key].files
              }
            }
          }
        }
      }
    }
    // Sort results by size before returning
    results.sort((a, b) => b.size - a.size)
    return results
  }

  function gigabyteCalc(size, units) {
    let gbUsed = 0
    if (units === 'Gb') {
      gbUsed = Number(size)
    } else if (units === 'Mb') {
      gbUsed = Number(size) / 1000
    } else {
      // kb
      gbUsed = Number(size) / 1e6
    }
    return gbUsed
  }

  // Fetch a specific JSON file and store its content
  async function fetchFile(name) {
    if (!metricsBaseUrl.value) {
      error.value = 'VITE_DATA_DISTRIBUTION_METRICS_URL is not configured.'
      return
    }
    if (!name) {
      error.value = 'No file name specified.'
      return
    }

    loadingFile.value = true
    error.value = null

    try {
      const url = `${metricsBaseUrl.value}/${name}`
      const res = await fetch(url)

      if (!res.ok) {
        throw new Error(`Failed to fetch file ${name}: ${res.status} ${res.statusText}`)
      }

      const data = await res.json()
      selectedFile.value = name
      selectedFileData.value = data
    } catch (e) {
      error.value = e instanceof Error ? e.message : String(e)
      selectedFileData.value = null
    } finally {
      loadingFile.value = false
    }
  }

  // Convenience method: get raw JSON as a pretty string
  const rawJson = computed(() =>
    selectedFileData.value ? JSON.stringify(selectedFileData.value, null, 2) : '',
  )

  async function refresh() {
    selectedStartDate.value = false
    metricDataJson.value = {}
    availableDatasets.value = []
    dropdownDatasetOptions.value = [{ label: 'All Datasets', value: 'total' }]
    metricFileTableTotals.value = []
    fileTotals.value = []
    sizeTotals.value = []
    await fetchFileList()

    const latest = files.value[files.value.length - 1]
    await fetchFile(latest)
  }

  return {
    // state
    metricsBaseUrl,
    files,
    selectedFile,
    selectedFileData,
    loadingList,
    loadingFile,
    error,

    errorsList,

    // getters
    hasData,
    rawJson,

    // actions
    fetchFileList,
    fetchFile,
    refresh,
    obtainTableResults,
    gigabyteCalc,

    // Data and reference keys from metric files
    // Used for the Metric File Data graph and table
    metricDataJson,
    metricFileTableTotals,
    availableDatasets,

    // Totals for initial graphs for all datasets across
    // all dates
    sizeTotals,
    fileTotals,

    // For keeping track of selected and available dates for the metric files
    startAndEndDates,
    minDate,
    maxDate,

    // For storing selectable options of the Metrics File Data graph
    dropdownDatasetOptions,
    dataTypeOptions,

    // For initialializing selected options of the
    // Metrics File Data graph on startup
    selectedMetric,
    selectedDataset,

    metricFileTableData,
    selectedTab,
    lastLoad,
  }
})
