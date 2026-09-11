import { defineStore } from 'pinia'
import { ref } from 'vue'
import mqtt from 'mqtt'

const MQTT_BROKER = import.meta.env.VITE_BROKER_URL
const MQTT_TOPIC_ERRORS = import.meta.env.VITE_TOPIC_ERRORS

const options = {
  username: import.meta.env.VITE_BROKER_USERNAME,
  password: import.meta.env.VITE_BROKER_PASSWORD,
  keepalive: 60,
  protocolVersion: 5,
  reconnectPeriod: 1000,
  connectTimeout: 30 * 1000,
}

export const useErrorMsg = defineStore('errors', () => {
  // Values associated with the n-grid-items
  // error statistics on Overview page
  const totalNumErrors = ref(0)
  const totalElapsedTime = ref(0)

  const receivedErrorsChartData = ref([0, 0, 0, 0, 0])
  const numErrorsInMin = ref(0)

  const errorsList = ref([]) // Errors used in the Monitoring page

  // Connect and subscribe to the error notifications service
  const monitorClient = mqtt.connect(MQTT_BROKER, options)
  monitorClient.on('connect', function () {
    monitorClient.subscribe(MQTT_TOPIC_ERRORS, function (err) {
      if (!err) {
        console.debug('Connected for monitoring!')
      }
    })
  })
  monitorClient.on('error', (err) => {
    console.error('Connection error: ', err)
    monitorClient.end()
  })
  monitorClient.on('reconnect', () => {
    console.error('Reconnecting...')
  })
  monitorClient.on('message', function (topic, message) {
    try {
      const monitorContent = JSON.parse(message.toString())
      const invalidStatus = ['WARNING', 'ERROR', 'CRITICAL']
      if (
        'data' in monitorContent &&
        'severity' in monitorContent.data &&
        invalidStatus.includes(monitorContent.data.severity) &&
        'content' in monitorContent.data &&
        'title' in monitorContent.data.content
      ) {
        totalNumErrors.value = totalNumErrors.value + 1
        numErrorsInMin.value = numErrorsInMin.value + 1
        monitorContent.timeElapsed = `Time elapsed: 0 mins`
        errorsList.value.unshift(monitorContent)
      }
    } catch {
      console.error('Unexpected format detected for received error message')
    }
  })

  function incrementErrorMins() {
    totalElapsedTime.value = totalElapsedTime.value + 1

    const currentTime = new Date()
    for (const error of errorsList.value) {
      if ('timeElapsed' in error) {
        const postedTime = new Date(error.time)
        const timeDifference = currentTime - postedTime
        if (timeDifference / (1000 * 60 * 60) >= 1) {
          // At least 1 hour since error was first posted
          const timeRoundedDownHrs = Math.floor(timeDifference / (1000 * 60 * 60))
          error.timeElapsed = `Time elapsed: ${timeRoundedDownHrs} hrs`
        } else {
          const timeRoundedDownMins = Math.floor(timeDifference / (1000 * 60))
          error.timeElapsed = `Time elapsed: ${timeRoundedDownMins} mins`
        }
      }
    }

    // Shift over values of Received Errors graph
    const receivedErrorsLength = receivedErrorsChartData.value.length
    for (let x = 0; x < receivedErrorsLength; x++) {
      if (x + 1 === receivedErrorsChartData.value.length) {
        receivedErrorsChartData.value[x] = numErrorsInMin.value
      } else {
        receivedErrorsChartData.value[x] = receivedErrorsChartData.value[x + 1]
      }
    }
    numErrorsInMin.value = 0
  }
  setInterval(incrementErrorMins, 60000)

  function lessThanLimit(err) {
    const currentTime = new Date()
    const postedTime = new Date(err.time)
    const timeDifference = currentTime - postedTime
    return (timeDifference / (1000 * 60 * 60 * 24) <= 7)
  }

  function updateStoredErrorsHourly() {
    // Need to remove errors older than 7 days
    errorsList.value = errorsList.value.filter(lessThanLimit)
    totalNumErrors.value = errorsList.value.length
  }
  setInterval(updateStoredErrorsHourly, 3600000)

  function resetElapsedTimeDaily() {
    totalElapsedTime.value = 0
  }
  setInterval(resetElapsedTimeDaily, 86400000)
  return {
    totalNumErrors,
    totalElapsedTime,
    receivedErrorsChartData,
    errorsList,
  }
})
