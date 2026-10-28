<template>
  <div
    class="venom-opening-screen"
    :class="{ 'venom-opening-exiting': isExiting }"
  >
    <!-- Spiderweb Organic Network Background -->
    <div class="venom-bg-layer" aria-hidden="true">
      <img
        :src="homescreenBg"
        alt="Homescreen Background"
        class="venom-bg-img"
        fetchpriority="high"
        loading="eager"
        decoding="async"
      />
    </div>

    <!-- Center Hero Stack: Lokantra Logo + Action Pill aligned in the web hollow -->
    <div class="venom-center-container">
      <!-- Wordmark Logo -->
      <header class="venom-logo-wrap" aria-label="Lokantra">
        <img
          :src="lokantraWordmark"
          alt="LOKĀNTRA"
          class="lokantra-brand-wordmark"
        />
      </header>

      <!-- Center 3D Venom Symbiote Pill Button -->
      <div
        class="btn-wrapper"
        ref="wrapperRef"
        id="btnWrapper"
        @click="onBtnClick"
        @pointerdown="onBtnPointerDown"
        @pointerup="onBtnPointerUp"
      >
        <button
          class="venom-btn"
          ref="btnRef"
          id="venomBtn"
          @click="onBtnClick"
          @pointerdown="onBtnPointerDown"
          @pointerup="onBtnPointerUp"
          title="PREDICT the UNPREDICTABLE"
          aria-label="PREDICT the UNPREDICTABLE"
        >
          <span class="venom-btn-inner">
            <span class="venom-btn-text">PREDICT the UNPREDICTABLE</span>
            <svg
              class="venom-btn-arrow"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2.2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <line x1="5" y1="12" x2="19" y2="12"></line>
              <polyline points="12 5 19 12 12 19"></polyline>
            </svg>
          </span>
        </button>
      </div>
    </div>

    <!-- Symbiote Canvas Simulation -->
    <canvas id="symbiote-canvas" ref="canvasRef"></canvas>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import lokantraWordmark from '@/assets/logo/lokantra_wordmark.png'
import homescreenBg from '@/assets/homescreen_backgorund.png'
import { useSound } from '@/hooks/use-sound'
import { uiBlizzardStoreConfirmPurchaseSound } from '@/sounds/ui-blizzard-store-confirm-purchase'

const emit = defineEmits(['enter'])
const [play] = useSound(uiBlizzardStoreConfirmPurchaseSound)

const canvasRef = ref(null)
const btnRef = ref(null)
const wrapperRef = ref(null)
const isExiting = ref(false)
const buttonOffsetX = ref(68)

let ctx = null
let animId = null

let width = window.innerWidth
let height = window.innerHeight
let dpr = Math.min(window.devicePixelRatio || 1, 2)
let baseBtnRect = { width: 340, height: 72 }

const mouse = {
  x: width / 2 + 45,
  y: height / 2 - 145,
  vx: 0,
  vy: 0,
  speed: 0,
  userMoved: false
}

function rand(min, max) {
  return min + Math.random() * (max - min)
}

function updateMetrics() {
  if (!canvasRef.value || !btnRef.value) return
  width = window.innerWidth
  height = window.innerHeight
  dpr = Math.min(window.devicePixelRatio || 1, 2)

  canvasRef.value.width = width * dpr
  canvasRef.value.height = height * dpr
  if (ctx) {
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
  }

  baseBtnRect = {
    width: btnRef.value.offsetWidth || 340,
    height: btnRef.value.offsetHeight || 72
  }

  // Optical rightward shift to balance within the asymmetric spiderweb clearing
  if (width < 640) {
    buttonOffsetX.value = Math.round(width * 0.03)
  } else if (width < 1024) {
    buttonOffsetX.value = Math.round(width * 0.04)
  } else {
    buttonOffsetX.value = Math.min(85, Math.max(55, Math.round(width * 0.042)))
  }
}

function onPointerMove(e) {
  mouse.userMoved = true
  mouse.vx = e.clientX - mouse.x
  mouse.vy = e.clientY - mouse.y
  mouse.speed = Math.hypot(mouse.vx, mouse.vy)
  mouse.x = e.clientX
  mouse.y = e.clientY
}

function onTouchMove(e) {
  if (e.touches && e.touches.length > 0) {
    mouse.userMoved = true
    const touch = e.touches[0]
    mouse.vx = touch.clientX - mouse.x
    mouse.vy = touch.clientY - mouse.y
    mouse.speed = Math.hypot(mouse.vx, mouse.vy)
    mouse.x = touch.clientX
    mouse.y = touch.clientY
  }
}

// Point & outward normal on the stadium/pill perimeter given a local parameter angle & depth inset
function getPillPoint(angle, cx, cy, w, h, inset = 2) {
  const rx = Math.max(8, w / 2 - inset)
  const ry = Math.max(8, h / 2 - inset)
  const halfStraight = Math.max(0, rx - ry)

  const dx = Math.cos(angle)
  const dy = Math.sin(angle)

  const rawX = dx * rx * 1.15
  const spineX = Math.max(-halfStraight, Math.min(halfStraight, rawX))

  const vx = dx * rx - spineX
  const vy = dy * ry
  const len = Math.hypot(vx, vy) || 1
  const nx = vx / len
  const ny = vy / len

  return {
    x: cx + spineX + nx * ry,
    y: cy + ny * ry,
    nx,
    ny
  }
}

// Chaotic snap droplets & flying symbiote specks
const droplets = []
function spawnSnapParticles(x, y, vx, vy, count = 3) {
  for (let i = 0; i < count; i++) {
    const ang = rand(-0.9, 0.9)
    const c = Math.cos(ang)
    const s = Math.sin(ang)
    const mult = rand(0.25, 0.85)
    droplets.push({
      x,
      y,
      vx: (vx * c - vy * s) * mult + rand(-1.5, 1.5),
      vy: (vx * s + vy * c) * mult + rand(-1.5, 1.5),
      r: rand(0.8, 2.1),
      life: 1,
      decay: rand(0.025, 0.055)
    })
  }
}

// Lingering spiky drips on the button edge after a tendril snaps off
const buttonSpikes = []
function spawnButtonSpike(anchorAngle, length, width, recoilDir) {
  if (buttonSpikes.length > 18) buttonSpikes.shift()
  buttonSpikes.push({
    angle: anchorAngle,
    length: Math.min(48, Math.max(12, length)),
    maxLength: Math.min(48, Math.max(12, length)),
    width: width,
    bend: recoilDir * rand(6, 18),
    bendVel: 0,
    life: 1,
    decay: rand(0.012, 0.028)
  })
}

// Chaotic, Asynchronous Symbiote Tendril
class ChaoticTendril {
  constructor(id) {
    this.id = id
    this.numNodes = 10
    this.nodes = Array.from({ length: this.numNodes }, () => ({
      x: width / 2,
      y: height / 2,
      oldX: width / 2,
      oldY: height / 2,
      nx: 0,
      ny: -1
    }))
    this.state = 'dormant' // 'attached' | 'snapping' | 'dormant'
    this.cooldown = Math.floor(rand(0, 25))
    this.resetTraits()
  }

  resetTraits() {
    const roll = Math.random()
    if (roll < 0.28) {
      this.type = 'heavy'
      this.rootWidth = rand(2.8, 4.6)
      this.midWidth = rand(1.05, 1.85)
      this.tipWidth = rand(1.2, 2.1)
      this.maxLength = rand(210, 340)
      this.maxAge = rand(95, 240)
    } else if (roll < 0.72) {
      this.type = 'medium'
      this.rootWidth = rand(1.5, 2.7)
      this.midWidth = rand(0.55, 1.05)
      this.tipWidth = rand(0.65, 1.2)
      this.maxLength = rand(150, 290)
      this.maxAge = rand(45, 150)
    } else {
      this.type = 'thin'
      this.rootWidth = rand(0.8, 1.5)
      this.midWidth = rand(0.28, 0.55)
      this.tipWidth = rand(0.35, 0.65)
      this.maxLength = rand(110, 250)
      this.maxAge = rand(25, 95)
    }

    this.age = 0
    this.inset = rand(1.5, 7.5)
    this.tipOffsetX = rand(-14, 14)
    this.tipOffsetY = rand(-14, 14)
    this.bowDirection = rand(-34, 34)
    this.turbulenceFreq = rand(0.04, 0.11)
    this.turbulencePhase = rand(0, Math.PI * 2)
    this.turbulenceAmp = rand(1.5, 6.5)
    this.slackFactor = rand(0.86, 1.08)
    this.gravityScale = rand(0.08, 0.35)

    const numForks = Math.random() < 0.65 ? (Math.random() < 0.4 ? 2 : 1) : 0
    this.rootForks = []
    for (let i = 0; i < numForks; i++) {
      this.rootForks.push({
        nodeIdx: Math.floor(rand(1, 5)),
        angleDelta: (Math.random() < 0.5 ? -1 : 1) * rand(0.04, 0.22),
        thickness: rand(0.35, 0.75),
        curvePull: rand(-8, 8)
      })
    }

    this.hasMidSplit = Math.random() < 0.45
    this.midSplitNode = Math.floor(rand(3, 7))
    this.midSplitTipX = rand(-18, 18)
    this.midSplitTipY = rand(-18, 18)
    this.midSplitBow = rand(-16, 16)
  }

  spawn(cx, cy, bw, bh, dirToCursor, clusterAngles) {
    this.resetTraits()

    if (clusterAngles.length > 0 && Math.random() < 0.78) {
      const cluster = clusterAngles[Math.floor(Math.random() * clusterAngles.length)]
      this.anchorAngle = cluster + rand(-0.22, 0.22)
    } else {
      this.anchorAngle = dirToCursor + rand(-1.15, 1.15)
    }

    this.anchorCreep = rand(0.001, 0.008)

    const anchor = getPillPoint(this.anchorAngle, cx, cy, bw, bh, this.inset)
    this.anchorPt = anchor

    const distToMouse = Math.hypot(mouse.x - anchor.x, mouse.y - anchor.y)
    if (distToMouse > this.maxLength * 0.92) {
      this.cooldown = Math.floor(rand(4, 15))
      return
    }

    this.state = 'attached'
    this.age = 0

    for (let i = 0; i < this.numNodes; i++) {
      const t = i / (this.numNodes - 1)
      const jitterX = Math.sin(t * Math.PI) * this.bowDirection * 0.35
      const jitterY = Math.cos(t * Math.PI) * this.bowDirection * 0.35
      const px = anchor.x + (mouse.x + this.tipOffsetX - anchor.x) * t + jitterX
      const py = anchor.y + (mouse.y + this.tipOffsetY - anchor.y) * t + jitterY
      this.nodes[i].x = px
      this.nodes[i].y = py
      this.nodes[i].oldX = px - rand(-3, 3)
      this.nodes[i].oldY = py - rand(-3, 3)
    }
  }

  snap() {
    if (this.state !== 'attached') return
    this.state = 'snapping'
    this.snapTimer = 0

    const anchor = this.anchorPt
    const tip = this.nodes[this.numNodes - 1]
    const mid = this.nodes[Math.floor(this.numNodes * 0.55)]

    const dx = anchor.x - tip.x
    const dy = anchor.y - tip.y
    const dist = Math.hypot(dx, dy) || 1
    const whip = Math.min(28, dist * 0.12)

    spawnSnapParticles(
      mid.x,
      mid.y,
      (dx / dist) * whip * 0.45,
      (dy / dist) * whip * 0.45,
      Math.random() < 0.5 ? 2 : 1
    )

    spawnButtonSpike(
      this.anchorAngle,
      Math.min(42, dist * 0.24),
      this.rootWidth * 0.9,
      Math.sign(this.bowDirection || 1)
    )

    for (let i = 1; i < this.numNodes; i++) {
      const f = i / (this.numNodes - 1)
      const perpX = -dy / dist
      const perpY = dx / dist
      const wildCurl = rand(-12, 12) * Math.sin(f * Math.PI)
      this.nodes[i].oldX = this.nodes[i].x - ((dx / dist) * whip * f + perpX * wildCurl)
      this.nodes[i].oldY = this.nodes[i].y - ((dy / dist) * whip * f + perpY * wildCurl)
    }
  }

  update(cx, cy, bw, bh, dirToCursor, clusterAngles, frameCount) {
    if (this.state === 'dormant') {
      this.cooldown--
      if (this.cooldown <= 0) {
        this.spawn(cx, cy, bw, bh, dirToCursor, clusterAngles)
      }
      return
    }

    this.age++

    let angleDiff = ((dirToCursor - this.anchorAngle + Math.PI) % (Math.PI * 2)) - Math.PI
    if (angleDiff < -Math.PI) angleDiff += Math.PI * 2
    this.anchorAngle += angleDiff * this.anchorCreep

    const anchor = getPillPoint(this.anchorAngle, cx, cy, bw, bh, this.inset)
    this.anchorPt = anchor

    const targetTipX = mouse.x + this.tipOffsetX
    const targetTipY = mouse.y + this.tipOffsetY
    const dx = targetTipX - anchor.x
    const dy = targetTipY - anchor.y
    const stretchDist = Math.hypot(dx, dy) || 1
    this.stretchRatio = Math.min(1.3, stretchDist / this.maxLength)

    const ux = dx / stretchDist
    const uy = dy / stretchDist
    const perpX = -uy
    const perpY = ux

    const dotNormal = ux * anchor.nx + uy * anchor.ny

    if (this.state === 'attached') {
      const randomCut =
        this.age > this.maxAge ||
        (mouse.speed > 14 && Math.random() < 0.08) ||
        (stretchDist > 130 && Math.random() < 0.018)

      if (stretchDist > this.maxLength || (dotNormal < -0.15 && stretchDist > 60) || randomCut) {
        this.snap()
      }
    } else if (this.state === 'snapping') {
      this.snapTimer++
      const tipDist = Math.hypot(
        this.nodes[this.numNodes - 1].x - anchor.x,
        this.nodes[this.numNodes - 1].y - anchor.y
      )
      if (tipDist < 14 || this.snapTimer > 18) {
        this.state = 'dormant'
        this.cooldown = Math.floor(rand(1, 14))
        return
      }
    }

    const damping = this.state === 'attached' ? 0.81 : 0.72

    for (let i = 1; i < this.numNodes; i++) {
      const n = this.nodes[i]
      const vx = (n.x - n.oldX) * damping
      const vy = (n.y - n.oldY) * damping
      n.oldX = n.x
      n.oldY = n.y

      const s = i / (this.numNodes - 1)
      const wave =
        Math.sin(frameCount * this.turbulenceFreq + this.turbulencePhase + i * 0.7) *
        this.turbulenceAmp *
        Math.sin(s * Math.PI) *
        (1 - Math.min(0.85, this.stretchRatio * 0.7))

      n.x += vx + perpX * wave * 0.15
      n.y += vy + this.gravityScale + perpY * wave * 0.15

      if (this.state === 'snapping') {
        n.x += (anchor.x - n.x) * (0.24 + s * 0.18)
        n.y += (anchor.y - n.y) * (0.24 + s * 0.18)
      }
    }

    this.nodes[0].x = anchor.x
    this.nodes[0].y = anchor.y

    const last = this.nodes[this.numNodes - 1]
    if (this.state === 'attached') {
      last.x = targetTipX
      last.y = targetTipY
    }

    const segLen = ((this.state === 'attached' ? stretchDist : 8) / (this.numNodes - 1)) * this.slackFactor

    for (let iter = 0; iter < 4; iter++) {
      this.nodes[0].x = anchor.x
      this.nodes[0].y = anchor.y
      if (this.state === 'attached') {
        last.x = targetTipX
        last.y = targetTipY
      }

      for (let i = 0; i < this.numNodes - 1; i++) {
        const a = this.nodes[i]
        const b = this.nodes[i + 1]
        const sdx = b.x - a.x
        const sdy = b.y - a.y
        const d = Math.hypot(sdx, sdy) || 0.0001
        const diff = (d - segLen) / d

        if (i === 0) {
          b.x -= sdx * diff * 0.7
          b.y -= sdy * diff * 0.7
        } else if (i === this.numNodes - 2 && this.state === 'attached') {
          a.x += sdx * diff * 0.7
          a.y += sdy * diff * 0.7
        } else {
          a.x += sdx * diff * 0.45
          a.y += sdy * diff * 0.45
          b.x -= sdx * diff * 0.45
          b.y -= sdy * diff * 0.45
        }
      }

      if (this.state === 'attached' && iter === 0) {
        for (let i = 1; i < this.numNodes - 1; i++) {
          const s = i / (this.numNodes - 1)
          const bow = Math.sin(s * Math.PI) * this.bowDirection * (1 - Math.min(0.75, this.stretchRatio * 0.6))
          const normalOut = Math.pow(1 - s, 2) * Math.min(18, stretchDist * 0.12)

          const goalX = anchor.x + dx * s + perpX * bow + anchor.nx * normalOut
          const goalY = anchor.y + dy * s + perpY * bow + anchor.ny * normalOut

          this.nodes[i].x += (goalX - this.nodes[i].x) * 0.065
          this.nodes[i].y += (goalY - this.nodes[i].y) * 0.065
        }
      }
    }

    for (let i = 0; i < this.numNodes; i++) {
      const prev = this.nodes[Math.max(0, i - 1)]
      const next = this.nodes[Math.min(this.numNodes - 1, i + 1)]
      const tx = next.x - prev.x
      const ty = next.y - prev.y
      const len = Math.hypot(tx, ty) || 1
      this.nodes[i].nx = -ty / len
      this.nodes[i].ny = tx / len
    }
  }

  getRadiusAt(s) {
    const thinFactor = Math.max(0.24, 1 - this.stretchRatio * 0.62)
    const rootFlare = Math.pow(Math.max(0, 1 - s * 3.4), 2.4) * this.rootWidth
    const tipFlare =
      this.state === 'attached'
        ? Math.pow(Math.max(0, (s - 0.8) / 0.2), 2.0) * this.tipWidth
        : 0
    const body = this.midWidth * thinFactor
    return rootFlare + body + tipFlare
  }
}

const MAX_TENDRILS = 24
let tendrils = []

function applyChaoticMidAirKnots() {
  for (let i = 0; i < tendrils.length; i++) {
    const a = tendrils[i]
    if (a.state !== 'attached') continue

    for (let j = i + 1; j < tendrils.length; j++) {
      const b = tendrils[j]
      if (b.state !== 'attached') continue

      const nodeIdx = 3 + ((i + j) % 4)
      const na = a.nodes[nodeIdx]
      const nb = b.nodes[nodeIdx]
      const dx = nb.x - na.x
      const dy = nb.y - na.y
      const d = Math.hypot(dx, dy)

      if (d > 1 && d < 22) {
        const pinch = (1 - d / 22) * 0.18
        na.x += dx * pinch
        na.y += dy * pinch
        nb.x -= dx * pinch
        nb.y -= dy * pinch
      }
    }
  }
}

function drawRootAndBranches(t, cx, cy, bw, bh) {
  if (!ctx) return
  const pts = t.nodes
  const span = Math.hypot(pts[pts.length - 1].x - pts[0].x, pts[pts.length - 1].y - pts[0].y)
  if (span < 4) return

  const n0 = pts[0]
  const n1 = pts[1]
  const dx = n1.x - n0.x
  const dy = n1.y - n0.y
  const d = Math.hypot(dx, dy) || 1
  const ux = dx / d
  const uy = dy / d
  const tx = -uy
  const ty = ux

  const footW = t.rootWidth * 2.1
  const pullLen = Math.min(16, span * 0.25)

  ctx.beginPath()
  ctx.moveTo(n0.x + tx * footW, n0.y + ty * footW)
  ctx.quadraticCurveTo(n0.x + ux * 2.5, n0.y + uy * 2.5, n0.x + ux * pullLen, n0.y + uy * pullLen)
  ctx.quadraticCurveTo(n0.x + ux * 2.5, n0.y + uy * 2.5, n0.x - tx * footW, n0.y - ty * footW)
  ctx.closePath()
  ctx.fillStyle = '#000000'
  ctx.fill()

  const thinFactor = Math.max(0.28, 1 - t.stretchRatio * 0.55)

  for (const fork of t.rootForks) {
    const forkAnchor = getPillPoint(
      t.anchorAngle + fork.angleDelta,
      cx,
      cy,
      bw,
      bh,
      t.inset
    )
    const targetNode = pts[fork.nodeIdx]
    const midX = (forkAnchor.x + targetNode.x) * 0.5 + forkAnchor.nx * 6 + tx * fork.curvePull
    const midY = (forkAnchor.y + targetNode.y) * 0.5 + forkAnchor.ny * 6 + ty * fork.curvePull

    ctx.beginPath()
    ctx.moveTo(forkAnchor.x, forkAnchor.y)
    ctx.quadraticCurveTo(midX, midY, targetNode.x, targetNode.y)
    ctx.lineWidth = Math.max(0.4, t.midWidth * fork.thickness * thinFactor * 1.35)
    ctx.lineCap = 'round'
    ctx.strokeStyle = '#000000'
    ctx.stroke()
  }

  if (t.hasMidSplit && t.state === 'attached' && span > 55) {
    const splitStart = pts[t.midSplitNode]
    const endX = mouse.x + t.midSplitTipX * 0.5
    const endY = mouse.y + t.midSplitTipY * 0.5
    const ctrlX = (splitStart.x + endX) * 0.5 + splitStart.nx * t.midSplitBow
    const ctrlY = (splitStart.y + endY) * 0.5 + splitStart.ny * t.midSplitBow

    ctx.beginPath()
    ctx.moveTo(splitStart.x, splitStart.y)
    ctx.quadraticCurveTo(ctrlX, ctrlY, endX, endY)
    ctx.lineWidth = Math.max(0.35, t.midWidth * 0.55 * thinFactor)
    ctx.strokeStyle = 'rgba(8, 8, 12, 0.88)'
    ctx.stroke()
  }
}

function drawTendrilStrand(t) {
  if (!ctx) return
  const pts = t.nodes
  const span = Math.hypot(pts[pts.length - 1].x - pts[0].x, pts[pts.length - 1].y - pts[0].y)
  if (span < 4) return

  const leftPts = []
  const rightPts = []

  for (let i = 0; i < pts.length; i++) {
    const s = i / (pts.length - 1)
    const r = t.getRadiusAt(s)
    const p = pts[i]
    leftPts.push({ x: p.x + p.nx * r, y: p.y + p.ny * r })
    rightPts.push({ x: p.x - p.nx * r, y: p.y - p.ny * r })
  }

  ctx.beginPath()
  ctx.moveTo(leftPts[0].x, leftPts[0].y)

  for (let i = 1; i < leftPts.length - 1; i++) {
    const xc = (leftPts[i].x + leftPts[i + 1].x) * 0.5
    const yc = (leftPts[i].y + leftPts[i + 1].y) * 0.5
    ctx.quadraticCurveTo(leftPts[i].x, leftPts[i].y, xc, yc)
  }
  ctx.lineTo(leftPts[leftPts.length - 1].x, leftPts[leftPts.length - 1].y)

  const lastP = pts[pts.length - 1]
  ctx.arc(lastP.x, lastP.y, t.getRadiusAt(1), 0, Math.PI * 2)

  ctx.lineTo(rightPts[rightPts.length - 1].x, rightPts[rightPts.length - 1].y)

  for (let i = rightPts.length - 2; i >= 1; i--) {
    const xc = (rightPts[i].x + rightPts[i - 1].x) * 0.5
    const yc = (rightPts[i].y + rightPts[i - 1].y) * 0.5
    ctx.quadraticCurveTo(rightPts[i].x, rightPts[i].y, xc, yc)
  }
  ctx.lineTo(rightPts[0].x, rightPts[0].y)
  ctx.closePath()

  ctx.fillStyle = '#000000'
  ctx.fill()
}

function drawDynamicWebFilaments() {
  if (!ctx) return
  for (let i = 0; i < tendrils.length; i++) {
    const a = tendrils[i]
    if (a.state !== 'attached') continue

    for (let j = i + 1; j < tendrils.length; j++) {
      const b = tendrils[j]
      if (b.state !== 'attached') continue

      const pairs = [
        [1, 2, 38],
        [2, 3, 34],
        [3, 5, 32],
        [5, 6, 28],
        [7, 8, 28]
      ]

      for (const [ia, ib, maxDist] of pairs) {
        const pa = a.nodes[ia]
        const pb = b.nodes[ib]
        const d = Math.hypot(pb.x - pa.x, pb.y - pa.y)

        if (d > 2 && d < maxDist) {
          const ratio = 1 - d / maxDist
          const prevX = (a.nodes[ia - 1].x + b.nodes[ib - 1].x) * 0.5
          const prevY = (a.nodes[ia - 1].y + b.nodes[ib - 1].y) * 0.5
          const midX = (pa.x + pb.x) * 0.5
          const midY = (pa.y + pb.y) * 0.5
          const ctrlX = midX + (prevX - midX) * 0.38
          const ctrlY = midY + (prevY - midY) * 0.38

          ctx.beginPath()
          ctx.moveTo(pa.x, pa.y)
          ctx.quadraticCurveTo(ctrlX, ctrlY, pb.x, pb.y)
          ctx.lineWidth = Math.max(0.3, ratio * 1.15)
          ctx.strokeStyle = `rgba(7, 7, 10, ${ratio * 0.85})`
          ctx.stroke()
        }
      }
    }
  }
}

function updateAndDrawButtonSpikes(cx, cy, bw, bh) {
  if (!ctx) return
  for (let i = buttonSpikes.length - 1; i >= 0; i--) {
    const sp = buttonSpikes[i]
    sp.life -= sp.decay
    sp.length *= 0.94
    sp.bendVel = (sp.bendVel - sp.bend * 0.18) * 0.78
    sp.bend += sp.bendVel

    if (sp.life <= 0 || sp.length < 2) {
      buttonSpikes.splice(i, 1)
      continue
    }

    const root = getPillPoint(sp.angle, cx, cy, bw, bh, 2.5)
    const tx = -root.ny
    const ty = root.nx

    const tipX = root.x + root.nx * sp.length + tx * sp.bend * 0.4
    const tipY = root.y + root.ny * sp.length + ty * sp.bend * 0.4 + (1 - sp.life) * 8
    const baseHalf = sp.width * sp.life * 1.6

    ctx.beginPath()
    ctx.moveTo(root.x + tx * baseHalf, root.y + ty * baseHalf)
    ctx.quadraticCurveTo(
      root.x + root.nx * sp.length * 0.45 + tx * sp.bend * 0.2,
      root.y + root.ny * sp.length * 0.45 + ty * sp.bend * 0.2,
      tipX,
      tipY
    )
    ctx.quadraticCurveTo(
      root.x + root.nx * sp.length * 0.45 - tx * sp.bend * 0.1,
      root.y + root.ny * sp.length * 0.45 - ty * sp.bend * 0.1,
      root.x - tx * baseHalf,
      root.y - ty * baseHalf
    )
    ctx.closePath()
    ctx.fillStyle = '#000000'
    ctx.fill()
  }
}

let shiftX = 0, shiftY = 0
let velX = 0, velY = 0
let tiltX = 0, tiltY = 0
let frameCount = 0
let demoTime = -1.1
const clusterOffsets = [-0.45, 0.08, 0.52]

function animate() {
  if (!ctx) return
  frameCount++
  ctx.clearRect(0, 0, width, height)

    let btnBaseX = width / 2
  let btnBaseY = height * 0.54
  if (btnRef.value) {
    const rect = btnRef.value.getBoundingClientRect()
    btnBaseX = rect.left + rect.width / 2 - shiftX
    btnBaseY = rect.top + rect.height / 2 - shiftY
  }
  const screenCenterX = btnBaseX
  const screenCenterY = btnBaseY

  if (!mouse.userMoved) {
    demoTime += 0.022
    const orbitX = Math.cos(demoTime) * 155 + Math.sin(demoTime * 2.3) * 45
    const orbitY = Math.sin(demoTime * 1.4) * 145 - 20
    mouse.vx = screenCenterX + orbitX - mouse.x
    mouse.vy = screenCenterY + orbitY - mouse.y
    mouse.speed = Math.hypot(mouse.vx, mouse.vy)
    mouse.x = screenCenterX + orbitX
    mouse.y = screenCenterY + orbitY
  } else {
    mouse.speed *= 0.85
  }

  const btnCx = screenCenterX + shiftX
  const btnCy = screenCenterY + shiftY
  const bw = baseBtnRect.width
  const bh = baseBtnRect.height

  const dirToCursor = Math.atan2(mouse.y - btnCy, mouse.x - btnCx)

  for (let c = 0; c < clusterOffsets.length; c++) {
    if (Math.random() < 0.04) {
      clusterOffsets[c] = rand(-0.95, 0.95)
    }
  }
  const clusterAngles = clusterOffsets.map(off => dirToCursor + off)

  let totalPullX = 0
  let totalPullY = 0
  let attachedCount = 0

  for (let i = 0; i < tendrils.length; i++) {
    const t = tendrils[i]
    t.update(btnCx, btnCy, bw, bh, dirToCursor, clusterAngles, frameCount)

    if (t.state === 'attached') {
      attachedCount++
      const tip = t.nodes[t.numNodes - 1]
      const root = t.nodes[0]
      const weight = t.type === 'heavy' ? 0.005 : 0.0025
      totalPullX += (tip.x - root.x) * weight
      totalPullY += (tip.y - root.y) * weight
    }
  }

  applyChaoticMidAirKnots()

  // Dampen jitter when mouse is hovering near or over the button to keep it easy to click
  const isOverButton = Math.abs(mouse.x - btnCx) < (bw / 2 + 25) && Math.abs(mouse.y - btnCy) < (bh / 2 + 25)
  const maxShift = isOverButton ? 7 : 20
  const maxTilt = isOverButton ? 5 : 15

  const targetX = Math.max(-maxShift, Math.min(maxShift, totalPullX))
  const targetY = Math.max(-maxShift, Math.min(maxShift, totalPullY))
  velX = (velX + (targetX - shiftX) * 0.15) * 0.78
  velY = (velY + (targetY - shiftY) * 0.15) * 0.78
  shiftX += velX
  shiftY += velY

  const targetTiltX = Math.max(-maxTilt, Math.min(maxTilt, -shiftY * 0.75))
  const targetTiltY = Math.max(-maxTilt, Math.min(maxTilt, shiftX * 0.75))
  tiltX += (targetTiltX - tiltX) * 0.15
  tiltY += (targetTiltY - tiltY) * 0.15

  if (wrapperRef.value) {
    wrapperRef.value.style.transform = `translate3d(${shiftX.toFixed(2)}px, ${shiftY.toFixed(2)}px, 0) rotateX(${tiltX.toFixed(2)}deg) rotateY(${tiltY.toFixed(2)}deg)`
  }

  updateAndDrawButtonSpikes(btnCx, btnCy, bw, bh)
  drawDynamicWebFilaments()

  for (let i = 0; i < tendrils.length; i++) {
    const t = tendrils[i]
    if (t.state === 'dormant') continue
    drawRootAndBranches(t, btnCx, btnCy, bw, bh)
    drawTendrilStrand(t)
  }

  if (attachedCount > 0) {
    for (let i = 0; i < tendrils.length; i++) {
      const t = tendrils[i]
      if (t.state !== 'attached') continue
      const nLast = t.nodes[t.numNodes - 1]
      const nPre = t.nodes[t.numNodes - 2]

      ctx.beginPath()
      ctx.moveTo(nPre.x, nPre.y)
      ctx.quadraticCurveTo(nLast.x, nLast.y, mouse.x, mouse.y)
      ctx.lineWidth = Math.max(0.4, t.tipWidth * 0.75)
      ctx.lineCap = 'round'
      ctx.strokeStyle = '#000000'
      ctx.stroke()
    }
  }

  for (let i = droplets.length - 1; i >= 0; i--) {
    const d = droplets[i]
    d.x += d.vx
    d.y += d.vy
    d.vx *= 0.91
    d.vy = d.vy * 0.91 + 0.12
    d.life -= d.decay

    if (d.life <= 0) {
      droplets.splice(i, 1)
      continue
    }

    ctx.beginPath()
    ctx.arc(d.x, d.y, d.r * d.life, 0, Math.PI * 2)
    ctx.fillStyle = '#000000'
    ctx.fill()
  }

  animId = requestAnimationFrame(animate)
}

let hasEntered = false
let pointerDownPos = null

function triggerEnter(e) {
  if (e) {
    if (e.stopPropagation) e.stopPropagation()
  }
  if (hasEntered || isExiting.value) return
  hasEntered = true
  isExiting.value = true

  try {
    play()
  } catch (err) {
    console.warn('Audio play error:', err)
  }

  // Dramatic symbiote snap upon click
  for (const t of tendrils) {
    if (t.state === 'attached') {
      t.snap()
    }
  }
  spawnSnapParticles(mouse.x, mouse.y, rand(-5, 5), rand(-5, 5), 10)

  // Immediately notify parent to redirect to /home without artificial delay
  emit('enter')
}

function onBtnPointerDown(e) {
  if (hasEntered || isExiting.value) return
  pointerDownPos = { x: e.clientX, y: e.clientY }
}

function onBtnPointerUp(e) {
  if (!pointerDownPos || hasEntered || isExiting.value) return
  const dist = Math.hypot(e.clientX - pointerDownPos.x, e.clientY - pointerDownPos.y)
  pointerDownPos = null
  if (dist < 35) {
    triggerEnter(e)
  }
}

function onWindowPointerUp(e) {
  if (!pointerDownPos || hasEntered || isExiting.value) return
  const dist = Math.hypot(e.clientX - pointerDownPos.x, e.clientY - pointerDownPos.y)
  pointerDownPos = null
  if (dist < 45) {
    triggerEnter(e)
  }
}

function onBtnClick(e) {
  triggerEnter(e)
}

onMounted(() => {
  nextTick(() => {
    if (!canvasRef.value) return
    ctx = canvasRef.value.getContext('2d')
    tendrils = Array.from({ length: MAX_TENDRILS }, (_, i) => new ChaoticTendril(i))

    updateMetrics()

    window.addEventListener('resize', updateMetrics)
    window.addEventListener('pointermove', onPointerMove, { passive: true })
    window.addEventListener('touchmove', onTouchMove, { passive: true })
    window.addEventListener('pointerup', onWindowPointerUp)

    animId = requestAnimationFrame(animate)
  })
})

onUnmounted(() => {
  if (animId) cancelAnimationFrame(animId)
  window.removeEventListener('resize', updateMetrics)
  window.removeEventListener('pointermove', onPointerMove)
  window.removeEventListener('touchmove', onTouchMove)
  window.removeEventListener('pointerup', onWindowPointerUp)
})
</script>

<style scoped>
.venom-opening-screen {
  position: fixed;
  inset: 0;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  background: radial-gradient(circle at 50% 44%, #f7f8fa 0%, #e5e8ef 58%, #d2d7e0 100%);
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Inter", "Segoe UI", Roboto, sans-serif;
  display: flex;
  align-items: center;
  justify-content: center;
  perspective: 1000px;
  z-index: 100;
  transition: opacity 0.5s cubic-bezier(0.4, 0, 0.2, 1), transform 0.5s cubic-bezier(0.4, 0, 0.2, 1), filter 0.5s ease;
  will-change: opacity, transform, filter;
  user-select: none;
}

.venom-opening-screen.venom-opening-exiting {
  opacity: 0;
  transform: scale(1.05);
  filter: blur(10px);
  pointer-events: none;
}

/* Spiderweb Background Layer */
.venom-bg-layer {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 1;
  overflow: hidden;
}

.venom-bg-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center center;
  display: block;
  user-select: none;
  filter: contrast(1.04) brightness(1.0);
  transform: translateZ(0);
}

/* Central Content Container matching reference composition */
.venom-center-container {
  position: absolute;
  top: 39%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: clamp(28px, 4.4vh, 48px);
  z-index: 10;
  pointer-events: auto;
  width: 100%;
  max-width: 90vw;
}

.venom-logo-wrap {
  display: flex;
  justify-content: center;
  align-items: center;
}

.lokantra-brand-wordmark {
  height: clamp(80px, 12vw, 135px);
  max-width: min(90vw, 620px);
  width: auto;
  object-fit: contain;
  display: block;
  user-select: none;
  filter: drop-shadow(0 4px 18px rgba(0, 0, 0, 0.14));
  transition: transform 0.3s ease, filter 0.3s ease;
}

.lokantra-brand-wordmark:hover {
  transform: scale(1.02);
  filter: drop-shadow(0 6px 24px rgba(0, 0, 0, 0.22));
}

#symbiote-canvas {
  position: fixed;
  inset: 0;
  width: 100vw;
  height: 100vh;
  pointer-events: none;
  z-index: 4;
  filter: drop-shadow(0 6px 10px rgba(0, 0, 0, 0.16));
}

.btn-wrapper {
  position: relative;
  z-index: 10;
  transform-style: preserve-3d;
  will-change: transform;
  cursor: pointer;
  display: flex;
  justify-content: center;
}

.venom-btn {
  position: relative;
  padding: clamp(12px, 1.6vh, 16px) clamp(28px, 3.2vw, 42px);
  border-radius: 9999px;
  border: none;
  outline: none;
  cursor: pointer;
  touch-action: manipulation;
  user-select: none;
  background: #000000;
  color: #ffffff;
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Inter", "Segoe UI", Roboto, sans-serif;
  font-size: clamp(13px, 1.25vw, 16px);
  font-weight: 500;
  letter-spacing: 0.04em;
  white-space: nowrap;
  box-shadow:
    0 18px 36px -6px rgba(0, 0, 0, 0.45),
    0 8px 16px -4px rgba(0, 0, 0, 0.3);
  transform-style: preserve-3d;
  transition: transform 0.2s ease, box-shadow 0.2s ease, background 0.2s ease;
}

.venom-btn:hover {
  background: #0a0a0a;
  transform: scale(1.015);
  box-shadow:
    0 22px 42px -6px rgba(0, 0, 0, 0.55),
    0 10px 20px -4px rgba(0, 0, 0, 0.35);
}

.venom-btn-inner {
  position: relative;
  z-index: 2;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 14px;
  pointer-events: none;
}

.venom-btn-text {
  letter-spacing: 0.04em;
}

.venom-btn-arrow {
  width: clamp(16px, 1.4vw, 19px);
  height: clamp(16px, 1.4vw, 19px);
  transition: transform 0.25s ease;
}

.venom-btn:hover .venom-btn-arrow {
  transform: translateX(4px);
}

.venom-btn:active {
  cursor: pointer;
  transform: scale(0.98);
  box-shadow:
    0 10px 20px -6px rgba(0, 0, 0, 0.5),
    0 4px 8px -2px rgba(0, 0, 0, 0.3);
}
</style>
