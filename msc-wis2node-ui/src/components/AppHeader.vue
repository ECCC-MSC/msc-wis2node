<script setup>
import { NLayoutHeader, NButton, NIcon, NSpace, NText } from 'naive-ui'
import { SunnyOutline, MoonOutline } from '@vicons/ionicons5'

const props = defineProps({
  title: {
    type: String,
    default: 'Dashboard',
  },
  subtitle: {
    type: String,
    default: 'Simple Naive UI starter dashboard',
  },
  isDark: {
    type: Boolean,
    required: true,
  },
})

const emit = defineEmits(['toggle-theme'])

const handleToggle = () => {
  emit('toggle-theme')
}
</script>

<template>
  <n-layout-header bordered class="app-header">
    <div class="app-header-left">
      <h2 class="app-header-title">{{ title }}</h2>
      <n-text depth="3">{{ subtitle }}</n-text>
    </div>

    <n-space align="center">
      <n-button quaternary @click="handleToggle">
        <n-icon size="18" class="theme-toggle-icon">
          <component :is="isDark ? SunnyOutline : MoonOutline" />
        </n-icon>
        {{ isDark ? 'Light' : 'Dark' }} mode
      </n-button>
    </n-space>
  </n-layout-header>
</template>

<style scoped>
.app-header {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
}

.app-header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.app-header-title {
  margin: 0;
}

.theme-toggle-icon {
  margin-right: 6px;
}
</style>
