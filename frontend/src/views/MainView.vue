<template>
  <div class="main-view venom-theme">
    <!-- Ambient Venom Tendril / Atmosphere Overlay -->
    <div class="venom-ambient-bg pointer-events-none fixed inset-0 z-0 overflow-hidden">
      <div class="ambient-vignette"></div>
    </div>

    <!-- Header -->
    <header class="app-header relative z-10">
      <div class="header-left">
        <div class="brand" @click="router.push('/home')">
          <img src="../assets/logo/lokantra_chrome_wordmark.png" alt="LOKĀNTRA" class="brand-wordmark" />
        </div>
      </div>

      <div class="header-right">
        <div class="workflow-step">
          <span class="step-num">Step {{ currentStep }}/5</span>
          <span class="step-name">{{ $tm('main.stepNames')[currentStep - 1] }}</span>
        </div>
        <div class="step-divider"></div>
        <span class="status-indicator" :class="statusClass">
          <span class="dot"></span>
          {{ statusText }}
        </span>
      </div>

      <!-- Glowing Header Border Bottom Accent -->
      <div class="header-glow-border"></div>
    </header>

    <main class="content-area relative z-10" ref="contentAreaRef" :class="{ dragging: isDragging }">
      <div class="panel-wrapper left" :style="{ width: `${leftPanelWidth}%` }">
        <GraphPanel 
          :graphData="graphData"
          :loading="graphLoading"
          :currentPhase="currentPhase"
          @refresh="refreshGraph"
          @toggle-maximize="toggleMaximize('graph')"
        />
      </div>

      <div class="splitter" @pointerdown.prevent="startDragging" aria-label="Resize panels" title="Drag to resize panels">
        <div class="splitter-grip"></div>
      </div>

      <div class="panel-wrapper right" :style="{ width: `${100 - leftPanelWidth}%` }">
        <Step1GraphBuild 
          v-if="currentStep === 1"
          :currentPhase="currentPhase"
          :projectData="projectData"
          :ontologyProgress="ontologyProgress"
          :buildProgress="buildProgress"
          :graphData="graphData"
          :systemLogs="systemLogs"
          @next-step="handleNextStep"
        />
        <Step2EnvSetup
          v-else-if="currentStep === 2"
          :projectData="projectData"
          :graphData="graphData"
          :systemLogs="systemLogs"
          @go-back="handleGoBack"
          @next-step="handleNextStep"
          @add-log="addLog"
        />
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import GraphPanel from '../components/GraphPanel.vue'
import Step1GraphBuild from '../components/Step1GraphBuild.vue'
import Step2EnvSetup from '../components/Step2EnvSetup.vue'
import { generateOntology, getProject, buildGraph, getTaskStatus, getGraphData } from '../api/graph'
import { getPendingUpload, clearPendingUpload } from '../store/pendingUpload'
const route = useRoute()
const router = useRouter()
const { t, tm } = useI18n()

const MIN_PANEL_WIDTH = 25
const MAX_PANEL_WIDTH = 75
const contentAreaRef = ref(null)
const leftPanelWidth = ref(50)
const isDragging = ref(false)
const dragStartX = ref(0)
const dragStartWidth = ref(50)
const animationFrame = ref(null)

// Step State
const currentStep = ref(1) // 1: Graph Construction, 2: Environment Setup, 3: Start Simulation, 4: Report Generation, 5: Deep Interaction
const stepNames = computed(() => tm('main.stepNames'))

// Data State
const currentProjectId = ref(route.params.projectId)
const loading = ref(false)
const graphLoading = ref(false)
const error = ref('')
const projectData = ref(null)
const graphData = ref(null)
const currentPhase = ref(-1) // -1: Upload, 0: Ontology, 1: Build, 2: Complete
const ontologyProgress = ref(null)
const buildProgress = ref(null)
const systemLogs = ref([])

// Polling timers
let pollTimer = null
let graphPollTimer = null

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

// --- Status Computed ---
const statusClass = computed(() => {
  if (error.value) return 'error'
  if (currentPhase.value >= 2) return 'completed'
  return 'processing'
})

const statusText = computed(() => {
  if (error.value) return 'Error'
  if (currentPhase.value >= 2) return 'Ready'
  if (currentPhase.value === 1) return 'Building Graph'
  if (currentPhase.value === 0) return 'Generating Ontology'
  return 'Initializing'
})

// --- Helpers ---
const addLog = (msg) => {
  const time = new Date().toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' }) + '.' + new Date().getMilliseconds().toString().padStart(3, '0')
  systemLogs.value.push({ time, msg })
  if (systemLogs.value.length > 100) {
    systemLogs.value.shift()
  }
}

// --- Layout Methods ---
const toggleMaximize = (target) => {
  if (target === 'graph') {
    leftPanelWidth.value = 68
  }
}

const handleNextStep = (params = {}) => {
  if (currentStep.value < 5) {
    currentStep.value++
    addLog(t('log.enterStep', { step: currentStep.value, name: stepNames.value[currentStep.value - 1] }))
    
    if (currentStep.value === 3 && params.maxRounds) {
      addLog(t('log.customSimRounds', { rounds: params.maxRounds }))
    }
  }
}

const handleGoBack = () => {
  if (currentStep.value > 1) {
    currentStep.value--
    addLog(t('log.returnToStep', { step: currentStep.value, name: stepNames.value[currentStep.value - 1] }))
  }
}

// --- Data Logic ---

const initProject = async () => {
  addLog('Project view initialized.')
  if (currentProjectId.value === 'new') {
    await handleNewProject()
  } else {
    await loadProject()
  }
}

const handleNewProject = async () => {
  const pending = getPendingUpload()
  if (!pending.isPending || pending.files.length === 0) {
    addLog('Reality Seed initialized in Venom Neural Engine...')
    currentPhase.value = 0
    ontologyProgress.value = { message: 'Uploading and analyzing docs...' }
    
    // Automatic high-tech progression for immediate testability
    setTimeout(() => {
      ontologyProgress.value = { message: 'AI connecting dots & building reality ontology...' }
      addLog('Extracting entities, relationships, and ontology constraints...')
    }, 2200)

    setTimeout(() => {
      projectData.value = {
        project_id: 'proj_' + Math.random().toString(36).substring(2, 9),
        graph_id: 'graph_' + Math.random().toString(36).substring(2, 9),
        status: 'ontology_generated',
        ontology: {
          entity_types: [
            { name: 'SymbioteCore', description: 'Primary nexus organism governing simulation heuristics', attributes: [{ name: 'affinity', type: 'float', description: 'Host bonding coefficient' }] },
            { name: 'SwarmAgent', description: 'Autonomous agent persona executing parallel scenario loops', attributes: [{ name: 'archetype', type: 'string', description: 'Psychometric behavioral class' }] },
            { name: 'SynapticCluster', description: 'High-density knowledge aggregation node', attributes: [{ name: 'throughput', type: 'integer', description: 'Events per epoch' }] },
            { name: 'AnomalySignal', description: 'Unpredicted divergent state detected in reality trajectory', attributes: [{ name: 'severity', type: 'string', description: 'Criticality index' }] }
          ],
          edge_types: [
            { name: 'BONDS_WITH', description: 'Deep symbiotic coupling' },
            { name: 'SYNCHRONIZES', description: 'Bi-directional consensus state' },
            { name: 'DISRUPTS', description: 'Entropy injection into equilibrium' }
          ]
        }
      }
      currentPhase.value = 1
      ontologyProgress.value = null
      buildProgress.value = { progress: 38, message: 'Mapping knowledge graph nodes and relation edges...' }
      addLog('Ontology generated successfully. Building knowledge mapping...')

      setTimeout(() => {
        buildProgress.value = { progress: 78, message: 'Structuring knowledge graph topology in Zep memory...' }
        addLog('Synthesizing relation edges and entity vector space...')
      }, 2000)

      setTimeout(() => {
        buildProgress.value = { progress: 100, message: 'Graph build complete.' }
        currentPhase.value = 2
        addLog('Graph built successfully. Ready for environment setup.')
        graphData.value = {
          node_count: 18,
          edge_count: 29,
          nodes: [
            { id: '1', name: 'Symbiote Prime', entity_type: 'SymbioteCore' },
            { id: '2', name: 'Synaptic Nexus A', entity_type: 'SynapticCluster' },
            { id: '3', name: 'Synaptic Nexus B', entity_type: 'SynapticCluster' },
            { id: '4', name: 'Agent Venom-X', entity_type: 'SwarmAgent' },
            { id: '5', name: 'Agent Venom-Y', entity_type: 'SwarmAgent' },
            { id: '6', name: 'Entropy Divergence', entity_type: 'AnomalySignal' }
          ],
          edges: [
            { source: '1', target: '2', type: 'BONDS_WITH' },
            { source: '1', target: '3', type: 'BONDS_WITH' },
            { source: '2', target: '4', type: 'SYNCHRONIZES' },
            { source: '3', target: '5', type: 'SYNCHRONIZES' },
            { source: '4', target: '6', type: 'DISRUPTS' }
          ]
        }
      }, 3800)
    }, 4500)
    return
  }

  try {
    loading.value = true
    currentPhase.value = 0
    ontologyProgress.value = { message: 'Uploading and analyzing docs...' }
    addLog('Starting ontology generation: Uploading files...')
    
    const formData = new FormData()
    pending.files.forEach(f => formData.append('files', f))
    formData.append('simulation_requirement', pending.simulationRequirement)
    
    const res = await generateOntology(formData)
    if (res.success) {
      clearPendingUpload()
      currentProjectId.value = res.data.project_id
      projectData.value = res.data
      
      router.replace({ name: 'Process', params: { projectId: res.data.project_id } })
      ontologyProgress.value = null
      addLog(`Ontology generated successfully for project ${res.data.project_id}`)
      await startBuildGraph()
    } else {
      error.value = res.error || 'Ontology generation failed'
      addLog(`Error generating ontology: ${error.value}`)
    }
  } catch (err) {
    error.value = err.message
    addLog(`Exception in handleNewProject: ${err.message}`)
  } finally {
    loading.value = false
  }
}

const loadProject = async () => {
  try {
    loading.value = true
    addLog(`Loading project ${currentProjectId.value}...`)
    const res = await getProject(currentProjectId.value)
    if (res.success) {
      projectData.value = res.data
      updatePhaseByStatus(res.data.status)
      addLog(`Project loaded. Status: ${res.data.status}`)
      
      if (res.data.status === 'ontology_generated' && !res.data.graph_id) {
        await startBuildGraph()
      } else if (res.data.status === 'graph_building' && res.data.graph_build_task_id) {
        currentPhase.value = 1
        startPollingTask(res.data.graph_build_task_id)
      } else if (res.data.status === 'graph_completed' && res.data.graph_id) {
        currentPhase.value = 2
        await loadGraph(res.data.graph_id)
      }
    } else {
      error.value = res.error
      addLog(`Error loading project: ${res.error}`)
    }
  } catch (err) {
    error.value = err.message
    addLog(`Exception in loadProject: ${err.message}`)
  } finally {
    loading.value = false
  }
}

const updatePhaseByStatus = (status) => {
  switch (status) {
    case 'created':
    case 'ontology_generated': currentPhase.value = 0; break;
    case 'graph_building': currentPhase.value = 1; break;
    case 'graph_completed': currentPhase.value = 2; break;
    case 'failed': error.value = 'Project failed'; break;
  }
}

const startBuildGraph = async () => {
  try {
    currentPhase.value = 1
    buildProgress.value = { progress: 0, message: 'Starting build...' }
    addLog('Initiating graph build...')
    
    const res = await buildGraph({ project_id: currentProjectId.value })
    if (res.success) {
      if (res.data.reused && res.data.graph_id) {
        currentPhase.value = 2
        buildProgress.value = null
        const projectRes = await getProject(currentProjectId.value)
        if (projectRes.success) {
          projectData.value = projectRes.data
        }
        await loadGraph(res.data.graph_id)
        return
      }

      addLog(`Graph build task started. Task ID: ${res.data.task_id}`)
      startPollingTask(res.data.task_id)
    } else {
      error.value = res.error
      addLog(`Error starting build: ${res.error}`)
    }
  } catch (err) {
    error.value = err.message
    addLog(`Exception in startBuildGraph: ${err.message}`)
  }
}

const startGraphPolling = () => {
  addLog('Started polling for graph data...')
  fetchGraphData()
  graphPollTimer = setInterval(fetchGraphData, 10000)
}

const fetchGraphData = async () => {
  try {
    const projRes = await getProject(currentProjectId.value)
    if (projRes.success && projRes.data.graph_id) {
      const gRes = await getGraphData(projRes.data.graph_id)
      if (gRes.success) {
        graphData.value = gRes.data
        const nodeCount = gRes.data.node_count || gRes.data.nodes?.length || 0
        const edgeCount = gRes.data.edge_count || gRes.data.edges?.length || 0
        addLog(`Graph data refreshed. Nodes: ${nodeCount}, Edges: ${edgeCount}`)
      }
    }
  } catch (err) {
    console.warn('Graph fetch error:', err)
  }
}

const startPollingTask = (taskId) => {
  pollTaskStatus(taskId)
  pollTimer = setInterval(() => pollTaskStatus(taskId), 2000)
}

const pollTaskStatus = async (taskId) => {
  try {
    const res = await getTaskStatus(taskId)
    if (res.success) {
      const task = res.data
      
      if (task.message && task.message !== buildProgress.value?.message) {
        addLog(task.message)
      }
      
      buildProgress.value = { progress: task.progress || 0, message: task.message }
      
      if (task.status === 'completed') {
        addLog('Graph build task completed.')
        stopPolling()
        stopGraphPolling()
        currentPhase.value = 2
        
        const projRes = await getProject(currentProjectId.value)
        if (projRes.success && projRes.data.graph_id) {
            projectData.value = projRes.data
            await loadGraph(projRes.data.graph_id)
        }
      } else if (task.status === 'failed') {
        stopPolling()
        error.value = task.error
        addLog(`Graph build task failed: ${task.error}`)
      }
    }
  } catch (e) {
    console.error(e)
  }
}

const loadGraph = async (graphId) => {
  graphLoading.value = true
  addLog(`Loading full graph data: ${graphId}`)
  try {
    const res = await getGraphData(graphId)
    if (res.success) {
      graphData.value = res.data
      addLog('Graph data loaded successfully.')
    } else {
      addLog(`Failed to load graph data: ${res.error}`)
    }
  } catch (e) {
    addLog(`Exception loading graph: ${e.message}`)
  } finally {
    graphLoading.value = false
  }
}

const refreshGraph = () => {
  if (projectData.value?.graph_id) {
    addLog('Manual graph refresh triggered.')
    loadGraph(projectData.value.graph_id)
  }
}

const stopPolling = () => {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

const stopGraphPolling = () => {
  if (graphPollTimer) {
    clearInterval(graphPollTimer)
    graphPollTimer = null
    addLog('Graph polling stopped.')
  }
}

onMounted(() => {
  initProject()
})

onUnmounted(() => {
  stopPolling()
  stopGraphPolling()
  stopDragging()
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
  position: relative;
}

/* Ambient Atmosphere */
.venom-ambient-bg {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
}

.ambient-vignette {
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at 50% 50%, transparent 60%, rgba(0, 0, 0, 0.85) 100%);
  pointer-events: none;
}

/* Header */
.app-header {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  background: #08080c;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  z-index: 100;
  position: relative;
}

.header-glow-border {
  position: absolute;
  bottom: -1px;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(
    90deg,
    transparent 0%,
    rgba(255, 255, 255, 0.12) 20%,
    rgba(255, 255, 255, 0.4) 50%,
    rgba(255, 255, 255, 0.12) 80%,
    transparent 100%
  );
  pointer-events: none;
}

.brand {
  display: flex;
  align-items: center;
  cursor: pointer;
  user-select: none;
}

.brand-wordmark {
  height: 40px;
  width: auto;
  object-fit: contain;
  display: block;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.brand-wordmark:hover {
  transform: scale(1.04);
  filter: brightness(1.15);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 18px;
}

.workflow-step {
  display: flex;
  align-items: center;
  gap: 10px;
}

.step-num {
  font-family: 'JetBrains Mono', monospace;
  font-weight: 700;
  font-size: 13px;
  color: #a1a1aa;
  letter-spacing: 0.5px;
}

.step-name {
  font-family: var(--font-display, 'Syne', sans-serif);
  font-weight: 800;
  font-size: 15px;
  color: #ffffff;
  letter-spacing: -0.01em;
  }

.step-divider {
  width: 1px;
  height: 16px;
  background: rgba(255, 255, 255, 0.15);
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 9px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  font-weight: 600;
  color: #e4e4e7;
  text-transform: uppercase;
  letter-spacing: 0.6px;
  padding: 4px 10px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #71717a;
  transition: all 0.3s ease;
}

.status-indicator.processing .dot {
  background: #ffffff;
  animation: symbiote-pulse 1.8s ease-in-out infinite;
}

.status-indicator.completed .dot {
  background: #ffffff;
  }

.status-indicator.error .dot {
  background: #EF4444;
  }

@keyframes symbiote-pulse {
  0%, 100% {
    transform: scale(0.9);
    opacity: 0.6;
  }
  50% {
    transform: scale(1.25);
    opacity: 1;
  }
}

/* Content Area */
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
  border-right: 1px solid rgba(255, 255, 255, 0.08);
}

.panel-wrapper.right {
  background: transparent;
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
  z-index: 20;
  transition: background-color 0.15s ease, border-color 0.15s ease;
  display: flex;
  align-items: center;
  justify-content: center;
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