<script setup>
// Naive UI
import { NConfigProvider, darkTheme } from 'naive-ui'
import { NLayout } from 'naive-ui'
import { useRouter, useRoute } from 'vue-router'

import { storeToRefs } from 'pinia'

// Vue
import { ref, computed, onMounted, h } from 'vue'
import { useDataDistributionMetrics } from './stores/useDataDistributionMetrics'
import { useNotifMsg } from './stores/useNotifMsg'
import { useErrorMsg } from './stores/useErrorMsg'
import { useDarkTheme } from './stores/useDarkTheme'

// Local components
import AppSidebar from './components/AppSidebar.vue'
import AppHeader from './components/AppHeader.vue'

import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { faHouse } from '@fortawesome/free-solid-svg-icons'
import { faEye } from '@fortawesome/free-solid-svg-icons'

const metricsStore = useDataDistributionMetrics()
const { availableDatasets, files, selectedFile } = storeToRefs(metricsStore)
const { fetchFileList, fetchFile } = metricsStore
const router = useRouter()

useNotifMsg()
useErrorMsg()

// Dark mode handling
const darkThemeStore = useDarkTheme()
const { isDark } = storeToRefs(darkThemeStore)
const { toggleTheme } = darkThemeStore

const themeSwitcher = computed(() => (isDark.value ? darkTheme : null))

// sidebar menu options for MQTT dashboard
const menuOptions = [
  {
    label: 'Overview',
    key: '/',
    icon: () => h(FontAwesomeIcon, { icon: faHouse }),
  },
  {
    label: 'Monitoring',
    key: '/monitoring',
    icon: () => h(FontAwesomeIcon, { icon: faEye }),
  },
]
const route = useRoute()

const activeKey = ref('')

function nav() {
  router.push(activeKey.value)
}

onMounted(async () => {
  if (availableDatasets.value.length === 0) {
    await fetchFileList()
  }
  if (files.value.length > 0 && !selectedFile.value) {
    const latest = files.value[files.value.length - 1]
    await fetchFile(latest)
  }
  activeKey.value = route.path
})
</script>

<template>
  <n-config-provider :theme="themeSwitcher">
    <n-layout has-sider class="app-layout">
      <!-- SIDEBAR COMPONENT -->
      <AppSidebar
        v-model:value="activeKey"
        :options="menuOptions"
        title="msc-wis2node-ui"
        @update:value="nav()"
      />

      <!-- MAIN AREA -->
      <n-layout>
        <!-- HEADER COMPONENT -->
        <AppHeader
          :is-dark="isDark"
          title="Metrics Dashboard"
          subtitle="Live metrics for msc-wis2node"
          @toggle-theme="toggleTheme"
        />

        <main>
          <RouterView />
        </main>
      </n-layout>
    </n-layout>
  </n-config-provider>
</template>

<style scoped>
.app-layout {
  /* let Naive UI handle header/sider sizing;
     we just want full viewport height */
  min-height: 100vh;
}

/* Only keep minimal presentation styles that Naive UI
   doesn't provide out of the box */
.app-content {
  padding: 8px;
}

/* Stat cards */
.stat-value {
  font-size: 28px;
  font-weight: 600;
  margin-top: 8px;
}

/* Activity section */
.activity-card {
  margin-top: 24px;
}

.activity-text {
  margin: 0 0 16px;
}
</style>
