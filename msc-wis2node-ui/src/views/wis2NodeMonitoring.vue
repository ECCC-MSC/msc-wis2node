<script setup>
// Need to grab errors from the store. The time, subject, severity and description (message)
// of the error will be displayed in the table.
import { storeToRefs } from 'pinia'
import { useDarkTheme } from '@/stores/useDarkTheme'
import { useErrorMsg } from '@/stores/useErrorMsg'
import { NButton, NDataTable, NModal, NCard, NTag } from 'naive-ui'
import { h, ref, computed } from 'vue'
import { prettyPrintJson } from 'pretty-print-json'
import '../../node_modules/pretty-print-json/dist/css/pretty-print-json.css'

const darkThemeStore = useDarkTheme()
const { isDark } = storeToRefs(darkThemeStore)

const errorsStore = useErrorMsg()
const { errorsList } = storeToRefs(errorsStore)

const showModal = ref(false)
const selectedModal = ref()
const columns = [
  {
    title: 'Time',
    key: 'time',
    resizable: true,
    render(row) {
      let timePosted = h('span', row.time + ' ')
      let timeElapsed = h(
        NTag,
        {
          style: {
            marginRight: '6px',
          },
          type: 'info',
          bordered: false,
        },
        {
          default: () => row.timeElapsed,
        },
      )
      return [timePosted, timeElapsed]
    },
  },
  {
    title: 'Subject',
    key: 'subject',
    ellipsis: {
      tooltip: true,
    },
  },
  {
    title: 'Severity',
    key: 'data.severity',
  },
  {
    title: 'Description',
    key: 'data.content.title',
    ellipsis: {
      tooltip: true,
    },
  },
  {
    title: 'JSON',
    key: 'json',
    render(row) {
      return h(
        NButton,
        {
          size: 'small',
          onClick: () => {
            let rowCopy = { ...row }
            delete rowCopy.timeElapsed
            selectedModal.value = rowCopy
            showModal.value = true
          },
        },
        { default: () => 'Display as JSON' },
      )
    },
  },
]

function addColour(json) {
  return prettyPrintJson.toHtml(json)
}
const highlightedJson = computed(() => addColour(selectedModal.value))

const pagination = {
  pageSize: 15,
}
</script>

<template>
  <h1>List of errors</h1>

  <pre id="account" class="json-container"></pre>

  <div id="myModal" class="dark-mode">
    <n-modal class="json-container" v-model:show="showModal" title="My Modal" style="width: 1500px">
      <n-card>
        <div
          :class="{ 'dark-mode': isDark }"
          style="white-space: pre-wrap"
          v-html="highlightedJson"
        ></div>
        <n-button @click="showModal = false">Close</n-button>
      </n-card>
    </n-modal>
  </div>
  <div>
    <n-data-table
      size="small"
      :columns="columns"
      :data="errorsList"
      :pagination="pagination"
      :bordered="false"
    />
  </div>
</template>
