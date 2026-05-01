import { defineStore } from 'pinia'
import { ref } from 'vue'
import mqtt from 'mqtt'

const MQTT_BROKER = import.meta.env.VITE_BROKER_URL
const MQTT_TOPIC_NOTIFICATION = import.meta.env.VITE_TOPIC_NOTIFICATION

const options = {
  username: import.meta.env.VITE_BROKER_USERNAME,
  password: import.meta.env.VITE_BROKER_PASSWORD,
  keepalive: 60,
  protocolVersion: 5,
  reconnectPeriod: 1000,
  connectTimeout: 30 * 1000,
}

export const useNotifMsg = defineStore('notifs', () => {
  // Values associated with the n-grid-items
  // notification statistics on Overview page
  const totalNumMsg = ref(0)
  const currMinNumMsg = ref(0)
  const avgMessages = ref(0)
  const timeUntilUpdate = ref(60)

  const avgMsgChartData = ref([0, 0, 0, 0, 0, 0, 0])

  // Connect and subscribe to notifications service
  const notifClient = mqtt.connect(MQTT_BROKER, options)
  notifClient.on('connect', function () {
    notifClient.subscribe(MQTT_TOPIC_NOTIFICATION, function (err) {
      if (!err) {
        console.debug('Connected for notifications!')
      }
    })
  })
  notifClient.on('error', (err) => {
    console.error('Connection error: ', err)
    notifClient.end()
  })
  notifClient.on('reconnect', () => {
    console.error('Reconnecting...')
  })
  notifClient.on('message', function () {
    currMinNumMsg.value = currMinNumMsg.value + 1
    totalNumMsg.value = totalNumMsg.value + 1
  })

  // Update the msg/s value every min
  function msgPerSecCalc() {
    avgMessages.value = Math.round(currMinNumMsg.value / 60)
    currMinNumMsg.value = 0
    timeUntilUpdate.value = 60

    // Shifting over values of notif/s graph
    for (let i = 0; i < avgMsgChartData.value.length; i++) {
      if (i + 1 === avgMsgChartData.value.length) {
        avgMsgChartData.value[i] = avgMessages.value
      } else {
        avgMsgChartData.value[i] = avgMsgChartData.value[i + 1]
      }
    }
  }
  setInterval(msgPerSecCalc, 60000)

  function countDown() {
    if (timeUntilUpdate.value > 0) {
      timeUntilUpdate.value = timeUntilUpdate.value - 1
    }
  }
  setInterval(countDown, 1000)

  return {
    totalNumMsg,
    currMinNumMsg,
    avgMessages,
    timeUntilUpdate,
    avgMsgChartData,
  }
})
