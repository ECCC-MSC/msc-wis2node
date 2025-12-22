// useDataDistributionMetrics.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

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

  // Getters
  const hasData = computed(() => !!selectedFileData.value)

  // Actions

  // Fetch list of JSON files by scraping the HTML index
  async function fetchFileList() {
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

      // Optional: sort filenames (directory listing might already be sorted)
      jsonFiles.sort()

      files.value = jsonFiles
    } catch (e) {
      error.value = e instanceof Error ? e.message : String(e)
      files.value = []
    } finally {
      loadingList.value = false
    }
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

  return {
    // state
    metricsBaseUrl,
    files,
    selectedFile,
    selectedFileData,
    loadingList,
    loadingFile,
    error,

    // getters
    hasData,
    rawJson,

    // actions
    fetchFileList,
    fetchFile,
  }
})
