<template>
  <div class="workbench-panel">
                <!-- Venom Cyber Grid & Web Strings Background Patterns Layer (Pure Glass Backing) -->
    <div class="workbench-venom-bg pointer-events-none select-none absolute inset-0 z-0 overflow-hidden">
      <!-- 1. Cyber Perspective Ceiling & Floor Plane Grid Lines -->
      <svg class="cyber-grid-svg absolute inset-0 w-full h-full" viewBox="0 0 800 1200" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <linearGradient id="gridLineFade" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stop-color="#ffffff" stop-opacity="0.4" />
            <stop offset="30%" stop-color="#ffffff" stop-opacity="0.2" />
            <stop offset="70%" stop-color="#ffffff" stop-opacity="0.15" />
            <stop offset="100%" stop-color="#ffffff" stop-opacity="0.3" />
          </linearGradient>
        </defs>
        <!-- Horizontal grid lines across all 3 card zones -->
        <line x1="0" y1="40" x2="800" y2="40" stroke="url(#gridLineFade)" stroke-width="1" />
        <line x1="0" y1="120" x2="800" y2="120" stroke="url(#gridLineFade)" stroke-width="1.2" />
        <line x1="0" y1="220" x2="800" y2="220" stroke="url(#gridLineFade)" stroke-width="1" />
        <line x1="0" y1="360" x2="800" y2="360" stroke="url(#gridLineFade)" stroke-width="1.2" />
        <line x1="0" y1="520" x2="800" y2="520" stroke="url(#gridLineFade)" stroke-width="1" />
        <line x1="0" y1="680" x2="800" y2="680" stroke="url(#gridLineFade)" stroke-width="1.2" />
        <line x1="0" y1="840" x2="800" y2="840" stroke="url(#gridLineFade)" stroke-width="1" />
        <line x1="0" y1="1020" x2="800" y2="1020" stroke="url(#gridLineFade)" stroke-width="1.2" />
        <line x1="0" y1="1160" x2="800" y2="1160" stroke="url(#gridLineFade)" stroke-width="1" />
        <!-- Vertical grid lines -->
        <line x1="40" y1="0" x2="40" y2="1200" stroke="url(#gridLineFade)" stroke-width="1.2" />
        <line x1="160" y1="0" x2="160" y2="1200" stroke="url(#gridLineFade)" stroke-width="1" />
        <line x1="320" y1="0" x2="320" y2="1200" stroke="url(#gridLineFade)" stroke-width="1.2" />
        <line x1="480" y1="0" x2="480" y2="1200" stroke="url(#gridLineFade)" stroke-width="1" />
        <line x1="640" y1="0" x2="640" y2="1200" stroke="url(#gridLineFade)" stroke-width="1.2" />
        <line x1="760" y1="0" x2="760" y2="1200" stroke="url(#gridLineFade)" stroke-width="1" />
        <!-- Perspective converging lines -->
        <line x1="0" y1="0" x2="400" y2="600" stroke="url(#gridLineFade)" stroke-width="0.8" />
        <line x1="800" y1="0" x2="400" y2="600" stroke="url(#gridLineFade)" stroke-width="0.8" />
        <line x1="0" y1="1200" x2="400" y2="600" stroke="url(#gridLineFade)" stroke-width="0.8" />
        <line x1="800" y1="1200" x2="400" y2="600" stroke="url(#gridLineFade)" stroke-width="0.8" />
      </svg>

      <!-- 2. Venomous Web Strands, Fissure Cracks & Suspension Cables -->
      <svg class="venom-webs-svg absolute inset-0 w-full h-full" viewBox="0 0 800 1200" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <linearGradient id="wbSheen" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#ffffff" stop-opacity="0.95" />
            <stop offset="25%" stop-color="#d4d4d8" stop-opacity="0.75" />
            <stop offset="60%" stop-color="#71717a" stop-opacity="0.5" />
            <stop offset="100%" stop-color="#ffffff" stop-opacity="0.9" />
          </linearGradient>
          <linearGradient id="fisGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#ffffff" stop-opacity="1" />
            <stop offset="50%" stop-color="#e4e4e7" stop-opacity="0.75" />
            <stop offset="100%" stop-color="#a1a1aa" stop-opacity="0.45" />
          </linearGradient>
          <radialGradient id="dropGrad" cx="35%" cy="30%" r="65%">
            <stop offset="0%" stop-color="#ffffff" stop-opacity="1" />
            <stop offset="30%" stop-color="#a1a1aa" stop-opacity="0.85" />
            <stop offset="75%" stop-color="#27272a" stop-opacity="0.95" />
            <stop offset="100%" stop-color="#09090b" stop-opacity="1" />
          </radialGradient>
        </defs>

        <!-- SPREADING FRACTURE CRACKS (running through Step 01, 02, and 03) -->
        <g class="fissure-cracks-group">
          <g stroke="url(#fisGrad)" stroke-linecap="round" stroke-linejoin="bevel">
            <!-- Crack 1: Top-left down through Step 01 & Step 02 -->
            <path d="M 0,40 L 90,95 L 140,80 L 210,175 L 270,230 L 350,265 L 430,360 L 390,440 L 460,520 L 520,610 L 490,700 L 570,810 L 630,920 L 720,1050 L 800,1110" stroke-width="2.2" fill="none" />
            <path d="M 140,80 L 190,35 L 250,20" stroke-width="1.3" fill="none" />
            <path d="M 270,230 L 330,205 L 400,210" stroke-width="1.3" fill="none" />
            <path d="M 430,360 L 490,410 L 530,475" stroke-width="1.4" fill="none" />
            <path d="M 520,610 L 580,570 L 640,560" stroke-width="1.3" fill="none" />
            <path d="M 570,810 L 640,830 L 700,790" stroke-width="1.4" fill="none" />
            <!-- Crack 2: Right edge through Step 02 & Step 03 -->
            <path d="M 800,320 L 710,380 L 660,360 L 580,450 L 530,520 L 440,550 L 370,640 L 320,720 L 250,760 L 180,870 L 110,910 L 0,980" stroke-width="2" fill="none" />
            <path d="M 660,360 L 620,310 L 580,290" stroke-width="1.2" fill="none" />
            <path d="M 440,550 L 390,520 L 340,530" stroke-width="1.2" fill="none" />
            <path d="M 320,720 L 270,690 L 220,700" stroke-width="1.2" fill="none" />
          </g>
        </g>

        <!-- CORNER & EDGE SPIDERWEBS -->
        <g class="corner-webs-group">
          <!-- Top-Left Radial Web Spokes & Drooping Arcs (Step 01 zone) -->
          <g stroke="rgba(255,255,255,0.6)" stroke-width="1.2" fill="none">
            <line x1="0" y1="0" x2="320" y2="70" />
            <line x1="0" y1="0" x2="260" y2="190" />
            <line x1="0" y1="0" x2="160" y2="300" />
            <line x1="0" y1="0" x2="50" y2="380" />
          </g>
          <g stroke="url(#wbSheen)" stroke-width="1.8" fill="none">
            <path d="M 85,0 Q 68,32 50,74 Q 34,100 0,116" />
            <path d="M 180,0 Q 152,70 114,152 Q 70,212 0,238" />
            <path d="M 295,0 Q 250,108 188,232 Q 108,328 0,382" />
            <path d="M 425,0 Q 355,158 272,334 Q 158,464 0,538" />
          </g>

          <!-- Top-Right Radial Web Spokes & Drooping Arcs -->
          <g stroke="rgba(255,255,255,0.6)" stroke-width="1.2" fill="none">
            <line x1="800" y1="0" x2="480" y2="70" />
            <line x1="800" y1="0" x2="540" y2="190" />
            <line x1="800" y1="0" x2="640" y2="300" />
            <line x1="800" y1="0" x2="750" y2="380" />
          </g>
          <g stroke="url(#wbSheen)" stroke-width="1.8" fill="none">
            <path d="M 715,0 Q 732,32 750,74 Q 766,100 800,116" />
            <path d="M 620,0 Q 648,70 686,152 Q 730,212 800,238" />
            <path d="M 505,0 Q 550,108 612,232 Q 692,328 800,382" />
            <path d="M 375,0 Q 445,158 528,334 Q 642,464 800,538" />
          </g>

          <!-- Bottom-Left Radial Web Spokes & Arcs (Step 03 zone) -->
          <g stroke="rgba(255,255,255,0.5)" stroke-width="1.2" fill="none">
            <line x1="0" y1="1200" x2="280" y2="1080" />
            <line x1="0" y1="1200" x2="220" y2="970" />
            <line x1="0" y1="1200" x2="130" y2="880" />
          </g>
          <g stroke="url(#wbSheen)" stroke-width="1.6" fill="none">
            <path d="M 0,1050 Q 80,1060 150,1200" />
            <path d="M 0,920 Q 150,960 270,1200" />
            <path d="M 0,780 Q 220,840 390,1200" />
          </g>

          <!-- Bottom-Right Radial Web Spokes & Arcs -->
          <g stroke="rgba(255,255,255,0.5)" stroke-width="1.2" fill="none">
            <line x1="800" y1="1200" x2="520" y2="1080" />
            <line x1="800" y1="1200" x2="580" y2="970" />
            <line x1="800" y1="1200" x2="670" y2="880" />
          </g>
          <g stroke="url(#wbSheen)" stroke-width="1.6" fill="none">
            <path d="M 800,1050 Q 720,1060 650,1200" />
            <path d="M 800,920 Q 650,960 530,1200" />
            <path d="M 800,780 Q 580,840 410,1200" />
          </g>
        </g>

        <!-- HANGING CATENARY SUSPENSION WEB STRINGS (Directly crossing behind Step 01, Step 02, and Step 03) -->
        <g class="hanging-cables-group">
          <g stroke="url(#wbSheen)" stroke-width="2" fill="none">
            <!-- Cable passing through Step 01 -->
            <path d="M 0,80 Q 400,240 800,90" />
            <path d="M 0,180 Q 420,380 800,190" />
            <!-- Cable passing between Step 01 & Step 02 -->
            <path d="M 0,310 Q 380,510 800,320" />
            <!-- Cable passing right through Step 02 (Knowledge Mapping & Stats) -->
            <path d="M 0,460 Q 440,680 800,470" />
            <path d="M 0,610 Q 400,810 800,620" />
            <!-- Cable passing through Step 03 (Action button area) -->
            <path d="M 0,760 Q 420,960 800,770" />
            <path d="M 0,920 Q 390,1100 800,930" />

            <!-- Diagonal cross-bracing web filaments connecting cables -->
            <path d="M 160,110 Q 240,210 320,290" />
            <path d="M 640,110 Q 560,210 480,290" />
            <path d="M 220,340 Q 300,460 380,570" />
            <path d="M 580,340 Q 500,460 420,570" />
            <path d="M 180,630 Q 280,750 360,860" />
            <path d="M 620,630 Q 520,750 440,860" />
          </g>
        </g>

        <!-- DANGLING VERTICAL DRIP FILAMENTS & PEARL DROPLETS -->
        <g class="hanging-droplets-group">
          <g stroke="rgba(255,255,255,0.5)" stroke-width="1.2" fill="none">
            <line x1="180" y1="0" x2="180" y2="210" />
            <line x1="310" y1="0" x2="310" y2="330" />
            <line x1="490" y1="0" x2="490" y2="280" />
            <line x1="620" y1="0" x2="620" y2="200" />
            <line x1="240" y1="360" x2="240" y2="520" />
            <line x1="560" y1="360" x2="560" y2="540" />
            <line x1="380" y1="580" x2="380" y2="760" />
            <line x1="450" y1="780" x2="450" y2="980" />
          </g>
          <!-- Glossy Hanging Venom Pearls -->
          <g>
            <circle cx="180" cy="214" r="5.5" fill="url(#dropGrad)" stroke="#ffffff" stroke-width="1" />
            <circle cx="310" cy="335" r="6.5" fill="url(#dropGrad)" stroke="#ffffff" stroke-width="1" />
            <circle cx="490" cy="284" r="6" fill="url(#dropGrad)" stroke="#ffffff" stroke-width="1" />
            <circle cx="620" cy="204" r="5" fill="url(#dropGrad)" stroke="#ffffff" stroke-width="1" />
            <circle cx="240" cy="525" r="6" fill="url(#dropGrad)" stroke="#ffffff" stroke-width="1" />
            <circle cx="560" cy="545" r="6" fill="url(#dropGrad)" stroke="#ffffff" stroke-width="1" />
            <circle cx="380" cy="765" r="6.5" fill="url(#dropGrad)" stroke="#ffffff" stroke-width="1" />
            <circle cx="450" cy="985" r="7" fill="url(#dropGrad)" stroke="#ffffff" stroke-width="1" />
          </g>
        </g>
      </svg>
    </div>

    <div class="scroll-container relative z-10">
      <!-- Step 01: Ontology -->
      <div class="step-card" :class="{ 'active': currentPhase === 0, 'completed': currentPhase > 0 }">
        <div class="card-header">
          <div class="step-info">
            <span class="step-num">01</span>
            <span class="step-title">Reality Blueprint</span>
          </div>
          <div class="step-status">
            <span v-if="currentPhase > 0" class="badge success">{{ $t('step1.ontologyCompleted') }}</span>
            <span v-else-if="currentPhase === 0" class="badge processing">{{ $t('step1.ontologyGenerating') }}</span>
            <span v-else class="badge pending">{{ $t('step1.ontologyPending') }}</span>
          </div>
        </div>
        
        <div class="card-content">
          <div class="api-note"><span class="method-tag">POST</span><code>/api/graph/ontology/generate</code></div>
          <p class="description">
            {{ $t('step1.ontologyDesc') }}
          </p>

          <!-- Loading / Progress -->
          <div v-if="currentPhase === 0 && ontologyProgress" class="progress-section">
            <div class="spinner-sm"></div>
            <span>{{ ontologyProgress.message || $t('step1.analyzingDocs') }}</span>
          </div>

          <!-- Detail Overlay -->
          <div v-if="selectedOntologyItem" class="ontology-detail-overlay">
            <div class="detail-header">
               <div class="detail-title-group">
                  <span class="detail-type-badge">{{ selectedOntologyItem.itemType === 'entity' ? 'ENTITY' : 'RELATION' }}</span>
                  <span class="detail-name">{{ selectedOntologyItem.name }}</span>
               </div>
               <button class="close-btn" @click="selectedOntologyItem = null">×</button>
            </div>
            <div class="detail-body">
               <div class="detail-desc">{{ selectedOntologyItem.description }}</div>
               
               <!-- Attributes -->
               <div class="detail-section" v-if="selectedOntologyItem.attributes?.length">
                  <span class="section-label">ATTRIBUTES</span>
                  <div class="attr-list">
                     <div v-for="attr in selectedOntologyItem.attributes" :key="attr.name" class="attr-item">
                        <span class="attr-name">{{ attr.name }}</span>
                        <span class="attr-type">({{ attr.type }})</span>
                        <span class="attr-desc">{{ attr.description }}</span>
                     </div>
                  </div>
               </div>

               <!-- Examples (Entity) -->
               <div class="detail-section" v-if="selectedOntologyItem.examples?.length">
                  <span class="section-label">EXAMPLES</span>
                  <div class="example-list">
                     <span v-for="ex in selectedOntologyItem.examples" :key="ex" class="example-tag">{{ ex }}</span>
                  </div>
               </div>

               <!-- Source/Target (Relation) -->
               <div class="detail-section" v-if="selectedOntologyItem.source_targets?.length">
                  <span class="section-label">CONNECTIONS</span>
                  <div class="conn-list">
                     <div v-for="(conn, idx) in selectedOntologyItem.source_targets" :key="idx" class="conn-item">
                        <span class="conn-node">{{ conn.source }}</span>
                        <span class="conn-arrow">→</span>
                        <span class="conn-node">{{ conn.target }}</span>
                     </div>
                  </div>
               </div>
            </div>
          </div>

          <!-- Generated Entity Tags -->
          <div v-if="projectData?.ontology?.entity_types" class="tags-container" :class="{ 'dimmed': selectedOntologyItem }">
            <span class="tag-label">GENERATED ENTITY TYPES</span>
            <div class="tags-list">
              <span 
                v-for="entity in projectData.ontology.entity_types" 
                :key="entity.name" 
                class="entity-tag clickable"
                @click="selectOntologyItem(entity, 'entity')"
              >
                {{ entity.name }}
              </span>
            </div>
          </div>

          <!-- Generated Relation Tags -->
          <div v-if="projectData?.ontology?.edge_types" class="tags-container" :class="{ 'dimmed': selectedOntologyItem }">
            <span class="tag-label">GENERATED RELATION TYPES</span>
            <div class="tags-list">
              <span 
                v-for="rel in projectData.ontology.edge_types" 
                :key="rel.name" 
                class="entity-tag clickable"
                @click="selectOntologyItem(rel, 'relation')"
              >
                {{ rel.name }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Step 02: Graph Build -->
      <div class="step-card" :class="{ 'active': currentPhase === 1, 'completed': currentPhase > 1 }">
        <div class="card-header">
          <div class="step-info">
            <span class="step-num">02</span>
            <span class="step-title">Knowledge Mapping</span>
          </div>
          <div class="step-status">
            <span v-if="currentPhase > 1" class="badge success">{{ $t('step1.ontologyCompleted') }}</span>
            <span v-else-if="currentPhase === 1" class="badge processing">{{ buildProgress?.progress || 0 }}%</span>
            <span v-else class="badge pending">{{ $t('step1.ontologyPending') }}</span>
          </div>
        </div>

        <div class="card-content">
          <div class="api-note"><span class="method-tag">POST</span><code>/api/graph/build</code></div>
          <p class="description">
            {{ $t('step1.graphRagDesc') }}
          </p>
          
          <!-- Stats Cards -->
          <div class="stats-grid">
            <div class="stat-card">
              <span class="stat-value">{{ graphStats.nodes }}</span>
              <span class="stat-label">{{ $t('step1.entityNodes') }}</span>
            </div>
            <div class="stat-card">
              <span class="stat-value">{{ graphStats.edges }}</span>
              <span class="stat-label">{{ $t('step1.relationEdges') }}</span>
            </div>
            <div class="stat-card">
              <span class="stat-value">{{ graphStats.types }}</span>
              <span class="stat-label">{{ $t('step1.schemaTypes') }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Step 03: Complete -->
      <div class="step-card" :class="{ 'active': currentPhase === 2, 'completed': currentPhase >= 2 }">
        <div class="card-header">
          <div class="step-info">
            <span class="step-num">03</span>
            <span class="step-title">Graph Built. Brain Relaxed.</span>
          </div>
          <div class="step-status">
            <span v-if="currentPhase >= 2" class="badge accent">{{ $t('step1.inProgress') }}</span>
          </div>
        </div>
        
        <div class="card-content">
          <div class="api-note"><span class="method-tag">POST</span><code>/api/simulation/create</code></div>
          <p class="description">{{ $t('step1.buildCompleteDesc') }}</p>
          <button 
            class="venom-action-btn" 
            :disabled="currentPhase < 2 || creatingSimulation"
            @click="handleEnterEnvSetup"
          >
            <span class="btn-inner-content">
              <span v-if="creatingSimulation" class="spinner-sm"></span>
              <span>{{ creatingSimulation ? $t('step1.creating') : $t('step1.enterEnvSetup') + ' ➝' }}</span>
            </span>
          </button>
        </div>
      </div>
    </div>

    <!-- Floating Windows Terminal Component -->
    <FloatingTerminal
      title="SYSTEM DASHBOARD"
      :logs="systemLogs"
    />
  </div>
</template>

<script setup>
import { computed, ref, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { createSimulation } from '../api/simulation'
import FloatingTerminal from './FloatingTerminal.vue'

const router = useRouter()
const { t } = useI18n()

const props = defineProps({
  currentPhase: { type: Number, default: 0 },
  projectData: Object,
  ontologyProgress: Object,
  buildProgress: Object,
  graphData: Object,
  systemLogs: { type: Array, default: () => [] }
})

defineEmits(['next-step'])

const selectedOntologyItem = ref(null)
const logContent = ref(null)
const creatingSimulation = ref(false)

// Enter environment setup - create simulation and navigate
const handleEnterEnvSetup = async () => {
  if (!props.projectData?.project_id || !props.projectData?.graph_id) {
    console.error('Missing project or graph information')
    return
  }
  
  creatingSimulation.value = true
  
  try {
    const res = await createSimulation({
      project_id: props.projectData.project_id,
      graph_id: props.projectData.graph_id,
      enable_twitter: true,
      enable_reddit: true
    })
    
    if (res.success && res.data?.simulation_id) {
      // Navigate to simulation page
      router.push({
        name: 'Simulation',
        params: { simulationId: res.data.simulation_id }
      })
    } else {
      console.error('Failed to create simulation:', res.error)
      alert(t('step1.createSimulationFailed', { error: res.error || t('common.unknownError') }))
    }
  } catch (err) {
    console.error('Exception creating simulation:', err)
    alert(t('step1.createSimulationException', { error: err.message }))
  } finally {
    creatingSimulation.value = false
  }
}

const selectOntologyItem = (item, type) => {
  selectedOntologyItem.value = { ...item, itemType: type }
}

const graphStats = computed(() => {
  const nodes = props.graphData?.node_count || props.graphData?.nodes?.length || 0
  const edges = props.graphData?.edge_count || props.graphData?.edges?.length || 0
  const types = props.projectData?.ontology?.entity_types?.length || 0
  return { nodes, edges, types }
})

const formatDate = (dateStr) => {
  if (!dateStr) return '--:--:--'
  const d = new Date(dateStr)
  return d.toLocaleTimeString('en-US', { hour12: false }) + '.' + d.getMilliseconds()
}

// Auto-scroll logs
watch(() => props.systemLogs.length, () => {
  nextTick(() => {
    if (logContent.value) {
      logContent.value.scrollTop = logContent.value.scrollHeight
    }
  })
})
</script>

<style scoped>
.workbench-panel {
  height: 100%;
  background: radial-gradient(circle at 85% 15%, #0e0e14 0%, #060608 60%, #020203 100%);
  color: #f5f5f7;
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
  font-family: var(--font-body, system-ui, sans-serif);
}

.workbench-venom-bg {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 0;
}

.cyber-grid-svg {
  opacity: 0.18;
}

.venom-webs-svg {
  opacity: 0.35;
}

.hanging-cables-group { animation: none; }

.hanging-droplets-group { animation: none; }

.fissure-cracks-group { animation: none; }

@keyframes web-breathe {
  0% { transform: scaleY(1) translateY(0); }
  50% { transform: scaleY(1.025) translateY(2px); }
  100% { transform: scaleY(0.985) translateY(-2px); }
}

@keyframes web-drip-sway {
  0% { transform: rotate(0deg); }
  50% { transform: rotate(0.4deg); }
  100% { transform: rotate(-0.4deg); }
}

@keyframes crack-pulse {
  0%, 100% { opacity: 0.85; }
  50% { opacity: 1; }
}

.scroll-container {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* Custom dark scrollbar */
.scroll-container::-webkit-scrollbar {
  width: 6px;
}

.scroll-container::-webkit-scrollbar-track {
  background: transparent;
}

.scroll-container::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.12);
  border-radius: 999px;
}

.scroll-container::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.25);
}

/* ===== Step Cards (Substantial Dark Obsidian Glass - High Color Weight) ===== */
.step-card {
  background: rgba(12, 12, 16, 0.78);
  border-radius: 18px;
  padding: 24px;
  border: 1px solid rgba(255, 255, 255, 0.13);
transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
  position: relative;
  z-index: 10;
}

.step-card:hover {
  transform: translateX(4px);
  border-color: rgba(255, 255, 255, 0.38);
  background: rgba(18, 18, 24, 0.9);
}

.step-card.active {
  border-color: #FFFFFF;
  background: rgba(16, 16, 22, 0.86);
}

.step-card.completed {
  border-color: rgba(255, 255, 255, 0.25);
  background: rgba(12, 12, 16, 0.78);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 18px;
}

.step-info {
  display: flex;
  align-items: center;
  gap: 14px;
}

.step-num {
  font-family: 'JetBrains Mono', monospace;
  font-size: 22px;
  font-weight: 800;
  color: #71717a;
  letter-spacing: -0.5px;
  transition: all 0.3s ease;
}

.step-card.active .step-num {
  color: #FFFFFF;
}

.step-card.completed .step-num {
  color: #FFFFFF;
}

.step-title {
  font-family: var(--font-display, 'Syne', sans-serif);
  font-weight: 700;
  font-size: 16px;
  color: #ffffff;
  letter-spacing: -0.01em;
}

/* Status Badges - Black & White */
.badge {
  font-family: 'JetBrains Mono', monospace;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.6px;
  padding: 4px 12px;
  border-radius: 999px;
  text-transform: uppercase;
transition: all 0.25s ease;
}

.badge.processing,
.badge.accent {
  background: rgba(255, 255, 255, 0.12);
  border: 1px solid #FFFFFF;
  color: #FFFFFF;
}

.badge.success {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.45);
  color: #FFFFFF;
}

.badge.pending {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #71717a;
}

/* API Note High-Tech Chip */
.api-note {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  color: #a1a1aa;
  background: rgba(18, 18, 24, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.1);
border-radius: 8px;
  padding: 5px 12px;
  margin-bottom: 14px;
}

.method-tag {
  color: #000000;
  background: #FFFFFF;
  font-weight: 800;
  font-size: 10px;
  padding: 1px 6px;
  border-radius: 4px;
  letter-spacing: 0.5px;
}

.description {
  font-size: 13px;
  color: #a1a1ad;
  line-height: 1.6;
  margin-bottom: 18px;
}

/* Progress / Spinner - Black & White */
.progress-section {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 13px;
  font-weight: 500;
  color: #FFFFFF;
  padding: 12px 18px;
  background: rgba(22, 22, 28, 0.78);
  border: 1px solid rgba(255, 255, 255, 0.2);
border-radius: 12px;
  margin-bottom: 16px;
  animation: pulse-progress-bw 2.5s ease-in-out infinite alternate;
}

@keyframes pulse-progress-bw {
  0% { border-color: rgba(255, 255, 255, 0.15); }
  100% { border-color: rgba(255, 255, 255, 0.45); }
}

.spinner-sm {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-top-color: #FFFFFF;
  border-radius: 50%;
  animation: spin 0.9s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

/* Tags */
.tags-container {
  margin-top: 14px;
  transition: opacity 0.3s;
}

.tags-container.dimmed {
  opacity: 0.3;
  pointer-events: none;
}

.tag-label {
  display: block;
  font-family: 'JetBrains Mono', monospace;
  font-size: 10px;
  color: #71717a;
  letter-spacing: 0.6px;
  margin-bottom: 10px;
  font-weight: 600;
}

.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.entity-tag {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.12);
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 11px;
  color: #f4f4f5;
  font-family: 'JetBrains Mono', monospace;
transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.entity-tag.clickable {
  cursor: pointer;
}

.entity-tag.clickable:hover {
  background: rgba(255, 255, 255, 0.12);
  border-color: rgba(255, 255, 255, 0.38);
  color: #ffffff;
  transform: translateY(-1px);
}

/* Detail Overlay */
.ontology-detail-overlay {
  position: absolute;
  top: 60px;
  left: 20px;
  right: 20px;
  bottom: 20px;
  background: rgba(10, 10, 14, 0.85);
z-index: 15;
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  animation: fadeIn 0.25s ease-out;
}

@keyframes fadeIn { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: translateY(0); } }

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 18px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.03);
}

.detail-title-group {
  display: flex;
  align-items: center;
  gap: 10px;
}

.detail-type-badge {
  font-family: 'JetBrains Mono', monospace;
  font-size: 10px;
  font-weight: 800;
  color: #000000;
  background: #FFFFFF;
  padding: 3px 8px;
  border-radius: 4px;
  text-transform: uppercase;
}

.detail-name {
  font-size: 14px;
  font-weight: 700;
  font-family: 'JetBrains Mono', monospace;
  color: #ffffff;
}

.close-btn {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 50%;
  width: 26px;
  height: 26px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  color: #a1a1aa;
  cursor: pointer;
  transition: all 0.2s;
}

.close-btn:hover {
  background: #ffffff;
  color: #000000;
  border-color: #ffffff;
}

.detail-body {
  flex: 1;
  overflow-y: auto;
  padding: 18px;
}

.detail-desc {
  font-size: 13px;
  color: #d4d4d8;
  line-height: 1.6;
  margin-bottom: 18px;
  padding-bottom: 14px;
  border-bottom: 1px dashed rgba(255, 255, 255, 0.1);
}

.detail-section {
  margin-bottom: 18px;
}

.section-label {
  display: block;
  font-family: 'JetBrains Mono', monospace;
  font-size: 10px;
  font-weight: 700;
  color: #71717a;
  margin-bottom: 10px;
  letter-spacing: 0.6px;
}

.attr-list, .conn-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.attr-item {
  font-size: 12px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: baseline;
  padding: 6px 10px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 6px;
}

.attr-name {
  font-family: 'JetBrains Mono', monospace;
  font-weight: 600;
  color: #ffffff;
}

.attr-type {
  color: #a1a1aa;
  font-size: 11px;
}

.attr-desc {
  color: #d4d4d8;
  flex: 1;
  min-width: 150px;
}

.example-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.example-tag {
  font-size: 11px;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.12);
  padding: 4px 10px;
  border-radius: 999px;
  color: #e4e4e7;
}

.conn-item {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 12px;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 6px;
  font-family: 'JetBrains Mono', monospace;
}

.conn-node {
  font-weight: 600;
  color: #ffffff;
}

.conn-arrow {
  color: #FFFFFF;
}

/* Step 02 Stats Cards - Increased Color Weight */
.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 14px;
  background: rgba(8, 8, 12, 0.65);
  border: 1px solid rgba(255, 255, 255, 0.08);
padding: 18px;
  border-radius: 14px;
}

.stat-card {
  text-align: center;
  background: rgba(20, 20, 26, 0.78);
  border: 1px solid rgba(255, 255, 255, 0.12);
border-radius: 12px;
  padding: 16px 10px;
  transition: all 0.2s ease;
}

.stat-card:hover {
  background: rgba(28, 28, 36, 0.9);
  border-color: rgba(255, 255, 255, 0.35);
  transform: translateY(-2px);
}

.stat-value {
  display: block;
  font-size: 26px;
  font-weight: 800;
  color: #ffffff;
  font-family: 'JetBrains Mono', monospace;
}

.stat-label {
  font-family: 'JetBrains Mono', monospace;
  font-size: 10px;
  color: #71717a;
  text-transform: uppercase;
  margin-top: 6px;
  display: block;
  letter-spacing: 0.8px;
}

/* ===== Step 03 Enter Environment Setup Action Button ===== */
.venom-action-btn {
  width: 100%;
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 15px 28px;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  outline: none;
  cursor: pointer;
  background: rgba(22, 22, 30, 0.9);
color: #FFFFFF;
  font-family: var(--font-display, 'Syne', sans-serif);
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 0.3px;
  transition: background 0.2s ease, border-color 0.2s ease, color 0.2s ease, transform 0.2s ease;
  user-select: none;
}

.btn-inner-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.venom-action-btn:hover:not(:disabled) {
  background: #FFFFFF;
  border-color: #FFFFFF;
  color: #000000;
  transform: translateY(-1px);
}

.venom-action-btn:active:not(:disabled) {
  transform: translateY(0);
  background: #e4e4e7;
  color: #000000;
}

.venom-action-btn:disabled {
  background: rgba(255, 255, 255, 0.02);
  color: #52525b;
  border: 1px solid rgba(255, 255, 255, 0.08);
  cursor: not-allowed;
}
</style>