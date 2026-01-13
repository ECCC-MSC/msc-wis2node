<script setup>
import { NLayoutSider, NMenu } from 'naive-ui'
import { computed } from 'vue'

// Props
const props = defineProps({
  value: {
    type: String,
    default: 'overview',
  },
  options: {
    type: Array,
    default: () => [],
  },
  width: {
    type: Number,
    default: 200,
  },
  collapsedWidth: {
    type: Number,
    default: 64,
  },
  title: {
    type: String,
    default: 'msc-wis2node-ui',
  },
})

// Emit update for v-model
const emit = defineEmits(['update:value'])

// v-model wrapper
const activeKey = computed({
  get: () => props.value,
  set: (val) => emit('update:value', val),
})
</script>

<template>
  <n-layout-sider
    bordered
    collapse-mode="width"
    :collapsed-width="collapsedWidth"
    :width="width"
    show-trigger
  >
    <div class="app-sider-title">
      {{ title }}
    </div>

    <n-menu v-model:value="activeKey" :options="options" />
  </n-layout-sider>
</template>

<style scoped>
.app-sider-title {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 18px;
}
</style>
