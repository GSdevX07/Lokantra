<template>
  <div class="main-view venom-theme">
    <!-- Header -->
    <header class="app-header">
      <div class="header-left">
        <div class="brand" @click="router.push('/home')"><img src="../assets/logo/lokantra_chrome_wordmark.png" alt="LOKĀNTRA" class="brand-wordmark" /></div>
      </div>
      


      <div class="header-right">
        
        <div class="workflow-step">
          <span class="step-num">Step 3/5</span>
          <span class="step-name">{{ $tm('main.stepNames')[2] }}</span>
        </div>
        <div class="step-divider"></div>
        <span class="status-indicator" :class="statusClass">
          <span class="dot"></span>
          {{ statusText }}
        </span>
      </div>
    </header>

    <!-- Main Content Area -->
    <main class="content-area" ref="contentAreaRef" :class="{ dragging: isDragging }">
      <!-- Left Panel: Graph -->
      <div class="panel-wrapper left" :style="{ width: `${leftPanelWidth}%` }">
        <GraphPanel 
          :graphData="graphData"
          :loading="graphLoading"
          :currentPhase="3"
          :isSimulating="isSimulating"
          @refresh="refreshGraph"
          @toggle-maximize="toggleMaximize('graph')"
        />
      </div>

      <!-- Middle Splitter -->
      <div class="splitter" @pointerdown.prevent="startDragging" aria-label="Resize panels" title="Drag to resize panels">
        <div class="splitter-grip"></div>
      </div>

      <!-- Right Panel: Step 3 Start Simulation -->
      <div class="panel-wrapper right" :style="{ width: `${100 - leftPanelWidth}%` }">
        <Step3Simulation
          :simulationId="currentSimulationId"
          :maxRounds="maxRounds"
          :minutesPerRound="minutesPerRound"
          :projectData="projectData"
          :graphData="graphData"
          :systemLogs="systemLogs"
          @go-back="handleGoBack"
          @next-step="handleNextStep"
          @add-log="addLog"
          @update-status="updateStatus"
        />
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import GraphPanel from '../components/GraphPanel.vue'
import Step3Simulation from '../components/Step3Simulation.vue'
import { getProject, getGraphData } from '../api/graph'
import { getSimulation, getSimulationConfig, stopSimulation, closeSimulationEnv, getEnvStatus } from '../api/simulation'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()

// Props
const props = defineProps({
  simulationId: String
})

const MIN_PANEL_WIDTH = 25
const MAX_PANEL_WIDTH = 75
const contentAreaRef = ref(null)
const leftPanelWidth = ref(50)
const isDragging = ref(false)
const dragStartX = ref(0)
const dragStartWidth = ref(50)
const animationFrame = ref(null)

const clampPanelWidth = (value) => Math.min(MAX_PANEL_WIDTH, Math.max(MIN_PANEL_WIDTH, value))

const applyPanelWidth = (nextWidth) => {
  if (animationFrame.value) cancelAnimationFrame(animationFrame.value)
  animationFrame.value = requestAnimationFrame(() => {
    leftPanelWidth.value = clampPanelWidth(nextWidth)
    animationFrame.value = null
  })
}

const startDragging = (event) => {
  if (!contentAreaRef.value) return
  isDragging.value = true
  dragStartX.value = event.clientX
  dragStartWidth.value = leftPanelWidth.value

  window.addEventListener('pointermove', handleDrag)
  window.addEventListener('pointerup', stopDragging)
  window.addEventListener('pointercancel', stopDragging)
}

const handleDrag = (event) => {
  if (!isDragging.value || !contentAreaRef.value) return
  const rect = contentAreaRef.value.getBoundingClientRect()
  const deltaPercent = ((event.clientX - dragStartX.value) / rect.width) * 100
  applyPanelWidth(dragStartWidth.value + deltaPercent)
}

const stopDragging = () => {
  isDragging.value = false
  if (animationFrame.value) {
    cancelAnimationFrame(animationFrame.value)
    animationFrame.value = null
  }
  window.removeEventListener('pointermove', handleDrag)
  window.removeEventListener('pointerup', stopDragging)
  window.removeEventListener('pointercancel', stopDragging)
}

// Data State
const currentSimulationId = ref(route.params.simulationId)
// Fetch maxRounds directly from query params during initialization to ensure child components have access immediately
const maxRounds = ref(route.query.maxRounds ? parseInt(route.query.maxRounds) : null)
const minutesPerRound = ref(30) // Default 30 minutes per round
const projectData = ref(null)
const graphData = ref(null)
const graphLoading = ref(false)
const systemLogs = ref([])
const currentStatus = ref('processing') // processing | completed | error



// --- Status Computed ---
const statusClass = computed(() => {
  return currentStatus.value
})

const statusText = computed(() => {
  if (currentStatus.value === 'error') return 'Error'
  if (currentStatus.value === 'completed') return 'Completed'
  return 'Running'
})

const isSimulating = computed(() => currentStatus.value === 'processing')

// --- Helpers ---
const addLog = (msg) => {
  const time = new Date().toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' }) + '.' + new Date().getMilliseconds().toString().padStart(3, '0')
  systemLogs.value.push({ time, msg })
  if (systemLogs.value.length > 200) {
    systemLogs.value.shift()
  }
}

const updateStatus = (status) => {
  currentStatus.value = status
}

// --- Layout Methods ---
const toggleMaximize = (target) => {
  if (target === 'graph') {
    leftPanelWidth.value = 68
  }
}

const handleGoBack = async () => {
  // Before returning to Step 2, close the running simulation
  addLog(t('log.preparingGoBack'))
  
  // Stop polling
  stopGraphRefresh()
  
  try {
    // Try graceful shutdown of simulation environment first
    const envStatusRes = await getEnvStatus({ simulation_id: currentSimulationId.value })
    
    if (envStatusRes.success && envStatusRes.data?.env_alive) {
      addLog(t('log.closingSimEnv'))
      try {
        await closeSimulationEnv({ 
          simulation_id: currentSimulationId.value,
          timeout: 10
        })
        addLog(t('log.simEnvClosed'))
      } catch (closeErr) {
        addLog(t('log.closeSimEnvFailed'))
        try {
          await stopSimulation({ simulation_id: currentSimulationId.value })
          addLog(t('log.simForceStopSuccess'))
        } catch (stopErr) {
          addLog(t('log.forceStopFailed', { error: stopErr.message }))
        }
      }
    } else {
      // Environment not running, check if process needs stopping
      if (isSimulating.value) {
        addLog(t('log.stoppingSimProcess'))
        try {
          await stopSimulation({ simulation_id: currentSimulationId.value })
          addLog(t('log.simStopped'))
        } catch (err) {
          addLog(t('log.stopSimFailed', { error: err.message }))
        }
      }
    }
  } catch (err) {
    addLog(t('log.checkStatusFailed', { error: err.message }))
  }
  
  // Return to Step 2 (Environment Setup)
  router.push({ name: 'Simulation', params: { simulationId: currentSimulationId.value } })
}

const handleNextStep = () => {
  // Step3Simulation component directly handles report generation and routing navigation
  // This method is kept as a fallback only
  addLog(t('log.enterStep4'))
}

// --- Data Logic ---
const loadSimulationData = async () => {
  try {
    addLog(t('log.loadingSimData', { id: currentSimulationId.value }))
    
    // Get simulation info
    const simRes = await getSimulation(currentSimulationId.value)
    if (simRes.success && simRes.data) {
      const simData = simRes.data
      
      // Get simulation config to obtain minutes_per_round
      try {
        const configRes = await getSimulationConfig(currentSimulationId.value)
        if (configRes.success && configRes.data?.time_config?.minutes_per_round) {
          minutesPerRound.value = configRes.data.time_config.minutes_per_round
          addLog(t('log.timeConfig', { minutes: minutesPerRound.value }))
        }
      } catch (configErr) {
        addLog(t('log.timeConfigFetchFailed', { minutes: minutesPerRound.value }))
      }
      
      // Get project info
      if (simData.project_id) {
        const projRes = await getProject(simData.project_id)
        if (projRes.success && projRes.data) {
          projectData.value = projRes.data
          addLog(t('log.projectLoadSuccess', { id: projRes.data.project_id }))
          
          // Get graph data
          if (projRes.data.graph_id) {
            await loadGraph(projRes.data.graph_id)
          }
        }
      }
    } else {
      addLog(t('log.loadSimDataFailed', { error: simRes.error || t('common.unknownError') }))
    }
  } catch (err) {
    addLog(t('log.loadException', { error: err.message }))
  }
}

const loadGraph = async (graphId) => {
  // During simulation, auto refresh does not show full-screen loading to avoid flicker
  // Show loading during manual refresh or initial load
  if (!isSimulating.value) {
    graphLoading.value = true
  }
  
  try {
    const res = await getGraphData(graphId)
    if (res.success) {
      graphData.value = res.data
      if (!isSimulating.value) {
        addLog(t('log.graphDataLoadSuccess'))
      }
    }
  } catch (err) {
    addLog(t('log.graphLoadFailed', { error: err.message }))
  } finally {
    graphLoading.value = false
  }
}

const refreshGraph = () => {
  if (projectData.value?.graph_id) {
    loadGraph(projectData.value.graph_id)
  }
}

// --- Auto Refresh Logic ---
let graphRefreshTimer = null

const startGraphRefresh = () => {
  if (graphRefreshTimer) return
  addLog(t('log.graphRealtimeRefreshStart'))
  // Refresh once immediately, then refresh every 30 seconds
  graphRefreshTimer = setInterval(refreshGraph, 30000)
}

const stopGraphRefresh = () => {
  if (graphRefreshTimer) {
    clearInterval(graphRefreshTimer)
    graphRefreshTimer = null
    addLog(t('log.graphRealtimeRefreshStop'))
  }
}

watch(isSimulating, (newValue) => {
  if (newValue) {
    startGraphRefresh()
  } else {
    stopGraphRefresh()
  }
}, { immediate: true })

onMounted(() => {
  addLog(t('log.simRunViewInit'))
  
  // Record maxRounds configuration (value already obtained from query params during init)
  if (maxRounds.value) {
    addLog(t('log.customRounds', { rounds: maxRounds.value }))
  }
  
  loadSimulationData()
})

onUnmounted(() => {
  stopGraphRefresh()
})
</script>

<style scoped>
.main-view {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: radial-gradient(circle at 50% 0%, #0d0d12 0%, #050507 50%, #000000 100%);
  color: #f5f5f7;
  overflow: hidden;
  font-family: var(--font-body, system-ui, sans-serif);
}

/* Header */
.app-header {
  height: 64px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  background: #08080c;
  z-index: 100;
  position: relative;
}

.brand-wordmark {
  height: 44px;
  width: auto;
  object-fit: contain;
  display: block;
  cursor: pointer;
  transition: transform 0.2s ease;
}

.brand-wordmark:hover {
  transform: scale(1.03);
}

.brand {
  display: flex;
  align-items: center;
  font-family: 'JetBrains Mono', monospace;
  font-weight: 800;
  font-size: 18px;
  letter-spacing: 1px;
  cursor: pointer;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.workflow-step {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.step-num {
  font-family: 'JetBrains Mono', monospace;
  font-weight: 700;
  color: #a1a1aa;
}

.step-name {
  font-family: var(--font-display, 'Syne', sans-serif);
  font-weight: 800;
  color: #ffffff;
}

.step-divider {
  width: 1px;
  height: 14px;
  background-color: rgba(255, 255, 255, 0.15);
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #a1a1aa;
  font-weight: 500;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #CCC;
}

.status-indicator.processing .dot { background: #ffffff; animation: pulse 1s infinite; }
.status-indicator.completed .dot { background: #ffffff; }
.status-indicator.error .dot { background: #F44336; }

@keyframes pulse { 50% { opacity: 0.5; } }

/* Content */
.content-area {
  flex: 1;
  display: flex;
  position: relative;
  overflow: hidden;
}

.panel-wrapper {
  height: 100%;
  overflow: hidden;
  transition: width 0.08s ease;
}

.panel-wrapper.left {
  min-width: 25%;
  max-width: 75%;
}

.content-area.dragging .panel-wrapper,
.content-area.dragging .splitter {
  user-select: none;
  -webkit-user-select: none;
}

.content-area.dragging .panel-wrapper {
  transition: none !important;
  pointer-events: none;
}

.panel-wrapper.right {
  min-width: 25%;
  max-width: 75%;
}

/* Splitter */
.splitter {
  position: relative;
  width: 12px;
  min-width: 12px;
  cursor: col-resize;
  background: rgba(5, 5, 8, 0.6);
  border-left: 1px solid rgba(255, 255, 255, 0.08);
  border-right: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 20;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.splitter-grip {
  width: 4px;
  height: 44px;
  border-radius: 9999px;
  background: rgba(255, 255, 255, 0.2);
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.splitter:hover,
.splitter:active {
  background: rgba(20, 20, 28, 0.9);
  border-color: rgba(255, 255, 255, 0.25);
}

.splitter:hover .splitter-grip,
.splitter:active .splitter-grip {
  background: #ffffff;
  transform: scaleY(1.15);
}
</style>
