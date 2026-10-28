<template>
  <div class="main-view venom-theme">
    <!-- Header -->
    <header class="app-header">
      <div class="header-left">
        <div class="brand" @click="router.push('/home')"><img src="../assets/logo/lokantra_chrome_wordmark.png" alt="LOKĀNTRA" class="brand-wordmark" /></div>
      </div>
      


      <div class="header-right">
        
        <div class="workflow-step">
          <span class="step-num">Step 2/5</span>
          <span class="step-name">{{ $tm('main.stepNames')[1] }}</span>
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
          :currentPhase="2"
          @refresh="refreshGraph"
          @toggle-maximize="toggleMaximize('graph')"
        />
      </div>

      <!-- Middle Splitter -->
      <div class="splitter" @pointerdown.prevent="startDragging" aria-label="Resize panels" title="Drag to resize panels">
        <div class="splitter-grip"></div>
      </div>

      <!-- Right Panel: Step 2 Environment Setup -->
      <div class="panel-wrapper right" :style="{ width: `${100 - leftPanelWidth}%` }">
        <Step2EnvSetup
          :simulationId="currentSimulationId"
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
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import GraphPanel from '../components/GraphPanel.vue'
import Step2EnvSetup from '../components/Step2EnvSetup.vue'
import { getProject, getGraphData } from '../api/graph'
import { getSimulation, stopSimulation, getEnvStatus, closeSimulationEnv } from '../api/simulation'
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
  if (currentStatus.value === 'completed') return 'Ready'
  return 'Preparing'
})

// --- Helpers ---
const addLog = (msg) => {
  const time = new Date().toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' }) + '.' + new Date().getMilliseconds().toString().padStart(3, '0')
  systemLogs.value.push({ time, msg })
  if (systemLogs.value.length > 100) {
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

const handleGoBack = () => {
  // Return to process page
  if (projectData.value?.project_id) {
    router.push({ name: 'Process', params: { projectId: projectData.value.project_id } })
  } else {
    router.push('/home')
  }
}

const handleNextStep = (params = {}) => {
  addLog(t('log.enterStep3'))

  // Record simulation round config
  if (params.maxRounds) {
    addLog(t('log.customRoundsConfig', { rounds: params.maxRounds }))
  } else {
    addLog(t('log.useAutoRounds'))
  }
  
  // Build route params
  const routeParams = {
    name: 'SimulationRun',
    params: { simulationId: currentSimulationId.value }
  }
  
  // Pass customized rounds via query params if present
  if (params.maxRounds) {
    routeParams.query = { maxRounds: params.maxRounds }
  }
  
  // Navigate to Step 3 page
  router.push(routeParams)
}

// --- Data Logic ---

/**
 * Check and close running simulation
 * When user returns from Step 3 to Step 2, assume user wants to exit simulation
 */
const checkAndStopRunningSimulation = async () => {
  if (!currentSimulationId.value) return
  
  try {
    // Check if simulation environment is alive first
    const envStatusRes = await getEnvStatus({ simulation_id: currentSimulationId.value })
    
    if (envStatusRes.success && envStatusRes.data?.env_alive) {
      addLog(t('log.detectedSimEnvRunning'))
      
      // Attempt graceful shutdown of simulation environment
      try {
        const closeRes = await closeSimulationEnv({ 
          simulation_id: currentSimulationId.value,
          timeout: 10  // 10 second timeout
        })
        
        if (closeRes.success) {
          addLog(t('log.simEnvClosed'))
        } else {
          addLog(t('log.closeSimEnvFailedWithError', { error: closeRes.error || t('common.unknownError') }))
          // If graceful shutdown fails, attempt force stop
          await forceStopSimulation()
        }
      } catch (closeErr) {
        addLog(t('log.closeSimEnvException', { error: closeErr.message }))
        // If graceful shutdown throws exception, attempt force stop
        await forceStopSimulation()
      }
    } else {
      // Environment not running, but process may still exist; check simulation status
      const simRes = await getSimulation(currentSimulationId.value)
      if (simRes.success && simRes.data?.status === 'running') {
        addLog(t('log.detectedSimRunning'))
        await forceStopSimulation()
      }
    }
  } catch (err) {
    // Failure to check environment status does not affect subsequent flow
    console.warn('Failed to check simulation status:', err)
  }
}

/**
 * Force stop simulation
 */
const forceStopSimulation = async () => {
  try {
    const stopRes = await stopSimulation({ simulation_id: currentSimulationId.value })
    if (stopRes.success) {
      addLog(t('log.simForceStopSuccess'))
    } else {
      addLog(t('log.forceStopSimFailed', { error: stopRes.error || t('common.unknownError') }))
    }
  } catch (err) {
    addLog(t('log.forceStopSimException', { error: err.message }))
  }
}

const loadSimulationData = async () => {
  try {
    addLog(t('log.loadingSimData', { id: currentSimulationId.value }))

    // Get simulation info
    const simRes = await getSimulation(currentSimulationId.value)
    if (simRes.success && simRes.data) {
      const simData = simRes.data

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
  graphLoading.value = true
  try {
    const res = await getGraphData(graphId)
    if (res.success) {
      graphData.value = res.data
      addLog(t('log.graphDataLoadSuccess'))
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

onMounted(async () => {
  addLog(t('log.simViewInit'))
  
  // Check and close running simulation (when user returns from Step 3)
  await checkAndStopRunningSimulation()
  
  // Load simulation data
  loadSimulationData()
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

.brand-wordmark {
  filter: drop-shadow(0 0 20px rgba(255, 255, 255, 0.22)) drop-shadow(0 4px 12px rgba(0, 0, 0, 0.95));
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}
.brand-wordmark:hover {
  transform: scale(1.04);
  filter: drop-shadow(0 0 28px rgba(255, 255, 255, 0.38)) brightness(1.15);
}

.brand {
  display: flex;
  align-items: center;
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
  text-shadow: 0 0 16px rgba(255, 255, 255, 0.25);
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
  color: #666;
  font-weight: 500;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #CCC;
}

.status-indicator.processing .dot { background: #ffffff;  animation: pulse 1.8s infinite; }
.status-indicator.completed .dot { background: #ffffff;  }
.status-indicator.error .dot { background: #F44336; }

@keyframes pulse { 50% { opacity: 0.5; } }

/* Content */
.content-area {
  flex: 1;
  display: flex;
  position: relative;
  overflow: hidden;
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

.panel-wrapper {
  height: 100%;
  overflow: hidden;
  transition: width 0.08s ease;
}

.panel-wrapper.left {
  min-width: 25%;
  max-width: 75%;
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

