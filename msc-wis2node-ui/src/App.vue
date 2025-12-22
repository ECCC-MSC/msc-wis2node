<script setup>
// Naive UI
import { NConfigProvider, darkTheme } from 'naive-ui'
import { NLayout, NLayoutContent } from 'naive-ui'
import { NGrid, NGridItem, NText, NCard } from 'naive-ui'

// Vue
import { ref, computed } from 'vue'

// Local components
import AppSidebar from './components/AppSidebar.vue'
import AppHeader from './components/AppHeader.vue'
import ActivityCharts from './components/ActivityCharts.vue'

// Dark mode handling
const isDark = ref(true)
const themeSwitcher = computed(() => (isDark.value ? darkTheme : null))
const toggleTheme = () => {
  isDark.value = !isDark.value
}

// sidebar menu options for MQTT dashboard
const menuOptions = [
  { label: 'Overview', key: 'overview' },
  { label: 'Topics', key: 'topics' },
  { label: 'Clients', key: 'clients' },
  { label: 'QoS & Retained', key: 'qos-retained' },
  { label: 'Errors & Drops', key: 'errors' },
]
const activeKey = ref('overview')

const dataDistributionMetricsUrl = import.meta.env.VITE_DATA_DISTRIBUTION_METRICS_URL
</script>

<template>
  <n-config-provider :theme="themeSwitcher">
    <n-layout has-sider class="app-layout">
      <!-- SIDEBAR COMPONENT -->
      <AppSidebar v-model:value="activeKey" :options="menuOptions" title="msc-wis2node-ui" />

      <!-- MAIN AREA -->
      <n-layout>
        <!-- HEADER COMPONENT -->
        <AppHeader
          :is-dark="isDark"
          title="Metrics Dashboard"
          subtitle="Live metrics for msc-wis2node"
          @toggle-theme="toggleTheme"
        />

        <!-- CONTENT -->
        <n-layout-content class="app-content">
          <!-- Top metrics -->
          <n-grid cols="1 600:2 1000:4" x-gap="16" y-gap="16">
            <!-- Topic name -->
            <n-grid-item>
              <n-card>
                <n-text depth="3">MQTT Topic</n-text>
                <div class="stat-value">wis2/obs/temperature</div>
                <n-text depth="3">Current subscription</n-text>
              </n-card>
            </n-grid-item>

            <!-- Messages per second -->
            <n-grid-item>
              <n-card>
                <n-text depth="3">Messages / Second</n-text>
                <div class="stat-value">152</div>
                <n-text depth="3">Averaged over last 60s</n-text>
              </n-card>
            </n-grid-item>

            <!-- Last message / latency -->
            <n-grid-item>
              <n-card>
                <n-text depth="3">Last Message</n-text>
                <div class="stat-value">0.42 s</div>
                <n-text depth="3">Age since last payload</n-text>
              </n-card>
            </n-grid-item>

            <!-- Errors / drops -->
            <n-grid-item>
              <n-card>
                <n-text depth="3">Dropped / Error Messages</n-text>
                <div class="stat-value">3</div>
                <n-text type="error">in the last 5 minutes</n-text>
              </n-card>
            </n-grid-item>
          </n-grid>

          <!-- Activity / charts -->
          <div class="activity-card">
            <n-card title="Activity" size="large">
              <p class="activity-text">
                This is where you can put charts, tables or detailed analytics.
              </p>
              <p>
                dataDistributionMetricsUrl:
                <code>{{ dataDistributionMetricsUrl }}</code>
              </p>

              <ActivityCharts />
            </n-card>
          </div>
        </n-layout-content>
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
  padding: 16px;
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
