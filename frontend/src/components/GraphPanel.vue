<template>
  <div class="graph-panel">
    <div class="panel-header">
      <span class="panel-title">{{ $t('graph.panelTitle') }}</span>
      <!-- Top Toolbar (Internal Top Right) -->
      <div class="header-tools">
        <button class="tool-btn" @click="downloadGraphSvg" :disabled="loading || !graphData" title="Download Full Graph (SVG)">
          <svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="icon-download">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
            <polyline points="7 10 12 15 17 10"></polyline>
            <line x1="12" y1="15" x2="12" y2="3"></line>
          </svg>
          <span class="btn-text">Download SVG</span>
        </button>
        <button class="tool-btn" @click="fitGraphToView(500)" :disabled="loading || !graphData" title="Fit Entire Graph to View">
          <svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="15 3 21 3 21 9"></polyline>
            <polyline points="9 21 3 21 3 15"></polyline>
            <line x1="21" y1="3" x2="14" y2="10"></line>
            <line x1="3" y1="21" x2="10" y2="14"></line>
          </svg>
          <span class="btn-text">Fit View</span>
        </button>
        <button class="tool-btn" @click="$emit('refresh')" :disabled="loading" :title="$t('graph.refreshGraph')">
          <span class="icon-refresh" :class="{ 'spinning': loading }">↻</span>
          <span class="btn-text">Refresh</span>
        </button>
      </div>
    </div>
    
    <div class="graph-container" ref="graphContainer">
      <!-- Graph Visualization -->
      <div v-if="graphData" class="graph-view">
        <svg ref="graphSvg" class="graph-svg"></svg>
        
        <!-- Live refresh overlay indicator inside graph-view -->
        <transition name="fade">
          <div v-if="loading" class="graph-refreshing-badge">
            <span class="refresh-spinner-dot"></span>
            <span>Syncing Graph...</span>
          </div>
        </transition>
        
        <!-- Building/Simulating Hint -->
        <div v-if="currentPhase === 1 || isSimulating" class="graph-building-hint">
          <div class="memory-icon-wrapper">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="memory-icon">
              <path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96.44 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 4.44-4.04z" />
              <path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96.44 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-4.44-4.04z" />
            </svg>
          </div>
          {{ isSimulating ? $t('graph.graphMemoryRealtime') : $t('graph.realtimeUpdating') }}
        </div>
        
        <!-- Hint After Simulation Finishes -->
        <div v-if="showSimulationFinishedHint" class="graph-building-hint finished-hint">
          <div class="hint-icon-wrapper">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="hint-icon">
              <circle cx="12" cy="12" r="10"></circle>
              <line x1="12" y1="16" x2="12" y2="12"></line>
              <line x1="12" y1="8" x2="12.01" y2="8"></line>
            </svg>
          </div>
          <span class="hint-text">{{ $t('graph.pendingContentHint') }}</span>
          <button class="hint-close-btn" @click="dismissFinishedHint" :title="$t('graph.closeHint')">
            <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
        
        <!-- Node/Edge Details Panel -->
        <div v-if="selectedItem" class="detail-panel">
          <div class="detail-panel-header">
            <span class="detail-title">{{ selectedItem.type === 'node' ? $t('graph.nodeDetails') : $t('graph.relationship') }}</span>
            <span v-if="selectedItem.type === 'node'" class="detail-type-badge" :style="{ background: selectedItem.color, color: '#fff' }">
              {{ selectedItem.entityType }}
            </span>
            <button class="detail-close" @click="closeDetailPanel">×</button>
          </div>
          
          <!-- Node Details -->
          <div v-if="selectedItem.type === 'node'" class="detail-content">
            <div class="detail-row">
              <span class="detail-label">Name:</span>
              <span class="detail-value">{{ selectedItem.data.name }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">UUID:</span>
              <span class="detail-value uuid-text">{{ selectedItem.data.uuid }}</span>
            </div>
            <div class="detail-row" v-if="selectedItem.data.created_at">
              <span class="detail-label">Created:</span>
              <span class="detail-value">{{ formatDateTime(selectedItem.data.created_at) }}</span>
            </div>
            
            <!-- Properties -->
            <div class="detail-section" v-if="selectedItem.data.attributes && Object.keys(selectedItem.data.attributes).length > 0">
              <div class="section-title">Properties:</div>
              <div class="properties-list">
                <div v-for="(value, key) in selectedItem.data.attributes" :key="key" class="property-item">
                  <span class="property-key">{{ key }}:</span>
                  <span class="property-value">{{ value || 'None' }}</span>
                </div>
              </div>
            </div>
            
            <!-- Summary -->
            <div class="detail-section" v-if="selectedItem.data.summary">
              <div class="section-title">Summary:</div>
              <div class="summary-text">{{ selectedItem.data.summary }}</div>
            </div>
            
            <!-- Labels -->
            <div class="detail-section" v-if="selectedItem.data.labels && selectedItem.data.labels.length > 0">
              <div class="section-title">Labels:</div>
              <div class="labels-list">
                <span v-for="label in selectedItem.data.labels" :key="label" class="label-tag">
                  {{ label }}
                </span>
              </div>
            </div>
          </div>
          
          <!-- Edge Details -->
          <div v-else class="detail-content">
            <!-- Self-Loop Group Details -->
            <template v-if="selectedItem.data.isSelfLoopGroup">
              <div class="edge-relation-header self-loop-header">
                {{ selectedItem.data.source_name }} - Self Relations
                <span class="self-loop-count">{{ selectedItem.data.selfLoopCount }} items</span>
              </div>
              
              <div class="self-loop-list">
                <div 
                  v-for="(loop, idx) in selectedItem.data.selfLoopEdges" 
                  :key="loop.uuid || idx" 
                  class="self-loop-item"
                  :class="{ expanded: expandedSelfLoops.has(loop.uuid || idx) }"
                >
                  <div 
                    class="self-loop-item-header"
                    @click="toggleSelfLoop(loop.uuid || idx)"
                  >
                    <span class="self-loop-index">#{{ idx + 1 }}</span>
                    <span class="self-loop-name">{{ loop.name || loop.fact_type || 'RELATED' }}</span>
                    <span class="self-loop-toggle">{{ expandedSelfLoops.has(loop.uuid || idx) ? '−' : '+' }}</span>
                  </div>
                  
                  <div class="self-loop-item-content" v-show="expandedSelfLoops.has(loop.uuid || idx)">
                    <div class="detail-row" v-if="loop.uuid">
                      <span class="detail-label">UUID:</span>
                      <span class="detail-value uuid-text">{{ loop.uuid }}</span>
                    </div>
                    <div class="detail-row" v-if="loop.fact">
                      <span class="detail-label">Fact:</span>
                      <span class="detail-value fact-text">{{ loop.fact }}</span>
                    </div>
                    <div class="detail-row" v-if="loop.fact_type">
                      <span class="detail-label">Type:</span>
                      <span class="detail-value">{{ loop.fact_type }}</span>
                    </div>
                    <div class="detail-row" v-if="loop.created_at">
                      <span class="detail-label">Created:</span>
                      <span class="detail-value">{{ formatDateTime(loop.created_at) }}</span>
                    </div>
                    <div v-if="loop.episodes && loop.episodes.length > 0" class="self-loop-episodes">
                      <span class="detail-label">Episodes:</span>
                      <div class="episodes-list compact">
                        <span v-for="ep in loop.episodes" :key="ep" class="episode-tag small">{{ ep }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </template>
            
            <!-- Standard Edge Details -->
            <template v-else>
              <div class="edge-relation-header">
                {{ selectedItem.data.source_name }} → {{ selectedItem.data.name || 'RELATED_TO' }} → {{ selectedItem.data.target_name }}
              </div>
              
              <div class="detail-row">
                <span class="detail-label">UUID:</span>
                <span class="detail-value uuid-text">{{ selectedItem.data.uuid }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">Label:</span>
                <span class="detail-value">{{ selectedItem.data.name || 'RELATED_TO' }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">Type:</span>
                <span class="detail-value">{{ selectedItem.data.fact_type || 'Unknown' }}</span>
              </div>
              <div class="detail-row" v-if="selectedItem.data.fact">
                <span class="detail-label">Fact:</span>
                <span class="detail-value fact-text">{{ selectedItem.data.fact }}</span>
              </div>
              
              <!-- Episodes -->
              <div class="detail-section" v-if="selectedItem.data.episodes && selectedItem.data.episodes.length > 0">
                <div class="section-title">Episodes:</div>
                <div class="episodes-list">
                  <span v-for="ep in selectedItem.data.episodes" :key="ep" class="episode-tag">
                    {{ ep }}
                  </span>
                </div>
              </div>
              
              <div class="detail-row" v-if="selectedItem.data.created_at">
                <span class="detail-label">Created:</span>
                <span class="detail-value">{{ formatDateTime(selectedItem.data.created_at) }}</span>
              </div>
              <div class="detail-row" v-if="selectedItem.data.valid_at">
                <span class="detail-label">Valid From:</span>
                <span class="detail-value">{{ formatDateTime(selectedItem.data.valid_at) }}</span>
              </div>
            </template>
          </div>
        </div>
      </div>
      
      <!-- Waiting/Empty & Ingestion State - Venom Symbiote Core -->
      <div v-else class="graph-state venom-symbiote-empty" :class="{ 'is-loading': loading }">
        <div class="symbiote-core-wrapper">
          <div class="symbiote-pulse-ring ring-1"></div>
          <div class="symbiote-pulse-ring ring-2"></div>
          <div class="symbiote-pulse-ring ring-3"></div>
          
          <!-- Cybernetic scan beam active during data loading -->
          <div v-if="loading" class="symbiote-scan-beam"></div>

          <div class="symbiote-orbit-tracker orbit-cw">
            <div class="orbital-node node-1"></div>
            <div class="orbital-node node-2"></div>
          </div>
          <div class="symbiote-orbit-tracker orbit-ccw">
            <div class="orbital-node node-3"></div>
            <div class="orbital-node node-4"></div>
          </div>

          <div class="symbiote-nexus-glyph">
            <span class="nexus-symbol">❖</span>
          </div>
        </div>

        <div class="empty-status-wrap">
          <h3 class="empty-title">{{ emptyStateTitle }}</h3>
          <p class="empty-subtitle">
            <span class="pulse-spark" :class="{ 'active': loading }"></span>
            {{ emptyStateSubtitle }}
          </p>
          <div class="empty-endpoint-pill">
            <span class="pill-dot" :class="{ 'active': loading }"></span>
            <code>{{ emptyStateEndpoint }}</code>
          </div>
        </div>
      </div>
    </div>

    <!-- Bottom Legend (Bottom Left) -->
    <div v-if="graphData && entityTypes.length" class="graph-legend">
      <span class="legend-title">Entity Types</span>
      <div class="legend-items">
        <div class="legend-item" v-for="type in entityTypes" :key="type.name">
          <span class="legend-dot" :style="{ background: type.color }"></span>
          <span class="legend-label">{{ type.name }}</span>
        </div>
      </div>
    </div>
    
    <!-- Show Edge Labels Toggle -->
    <div v-if="graphData" class="edge-labels-toggle" :class="{ 'active': showEdgeLabels }">
      <label class="toggle-switch">
        <input type="checkbox" v-model="showEdgeLabels" />
        <span class="slider"></span>
      </label>
      <span class="toggle-label">Show Edge Labels</span>
    </div>

    <!-- Floating Zoom & Fit Controls (Bottom Right) -->
    <div v-if="graphData" class="graph-zoom-controls">
      <button class="zoom-btn" @click="zoomIn" title="Zoom In (+)">
        <span>+</span>
      </button>
      <button class="zoom-btn" @click="zoomOut" title="Zoom Out (−)">
        <span>−</span>
      </button>
      <button class="zoom-btn fit-btn" @click="fitGraphToView(500)" title="Fit Entire Graph into View">
        <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="15 3 21 3 21 9"></polyline>
          <polyline points="9 21 3 21 3 15"></polyline>
          <line x1="21" y1="3" x2="14" y2="10"></line>
          <line x1="3" y1="21" x2="10" y2="14"></line>
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick, computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
import * as d3 from 'd3'

const props = defineProps({
  graphData: Object,
  loading: Boolean,
  currentPhase: Number,
  isSimulating: Boolean
})

const emptyStateTitle = computed(() => {
  if (props.loading) {
    return t('graph.graphDataLoading') || 'Loading graph data...'
  }
  if (props.currentPhase === 1) {
    return 'Knowledge Graph Ingestion In Progress...'
  }
  if (props.currentPhase === 0) {
    return 'Analyzing Reality Seed & Generating Ontology...'
  }
  return t('graph.waitingOntology') || 'Waiting for ontology generation...'
})

const emptyStateSubtitle = computed(() => {
  if (props.loading) {
    return 'AI Symbiote Ingesting Nodes & Neural Synthesizing...'
  }
  if (props.currentPhase === 1) {
    return 'Extracting Entities, Constraints & Graph Relations...'
  }
  return 'AI Symbiote Neural Link Connecting Dots...'
})

const emptyStateEndpoint = computed(() => {
  if (props.loading) {
    return 'GET /api/graph/data'
  }
  if (props.currentPhase === 1) {
    return 'POST /api/graph/build'
  }
  return 'POST /api/graph/ontology/generate'
})

const emit = defineEmits(['refresh', 'toggle-maximize'])

const graphContainer = ref(null)
const graphSvg = ref(null)
const selectedItem = ref(null)
const showEdgeLabels = ref(true) // Default to showing edge labels
const expandedSelfLoops = ref(new Set()) // Expanded self-loop items
const showSimulationFinishedHint = ref(false) // Hint after simulation finishes
const wasSimulating = ref(false) // Track if previously simulating

// Close simulation finished hint
const dismissFinishedHint = () => {
  showSimulationFinishedHint.value = false
}

// Watch isSimulating change, detect simulation finish
watch(() => props.isSimulating, (newValue, oldValue) => {
  if (wasSimulating.value && !newValue) {
    // Change from simulating to non-simulating, display finished hint
    showSimulationFinishedHint.value = true
  }
  wasSimulating.value = newValue
}, { immediate: true })

// Toggle self-loop item expand/collapse state
const toggleSelfLoop = (id) => {
  const newSet = new Set(expandedSelfLoops.value)
  if (newSet.has(id)) {
    newSet.delete(id)
  } else {
    newSet.add(id)
  }
  expandedSelfLoops.value = newSet
}

// Compute entity types for legend
const entityTypes = computed(() => {
  if (!props.graphData?.nodes) return []
  const typeMap = {}
  // Aesthetically pleasing color palette
  const colors = ['#FF6B35', '#004E89', '#7B2D8E', '#1A936F', '#C5283D', '#E9724C', '#3498db', '#9b59b6', '#27ae60', '#f39c12']
  
  props.graphData.nodes.forEach(node => {
    const type = node.labels?.find(l => l !== 'Entity') || 'Entity'
    if (!typeMap[type]) {
      typeMap[type] = { name: type, count: 0, color: colors[Object.keys(typeMap).length % colors.length] }
    }
    typeMap[type].count++
  })
  return Object.values(typeMap)
})

// Format time
const formatDateTime = (dateStr) => {
  if (!dateStr) return ''
  try {
    const date = new Date(dateStr)
    return date.toLocaleString('en-US', { 
      month: 'short', 
      day: 'numeric', 
      year: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      hour12: true 
    })
  } catch {
    return dateStr
  }
}

const closeDetailPanel = () => {
  selectedItem.value = null
  expandedSelfLoops.value = new Set() // Reset expanded state
}

let currentSimulation = null
let linkLabelsRef = null
let linkLabelBgRef = null
let lastRenderedNodes = []
let currentZoomBehavior = null

const downloadGraphSvg = () => {
  if (!graphSvg.value || !lastRenderedNodes.length) return

  try {
    const svgEl = graphSvg.value

    // Clone SVG to isolate export from active canvas mutations
    const clone = svgEl.cloneNode(true)
    clone.setAttribute('xmlns', 'http://www.w3.org/2000/svg')
    clone.setAttribute('xmlns:xlink', 'http://www.w3.org/1999/xlink')

    // Remove zoom/pan transform on the cloned <g> so all nodes are in natural uncropped space
    const cloneG = clone.querySelector('g')
    if (cloneG) {
      cloneG.removeAttribute('transform')
    }

    // Determine the full bounding box enclosing EVERY node and label
    let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity
    lastRenderedNodes.forEach(n => {
      if (typeof n.x === 'number' && typeof n.y === 'number' && isFinite(n.x) && isFinite(n.y)) {
        minX = Math.min(minX, n.x - 35)
        maxX = Math.max(maxX, n.x + 110) // text label padding to the right
        minY = Math.min(minY, n.y - 35)
        maxY = Math.max(maxY, n.y + 35)
      }
    })

    // Also check live group getBBox as an extra bounds safety check
    try {
      const liveG = svgEl.querySelector('g')
      if (liveG && typeof liveG.getBBox === 'function') {
        const bbox = liveG.getBBox()
        if (bbox && bbox.width > 0 && bbox.height > 0 && isFinite(bbox.width) && isFinite(bbox.height)) {
          minX = Math.min(minX, bbox.x)
          maxX = Math.max(maxX, bbox.x + bbox.width)
          minY = Math.min(minY, bbox.y)
          maxY = Math.max(maxY, bbox.y + bbox.height)
        }
      }
    } catch (e) {}

    // Fallback if no valid points
    if (!isFinite(minX) || !isFinite(maxX) || maxX <= minX) {
      minX = 0; minY = 0; maxX = 1200; maxY = 800;
    }

    // Generous padding around the full perimeter so no node or label is near the edge
    const padding = 100
    const vx = Math.round(minX - padding)
    const vy = Math.round(minY - padding)
    const vw = Math.round(maxX - minX + padding * 2)
    const vh = Math.round(maxY - minY + padding * 2)

    clone.setAttribute('viewBox', `${vx} ${vy} ${vw} ${vh}`)
    clone.setAttribute('width', vw)
    clone.setAttribute('height', vh)

    // Create dark background rect as first child in SVG clone covering the entire viewBox
    const bgRect = document.createElementNS('http://www.w3.org/2000/svg', 'rect')
    bgRect.setAttribute('x', vx)
    bgRect.setAttribute('y', vy)
    bgRect.setAttribute('width', vw)
    bgRect.setAttribute('height', vh)
    bgRect.setAttribute('fill', '#08080c')
    clone.insertBefore(bgRect, clone.firstChild)

    // Ensure all typography renders cleanly in the exported vector SVG
    const styleEl = document.createElementNS('http://www.w3.org/2000/svg', 'style')
    styleEl.textContent = `
      text {
        font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      }
    `
    clone.insertBefore(styleEl, clone.firstChild)

    const serializer = new XMLSerializer()
    let svgString = serializer.serializeToString(clone)

    // Add standalone XML header
    if (!svgString.startsWith('<?xml')) {
      svgString = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n' + svgString
    }

    const svgBlob = new Blob([svgString], { type: 'image/svg+xml;charset=utf-8' })
    const URLObject = window.URL || window.webkitURL || window
    const svgUrl = URLObject.createObjectURL(svgBlob)

    const downloadLink = document.createElement('a')
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19)
    downloadLink.download = `knowledge-graph-full-${timestamp}.svg`
    downloadLink.href = svgUrl
    document.body.appendChild(downloadLink)
    downloadLink.click()
    document.body.removeChild(downloadLink)
    setTimeout(() => URLObject.revokeObjectURL(svgUrl), 1000)
  } catch (err) {
    console.error('downloadGraphSvg error:', err)
  }
}

const fitGraphToView = (duration = 600) => {
  if (!graphSvg.value || !graphContainer.value || !lastRenderedNodes.length) return

  const container = graphContainer.value
  const width = (container && container.clientWidth > 0) ? container.clientWidth : 900
  const height = (container && container.clientHeight > 0) ? container.clientHeight : 650

  let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity
  lastRenderedNodes.forEach(n => {
    if (typeof n.x === 'number' && typeof n.y === 'number' && isFinite(n.x) && isFinite(n.y)) {
      minX = Math.min(minX, n.x - 30)
      maxX = Math.max(maxX, n.x + 80)
      minY = Math.min(minY, n.y - 30)
      maxY = Math.max(maxY, n.y + 30)
    }
  })

  if (!isFinite(minX) || !isFinite(maxX) || maxX <= minX) return

  const graphWidth = maxX - minX
  const graphHeight = maxY - minY
  const midX = (minX + maxX) / 2
  const midY = (minY + maxY) / 2

  const padding = 70
  const scaleX = (width - padding * 2) / graphWidth
  const scaleY = (height - padding * 2) / graphHeight
  const targetScale = Math.min(Math.max(Math.min(scaleX, scaleY), 0.08), 1.6)

  const targetTranslateX = width / 2 - midX * targetScale
  const targetTranslateY = height / 2 - midY * targetScale

  const svg = d3.select(graphSvg.value)
  const transform = d3.zoomIdentity.translate(targetTranslateX, targetTranslateY).scale(targetScale)

  if (currentZoomBehavior) {
    if (duration > 0) {
      svg.transition().duration(duration).call(currentZoomBehavior.transform, transform)
    } else {
      svg.call(currentZoomBehavior.transform, transform)
    }
  }
}

const zoomIn = () => {
  if (!graphSvg.value || !currentZoomBehavior) return
  d3.select(graphSvg.value).transition().duration(250).call(currentZoomBehavior.scaleBy, 1.35)
}

const zoomOut = () => {
  if (!graphSvg.value || !currentZoomBehavior) return
  d3.select(graphSvg.value).transition().duration(250).call(currentZoomBehavior.scaleBy, 0.72)
}

const renderGraph = () => {
  if (!graphSvg.value || !props.graphData) return
  
  // Stop previous simulation
  if (currentSimulation) {
    currentSimulation.stop()
  }
  
  const container = graphContainer.value
  const width = (container && container.clientWidth > 0) ? container.clientWidth : 900
  const height = (container && container.clientHeight > 0) ? container.clientHeight : 650
  
  const svg = d3.select(graphSvg.value)
    .attr('width', width)
    .attr('height', height)
    .attr('viewBox', `0 0 ${width} ${height}`)
    
  svg.selectAll('*').remove()
  
  const nodesData = props.graphData.nodes || []
  const edgesData = props.graphData.edges || []
  
  if (nodesData.length === 0) return

  // Prep data supporting both uuid and id
  const nodeMap = {}
  nodesData.forEach(n => {
    const id = n.uuid || n.id
    if (id) nodeMap[id] = n
  })
  
  const nodes = nodesData.map(n => ({
    id: n.uuid || n.id,
    name: n.name || 'Unnamed',
    type: n.labels?.find(l => l !== 'Entity') || n.entity_type || 'Entity',
    rawData: n
  }))
  
  const nodeIds = new Set(nodes.map(n => n.id))

  const getEdgeSource = (e) => e.source_node_uuid || e.source?.id || e.source
  const getEdgeTarget = (e) => e.target_node_uuid || e.target?.id || e.target
  
  // Process edge data, compute edge counts and indices between pairs of nodes
  const edgePairCount = {}
  const selfLoopEdges = {} // Self-loop edges grouped by node
  const tempEdges = edgesData
    .filter(e => {
      const s = getEdgeSource(e)
      const t = getEdgeTarget(e)
      return s && t && nodeIds.has(s) && nodeIds.has(t)
    })
  
  // Count edges between each pair of nodes, collect self-loops
  tempEdges.forEach(e => {
    const s = getEdgeSource(e)
    const t = getEdgeTarget(e)
    if (s === t) {
      if (!selfLoopEdges[s]) {
        selfLoopEdges[s] = []
      }
      selfLoopEdges[s].push({
        ...e,
        source_name: nodeMap[s]?.name,
        target_name: nodeMap[t]?.name
      })
    } else {
      const pairKey = [s, t].sort().join('_')
      edgePairCount[pairKey] = (edgePairCount[pairKey] || 0) + 1
    }
  })
  
  // Track current edge index for each node pair
  const edgePairIndex = {}
  const processedSelfLoopNodes = new Set()
  const edges = []
  
  tempEdges.forEach(e => {
    const s = getEdgeSource(e)
    const t = getEdgeTarget(e)
    const isSelfLoop = s === t
    
    if (isSelfLoop) {
      if (processedSelfLoopNodes.has(s)) return
      processedSelfLoopNodes.add(s)
      
      const allSelfLoops = selfLoopEdges[s] || []
      const nodeName = nodeMap[s]?.name || 'Unknown'
      const labelText = `Self Relations (${allSelfLoops.length})`
      edges.push({
        source: s,
        target: t,
        type: 'SELF_LOOP',
        name: labelText,
        curvature: 0,
        isSelfLoop: true,
        _labelW: Math.max(labelText.length * 6.5 + 10, 24),
        _labelH: 15,
        rawData: {
          isSelfLoopGroup: true,
          source_name: nodeName,
          target_name: nodeName,
          selfLoopCount: allSelfLoops.length,
          selfLoopEdges: allSelfLoops
        }
      })
      return
    }
    
    const pairKey = [s, t].sort().join('_')
    const totalCount = edgePairCount[pairKey] || 1
    const currentIndex = edgePairIndex[pairKey] || 0
    edgePairIndex[pairKey] = currentIndex + 1
    
    const isReversed = s > t
    let curvature = 0
    if (totalCount > 1) {
      const curvatureRange = Math.min(1.2, 0.6 + totalCount * 0.15)
      curvature = ((currentIndex / (totalCount - 1)) - 0.5) * curvatureRange * 2
      if (isReversed) {
        curvature = -curvature
      }
    }
    
    const edgeName = e.name || e.fact_type || e.type || 'RELATED'
    edges.push({
      source: s,
      target: t,
      type: e.fact_type || e.type || e.name || 'RELATED',
      name: edgeName,
      curvature,
      isSelfLoop: false,
      pairIndex: currentIndex,
      pairTotal: totalCount,
      _labelW: Math.max(edgeName.length * 6.5 + 10, 24),
      _labelH: 15,
      rawData: {
        ...e,
        source_name: nodeMap[s]?.name,
        target_name: nodeMap[t]?.name
      }
    })
  })
    
  // Color scale
  const colorMap = {}
  entityTypes.value.forEach(t => colorMap[t.name] = t.color)
  const getColor = (type) => colorMap[type] || '#999'

  // Simulation - dynamically adjust node distance based on edge count
  const simulation = d3.forceSimulation(nodes)
    .alphaDecay(0.04)
    .velocityDecay(0.4)
    .force('link', d3.forceLink(edges).id(d => d.id).distance(d => {
      const baseDistance = 150
      const edgeCount = d.pairTotal || 1
      return baseDistance + (edgeCount - 1) * 50
    }))
    .force('charge', d3.forceManyBody().strength(-400))
    .force('center', d3.forceCenter(width / 2, height / 2))
    .force('collide', d3.forceCollide(50))
    .force('x', d3.forceX(width / 2).strength(0.04))
    .force('y', d3.forceY(height / 2).strength(0.04))
  
  currentSimulation = simulation

  simulation.on('end', () => {
    fitGraphToView(600)
  })

  // Settle frame check
  setTimeout(() => {
    fitGraphToView(450)
  }, 1200)

  const g = svg.append('g')
  
  lastRenderedNodes = nodes

  // Zoom and smooth scroll navigation
  const zoomBehavior = d3.zoom()
    .extent([[0, 0], [width, height]])
    .scaleExtent([0.05, 5])
    .on('zoom', (event) => {
      g.attr('transform', event.transform)
    })

  svg.call(zoomBehavior)
  currentZoomBehavior = zoomBehavior

  // Links - use path to support curved lines
  const linkGroup = g.append('g').attr('class', 'links')
  
  // Calculate curved path
  const getLinkPath = (d) => {
    const sx = d.source.x, sy = d.source.y
    const tx = d.target.x, ty = d.target.y
    
    // Detect self-loop
    if (d.isSelfLoop) {
      const loopRadius = 30
      const x1 = sx + 8
      const y1 = sy - 4
      const x2 = sx + 8
      const y2 = sy + 4
      return `M${x1},${y1} A${loopRadius},${loopRadius} 0 1,1 ${x2},${y2}`
    }
    
    if (d.curvature === 0) {
      return `M${sx},${sy} L${tx},${ty}`
    }
    
    const dx = tx - sx, dy = ty - sy
    const dist = Math.sqrt(dx * dx + dy * dy)
    const pairTotal = d.pairTotal || 1
    const offsetRatio = 0.25 + pairTotal * 0.05
    const baseOffset = Math.max(35, dist * offsetRatio)
    const offsetX = -dy / dist * d.curvature * baseOffset
    const offsetY = dx / dist * d.curvature * baseOffset
    const cx = (sx + tx) / 2 + offsetX
    const cy = (sy + ty) / 2 + offsetY
    
    return `M${sx},${sy} Q${cx},${cy} ${tx},${ty}`
  }
  
  // Calculate curve midpoint (for label positioning)
  const getLinkMidpoint = (d) => {
    const sx = d.source.x, sy = d.source.y
    const tx = d.target.x, ty = d.target.y
    
    if (d.isSelfLoop) {
      return { x: sx + 70, y: sy }
    }
    
    if (d.curvature === 0) {
      return { x: (sx + tx) / 2, y: (sy + ty) / 2 }
    }
    
    const dx = tx - sx, dy = ty - sy
    const dist = Math.sqrt(dx * dx + dy * dy)
    const pairTotal = d.pairTotal || 1
    const offsetRatio = 0.25 + pairTotal * 0.05
    const baseOffset = Math.max(35, dist * offsetRatio)
    const offsetX = -dy / dist * d.curvature * baseOffset
    const offsetY = dx / dist * d.curvature * baseOffset
    const cx = (sx + tx) / 2 + offsetX
    const cy = (sy + ty) / 2 + offsetY
    
    const midX = 0.25 * sx + 0.5 * cx + 0.25 * tx
    const midY = 0.25 * sy + 0.5 * cy + 0.25 * ty
    
    return { x: midX, y: midY }
  }
  
  const link = linkGroup.selectAll('path')
    .data(edges)
    .enter().append('path')
    .attr('stroke', 'rgba(255, 255, 255, 0.22)')
    .attr('stroke-width', 1.5)
    .attr('fill', 'none')
    .style('cursor', 'pointer')
    .on('click', (event, d) => {
      event.stopPropagation()
      linkGroup.selectAll('path').attr('stroke', 'rgba(255, 255, 255, 0.22)').attr('stroke-width', 1.5)
      linkLabelBg.attr('fill', 'rgba(12, 12, 16, 0.92)')
      linkLabels.attr('fill', '#d4d4d8')
      d3.select(event.target).attr('stroke', '#ffffff').attr('stroke-width', 3)
      
      selectedItem.value = {
        type: 'edge',
        data: d.rawData
      }
    })

  // Link labels background
  const linkLabelBg = linkGroup.selectAll('rect')
    .data(edges)
    .enter().append('rect')
    .attr('fill', 'rgba(12, 12, 16, 0.92)')
    .attr('rx', 3)
    .attr('ry', 3)
    .attr('width', d => d._labelW)
    .attr('height', d => d._labelH)
    .style('cursor', 'pointer')
    .style('pointer-events', 'all')
    .style('display', showEdgeLabels.value ? 'block' : 'none')
    .on('click', (event, d) => {
      event.stopPropagation()
      linkGroup.selectAll('path').attr('stroke', 'rgba(255, 255, 255, 0.22)').attr('stroke-width', 1.5)
      linkLabelBg.attr('fill', 'rgba(12, 12, 16, 0.92)')
      linkLabels.attr('fill', '#d4d4d8')
      link.filter(l => l === d).attr('stroke', '#ffffff').attr('stroke-width', 3)
      d3.select(event.target).attr('fill', 'rgba(52, 152, 219, 0.1)')
      
      selectedItem.value = {
        type: 'edge',
        data: d.rawData
      }
    })

  // Link labels
  const linkLabels = linkGroup.selectAll('text')
    .data(edges)
    .enter().append('text')
    .text(d => d.name)
    .attr('font-size', '9px')
    .attr('fill', '#d4d4d8')
    .attr('text-anchor', 'middle')
    .attr('dominant-baseline', 'middle')
    .style('cursor', 'pointer')
    .style('pointer-events', 'all')
    .style('font-family', 'system-ui, sans-serif')
    .style('display', showEdgeLabels.value ? 'block' : 'none')
    .on('click', (event, d) => {
      event.stopPropagation()
      linkGroup.selectAll('path').attr('stroke', 'rgba(255, 255, 255, 0.22)').attr('stroke-width', 1.5)
      linkLabelBg.attr('fill', 'rgba(12, 12, 16, 0.92)')
      linkLabels.attr('fill', '#d4d4d8')
      link.filter(l => l === d).attr('stroke', '#ffffff').attr('stroke-width', 3)
      d3.select(event.target).attr('fill', '#3498db')
      
      selectedItem.value = {
        type: 'edge',
        data: d.rawData
      }
    })
  
  // Save reference for external visibility control
  linkLabelsRef = linkLabels
  linkLabelBgRef = linkLabelBg

  // Nodes group
  const nodeGroup = g.append('g').attr('class', 'nodes')
  
  // Node circles
  const node = nodeGroup.selectAll('circle')
    .data(nodes)
    .enter().append('circle')
    .attr('r', 10)
    .attr('fill', d => getColor(d.type))
    .attr('stroke', 'rgba(255, 255, 255, 0.85)')
    .attr('stroke-width', 2.5)
    .style('cursor', 'pointer')
    .call(d3.drag()
      .on('start', (event, d) => {
        d.fx = d.x
        d.fy = d.y
        d._dragStartX = event.x
        d._dragStartY = event.y
        d._isDragging = false
      })
      .on('drag', (event, d) => {
        const dx = event.x - d._dragStartX
        const dy = event.y - d._dragStartY
        const distance = Math.sqrt(dx * dx + dy * dy)
        
        if (!d._isDragging && distance > 3) {
          d._isDragging = true
          simulation.alphaTarget(0.3).restart()
        }
        
        if (d._isDragging) {
          d.fx = event.x
          d.fy = event.y
        }
      })
      .on('end', (event, d) => {
        if (d._isDragging) {
          simulation.alphaTarget(0)
        }
        d.fx = null
        d.fy = null
        d._isDragging = false
      })
    )
    .on('click', (event, d) => {
      event.stopPropagation()
      node.attr('stroke', 'rgba(255, 255, 255, 0.85)').attr('stroke-width', 2.5)
      linkGroup.selectAll('path').attr('stroke', 'rgba(255, 255, 255, 0.22)').attr('stroke-width', 1.5)
      d3.select(event.target).attr('stroke', '#ffffff').attr('stroke-width', 4)
      link.filter(l => l.source.id === d.id || l.target.id === d.id)
        .attr('stroke', '#ffffff')
        .attr('stroke-width', 2.5)
      
      selectedItem.value = {
        type: 'node',
        data: d.rawData,
        entityType: d.type,
        color: getColor(d.type)
      }
    })
    .on('mouseenter', (event, d) => {
      if (!selectedItem.value || selectedItem.value.data?.uuid !== d.rawData.uuid) {
        d3.select(event.target).attr('stroke', '#ffffff').attr('stroke-width', 3)
      }
    })
    .on('mouseleave', (event, d) => {
      if (!selectedItem.value || selectedItem.value.data?.uuid !== d.rawData.uuid) {
        d3.select(event.target).attr('stroke', 'rgba(255, 255, 255, 0.85)').attr('stroke-width', 2.5)
      }
    })

  // Node Labels
  const nodeLabels = nodeGroup.selectAll('text')
    .data(nodes)
    .enter().append('text')
    .text(d => d.name.length > 8 ? d.name.substring(0, 8) + '…' : d.name)
    .attr('font-size', '11px')
    .attr('fill', '#ffffff')
    .attr('font-weight', '500')
    .attr('dx', 14)
    .attr('dy', 4)
    .style('pointer-events', 'none')
    .style('font-family', 'system-ui, sans-serif')

  simulation.on('tick', () => {
    link.attr('d', d => getLinkPath(d))
    
    if (showEdgeLabels.value) {
      linkLabels
        .attr('x', d => getLinkMidpoint(d).x)
        .attr('y', d => getLinkMidpoint(d).y)
      
      linkLabelBg
        .attr('x', d => getLinkMidpoint(d).x - d._labelW / 2)
        .attr('y', d => getLinkMidpoint(d).y - d._labelH / 2)
    }

    node
      .attr('cx', d => d.x)
      .attr('cy', d => d.y)

    nodeLabels
      .attr('x', d => d.x)
      .attr('y', d => d.y)
  })
  
  svg.on('click', () => {
    selectedItem.value = null
    node.attr('stroke', 'rgba(255, 255, 255, 0.85)').attr('stroke-width', 2.5)
    linkGroup.selectAll('path').attr('stroke', 'rgba(255, 255, 255, 0.22)').attr('stroke-width', 1.5)
    linkLabelBg.attr('fill', 'rgba(12, 12, 16, 0.92)')
    linkLabels.attr('fill', '#d4d4d8')
  })
}

watch(() => props.graphData, (newData) => {
  if (newData) {
    nextTick(renderGraph)
  }
}, { deep: true, immediate: true })

// Watch edge labels visibility toggle
watch(showEdgeLabels, (newVal) => {
  if (linkLabelsRef) {
    linkLabelsRef.style('display', newVal ? 'block' : 'none')
  }
  if (linkLabelBgRef) {
    linkLabelBgRef.style('display', newVal ? 'block' : 'none')
  }
  if (newVal && linkLabelsRef && linkLabelBgRef) {
    linkLabelsRef
      .attr('x', d => getLinkMidpoint(d).x)
      .attr('y', d => getLinkMidpoint(d).y)
    linkLabelBgRef
      .attr('x', d => getLinkMidpoint(d).x - d._labelW / 2)
      .attr('y', d => getLinkMidpoint(d).y - d._labelH / 2)
  }
})

const handleResize = () => {
  nextTick(renderGraph)
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
  if (props.graphData) {
    nextTick(renderGraph)
  }
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (currentSimulation) {
    currentSimulation.stop()
  }
})
</script>

<style scoped>
.graph-panel {
  position: relative;
  width: 100%;
  height: 100%;
  background: #08080c;
  overflow: hidden;
}

.panel-header {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  padding: 18px 24px;
  z-index: 10;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(to bottom, rgba(6, 6, 9, 0.95) 0%, rgba(6, 6, 9, 0) 100%);
  pointer-events: none;
}

.panel-title {
  font-family: var(--font-display, 'Syne', sans-serif);
  font-size: 14px;
  font-weight: 700;
  letter-spacing: -0.01em;
  color: #ffffff;
  /* no text shadow */
  pointer-events: auto;
}

.header-tools {
  pointer-events: auto;
  display: flex;
  gap: 10px;
  align-items: center;
}

.tool-btn {
  height: 32px;
  padding: 0 14px;
  border: 1px solid rgba(255, 255, 255, 0.14);
  background: rgba(18, 18, 24, 0.8);
    border-radius: 999px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  cursor: pointer;
  color: #e4e4e7;
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  font-weight: 600;
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
  /* no box shadow */
}

.tool-btn:hover:not(:disabled) {
  background: rgba(30, 30, 40, 0.95);
  border-color: rgba(255, 255, 255, 0.4);
  color: #ffffff;
  transform: translateY(-1px);
  /* no box shadow */
}

.tool-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.tool-btn .btn-text {
  font-size: 11px;
}

.icon-refresh.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }

.graph-container {
  width: 100%;
  height: 100%;
  position: relative;
}

.graph-view, .graph-svg {
  width: 100%;
  height: 100%;
  display: block;
}

/* ===== Venom Symbiote Neural Nexus (Empty/Waiting State) ===== */
.graph-state {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  pointer-events: none;
  z-index: 5;
  width: 100%;
}

/* Active Loading / Ingestion State Enhancements */
.graph-state.venom-symbiote-empty.is-loading .symbiote-orbit-tracker.orbit-cw {
  animation: orbit-rotate 7s linear infinite;
}

.graph-state.venom-symbiote-empty.is-loading .symbiote-orbit-tracker.orbit-ccw {
  animation: orbit-rotate 9s linear infinite reverse;
}

.graph-state.venom-symbiote-empty.is-loading .symbiote-pulse-ring.ring-1 {
  border-color: rgba(255, 255, 255, 0.65);
  animation: symbiote-ring-pulse 1.8s ease-out infinite;
}

.graph-state.venom-symbiote-empty.is-loading .symbiote-pulse-ring.ring-2 {
  border-color: rgba(255, 255, 255, 0.45);
  animation: symbiote-ring-pulse 1.8s ease-out infinite 0.6s;
}

.graph-state.venom-symbiote-empty.is-loading .symbiote-pulse-ring.ring-3 {
  border-color: rgba(255, 255, 255, 0.28);
  animation: symbiote-ring-pulse 1.8s ease-out infinite 1.2s;
}

.symbiote-scan-beam {
  position: absolute;
  left: 10%;
  width: 80%;
  height: 2px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.9), transparent);
  box-shadow: 0 0 10px rgba(255, 255, 255, 0.6);
  animation: symbiote-scan 2.2s ease-in-out infinite alternate;
  pointer-events: none;
  z-index: 4;
}

@keyframes symbiote-scan {
  0% { top: 15%; opacity: 0.2; }
  50% { opacity: 1; }
  100% { top: 85%; opacity: 0.2; }
}

.pulse-spark.active {
  background: #ffffff;
  box-shadow: 0 0 8px rgba(255, 255, 255, 0.85);
  animation: spark-blink 0.8s infinite;
}

.pill-dot.active {
  background: #ffffff;
  box-shadow: 0 0 8px rgba(255, 255, 255, 0.85);
  animation: spark-blink 1s infinite;
}

.graph-refreshing-badge {
  position: absolute;
  top: 14px;
  right: 14px;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 14px;
  border-radius: 999px;
  background: rgba(14, 14, 18, 0.88);
  border: 1px solid rgba(255, 255, 255, 0.18);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  color: #ffffff;
  backdrop-filter: blur(8px);
  z-index: 15;
  pointer-events: none;
}

.refresh-spinner-dot {
  width: 10px;
  height: 10px;
  border: 2px solid rgba(255, 255, 255, 0.25);
  border-top-color: #ffffff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
.graph-state.venom-symbiote-empty {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  pointer-events: none;
  z-index: 5;
}

.symbiote-core-wrapper {
  position: relative;
  width: 140px;
  height: 140px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 24px;
}

.symbiote-pulse-ring {
  position: absolute;
  border-radius: 50%;
  border: 1px solid rgba(255, 255, 255, 0.12);
  pointer-events: none;
}

.symbiote-pulse-ring.ring-1 {
  width: 80px;
  height: 80px;
  border-color: rgba(255, 255, 255, 0.35);
  animation: symbiote-ring-pulse 3s ease-out infinite;
}

.symbiote-pulse-ring.ring-2 {
  width: 110px;
  height: 110px;
  border-color: rgba(255, 255, 255, 0.2);
  animation: symbiote-ring-pulse 3s ease-out infinite 1s;
}

.symbiote-pulse-ring.ring-3 {
  width: 140px;
  height: 140px;
  border-color: rgba(255, 255, 255, 0.15);
  animation: symbiote-ring-pulse 3s ease-out infinite 2s;
}

@keyframes symbiote-ring-pulse {
  0% {
    transform: scale(0.65);
    opacity: 0.8;
  }
  50% {
    opacity: 0.4;
  }
  100% {
    transform: scale(1.35);
    opacity: 0;
  }
}

.symbiote-orbit-tracker {
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 50%;
}

.symbiote-orbit-tracker.orbit-cw {
  animation: orbit-rotate 12s linear infinite;
}

.symbiote-orbit-tracker.orbit-ccw {
  animation: orbit-rotate 16s linear infinite reverse;
}

@keyframes orbit-rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.orbital-node {
  position: absolute;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #ffffff;
  /* no box shadow */
}

.node-1 { top: 6px; left: 50%; transform: translateX(-50%); }
.node-2 { bottom: 6px; left: 50%; transform: translateX(-50%); }
.node-3 { top: 50%; left: 6px; transform: translateY(-50%); background: #ffffff; /* no box shadow */ }
.node-4 { top: 50%; right: 6px; transform: translateY(-50%); background: #ffffff; /* no box shadow */ }

.symbiote-nexus-glyph {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  background: radial-gradient(circle at 35% 35%, #2a2a34 0%, #101015 65%, #040406 100%);
  border: 1px solid rgba(255, 255, 255, 0.28);
  display: flex;
  align-items: center;
  justify-content: center;
  /* no box shadow */
  position: relative;
  z-index: 2;
  animation: nexus-float 3s ease-in-out infinite alternate;
}

@keyframes nexus-float {
  0% { transform: translateY(-2px) scale(0.98); }
  100% { transform: translateY(2px) scale(1.02); }
}

.nexus-symbol {
  font-size: 26px;
  color: #ffffff;
  /* no text shadow */
  animation: nexus-spin-subtle 8s ease-in-out infinite alternate;
}

@keyframes nexus-spin-subtle {
  0% { transform: rotate(-5deg) scale(0.95); }
  100% { transform: rotate(5deg) scale(1.05); }
}

.empty-status-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.empty-title {
  font-family: var(--font-display, 'Syne', sans-serif);
  font-size: 17px;
  font-weight: 700;
  letter-spacing: -0.01em;
  color: #ffffff;
  margin: 0;
  /* no text shadow */
}

.empty-subtitle {
  font-size: 13px;
  color: #a1a1aa;
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
}

.pulse-spark {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #ffffff;
  /* no box shadow */
  animation: spark-blink 1.5s infinite;
}

@keyframes spark-blink {
  0%, 100% { opacity: 0.3; transform: scale(0.8); }
  50% { opacity: 1; transform: scale(1.2); }
}

.empty-endpoint-pill {
  margin-top: 6px;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 4px 12px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.1);
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  color: #71717a;
}

.pill-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: #ffffff;
  /* no box shadow */
}

/* Entity Types Legend - Bottom Left */
.graph-legend {
  position: absolute;
  bottom: 24px;
  left: 24px;
  background: rgba(10, 10, 15, 0.9);
  padding: 14px 18px;
  border-radius: 14px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  /* no box shadow */
    z-index: 10;
}

.legend-title {
  display: block;
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  font-weight: 700;
  color: #ffffff;
  margin-bottom: 10px;
  text-transform: uppercase;
  letter-spacing: 0.8px;
}

.legend-items {
  display: flex;
  flex-wrap: wrap;
  gap: 10px 16px;
  max-width: 320px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #e4e4e7;
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
  /* no box shadow */
}

.legend-label {
  white-space: nowrap;
}

/* Edge Labels Toggle - Top Right */
.edge-labels-toggle {
  position: absolute;
  top: 60px;
  right: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
  background: rgba(10, 10, 15, 0.85);
  padding: 8px 14px;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.1);
    z-index: 10;
  transition: all 0.25s ease;
  user-select: none;
}

.edge-labels-toggle:hover {
  border-color: rgba(148, 163, 184, 0.35);
}

.edge-labels-toggle.active {
  border-color: rgba(148, 163, 184, 0.35);
  background: rgba(15, 23, 42, 0.7);
}

.toggle-switch {
  position: relative;
  display: inline-block;
  width: 36px;
  height: 20px;
}

.toggle-switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.14);
  border-radius: 20px;
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

.slider:before {
  position: absolute;
  content: "";
  height: 12px;
  width: 12px;
  left: 3px;
  bottom: 3px;
  background-color: #64748B;
  border-radius: 50%;
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

/* When turned ON: Slate grey #94A3B8 minimal, monochrome, and understated */
input:checked + .slider {
  background-color: #94A3B8;
  border-color: #94A3B8;
}

input:checked + .slider:before {
  transform: translateX(16px);
  background-color: #060608;
}

.toggle-label {
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  color: #94A3B8;
  letter-spacing: 0.3px;
  transition: color 0.25s ease;
}

.edge-labels-toggle.active .toggle-label {
  color: #F1F5F9;
}

/* Detail Panel - Right Side */
.detail-panel {
  position: absolute;
  top: 60px;
  right: 20px;
  width: 340px;
  max-height: calc(100% - 100px);
  background: rgba(10, 10, 15, 0.94);
  border: 1px solid rgba(255, 255, 255, 0.14);
  border-radius: 16px;
  /* no box shadow */
    overflow: hidden;
  font-family: var(--font-body, system-ui, sans-serif);
  font-size: 13px;
  z-index: 25;
  display: flex;
  flex-direction: column;
}

.detail-panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 18px;
  background: rgba(18, 18, 24, 0.9);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  flex-shrink: 0;
}

.detail-title {
  font-family: var(--font-display, 'Syne', sans-serif);
  font-weight: 700;
  color: #ffffff;
  font-size: 14px;
}

.detail-type-badge {
  padding: 4px 10px;
  border-radius: 999px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 10px;
  font-weight: 700;
  margin-left: auto;
  margin-right: 12px;
  text-transform: uppercase;
}

.detail-close {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 50%;
  width: 26px;
  height: 26px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  cursor: pointer;
  color: #a1a1aa;
  transition: all 0.2s;
}

.detail-close:hover {
  background: #ffffff;
  color: #000000;
  border-color: #ffffff;
}

.detail-content {
  padding: 18px;
  overflow-y: auto;
  flex: 1;
}

.detail-row {
  margin-bottom: 12px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.detail-label {
  color: #71717a;
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  font-weight: 600;
  min-width: 80px;
}

.detail-value {
  color: #f4f4f5;
  flex: 1;
  word-break: break-word;
}

.detail-value.uuid-text {
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  color: #a1a1aa;
}

.detail-value.fact-text {
  color: #e4e4e7;
  line-height: 1.5;
}

.detail-section {
  margin-top: 16px;
  padding-top: 14px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.section-title {
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  font-weight: 700;
  color: #ffffff;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 10px;
}

.property-item {
  display: flex;
  margin-bottom: 6px;
  font-size: 12px;
}

.property-key {
  color: #71717a;
  min-width: 100px;
  font-family: 'JetBrains Mono', monospace;
}

.property-value {
  color: #ffffff;
  flex: 1;
}

.summary-text {
  color: #d4d4d8;
  line-height: 1.5;
  font-size: 12px;
}

.labels-list, .episodes-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.label-tag, .episode-tag {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.12);
  color: #e4e4e7;
  padding: 3px 8px;
  border-radius: 6px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 10px;
}

/* Building / Simulating Hint */
.graph-building-hint {
  position: absolute;
  top: 70px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(12, 12, 16, 0.88);
    color: #ffffff;
  padding: 10px 22px;
  border-radius: 999px;
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 10px;
  /* no box shadow */
  border: 1px solid rgba(255, 255, 255, 0.14);
  font-weight: 500;
  z-index: 100;
}

.memory-icon-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  animation: breathe 2s ease-in-out infinite;
}

.memory-icon {
  width: 18px;
  height: 18px;
  color: #ffffff;
}

@keyframes breathe {
  0%, 100% { opacity: 0.7; transform: scale(1); /* no drop shadow */ }
  50% { opacity: 1; transform: scale(1.15); /* no drop shadow */ }
}

/* Self-loop styles */
.self-loop-header {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(255, 255, 255, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.3);
  padding: 10px 14px;
  border-radius: 8px;
  color: #ffffff;
}

.self-loop-count {
  margin-left: auto;
  font-size: 11px;
  color: #ffffff;
  background: rgba(255, 255, 255, 0.15);
  padding: 2px 8px;
  border-radius: 10px;
}

.self-loop-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.self-loop-item {
  background: rgba(20, 20, 26, 0.75);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px;
}

.self-loop-item-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  background: rgba(25, 25, 32, 0.9);
  cursor: pointer;
  transition: background 0.2s;
}

.self-loop-item-header:hover {
  background: rgba(35, 35, 45, 0.95);
}

.self-loop-index {
  font-size: 10px;
  font-weight: 600;
  color: #a1a1aa;
  background: rgba(255, 255, 255, 0.08);
  padding: 2px 6px;
  border-radius: 4px;
}

.self-loop-name {
  font-size: 12px;
  font-weight: 500;
  color: #ffffff;
  flex: 1;
}

.self-loop-toggle {
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
  color: #a1a1aa;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 4px;
}

.self-loop-item-content {
  padding: 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

/* Loading spinner */


.graph-view, .graph-svg {
  width: 100%;
  height: 100%;
  display: block;
  cursor: grab;
}

.graph-svg:active {
  cursor: grabbing;
}

.graph-zoom-controls {
  position: absolute;
  bottom: 24px;
  right: 24px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  background: #0e0e14;
  border: 1px solid rgba(255, 255, 255, 0.14);
  border-radius: 10px;
  padding: 6px;
  z-index: 20;
}

.zoom-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 6px;
  color: #ffffff;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.zoom-btn:hover {
  background: rgba(255, 255, 255, 0.18);
  border-color: rgba(255, 255, 255, 0.25);
  transform: scale(1.05);
}

.zoom-btn:active {
  transform: scale(0.95);
}

</style>