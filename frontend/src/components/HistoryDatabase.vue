<template>
  <div 
    class="history-database"
    :class="{ 'no-projects': projects.length === 0 && !loading }"
    ref="historyContainer"
  >
    <!-- Background decoration: technical grid lines (only shown when projects exist) -->
    <div v-if="projects.length > 0 || loading" class="tech-grid-bg">
      <div class="grid-pattern"></div>
      <div class="gradient-overlay"></div>
    </div>

    <!-- Title Area -->
    <div class="section-header">
      <div class="section-line"></div>
      <span class="section-title">{{ $t('history.title') }}</span>
      <div class="section-line"></div>
    </div>

    <!-- Card Container (only shown when projects exist) -->
    <div v-if="projects.length > 0" class="cards-container">
      <div 
        v-for="(project, index) in projects" 
        :key="project.simulation_id"
        class="project-card"
        :class="{ hovering: hoveringCard === index }"
        @mouseenter="handleCardHover(index)"
        @mouseleave="hoveringCard = null"
        @click="navigateToProject(project)"
      >
        <!-- Card Header: simulation_id and feature availability status -->
        <div class="card-header">
          <span class="card-id">{{ formatSimulationId(project.simulation_id) }}</span>
          <div class="card-status-icons">
            <span 
              class="status-icon" 
              :class="{ available: project.project_id, unavailable: !project.project_id }"
              :title="$t('history.graphBuild')"
            >&#9671;</span>
            <span 
              class="status-icon available" 
              :title="$t('history.envSetup')"
            >&#9672;</span>
            <span 
              class="status-icon" 
              :class="{ available: project.report_id, unavailable: !project.report_id }"
              :title="$t('history.analysisReport')"
            >&#9670;</span>
          </div>
        </div>

        <!-- File List Area -->
        <div class="card-files-wrapper">
          <!-- Corner decoration - viewfinder style -->
          <div class="corner-mark top-left-only"></div>
          
          <!-- File List -->
          <div class="files-list" v-if="project.files && project.files.length > 0">
            <div 
              v-for="(file, fileIndex) in project.files.slice(0, 3)" 
              :key="fileIndex"
              class="file-item"
            >
              <span class="file-tag" :class="getFileType(file.filename)">{{ getFileTypeLabel(file.filename) }}</span>
              <span class="file-name">{{ truncateFilename(file.filename, 20) }}</span>
            </div>
            <!-- If more files exist, show prompt -->
            <div v-if="project.files.length > 3" class="files-more">
              {{ $t('history.moreFiles', { count: project.files.length - 3 }) }}
            </div>
          </div>
          <!-- Placeholder when no files exist -->
          <div class="files-empty" v-else>
            <span class="empty-file-icon">&#9671;</span>
            <span class="empty-file-text">{{ $t('history.noFiles') }}</span>
          </div>
        </div>

        <!-- Card Title (uses first 20 characters of simulation requirement) -->
        <h3 class="card-title">{{ getSimulationTitle(project.simulation_requirement) }}</h3>

        <!-- Card Description (full simulation requirement display) -->
        <p class="card-desc">{{ truncateText(project.simulation_requirement, 55) }}</p>

        <!-- Card Footer -->
        <div class="card-footer">
          <div class="card-datetime">
            <span class="card-date">{{ formatDate(project.created_at) }}</span>
            <span class="card-time">{{ formatTime(project.created_at) }}</span>
          </div>
          <span class="card-progress" :class="getProgressClass(project)">
            <span class="status-dot">&#9679;</span> {{ formatRounds(project) }}
          </span>
        </div>
        
        <!-- Bottom decorative line (expands on hover) -->
        <div class="card-bottom-line"></div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <span class="loading-spinner"></span>
      <span class="loading-text">{{ $t('history.loadingText') }}</span>
    </div>

    <!-- History Replay Details Modal -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="selectedProject" class="modal-overlay" @click.self="closeModal">
          <div class="modal-content">
            <!-- Modal Header -->
            <div class="modal-header">
              <div class="modal-title-section">
                <span class="modal-id">{{ formatSimulationId(selectedProject.simulation_id) }}</span>
                <span class="modal-progress" :class="getProgressClass(selectedProject)">
                  <span class="status-dot">&#9679;</span> {{ formatRounds(selectedProject) }}
                </span>
                <span class="modal-create-time">{{ formatDate(selectedProject.created_at) }} {{ formatTime(selectedProject.created_at) }}</span>
              </div>
              <button class="modal-close" @click="closeModal">&times;</button>
            </div>

            <!-- Modal Content -->
            <div class="modal-body">
              <!-- Simulation Requirement -->
              <div class="modal-section">
                <div class="modal-label">{{ $t('history.simRequirement') }}</div>
                <div class="modal-requirement">{{ selectedProject.simulation_requirement || $t('common.none') }}</div>
              </div>

              <!-- File List -->
              <div class="modal-section">
                <div class="modal-label">{{ $t('history.relatedFiles') }}</div>
                <div class="modal-files" v-if="selectedProject.files && selectedProject.files.length > 0">
                  <div v-for="(file, index) in selectedProject.files" :key="index" class="modal-file-item">
                    <span class="file-tag" :class="getFileType(file.filename)">{{ getFileTypeLabel(file.filename) }}</span>
                    <span class="modal-file-name">{{ file.filename }}</span>
                  </div>
                </div>
                <div class="modal-empty" v-else>{{ $t('history.noRelatedFiles') }}</div>
              </div>
            </div>

            <!-- Deduction Replay Divider -->
            <div class="modal-divider">
              <span class="divider-line"></span>
              <span class="divider-text">{{ $t('history.replayTitle') }}</span>
              <span class="divider-line"></span>
            </div>

            <!-- Navigation Buttons -->
            <div class="modal-actions">
              <button 
                class="modal-btn btn-project" 
                @click="goToProject"
                @mouseenter="selectedProject.project_id && playHoverSound()"
                :disabled="!selectedProject.project_id"
              >
                <span class="btn-step">Step1</span>
                <span class="btn-icon">&#9671;</span>
                <span class="btn-text">{{ $t('history.step1Button') }}</span>
              </button>
              <button 
                class="modal-btn btn-simulation" 
                @click="goToSimulation"
                @mouseenter="playHoverSound"
              >
                <span class="btn-step">Step2</span>
                <span class="btn-icon">&#9672;</span>
                <span class="btn-text">{{ $t('history.step2Button') }}</span>
              </button>
              <button 
                class="modal-btn btn-report" 
                @click="goToReport"
                @mouseenter="selectedProject.report_id && playHoverSound()"
                :disabled="!selectedProject.report_id"
              >
                <span class="btn-step">Step4</span>
                <span class="btn-icon">&#9670;</span>
                <span class="btn-text">{{ $t('history.step4Button') }}</span>
              </button>
            </div>
            <!-- Non-replayable Hint -->
            <div class="modal-playback-hint">
              <span class="hint-text">{{ $t('history.replayHint') }}</span>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, onActivated, watch, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { getSimulationHistory } from '../api/simulation'
import hoverSoundSrc from '../assets/audio/hover.mp3'

const router = useRouter()
const route = useRoute()
const { t } = useI18n()

// State
const projects = ref([])
const loading = ref(true)
const hoveringCard = ref(null)
const historyContainer = ref(null)
const selectedProject = ref(null)  // Currently selected project (for modal)

// Keep a single horizontal row so the history scrolls sideways instead of expanding vertically.
const CARD_WIDTH = 280
const CARD_GAP = 24

// Get style class based on round progress
const getProgressClass = (simulation) => {
  const current = simulation.current_round || 0
  const total = simulation.total_rounds || 0
  
  if (total === 0 || current === 0) {
    // Not started
    return 'not-started'
  } else if (current >= total) {
    // Completed
    return 'completed'
  } else {
    // In progress
    return 'in-progress'
  }
}

// Format date (display date portion only)
const formatDate = (dateStr) => {
  if (!dateStr) return ''
  try {
    const date = new Date(dateStr)
    // Use local date components (like formatTime below) so the displayed day
    // matches the displayed time. toISOString() converts to UTC and can show
    // the wrong day for non-UTC clients near midnight.
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    return `${year}-${month}-${day}`
  } catch {
    return dateStr?.slice(0, 10) || ''
  }
}

// Format time (display HH:MM)
const formatTime = (dateStr) => {
  if (!dateStr) return ''
  try {
    const date = new Date(dateStr)
    const hours = date.getHours().toString().padStart(2, '0')
    const minutes = date.getMinutes().toString().padStart(2, '0')
    return `${hours}:${minutes}`
  } catch {
    return ''
  }
}

// Truncate text
const truncateText = (text, maxLength) => {
  if (!text) return ''
  return text.length > maxLength ? text.slice(0, maxLength) + '...' : text
}

// Generate title from simulation requirement (first 20 chars)
const getSimulationTitle = (requirement) => {
  if (!requirement) return t('history.untitledSimulation')
  const title = requirement.slice(0, 20)
  return requirement.length > 20 ? title + '...' : title
}

// Format simulation_id display (truncate to first 6 chars)
const formatSimulationId = (simulationId) => {
  if (!simulationId) return 'SIM_UNKNOWN'
  const prefix = simulationId.replace('sim_', '').slice(0, 6)
  return `SIM_${prefix.toUpperCase()}`
}

// Format rounds display (current round / total rounds)
const formatRounds = (simulation) => {
  const current = simulation.current_round || 0
  const total = simulation.total_rounds || 0
  if (total === 0) return t('history.notStarted')
  return t('history.roundsProgress', { current, total })
}

// Get file type (for styling)
const getFileType = (filename) => {
  if (!filename) return 'other'
  const ext = filename.split('.').pop()?.toLowerCase()
  const typeMap = {
    'pdf': 'pdf',
    'doc': 'doc', 'docx': 'doc',
    'xls': 'xls', 'xlsx': 'xls', 'csv': 'xls',
    'ppt': 'ppt', 'pptx': 'ppt',
    'txt': 'txt', 'md': 'txt', 'json': 'code',
    'jpg': 'img', 'jpeg': 'img', 'png': 'img', 'gif': 'img',
    'zip': 'zip', 'rar': 'zip', '7z': 'zip'
  }
  return typeMap[ext] || 'other'
}

// Get file type label text
const getFileTypeLabel = (filename) => {
  if (!filename) return 'FILE'
  const ext = filename.split('.').pop()?.toUpperCase()
  return ext || 'FILE'
}

// Truncate file name (preserve extension)
const truncateFilename = (filename, maxLength) => {
  if (!filename) return t('history.unknownFile')
  if (filename.length <= maxLength) return filename
  
  const ext = filename.includes('.') ? '.' + filename.split('.').pop() : ''
  const nameWithoutExt = filename.slice(0, filename.length - ext.length)
  const truncatedName = nameWithoutExt.slice(0, maxLength - ext.length - 3) + '...'
  return truncatedName + ext
}

// Audio pool for hover/open sound effects
let audioPool = []
const POOL_SIZE = 4

const getAudioElement = () => {
  if (typeof window === 'undefined') return null
  for (const a of audioPool) {
    if (a.paused || a.ended) {
      return a
    }
  }
  if (audioPool.length < POOL_SIZE) {
    const a = new Audio(hoverSoundSrc)
    a.volume = 0.5
    audioPool.push(a)
    return a
  }
  return audioPool[0]
}

const playHoverSound = () => {
  try {
    const sound = getAudioElement()
    if (sound) {
      sound.currentTime = 0
      sound.play().catch(() => {})
    }
  } catch (e) {}
}

const handleCardHover = (index) => {
  hoveringCard.value = index
  playHoverSound()
}

// Open project details modal
const navigateToProject = (simulation) => {
  playHoverSound()
  selectedProject.value = simulation
}

// Close modal
const closeModal = () => {
  selectedProject.value = null
}

// Navigate to graph construction page (Project)
const goToProject = () => {
  if (selectedProject.value?.project_id) {
    router.push({
      name: 'Process',
      params: { projectId: selectedProject.value.project_id }
    })
    closeModal()
  }
}

// Navigate to environment setup page (Simulation)
const goToSimulation = () => {
  if (selectedProject.value?.simulation_id) {
    router.push({
      name: 'Simulation',
      params: { simulationId: selectedProject.value.simulation_id }
    })
    closeModal()
  }
}

// Navigate to analysis report page (Report)
const goToReport = () => {
  if (selectedProject.value?.report_id) {
    router.push({
      name: 'Report',
      params: { reportId: selectedProject.value.report_id }
    })
    closeModal()
  }
}

// Load history projects
const loadHistory = async () => {
  try {
    loading.value = true
    const response = await getSimulationHistory(20)
    if (response.success) {
      projects.value = response.data || []
    }
  } catch (error) {
    console.error('Failed to load history projects:', error)
    projects.value = []
  } finally {
    loading.value = false
  }
}

// Listen to route changes, reload data when returning to home page
watch(() => route.path, (newPath) => {
  if (newPath === '/') {
    loadHistory()
  }
})

onMounted(async () => {
  await nextTick()
  await loadHistory()

  nextTick(() => {
    if (historyContainer.value) {
      historyContainer.value.scrollLeft = 0
    }
  })
})

// If using keep-alive, reload data when component is activated
onActivated(() => {
  loadHistory()
})

onUnmounted(() => {
  // No observer or expansion timers are needed in the horizontal layout.
})
</script>

<style scoped>
/* Container */
.history-database {
  position: relative;
  width: 100%;
  min-height: 280px;
  margin-top: 12px;
  padding: 12px 0 24px;
  overflow: hidden;
}

/* Simplified display when no projects */
.history-database.no-projects {
  min-height: auto;
  padding: 40px 0 20px;
}

/* Technical grid background */
.tech-grid-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  overflow: hidden;
  pointer-events: none;
}

/* Use CSS background pattern to create fixed-pitch square grid */
.grid-pattern {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: 
    linear-gradient(to right, rgba(255, 255, 255, 0.04) 1px, transparent 1px),
    linear-gradient(to bottom, rgba(255, 255, 255, 0.04) 1px, transparent 1px);
  background-size: 50px 50px;
  background-position: top left;
}

.gradient-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    linear-gradient(to right, rgba(0, 0, 0, 0.95) 0%, transparent 15%, transparent 85%, rgba(0, 0, 0, 0.95) 100%),
    linear-gradient(to bottom, rgba(0, 0, 0, 0.9) 0%, transparent 20%, transparent 80%, rgba(0, 0, 0, 0.9) 100%);
  pointer-events: none;
}

/* Title area */
.section-header {
  position: relative;
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 24px;
  margin-bottom: 8px;
  font-family: 'JetBrains Mono', 'SF Mono', monospace;
  padding: 0 40px;
}

.section-line {
  flex: 1;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.15), transparent);
  max-width: 300px;
}

.section-title {
  font-size: 0.8rem;
  font-weight: 500;
  color: #9CA3AF;
  letter-spacing: 3px;
  text-transform: uppercase;
}

/* Card container */
.cards-container {
  position: relative;
  display: flex;
  justify-content: flex-start;
  align-items: flex-start;
  gap: 16px;
  padding: 0 24px 8px 28px;
  margin-top: -6px;
  overflow-x: auto;
  overflow-y: hidden;
  white-space: nowrap;
  scroll-snap-type: x proximity;
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.cards-container::-webkit-scrollbar {
  display: none;
}

/* Project card */
.project-card {
  position: relative;
  flex: 0 0 280px;
  width: 280px;
  background: rgba(10, 10, 10, 0.75);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 14px;
  padding: 16px;
  cursor: pointer;
  box-shadow: 0 8px 24px -4px rgba(0, 0, 0, 0.8);
  transition: box-shadow 0.3s ease, border-color 0.3s ease, transform 200ms ease, opacity 200ms ease, background 0.3s ease;
  scroll-snap-align: start;
  transform: translateY(5px) scale(0.985);
  opacity: 0.98;
}

.project-card:hover {
  box-shadow: 0 16px 36px -6px rgba(0, 0, 0, 0.95), 0 0 20px rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.35);
  background: rgba(20, 20, 20, 0.92);
  transform: translateY(0) scale(1);
  z-index: 1000 !important;
}

.project-card.hovering {
  z-index: 1000 !important;
}

/* Card header */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  font-family: 'JetBrains Mono', 'SF Mono', monospace;
  font-size: 0.7rem;
}

.card-id {
  color: #94a3b8;
  letter-spacing: 0.5px;
  font-weight: 500;
}

/* Feature status icon group */
.card-status-icons {
  display: flex;
  align-items: center;
  gap: 6px;
}

.status-icon {
  font-size: 0.75rem;
  transition: all 0.2s ease;
  cursor: default;
}

.status-icon.available {
  opacity: 1;
  color: #ffffff;
  text-shadow: 0 0 8px rgba(255, 255, 255, 0.4);
}

.status-icon.unavailable {
  color: #475569;
  opacity: 0.4;
}

/* Round progress display */
.card-progress {
  display: flex;
  align-items: center;
  gap: 6px;
  letter-spacing: 0.5px;
  font-weight: 600;
  font-size: 0.65rem;
}

.status-dot {
  font-size: 0.5rem;
}

/* Progress status colors */
.card-progress.completed { color: #ffffff; text-shadow: 0 0 8px rgba(255, 255, 255, 0.5); }
.card-progress.in-progress { color: #cbd5e1; }
.card-progress.not-started { color: #64748b; }
.card-status.pending { color: #64748b; }

/* File list area */
.card-files-wrapper {
  position: relative;
  width: 100%;
  min-height: 48px;
  max-height: 110px;
  margin-bottom: 12px;
  padding: 8px 10px;
  background: rgba(8, 10, 16, 0.85);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  overflow: hidden;
}

.files-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

/* More files hint */
.files-more {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 3px 6px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.6rem;
  color: #94a3b8;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 3px;
  letter-spacing: 0.3px;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 6px;
  background: rgba(255, 255, 255, 0.04);
  border-radius: 4px;
  transition: all 0.2s ease;
}

.file-item:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: translateX(2px);
  border-color: rgba(255, 255, 255, 0.2);
}

/* Minimal file tag style */
.file-tag {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 16px;
  padding: 0 4px;
  border-radius: 2px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.55rem;
  font-weight: 600;
  line-height: 1;
  text-transform: uppercase;
  letter-spacing: 0.2px;
  flex-shrink: 0;
  min-width: 28px;
}

/* Dark metallic palette */
.file-tag.pdf { background: rgba(255, 255, 255, 0.15); color: #ffffff; }
.file-tag.doc { background: rgba(255, 255, 255, 0.12); color: #e2e8f0; }
.file-tag.xls { background: rgba(255, 255, 255, 0.15); color: #ffffff; }
.file-tag.ppt { background: rgba(255, 255, 255, 0.12); color: #e2e8f0; }
.file-tag.txt { background: rgba(255, 255, 255, 0.08); color: #cbd5e1; }
.file-tag.code { background: rgba(255, 255, 255, 0.15); color: #ffffff; }
.file-tag.img { background: rgba(255, 255, 255, 0.12); color: #e2e8f0; }
.file-tag.zip { background: rgba(255, 255, 255, 0.15); color: #ffffff; }
.file-tag.other { background: rgba(255, 255, 255, 0.06); color: #94a3b8; }

.file-name {
  font-family: 'Inter', sans-serif;
  font-size: 0.7rem;
  color: #cbd5e1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  letter-spacing: 0.1px;
}

/* Placeholder when no files */
.files-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  height: 48px;
  color: #64748b;
}

.empty-file-icon {
  font-size: 1rem;
  opacity: 0.5;
}

.empty-file-text {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.7rem;
  letter-spacing: 0.5px;
}

/* File area hover effect */
.project-card:hover .card-files-wrapper {
  border-color: rgba(255, 255, 255, 0.2);
  background: rgba(12, 15, 24, 0.95);
}

/* Corner decoration */
.corner-mark.top-left-only {
  position: absolute;
  top: 6px;
  left: 6px;
  width: 8px;
  height: 8px;
  border-top: 1.5px solid rgba(255, 255, 255, 0.4);
  border-left: 1.5px solid rgba(255, 255, 255, 0.4);
  pointer-events: none;
  z-index: 10;
}

/* Card title */
.card-title {
  font-family: 'Inter', -apple-system, sans-serif;
  font-size: 0.95rem;
  font-weight: 700;
  color: #ffffff;
  margin: 0 0 6px 0;
  line-height: 1.4;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  transition: color 0.3s ease;
}

.project-card:hover .card-title {
  color: #ffffff;
  text-shadow: 0 0 10px rgba(255, 255, 255, 0.4);
}

/* Card description */
.card-desc {
  font-family: 'Inter', sans-serif;
  font-size: 0.75rem;
  color: #94a3b8;
  margin: 0 0 16px 0;
  line-height: 1.5;
  height: 34px;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

/* Card footer */
.card-footer {
  position: relative;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.65rem;
  color: #64748b;
  font-weight: 500;
}

/* Date and time combination */
.card-datetime {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* Bottom round progress display */
.card-footer .card-progress {
  display: flex;
  align-items: center;
  gap: 6px;
  letter-spacing: 0.5px;
  font-weight: 600;
  font-size: 0.65rem;
}

.card-footer .status-dot {
  font-size: 0.5rem;
}

/* Progress status colors - footer */
.card-footer .card-progress.completed { color: #ffffff; }
.card-footer .card-progress.in-progress { color: #cbd5e1; }
.card-footer .card-progress.not-started { color: #64748b; }

/* Bottom decorative line */
.card-bottom-line {
  position: absolute;
  bottom: 0;
  left: 0;
  height: 2px;
  width: 0;
  background-color: #ffffff;
  box-shadow: 0 0 10px #ffffff;
  transition: width 0.5s cubic-bezier(0.23, 1, 0.32, 1);
  z-index: 20;
}

.project-card:hover .card-bottom-line {
  width: 100%;
}

/* Empty state */
.empty-state, .loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14px;
  padding: 48px;
  color: #64748b;
}

.empty-icon {
  font-size: 2rem;
  opacity: 0.5;
}

.loading-spinner {
  width: 24px;
  height: 24px;
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-top-color: #ffffff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Responsive */
@media (max-width: 1200px) {
  .project-card {
    width: 240px;
  }
}

@media (max-width: 768px) {
  .cards-container {
    padding: 0 20px;
  }
  .project-card {
    width: 200px;
  }
}

/* ===== History Replay Details Modal Styles ===== */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.85);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  backdrop-filter: blur(10px);
}

.modal-content {
  background: linear-gradient(180deg, #121212 0%, #000000 100%);
  width: 560px;
  max-width: 90vw;
  max-height: 85vh;
  overflow-y: auto;
  border: 1px solid rgba(255, 255, 255, 0.14);
  border-radius: 18px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 1), 0 0 40px rgba(0, 0, 0, 0.95);
  color: #f5f5f5;
}

/* Animation transitions */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active .modal-content {
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.modal-leave-active .modal-content {
  transition: all 0.2s ease-in;
}

.modal-enter-from .modal-content {
  transform: scale(0.95) translateY(10px);
  opacity: 0;
}

.modal-leave-to .modal-content {
  transform: scale(0.95) translateY(10px);
  opacity: 0;
}

/* Modal header */
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 32px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.02);
}

.modal-title-section {
  display: flex;
  align-items: center;
  gap: 16px;
}

.modal-id {
  font-family: 'JetBrains Mono', monospace;
  font-size: 1rem;
  font-weight: 600;
  color: #ffffff;
  letter-spacing: 0.5px;
}

.modal-progress {
  display: flex;
  align-items: center;
  gap: 6px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.75rem;
  font-weight: 600;
  padding: 4px 8px;
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.06);
}

.modal-progress.completed { color: #ffffff; background: rgba(255, 255, 255, 0.15); }
.modal-progress.in-progress { color: #cbd5e1; background: rgba(255, 255, 255, 0.08); }
.modal-progress.not-started { color: #64748b; background: rgba(255, 255, 255, 0.04); }

.modal-create-time {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.75rem;
  color: #64748b;
  letter-spacing: 0.3px;
}

.modal-close {
  width: 32px;
  height: 32px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.06);
  font-size: 1.25rem;
  color: #cbd5e1;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  border-radius: 50%;
}

.modal-close:hover {
  background: #ffffff;
  color: #000000;
  border-color: #ffffff;
}

/* Modal content */
.modal-body {
  padding: 24px 32px;
}

.modal-section {
  margin-bottom: 24px;
}

.modal-section:last-child {
  margin-bottom: 0;
}

.modal-label {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.75rem;
  color: #a3a3a3;
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 10px;
  font-weight: 500;
}

.modal-requirement {
  font-size: 0.95rem;
  color: #f5f5f5;
  line-height: 1.6;
  padding: 16px;
  background: rgba(8, 8, 8, 0.75);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
}

.modal-files {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: 200px;
  overflow-y: auto;
  padding-right: 4px;
}

/* Custom scrollbar styles */
.modal-files::-webkit-scrollbar {
  width: 4px;
}

.modal-files::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.04);
  border-radius: 2px;
}

.modal-files::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 2px;
}

.modal-files::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.4);
}

.modal-file-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 14px;
  background: rgba(14, 14, 14, 0.85);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  transition: all 0.2s ease;
}

.modal-file-item:hover {
  border-color: rgba(255, 255, 255, 0.3);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.7);
}

.modal-file-name {
  font-size: 0.85rem;
  color: #e5e5e5;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.modal-empty {
  font-size: 0.85rem;
  color: #737373;
  padding: 16px;
  background: rgba(8, 8, 8, 0.6);
  border: 1px dashed rgba(255, 255, 255, 0.12);
  border-radius: 6px;
  text-align: center;
}

/* Deduction replay divider */
.modal-divider {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 10px 32px 0;
  background: transparent;
}

.divider-line {
  flex: 1;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.12), transparent);
}

.divider-text {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.7rem;
  color: #737373;
  letter-spacing: 2px;
  text-transform: uppercase;
  white-space: nowrap;
}

/* Navigation buttons */
.modal-actions {
  display: flex;
  gap: 16px;
  padding: 20px 32px;
  background: transparent;
}

.modal-btn {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 16px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 8px;
  background: rgba(14, 14, 14, 0.85);
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
  overflow: hidden;
}

.modal-btn:hover:not(:disabled) {
  border-color: rgba(255, 255, 255, 0.38);
  background: rgba(24, 24, 24, 0.95);
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.8);
}

.modal-btn:disabled {
  opacity: 0.35;
  cursor: not-allowed;
  background: rgba(8, 8, 8, 0.4);
}

.btn-step {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.6rem;
  font-weight: 500;
  color: #737373;
  letter-spacing: 0.5px;
  text-transform: uppercase;
}

.btn-icon {
  font-size: 1.4rem;
  line-height: 1;
  transition: color 0.2s ease;
}

.btn-text {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.5px;
  color: #a3a3a3;
}

.modal-btn.btn-project .btn-icon { color: #ffffff; }
.modal-btn.btn-simulation .btn-icon { color: #d4d4d4; }
.modal-btn.btn-report .btn-icon { color: #a3a3a3; }

.modal-btn:hover:not(:disabled) .btn-text {
  color: #ffffff;
}

/* Non-replayable hint */
.modal-playback-hint {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 32px 20px;
  background: transparent;
}

.hint-text {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.7rem;
  color: #9CA3AF;
  letter-spacing: 0.3px;
  text-align: center;
  line-height: 1.5;
}
</style>
