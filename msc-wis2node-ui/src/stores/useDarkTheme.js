import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useDarkTheme = defineStore('themes', () => {
  const isDark = ref(true)
  const toggleTheme = () => {
    isDark.value = !isDark.value
  }
  return {
    isDark,
    toggleTheme,
  }
})
