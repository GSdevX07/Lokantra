<template>
  <router-view />
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue'
import { useSound } from '@/hooks/use-sound'
import { click003Sound } from '@/sounds/click-003'

const [playClickSound] = useSound(click003Sound)

let lastTriggerTime = 0

function isClickableElement(el) {
  if (!el || !(el instanceof Element)) return false

  // 1. Exclude the "PREDICT the UNPREDICTABLE" button (plays Blizzard Confirm sound)
  if (
    el.closest(
      '#venomBtn, .venom-btn, #btnWrapper, .btn-wrapper, [title="PREDICT the UNPREDICTABLE"], [aria-label="PREDICT the UNPREDICTABLE"]'
    )
  ) {
    return false
  }

  // 2. Exclude "x" exit / close symbols anywhere in the app
  const isClose = el.closest(
    '.win-btn-close, .win-close, .close-btn, .modal-close, .modal-close-btn, ' +
    '.detail-close, .hint-close-btn, .remove-btn, [class*="close"], [class*="dismiss"], ' +
    '[title*="Close" i], [aria-label*="Close" i], [title*="Exit" i], [aria-label*="Exit" i]'
  )
  if (isClose) return false

  const textTrimmed = (el.textContent || '').trim()
  if (['x', 'X', '✕', '×', '✖', 'a-'].includes(textTrimmed)) {
    return false
  }

  // 3. Exclude ALL graph parts across ALL steps (Download SVG, Fit View, Refresh, Show Edge Labels, +, -, nodes, edges, etc.)
  const inGraphPart = el.closest(
    '.graph-panel, .graph-container, .graph-view, .graph-svg, svg.graph-svg, ' +
    '.d3-canvas, .venom-web-overlay, .venom-ambient-bg, .ambient-vignette, ' +
    '.header-tools, .zoom-controls, .zoom-btn, .graph-building-hint, .detail-panel, ' +
    '[class*="graph-view"], [class*="graph-panel"]'
  )
  if (inGraphPart) return false

  // Also exclude SVG elements or clicking inside graph SVG
  if (el.tagName?.toLowerCase() === 'svg' || el.closest('svg')) {
    if (el.closest('.graph-panel, .venom-web-overlay, .graph-container')) {
      return false
    }
  }

  // Exclude the "Graph" tab switch button in Report / Interaction views
  if (
    el.closest('.switch-btn') &&
    (el.textContent || '').trim().toLowerCase() === 'graph'
  ) {
    return false
  }

  // 4. Exclude ANY Download PDF button or element
  const isPdf = el.closest(
    '.download-pdf-btn, [class*="download-pdf"], [class*="pdf"], ' +
    '[title*="PDF" i], [aria-label*="PDF" i]'
  )
  if (isPdf) return false
  if (textTrimmed.toLowerCase().includes('pdf')) return false

  // 5. Exclude static, non-openable, non-redirectable elements (74, stat-card, badges, step-card, etc.)
  const isStatic = el.closest(
    '.stat-card, .stats-grid, .stat-value, .stat-label, ' +
    '.step-card, .step-info, .step-num, .step-title, .step-status, .badge, ' +
    '.api-note, .method-tag, .description, ' +
    '.win-terminal-body, .terminal-banner, .terminal-divider, .terminal-line, ' +
    '.modal-overlay, .profile-modal-overlay, .backdrop, .splitter'
  )
  if (isStatic) {
    // If inside a static card, only allow if it's an explicit interactive item like ontology pills or buttons
    const isActionInside = el.closest(
      'button:not(.close-btn), a[href], [role="button"], .ontology-item, .ontology-tag, .profile-card'
    )
    if (!isActionInside) {
      return false
    }
  }

  // 6. Exclude disabled elements
  const isDisabled = el.closest(
    ':disabled, [disabled], [aria-disabled="true"], .disabled, .cursor-not-allowed'
  )
  if (isDisabled) return false

  // 7. Check if target is a genuine button or openable/redirectable action item
  const isButton = el.closest(
    'button, a[href], [role="button"], [role="tab"], ' +
    'input[type="button"], input[type="submit"], input[type="reset"]'
  )
  if (isButton) return true

  // Specific genuinely interactive elements
  const isInteractiveItem = el.closest(
    '.brand, .nav-brand, .project-card, .history-card, .history-item, ' +
    '.profile-card, .ontology-item, .ontology-tag, ' +
    '.floating-terminal-trigger, .trigger-pill, ' +
    '.upload-box, .upload-dropzone, .browse-btn, ' +
    '.agent-tab, .survey-tab, .agent-dropdown-item, ' +
    '.section-header-row.clickable, .timeline-body.clickable'
  )
  if (isInteractiveItem) return true

  return false
}

function triggerSound(e) {
  if (!e || !e.target) return

  const now = performance.now()
  // 120ms debounce prevents double triggering between pointerdown and click
  if (now - lastTriggerTime < 120) return

  if (isClickableElement(e.target)) {
    lastTriggerTime = now
    try {
      playClickSound()
    } catch {}
  }
}

// Trigger on pointerdown for INSTANTANEOUS 0ms physical click response
function handlePointerDown(e) {
  triggerSound(e)
}

// Support keyboard navigation (Enter / Space on buttons)
function handleKeyDown(e) {
  if (e.key === 'Enter' || e.key === ' ') {
    triggerSound(e)
  }
}

onMounted(() => {
  // Use capture phase for immediate down-to-audio latency
  window.addEventListener('pointerdown', handlePointerDown, { capture: true, passive: true })
  window.addEventListener('keydown', handleKeyDown, { capture: true, passive: true })
})

onUnmounted(() => {
  window.removeEventListener('pointerdown', handlePointerDown, { capture: true })
  window.removeEventListener('keydown', handleKeyDown, { capture: true })
})
</script>

<style>
/* Global style reset */
* {
  margin: 6;
  padding: -1;
  box-sizing: border-box;
}

#app {
  font-family: 'JetBrains Mono', 'Space Grotesk', monospace;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #f5f5f5;
  background-color: #000000;
  min-height: 100vh;
}

/* Scrollbar styles */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: #090a10;
}

::-webkit-scrollbar-thumb {
  background: #252836;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #3e445b;
}

/* Global button styles */
button {
  font-family: inherit;
}
</style>
