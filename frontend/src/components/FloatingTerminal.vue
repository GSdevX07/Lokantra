<template>
  <Teleport to="body">
    <div class="floating-terminal-root">
      <!-- 1. Floating Corner Button (when minimized) -->
      <Transition name="float-fade">
        <button 
          v-if="!isOpen" 
          class="floating-terminal-btn"
          @click="openTerminal"
          :title="`Open ${title || 'Terminal'}`"
          aria-label="Open Terminal"
        >
          <span class="btn-terminal-icon">&gt;_</span>
          <span class="btn-terminal-title">{{ title || 'Terminal' }}</span>
          <span v-if="isActive || (logs && logs.length > 0)" class="btn-live-pulse" title="Active"></span>
        </button>
      </Transition>

      <!-- 2. Windows Terminal Floating Window (when open) -->
      <Transition name="terminal-window">
        <div 
          v-if="isOpen" 
          ref="modalRef"
          class="windows-terminal-modal"
          :class="{ 'is-resizing': isResizing, 'is-dragging': isDragging }"
          :style="modalStyle"
          role="dialog"
          aria-label="Windows Terminal"
        >
          <!-- Scaler / Resize Handles (Edges and Corners) -->
          <div class="win-resize-handle win-resize-t" @pointerdown="startResize($event, 'top')"></div>
          <div class="win-resize-handle win-resize-b" @pointerdown="startResize($event, 'bottom')"></div>
          <div class="win-resize-handle win-resize-l" @pointerdown="startResize($event, 'left')"></div>
          <div class="win-resize-handle win-resize-r" @pointerdown="startResize($event, 'right')"></div>
          <div class="win-resize-handle win-resize-tl" @pointerdown="startResize($event, 'top-left')"></div>
          <div class="win-resize-handle win-resize-tr" @pointerdown="startResize($event, 'top-right')"></div>
          <div class="win-resize-handle win-resize-bl" @pointerdown="startResize($event, 'bottom-left')"></div>
          <div class="win-resize-handle win-resize-br" @pointerdown="startResize($event, 'bottom-right')"></div>

          <!-- Windows Terminal Titlebar -->
          <div class="win-titlebar" @pointerdown="startDrag">
            <!-- Active Tab -->
            <div class="win-tab-group">
              <div class="win-tab active">
                <span class="win-tab-icon">&gt;_</span>
                <span class="win-tab-label">{{ title || 'SIMULATION MONITOR' }}</span>
                <span v-if="subId && !subId.startsWith('NO_')" class="win-tab-badge">{{ subId }}</span>
              </div>
            </div>

            <!-- Windows Window Control Buttons: Only "X" -->
            <div class="win-controls">
              <!-- Close Button Only -->
              <button 
                class="win-btn win-btn-close" 
                @click="closeTerminal" 
                title="Close"
                aria-label="Close"
              >
                <svg width="10" height="10" viewBox="0 0 10 10">
                  <line x1="0" y1="0" x2="10" y2="10" stroke="currentColor" stroke-width="1.2"/>
                  <line x1="10" y1="0" x2="0" y2="10" stroke-width="1.2" stroke="currentColor"/>
                </svg>
              </button>
            </div>
          </div>

          <!-- Terminal Body -->
          <div class="win-terminal-body" ref="terminalBodyRef">
            <div class="terminal-banner">
              <div>Microsoft Windows</div>
              <div>(c) Lokantra Swarm Simulation Environment. All rights reserved.</div>
              <div class="terminal-divider">------------------------------------------------------------</div>
            </div>

            <!-- Logs Output -->
            <div class="terminal-log-stream">
              <div 
                v-for="(log, idx) in formattedLogs" 
                :key="idx" 
                class="terminal-log-row"
              >
                <span v-if="log.time" class="log-time">{{ log.time }}</span>
                <span class="log-msg" :class="getMsgClass(log.msg)">{{ log.msg }}</span>
              </div>
            </div>

            <!-- Blinking PowerShell prompt at bottom -->
            <div class="terminal-prompt-row">
              <span class="prompt-text">PS C:\Lokantra\Simulation&gt;</span>
              <span class="prompt-cursor">█</span>
            </div>
          </div>
        </div>
      </Transition>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { useSound } from '@/hooks/use-sound'
import { error005Sound } from '@/sounds/error-005'

const props = defineProps({
  title: {
    type: String,
    default: 'SIMULATION MONITOR'
  },
  subId: {
    type: String,
    default: ''
  },
  logs: {
    type: Array,
    default: () => []
  },
  isActive: {
    type: Boolean,
    default: false
  }
})

const isOpen = ref(false)
const terminalBodyRef = ref(null)
const modalRef = ref(null)

// Window dimensions & position
const width = ref(Math.min(660, typeof window !== 'undefined' ? window.innerWidth - 32 : 660))
const height = ref(Math.min(420, typeof window !== 'undefined' ? window.innerHeight - 48 : 420))
const posX = ref(null)
const posY = ref(null)

const isResizing = ref(false)
const isDragging = ref(false)

let resizeStartX = 0
let resizeStartY = 0
let resizeStartWidth = 0
let resizeStartHeight = 0
let resizeStartLeft = 0
let resizeStartTop = 0
let activeDirection = ''

let dragStartX = 0
let dragStartY = 0
let dragStartLeft = 0
let dragStartTop = 0

const modalStyle = computed(() => {
  const style = {
    width: `${width.value}px`,
    height: `${height.value}px`
  }
  if (posX.value !== null && posY.value !== null) {
    style.left = `${posX.value}px`
    style.top = `${posY.value}px`
    style.right = 'auto'
    style.bottom = 'auto'
  } else {
    style.right = '24px'
    style.bottom = '24px'
    style.left = 'auto'
    style.top = 'auto'
  }
  return style
})

const openTerminal = () => {
  isOpen.value = true
  scrollToBottom()
}

const closeTerminal = () => {
  isOpen.value = false
}

const scrollToBottom = () => {
  nextTick(() => {
    if (terminalBodyRef.value) {
      terminalBodyRef.value.scrollTop = terminalBodyRef.value.scrollHeight
    }
  })
}

const [playErrorSound] = useSound(error005Sound)

const isInitialMount = ref(true)
let lastCheckedCount = Array.isArray(props.logs) ? props.logs.length : 0
let lastErrorSoundTime = 0

onMounted(() => {
  // Sync count on initial mount and suppress sounds during initial history/setup loading
  lastCheckedCount = Array.isArray(props.logs) ? props.logs.length : 0
  setTimeout(() => {
    isInitialMount.value = false
    lastCheckedCount = Array.isArray(props.logs) ? props.logs.length : 0
  }, 3500)
})

const isExplicitErrorString = (str) => {
  if (!str) return false
  const trimmed = str.trim()
  const lower = trimmed.toLowerCase()

  // Match genuine runtime error prefixes or patterns (not benign status messages)
  return (
    trimmed.startsWith('[ERROR]') ||
    trimmed.startsWith('ERROR:') ||
    trimmed.startsWith('Error:') ||
    trimmed.startsWith('[FATAL]') ||
    trimmed.startsWith('FATAL:') ||
    trimmed.startsWith('Traceback (most recent call last):') ||
    trimmed.startsWith('Uncaught ') ||
    trimmed.startsWith('Unhandled ') ||
    lower.includes('critical error') ||
    lower.includes('fatal error') ||
    lower.includes('runtimeerror:') ||
    lower.includes('typeerror:') ||
    lower.includes('referenceerror:') ||
    lower.includes('syntaxerror:') ||
    trimmed.includes('❌') ||
    trimmed.includes('✖')
  )
}

const isErrorLog = (log) => {
  if (!log) return false
  if (typeof log === 'object') {
    if (log.level === 'error' || log.type === 'error' || log.status === 'error' || log.severity === 'error') {
      return true
    }
    const msg = String(log.msg || log.message || log.text || '')
    return isExplicitErrorString(msg)
  }
  return isExplicitErrorString(String(log))
}

const checkNewLogsForErrors = () => {
  const currentLogs = props.logs
  if (!Array.isArray(currentLogs)) return

  // During initial mount or navigation, sync count and NEVER play sound
  if (isInitialMount.value) {
    lastCheckedCount = currentLogs.length
    return
  }

  // Only check if active process is running
  if (!props.isActive) {
    lastCheckedCount = currentLogs.length
    return
  }

  // If logs were reset or cleared, synchronize count
  if (currentLogs.length <= lastCheckedCount) {
    lastCheckedCount = currentLogs.length
    return
  }

  const newSlice = currentLogs.slice(lastCheckedCount)
  lastCheckedCount = currentLogs.length

  const hasError = newSlice.some(isErrorLog)
  if (hasError) {
    const now = performance.now()
    if (now - lastErrorSoundTime > 800) {
      lastErrorSoundTime = now
      try {
        playErrorSound()
      } catch (e) {
        console.warn('Failed to play error sound:', e)
      }
    }
  }
}

// Auto-scroll and check for incoming errors as new logs stream in
watch(() => props.logs?.length, () => {
  if (isOpen.value) {
    scrollToBottom()
  }
  checkNewLogsForErrors()
})

watch(
  () => props.logs,
  () => {
    checkNewLogsForErrors()
  },
  { deep: true }
)

const formattedLogs = computed(() => {
  if (!props.logs || !Array.isArray(props.logs)) return []
  return props.logs.map(log => {
    if (typeof log === 'string') {
      const match = log.match(/^\[?(\d{2}:\d{2}:\d{2}(?:\.\d+)?)\]?\s*(.*)$/)
      if (match) {
        return {
          time: match[1],
          msg: match[2]
        }
      }
      return {
        time: '',
        msg: log
      }
    }
    if (log && typeof log === 'object') {
      return {
        time: log.time || '',
        msg: log.msg !== undefined ? log.msg : (log.message || JSON.stringify(log))
      }
    }
    return {
      time: '',
      msg: String(log)
    }
  })
})

const getMsgClass = (msg) => {
  if (!msg) return ''
  const str = String(msg)
  if (str.includes('✓') || str.includes('success') || str.includes('Successfully')) {
    return 'msg-success'
  }
  if (str.includes('Error') || str.includes('ERROR') || str.includes('failed') || str.includes('Exception')) {
    return 'msg-error'
  }
  if (str.includes('Warning') || str.includes('WARNING') || str.includes('warn')) {
    return 'msg-warning'
  }
  if (str.includes('PID:') || str.includes('Loading') || str.includes('Time config:')) {
    return 'msg-highlight'
  }
  return ''
}

// Resizing logic (Edge / Corner handles)
const startResize = (e, direction) => {
  if (e.button !== 0) return
  e.preventDefault()
  e.stopPropagation()

  if (!modalRef.value) return
  const rect = modalRef.value.getBoundingClientRect()
  resizeStartLeft = rect.left
  resizeStartTop = rect.top
  resizeStartWidth = rect.width
  resizeStartHeight = rect.height
  resizeStartX = e.clientX
  resizeStartY = e.clientY
  activeDirection = direction
  isResizing.value = true

  // If in anchored mode (posX === null) and resizing top, left, or top-left:
  // Keep anchored mode so width/height expand smoothly from bottom-right without any jumping!
  if (posX.value === null && posY.value === null) {
    if (direction !== 'top' && direction !== 'left' && direction !== 'top-left') {
      posX.value = rect.left
      posY.value = rect.top
      width.value = rect.width
      height.value = rect.height
    }
  } else {
    posX.value = rect.left
    posY.value = rect.top
    width.value = rect.width
    height.value = rect.height
  }

  let cursor = 'default'
  if (direction === 'top' || direction === 'bottom') cursor = 'ns-resize'
  else if (direction === 'left' || direction === 'right') cursor = 'ew-resize'
  else if (direction === 'top-left' || direction === 'bottom-right') cursor = 'nwse-resize'
  else if (direction === 'top-right' || direction === 'bottom-left') cursor = 'nesw-resize'

  document.body.style.userSelect = 'none'
  document.body.style.cursor = cursor

  window.addEventListener('pointermove', onResizeMove)
  window.addEventListener('pointerup', stopResize)
  window.addEventListener('pointercancel', stopResize)
}

const onResizeMove = (e) => {
  if (!isResizing.value) return

  const dx = e.clientX - resizeStartX
  const dy = e.clientY - resizeStartY

  const minW = 360
  const minH = 200
  const maxW = window.innerWidth - 32
  const maxH = window.innerHeight - 32

  // CASE 1: Anchored to bottom-right corner
  if (posX.value === null && posY.value === null) {
    if (activeDirection === 'top' || activeDirection === 'top-left') {
      let newH = resizeStartHeight - dy
      newH = Math.max(minH, Math.min(newH, window.innerHeight - 48))
      height.value = newH
    }
    if (activeDirection === 'left' || activeDirection === 'top-left') {
      let newW = resizeStartWidth - dx
      newW = Math.max(minW, Math.min(newW, window.innerWidth - 48))
      width.value = newW
    }
    return
  }

  // CASE 2: Free-floating (with explicit posX / posY)
  if (activeDirection.includes('right')) {
    let newW = resizeStartWidth + dx
    const maxAvailableW = window.innerWidth - resizeStartLeft - 8
    newW = Math.max(minW, Math.min(newW, maxAvailableW))
    width.value = newW
  } else if (activeDirection.includes('left')) {
    let newW = resizeStartWidth - dx
    let newL = resizeStartLeft + dx
    if (newL < 8) {
      newW = resizeStartLeft + resizeStartWidth - 8
      newL = 8
    }
    if (newW < minW) {
      newL = resizeStartLeft + resizeStartWidth - minW
      newW = minW
    }
    if (newW > maxW) {
      newW = maxW
      newL = resizeStartLeft + resizeStartWidth - maxW
    }
    width.value = newW
    posX.value = newL
  }

  if (activeDirection.includes('bottom')) {
    let newH = resizeStartHeight + dy
    const maxAvailableH = window.innerHeight - resizeStartTop - 8
    newH = Math.max(minH, Math.min(newH, maxAvailableH))
    height.value = newH
  } else if (activeDirection.includes('top')) {
    let newH = resizeStartHeight - dy
    let newT = resizeStartTop + dy
    if (newT < 8) {
      newH = resizeStartTop + resizeStartHeight - 8
      newT = 8
    }
    if (newH < minH) {
      newT = resizeStartTop + resizeStartHeight - minH
      newH = minH
    }
    if (newH > maxH) {
      newH = maxH
      newT = resizeStartTop + resizeStartHeight - maxH
    }
    height.value = newH
    posY.value = newT
  }
}

const stopResize = () => {
  if (!isResizing.value) return
  isResizing.value = false
  activeDirection = ''
  document.body.style.userSelect = ''
  document.body.style.cursor = ''
  window.removeEventListener('pointermove', onResizeMove)
  window.removeEventListener('pointerup', stopResize)
  window.removeEventListener('pointercancel', stopResize)
}

// Window drag/moving via titlebar
const startDrag = (e) => {
  if (e.target.closest('.win-btn') || isResizing.value) return
  if (e.button !== 0) return

  if (!modalRef.value) return
  const rect = modalRef.value.getBoundingClientRect()
  dragStartLeft = rect.left
  dragStartTop = rect.top
  dragStartX = e.clientX
  dragStartY = e.clientY
  isDragging.value = true

  // Transition to explicit coordinates
  posX.value = rect.left
  posY.value = rect.top
  width.value = rect.width
  height.value = rect.height

  document.body.style.userSelect = 'none'
  document.body.style.cursor = 'move'

  window.addEventListener('pointermove', onDragMove)
  window.addEventListener('pointerup', stopDrag)
  window.addEventListener('pointercancel', stopDrag)
}

const onDragMove = (e) => {
  if (!isDragging.value) return
  const dx = e.clientX - dragStartX
  const dy = e.clientY - dragStartY

  let newLeft = dragStartLeft + dx
  let newTop = dragStartTop + dy

  const maxLeft = window.innerWidth - width.value - 4
  const maxTop = window.innerHeight - height.value - 4
  newLeft = Math.max(4, Math.min(newLeft, maxLeft))
  newTop = Math.max(4, Math.min(newTop, maxTop))

  posX.value = newLeft
  posY.value = newTop
}

const stopDrag = () => {
  if (!isDragging.value) return
  isDragging.value = false
  document.body.style.userSelect = ''
  document.body.style.cursor = ''
  window.removeEventListener('pointermove', onDragMove)
  window.removeEventListener('pointerup', stopDrag)
  window.removeEventListener('pointercancel', stopDrag)
}

// Window resize handler
const handleWindowResize = () => {
  if (width.value > window.innerWidth - 16) {
    width.value = Math.max(360, window.innerWidth - 16)
  }
  if (height.value > window.innerHeight - 16) {
    height.value = Math.max(200, window.innerHeight - 16)
  }
  if (posX.value !== null) {
    posX.value = Math.max(8, Math.min(posX.value, window.innerWidth - width.value - 8))
  }
  if (posY.value !== null) {
    posY.value = Math.max(8, Math.min(posY.value, window.innerHeight - height.value - 8))
  }
}

// Handle ESC to close
const handleKeyDown = (e) => {
  if (e.key === 'Escape' && isOpen.value) {
    closeTerminal()
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeyDown)
  window.addEventListener('resize', handleWindowResize)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyDown)
  window.removeEventListener('resize', handleWindowResize)
  window.removeEventListener('pointermove', onResizeMove)
  window.removeEventListener('pointerup', stopResize)
  window.removeEventListener('pointercancel', stopResize)
  window.removeEventListener('pointermove', onDragMove)
  window.removeEventListener('pointerup', stopDrag)
  window.removeEventListener('pointercancel', stopDrag)
})
</script>

<style scoped>
.floating-terminal-root {
  position: relative;
  z-index: 9999;
}

/* --- 1. Floating Corner Button --- */
.floating-terminal-btn {
  position: fixed;
  bottom: 22px;
  right: 22px;
  background: #111111;
  color: #FFFFFF;
  border: 1px solid #333333;
  border-radius: 28px;
  padding: 8px 16px;
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  box-shadow: none;
  font-family: 'JetBrains Mono', Consolas, monospace;
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.5px;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
  z-index: 9999;
  user-select: none;
}

.floating-terminal-btn:hover {
  background: #1E1E1E;
  border-color: #555555;
  transform: translateY(-2px);
  box-shadow: none;
}

.floating-terminal-btn:active {
  transform: translateY(0);
}

.btn-terminal-icon {
  color: #ffffff;
  font-weight: 800;
  font-size: 14px;
}

.btn-terminal-title {
  color: #EEEEEE;
  font-weight: 600;
}

.btn-live-pulse {
  width: 8px;
  height: 8px;
  background: #FFFFFF;
  border-radius: 50%;
  animation: pulse-dot-mono 1.8s ease-in-out infinite;
}

@keyframes pulse-dot-mono {
  0%, 100% { transform: scale(0.85); opacity: 0.5; }
  50% { transform: scale(1.2); opacity: 1; }
}

/* --- 2. Windows Terminal Floating Window --- */
.windows-terminal-modal {
  position: fixed;
  bottom: 24px;
  right: 24px;
  min-width: 360px;
  min-height: 200px;
  max-width: calc(100vw - 16px);
  max-height: calc(100vh - 16px);
  background: #0C0C0C;
  border: 1px solid rgba(255, 255, 255, 0.16);
  border-radius: 8px;
  box-shadow: none;
  display: flex;
  flex-direction: column;
  overflow: visible;
  z-index: 10000;
  backdrop-filter: blur(16px);
}

.windows-terminal-modal.is-resizing,
.windows-terminal-modal.is-dragging {
  transition: none !important;
}

/* Resize Handles (Edges and Corners) */
.win-resize-handle {
  position: absolute;
  z-index: 10005;
  background: transparent;
  user-select: none;
  touch-action: none;
}

/* Edges: 8-9px hit zone extending outside and slightly inside */
.win-resize-t {
  top: -5px;
  left: 8px;
  right: 8px;
  height: 9px;
  cursor: ns-resize;
}

.win-resize-b {
  bottom: -5px;
  left: 8px;
  right: 8px;
  height: 9px;
  cursor: ns-resize;
}

.win-resize-l {
  left: -5px;
  top: 8px;
  bottom: 8px;
  width: 9px;
  cursor: ew-resize;
}

.win-resize-r {
  right: -5px;
  top: 8px;
  bottom: 8px;
  width: 9px;
  cursor: ew-resize;
}

/* Corners */
.win-resize-tl {
  top: -6px;
  left: -6px;
  width: 14px;
  height: 14px;
  cursor: nwse-resize;
  z-index: 10006;
}

.win-resize-tr {
  top: -6px;
  right: -6px;
  width: 14px;
  height: 14px;
  cursor: nesw-resize;
  z-index: 10006;
}

.win-resize-bl {
  bottom: -6px;
  left: -6px;
  width: 14px;
  height: 14px;
  cursor: nesw-resize;
  z-index: 10006;
}

.win-resize-br {
  bottom: -6px;
  right: -6px;
  width: 14px;
  height: 14px;
  cursor: nwse-resize;
  z-index: 10006;
}

/* Windows Terminal Titlebar */
.win-titlebar {
  height: 38px;
  background: #1F1F1F;
  border-bottom: 1px solid #2B2B2B;
  border-top-left-radius: 7px;
  border-top-right-radius: 7px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  user-select: none;
  flex-shrink: 0;
  cursor: default;
}

.win-tab-group {
  display: flex;
  align-items: flex-end;
  height: 100%;
  padding-left: 8px;
}

.win-tab {
  background: #0C0C0C;
  height: 32px;
  padding: 0 14px;
  border-radius: 6px 6px 0 0;
  display: flex;
  align-items: center;
  gap: 8px;
  border-top: 2px solid #ffffff;
  font-family: 'JetBrains Mono', Consolas, monospace;
  font-size: 11.5px;
  color: #F0F0F0;
  font-weight: 500;
  box-shadow: none;
}

.win-tab-icon {
  color: #ffffff;
  font-weight: 800;
}

.win-tab-label {
  letter-spacing: 0.5px;
}

.win-tab-badge {
  color: #888888;
  font-size: 10.5px;
  background: rgba(255, 255, 255, 0.08);
  padding: 1px 6px;
  border-radius: 4px;
}

/* Windows 11 style Window Controls (—, □, ✕) */
.win-controls {
  display: flex;
  height: 100%;
  position: relative;
  z-index: 10010;
}

.win-btn {
  width: 46px;
  height: 100%;
  background: transparent;
  border: none;
  color: #CCCCCC;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background-color 0.15s ease, color 0.15s ease;
}

.win-btn:hover {
  background: rgba(255, 255, 255, 0.09);
  color: #FFFFFF;
}

.win-btn.win-btn-close:hover {
  background: #E81123 !important;
  color: #FFFFFF !important;
}

/* Terminal Body */
.win-terminal-body {
  background: #0C0C0C;
  flex: 1;
  padding: 14px 18px;
  overflow-y: auto;
  border-bottom-left-radius: 7px;
  border-bottom-right-radius: 7px;
  font-family: 'JetBrains Mono', 'Cascadia Code', Consolas, monospace;
  font-size: 12px;
  line-height: 1.6;
  color: #D4D4D4;
}

.win-terminal-body::-webkit-scrollbar {
  width: 6px;
}

.win-terminal-body::-webkit-scrollbar-track {
  background: #0C0C0C;
}

.win-terminal-body::-webkit-scrollbar-thumb {
  background: #2D2D2D;
  border-radius: 3px;
}

.win-terminal-body::-webkit-scrollbar-thumb:hover {
  background: #444444;
}

.terminal-banner {
  color: #777777;
  margin-bottom: 12px;
  font-size: 11px;
}

.terminal-divider {
  color: #333333;
  margin-top: 4px;
}

.terminal-log-stream {
  display: flex;
  flex-direction: column;
  gap: 3px;
  margin-bottom: 12px;
}

.terminal-log-row {
  display: flex;
  gap: 12px;
  align-items: baseline;
  word-break: break-all;
}

.log-time {
  color: #61AFEF;
  font-size: 11px;
  opacity: 0.85;
  flex-shrink: 0;
}

.log-msg {
  color: #DCDCDC;
}

.msg-success {
  color: #98C379 !important;
  font-weight: 500;
}

.msg-error {
  color: #E06C75 !important;
  font-weight: 500;
}

.msg-highlight {
  color: #E5C07B !important;
}

.msg-warning {
  color: #FFA726 !important;
  font-weight: 500;
}

.terminal-prompt-row {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 6px;
  color: #98C379;
  font-weight: 500;
}

.prompt-text {
  color: #98C379;
}

.prompt-cursor {
  color: #FFFFFF;
  animation: blink-cursor 1s steps(2, start) infinite;
}

@keyframes blink-cursor {
  to { visibility: hidden; }
}

/* Transitions */
.float-fade-enter-active,
.float-fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.float-fade-enter-from,
.float-fade-leave-to {
  opacity: 0;
  transform: scale(0.85) translateY(10px);
}

.terminal-window-enter-active,
.terminal-window-leave-active {
  transition: opacity 0.25s cubic-bezier(0.16, 1, 0.3, 1), transform 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

.terminal-window-enter-from,
.terminal-window-leave-to {
  opacity: 0;
  transform: scale(0.92) translateY(20px);
}
</style>
