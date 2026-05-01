<script setup>
import { NLayoutSider, NLayoutHeader, NMenu } from 'naive-ui'
import { computed, ref, onMounted } from 'vue'

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
    default: 30,
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

const windowWidth = ref(window.innerWidth)
const windowHeight = ref(window.innerHeight)

const resizeSidebar = () => {
  windowWidth.value = window.innerWidth
  windowHeight.value = window.innerHeight
  siderCollapsed.value = isMobile.value
}

const isMobile = computed(() => windowWidth.value < 1000)
const siderCollapsed = ref(isMobile.value)

onMounted(() => {
  window.addEventListener('resize', resizeSidebar)
})

// Needed to implement side bar collapse
function siderChange() {
  siderCollapsed.value = !siderCollapsed.value
}
</script>

<template>
  <n-layout-sider
    bordered
    collapse-mode="width"
    :collapsed-width="collapsedWidth"
    :width="width"
    show-trigger
    :show-collapsed-content="false"
    :collapsed="siderCollapsed"
    v-on:update:collapsed="siderChange"
  >
    <n-layout-header class="app-sider-title">
      {{ title }}
    </n-layout-header>

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
