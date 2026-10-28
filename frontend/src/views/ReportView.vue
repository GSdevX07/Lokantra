<template>
  <div class="main-view venom-theme">
    <!-- Header -->
    <header class="app-header">
      <div class="header-left">
        <div class="brand" @click="router.push('/home')"><img src="../assets/logo/lokantra_chrome_wordmark.png" alt="LOKĀNTRA" class="brand-wordmark" /></div>
      </div>

      <!-- Center: 2 View Mode Switcher Buttons -->
      <div class="header-center">
        <div class="view-switcher">
          <button 
            class="switch-btn" 
            :class="{ active: viewMode === 'graph' }"
            @click="setMode('graph')"
            title="Switch to full Knowledge Graph view"
          >
            <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="18" cy="5" r="3"></circle>
              <circle cx="6" cy="12" r="3"></circle>
              <circle cx="18" cy="19" r="3"></circle>
              <line x1="8.59" y1="13.51" x2="15.42" y2="17.49"></line>
              <line x1="15.41" y1="6.51" x2="8.59" y2="10.49"></line>
            </svg>
            <span>Graph</span>
          </button>
          <button 
            class="switch-btn" 
            :class="{ active: viewMode === 'report' }"
            @click="setMode('report')"
            title="Switch to full Prediction Report view"
          >
            <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
              <polyline points="14 2 14 8 20 8"></polyline>
              <line x1="16" y1="13" x2="8" y2="13"></line>
              <line x1="16" y1="17" x2="8" y2="17"></line>
              <polyline points="10 9 9 9 8 9"></polyline>
            </svg>
            <span>Prediction Report</span>
          </button>
        </div>
      </div>

      <div class="header-right">
        <div class="workflow-step">
          <span class="step-num">Step 4/5</span>
          <span class="step-name">{{ $tm('main.stepNames')[3] }}</span>
        </div>
        <div class="step-divider"></div>
        <span class="status-indicator" :class="statusClass">
          <span class="dot"></span>
          {{ statusText }}
        </span>
      </div>
    </header>

    <main class="content-area" ref="contentAreaRef">
      <!-- Left Panel: Graph (Full width when viewMode === 'graph') -->
      <div 
        class="panel-wrapper left" 
        :class="{ 'is-hidden': viewMode !== 'graph' }"
        :style="leftPanelStyle"
      >
        <GraphPanel 
          :graphData="graphData"
          :loading="graphLoading"
          :currentPhase="4"
          :isSimulating="false"
          @refresh="refreshGraph"
          @toggle-maximize="toggleMaximize('graph')"
        />
      </div>

      <!-- Right Panel: Step 4 Report (Full width when viewMode === 'report') -->
      <div 
        class="panel-wrapper right" 
        :class="{ 'is-hidden': viewMode !== 'report' }"
        :style="rightPanelStyle"
      >
        <Step4Report
          :reportId="currentReportId"
          :simulationId="simulationId"
          :systemLogs="systemLogs"
          @add-log="addLog"
          @update-status="updateStatus"
        />
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import GraphPanel from '../components/GraphPanel.vue'
import Step4Report from '../components/Step4Report.vue'
import { getProject, getGraphData } from '../api/graph'
import { getSimulation } from '../api/simulation'
import { getReport } from '../api/report'
const route = useRoute()
const router = useRouter()
const { t } = useI18n()

// Props
const props = defineProps({
  reportId: String
})

// Layout State - Defaults to report view (the full content view)
const viewMode = ref('report') // 'graph' | 'report'

const setMode = (mode) => {
  viewMode.value = mode
  nextTick(() => {
    window.dispatchEvent(new Event('resize'))
  })
}

const leftPanelStyle = computed(() => {
  if (viewMode.value === 'graph') {
    return { width: '100%', display: 'block' }
  }
  return { width: '0%', display: 'none' }
})

const rightPanelStyle = computed(() => {
  if (viewMode.value === 'report') {
    return { width: '100%', display: 'block' }
  }
  return { width: '0%', display: 'none' }
})

// Data State
const currentReportId = ref(route.params.reportId)
const simulationId = ref(null)
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
  return 'Generating'
})

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
    if (viewMode.value === 'graph') {
      setMode('report')
    } else {
      setMode('graph')
    }
  }
}

// --- Data Logic ---
const loadReportData = async () => {
  try {
    addLog(t('log.loadReportData', { id: currentReportId.value }))

    // Get report info to obtain simulation_id
    const reportRes = await getReport(currentReportId.value)
    if (reportRes.success && reportRes.data) {
      const reportData = reportRes.data
      simulationId.value = reportData.simulation_id

      if (simulationId.value) {
        // Get simulation info
        const simRes = await getSimulation(simulationId.value)
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
        }
      }
    } else {
      addLog(t('log.getReportInfoFailed', { error: reportRes.error || t('common.unknownError') }))
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

// Watch route params
watch(() => route.params.reportId, (newId) => {
  if (newId && newId !== currentReportId.value) {
    currentReportId.value = newId
    loadReportData()
  }
}, { immediate: true })

onMounted(() => {
  addLog(t('log.reportViewInit'))
  loadReportData()
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

/* Header Center View Switcher */
.header-center {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  z-index: 10;
}

.view-switcher {
  display: flex;
  align-items: center;
  background: rgba(18, 18, 24, 0.85);
  border: 1px solid rgba(255, 255, 255, 0.12);
  padding: 3px;
  border-radius: 8px;
  gap: 4px;
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}

.switch-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  border: 1px solid transparent;
  background: transparent;
  padding: 6px 16px;
  font-size: 12px;
  font-weight: 700;
  color: #94A3B8;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
  letter-spacing: 0.03em;
  font-family: var(--font-body, system-ui, sans-serif);
}

.switch-btn svg {
  flex-shrink: 0;
  transition: stroke 0.2s ease;
}

.switch-btn:hover {
  color: #ffffff;
  background: rgba(255, 255, 255, 0.06);
}

.switch-btn.active {
  background: #ffffff;
  color: #000000;
  border-color: #ffffff;
  font-weight: 800;
  box-shadow: 0 2px 8px rgba(255, 255, 255, 0.15);
}

.switch-btn.active svg {
  stroke: #000000;
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

/* Content Area */
.content-area {
  flex: 1;
  display: flex;
  position: relative;
  overflow: hidden;
  width: 100%;
}

.panel-wrapper {
  height: 100%;
  overflow: hidden;
  transition: width 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.panel-wrapper.is-hidden {
  display: none !important;
}

.panel-wrapper.left {
  width: 100%;
}

.panel-wrapper.right {
  width: 100%;
}
</style>
