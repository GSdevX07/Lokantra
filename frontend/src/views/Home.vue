<template>
  <div class="home-container fixed inset-0 w-screen h-screen overflow-hidden text-neutral-100 select-none" style="font-family: var(--font-body);">
    <!-- Venom Opening Screen (appears as soon as we open the page) -->
    <Transition name="intro-dissolve">
      <VenomIntro
        v-if="showIntro"
        @enter="handleEnterHomepage"
      />
    </Transition>

    <!-- Interactive Background Canvas (0-latency preloaded frame sequence) -->
    <canvas
      ref="canvasRef"
      width="1920"
      height="1085"
      class="fixed inset-0 w-full h-full object-cover z-0 pointer-events-none transition-transform duration-500 ease-out"
      style="object-position: left center; transform: scale(1.1); transform-origin: left center; filter: contrast(1.18) brightness(0.82);"
    ></canvas>

    <!-- Venomous Ambient Atmosphere Overlays: Pure pitch black & shades of black -->
    <div class="fixed inset-0 pointer-events-none z-0 bg-radial-at-c from-transparent via-[#060606]/80 to-[#000000]/98"></div>
    <div class="fixed inset-0 pointer-events-none z-0 bg-gradient-to-r from-[#000000]/95 via-[#050505]/80 via-50% to-transparent"></div>

    <!-- Wordmark Logo: placed above bit right, directly above the human -->
    <header class="fixed top-2 sm:top-3 md:top-4 lg:top-5 left-1/2 sm:left-[68%] md:left-[72%] lg:left-[75%] -translate-x-1/2 z-30 pointer-events-auto flex justify-center items-center">
      <img
        src="../assets/logo/lokantra_wordmark.png"
        alt="LOKĀNTRA"
        class="h-12 sm:h-15 md:h-18 lg:h-20 max-w-[50vw] sm:max-w-[36vw] md:max-w-[30vw] w-auto object-contain cursor-pointer select-none filter drop-shadow-[0_0_25px_rgba(255,255,255,0.18)] drop-shadow-[0_4px_16px_rgba(0,0,0,0.95)] hover:brightness-[1.15] hover:scale-[1.03] transition-all duration-300"
        @click="handleLogoClick"
        title="LOKĀNTRA"
      />
    </header>

    <!-- HERO SECTION (Fixed full-screen, no scrolling) -->
    <main class="h-full w-full flex flex-col justify-center px-6 sm:px-12 md:px-16 lg:px-24 xl:px-28 pt-24 pb-12 relative z-10 overflow-hidden">
      <div class="w-full max-w-xl lg:max-w-2xl relative z-10 flex flex-col items-start text-left">
        <!-- 1. Blurred intro label -->
        <div
          class="pointer-events-none select-none mb-3 sm:mb-4 text-neutral-300/85"
          style="font-size: clamp(16px, 2.1vw, 22px); line-height: 1.35; font-weight: 450; font-family: var(--font-body); letter-spacing: -0.01em; filter: blur(0.8px);"
        >
          Hey there, meet <span class="text-white font-semibold tracking-wide">LOKĀNTRA</span>,<br />
          {{ $t('home.tagline') }}
        </div>

        <!-- 2. CRAZY BOLD HERO HIGHLIGHT: "Upload Reports, Predict The Unseen" -->
        <div class="hero-highlight-wrap mb-4 sm:mb-6 select-none">
          <h1 class="hero-highlight-title">
            <span class="hero-text-white">Upload Reports,</span>
            <span class="hero-text-venom-chrome">Predict The Unseen</span>
          </h1>
        </div>

        <!-- 3. Blurred normal content (Typewriter text) -->
        <p
          class="text-neutral-300/90 mb-6 sm:mb-8 select-text pointer-events-none"
          style="font-size: clamp(17px, 2.3vw, 24px); line-height: 1.45; font-weight: 450; min-height: 64px; font-family: var(--font-body); letter-spacing: -0.01em; filter: blur(0.8px);"
        >
          {{ displayedText }}<span v-if="!typewriterDone" class="inline-block w-[2px] h-[1.15em] bg-white align-middle ml-[2px] cursor-blink shadow-[0_0_8px_white]"></span>
        </p>

        <!-- 4. Venom Symbiote Action Buttons -->
        <div
          class="flex flex-wrap items-center gap-2.5 sm:gap-4 transition-all duration-500 ease-out pt-2"
          :style="{
            opacity: showPills ? 1 : 0,
            transform: showPills ? 'translateY(0)' : 'translateY(12px)'
          }"
        >
          <button
            @click="activeModal = 'console'"
            class="venom-pill-btn-primary group"
          >
            <span class="relative z-10 flex items-center gap-2.5">
              Start Simulation
              <span class="inline-block transition-transform duration-300 group-hover:translate-x-1.5 font-bold text-white">&rarr;</span>
            </span>
          </button>

          <button
            @click="activeModal = 'workflow'"
            class="venom-pill-btn-secondary"
          >
            Explore Workflow
          </button>

          <button
            @click="activeModal = 'history'"
            class="venom-pill-btn-secondary"
          >
            History Database
          </button>

          <button
            @click="activeModal = 'status'"
            class="venom-pill-btn-secondary"
          >
            System Architecture
          </button>
        </div>
      </div>
    </main>

    <!-- Modal Overlays for Features (Keeps page 100% fixed with zero scrolling) -->
    <Transition name="modal-fade">
      <div 
        v-if="activeModal" 
        class="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 md:p-8 bg-black/85 backdrop-blur-md"
        @click.self="activeModal = null"
      >
        <!-- Modal Backdrop Ambient Venom Web Strands (full-screen edges) -->
        <div class="modal-backdrop-webs pointer-events-none absolute inset-0 overflow-hidden z-0">
          <svg class="w-full h-full opacity-45" viewBox="0 0 1920 1080" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">
            <g stroke="#000000" stroke-width="4.5" stroke-opacity="0.95" fill="none">
              <path d="M 0,0 Q 480,310 960,270 T 1920,0" />
              <path d="M 0,160 Q 580,440 1120,400 T 1920,130" />
              <path d="M 0,390 Q 260,580 490,740" />
              <path d="M 1920,390 Q 1660,580 1430,740" />
            </g>
            <g stroke="rgba(255,255,255,0.28)" stroke-width="1.3" fill="none">
              <path d="M 0,0 Q 480,310 960,270 T 1920,0" />
              <path d="M 0,160 Q 580,440 1120,400 T 1920,130" />
              <path d="M 0,390 Q 260,580 490,740" />
              <path d="M 1920,390 Q 1660,580 1430,740" />
            </g>
          </svg>
        </div>

        <div class="modal-dialog relative w-full max-w-4xl max-h-[85vh] rounded-2xl shadow-2xl overflow-hidden flex flex-col text-neutral-100">
          <!-- VENOMOUS WEB STRINGS & FRACTURE CRACKS BACKGROUND LAYER -->
          <div class="modal-venom-web-bg pointer-events-none select-none absolute inset-0 z-0 overflow-hidden">
            <svg class="w-full h-full" viewBox="0 0 1200 800" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">
              <defs>
                <!-- Crack glow aura filter -->
                <filter id="crackAura" x="-20%" y="-20%" width="140%" height="140%">
                  <feGaussianBlur in="SourceGraphic" stdDeviation="2.5" />
                </filter>
                <!-- Droplet specular gradient -->
                <radialGradient id="dropletGrad" cx="35%" cy="30%" r="65%">
                  <stop offset="0%" stop-color="#ffffff" stop-opacity="0.95" />
                  <stop offset="25%" stop-color="#808080" stop-opacity="0.8" />
                  <stop offset="70%" stop-color="#141414" stop-opacity="0.95" />
                  <stop offset="100%" stop-color="#000000" stop-opacity="1" />
                </radialGradient>
                <!-- Web string sheen gradient -->
                <linearGradient id="webSheen" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stop-color="#ffffff" stop-opacity="0.65" />
                  <stop offset="30%" stop-color="#a3a3a3" stop-opacity="0.35" />
                  <stop offset="70%" stop-color="#333333" stop-opacity="0.2" />
                  <stop offset="100%" stop-color="#ffffff" stop-opacity="0.55" />
                </linearGradient>
                <!-- Fissure core gradient -->
                <linearGradient id="fissureGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stop-color="#ffffff" stop-opacity="0.85" />
                  <stop offset="50%" stop-color="#d4d4d4" stop-opacity="0.6" />
                  <stop offset="100%" stop-color="#666666" stop-opacity="0.3" />
                </linearGradient>
              </defs>

              <!-- LAYER 1: SPREADING OBSIDIAN FRACTURE CRACKS -->
              <g class="fissure-cracks-group">
                <!-- Aura blur layers for cracks -->
                <g filter="url(#crackAura)" stroke="#ffffff" stroke-opacity="0.2" stroke-linecap="round" stroke-linejoin="bevel">
                  <!-- Main Crack 1: Top-left jagged tear through center -->
                  <path d="M 0,45 L 115,95 L 170,80 L 250,165 L 315,220 L 410,255 L 505,350 L 580,340 L 685,465 L 760,490 L 875,605 L 970,625 L 1080,755 L 1130,790" stroke-width="4.5" fill="none" />
                  <path d="M 170,80 L 230,35 L 290,25" stroke-width="3" fill="none" />
                  <path d="M 315,220 L 385,195 L 470,200" stroke-width="3" fill="none" />
                  <path d="M 505,350 L 575,400 L 620,465" stroke-width="3" fill="none" />
                  <path d="M 760,490 L 805,440 L 870,425" stroke-width="3" fill="none" />

                  <!-- Main Crack 2: Bottom-right jagged fracture -->
                  <path d="M 1200,630 L 1090,585 L 1020,610 L 930,515 L 865,470 L 785,485 L 700,390 L 625,365 L 575,305 L 470,250 L 395,200" stroke-width="4.5" fill="none" />
                  <path d="M 1020,610 L 980,690 L 935,745" stroke-width="3" fill="none" />
                  <path d="M 865,470 L 820,420 L 770,370" stroke-width="3" fill="none" />

                  <!-- Minor fracture: Left edge puncture -->
                  <path d="M 0,430 L 95,445 L 160,410 L 235,470 L 295,455 L 360,530" stroke-width="3.5" fill="none" />
                  <path d="M 160,410 L 210,350 L 270,330" stroke-width="2.5" fill="none" />

                  <!-- Minor fracture: Top-right corner stress -->
                  <path d="M 1200,100 L 1105,130 L 1045,95 L 980,160 L 910,145" stroke-width="3" fill="none" />
                  <path d="M 1045,95 L 1025,35" stroke-width="2.5" fill="none" />
                </g>

                <!-- Sharp razor-core crack strokes -->
                <g stroke="url(#fissureGrad)" stroke-linecap="round" stroke-linejoin="bevel">
                  <path d="M 0,45 L 115,95 L 170,80 L 250,165 L 315,220 L 410,255 L 505,350 L 580,340 L 685,465 L 760,490 L 875,605 L 970,625 L 1080,755 L 1130,790" stroke-width="1.3" fill="none" />
                  <path d="M 170,80 L 230,35 L 290,25" stroke-width="0.9" fill="none" />
                  <path d="M 315,220 L 385,195 L 470,200" stroke-width="0.9" fill="none" />
                  <path d="M 505,350 L 575,400 L 620,465" stroke-width="0.9" fill="none" />
                  <path d="M 760,490 L 805,440 L 870,425" stroke-width="0.9" fill="none" />

                  <path d="M 1200,630 L 1090,585 L 1020,610 L 930,515 L 865,470 L 785,485 L 700,390 L 625,365 L 575,305 L 470,250 L 395,200" stroke-width="1.3" fill="none" />
                  <path d="M 1020,610 L 980,690 L 935,745" stroke-width="0.9" fill="none" />
                  <path d="M 865,470 L 820,420 L 770,370" stroke-width="0.9" fill="none" />

                  <path d="M 0,430 L 95,445 L 160,410 L 235,470 L 295,455 L 360,530" stroke-width="1.1" fill="none" />
                  <path d="M 160,410 L 210,350 L 270,330" stroke-width="0.8" fill="none" />
                  <path d="M 1200,100 L 1105,130 L 1045,95 L 980,160 L 910,145" stroke-width="1.1" fill="none" />
                  <path d="M 1045,95 L 1025,35" stroke-width="0.8" fill="none" />
                </g>
              </g>

              <!-- LAYER 2: TOP-LEFT & TOP-RIGHT CORNER SPIDERWEBS -->
              <g class="corner-webs-group">
                <!-- Top-Left Radial Spokes -->
                <g stroke="#000000" stroke-width="3.5" stroke-opacity="0.95" fill="none">
                  <line x1="0" y1="0" x2="260" y2="55" />
                  <line x1="0" y1="0" x2="215" y2="160" />
                  <line x1="0" y1="0" x2="130" y2="250" />
                  <line x1="0" y1="0" x2="40" y2="320" />
                </g>
                <g stroke="rgba(255,255,255,0.45)" stroke-width="1" fill="none">
                  <line x1="0" y1="0" x2="260" y2="55" />
                  <line x1="0" y1="0" x2="215" y2="160" />
                  <line x1="0" y1="0" x2="130" y2="250" />
                  <line x1="0" y1="0" x2="40" y2="320" />
                </g>
                <!-- Top-Left Drooping Concentric Arcs -->
                <g stroke="#000000" stroke-width="3.5" stroke-opacity="0.95" fill="none">
                  <path d="M 70,0 Q 55,26 42,60 Q 28,82 0,95" />
                  <path d="M 150,0 Q 125,58 95,125 Q 58,175 0,195" />
                  <path d="M 245,0 Q 205,90 155,190 Q 90,270 0,315" />
                  <path d="M 350,0 Q 295,130 225,275 Q 130,385 0,445" />
                </g>
                <g stroke="url(#webSheen)" stroke-width="1.3" fill="none">
                  <path d="M 70,0 Q 55,26 42,60 Q 28,82 0,95" />
                  <path d="M 150,0 Q 125,58 95,125 Q 58,175 0,195" />
                  <path d="M 245,0 Q 205,90 155,190 Q 90,270 0,315" />
                  <path d="M 350,0 Q 295,130 225,275 Q 130,385 0,445" />
                </g>

                <!-- Top-Right Radial Spokes -->
                <g stroke="#000000" stroke-width="3.5" stroke-opacity="0.95" fill="none">
                  <line x1="1200" y1="0" x2="940" y2="55" />
                  <line x1="1200" y1="0" x2="985" y2="160" />
                  <line x1="1200" y1="0" x2="1070" y2="250" />
                  <line x1="1200" y1="0" x2="1160" y2="320" />
                </g>
                <g stroke="rgba(255,255,255,0.45)" stroke-width="1" fill="none">
                  <line x1="1200" y1="0" x2="940" y2="55" />
                  <line x1="1200" y1="0" x2="985" y2="160" />
                  <line x1="1200" y1="0" x2="1070" y2="250" />
                  <line x1="1200" y1="0" x2="1160" y2="320" />
                </g>
                <!-- Top-Right Drooping Concentric Arcs -->
                <g stroke="#000000" stroke-width="3.5" stroke-opacity="0.95" fill="none">
                  <path d="M 1130,0 Q 1145,26 1158,60 Q 1172,82 1200,95" />
                  <path d="M 1050,0 Q 1075,58 1105,125 Q 1142,175 1200,195" />
                  <path d="M 955,0 Q 995,90 1045,190 Q 1110,270 1200,315" />
                  <path d="M 850,0 Q 905,130 975,275 Q 1070,385 1200,445" />
                </g>
                <g stroke="url(#webSheen)" stroke-width="1.3" fill="none">
                  <path d="M 1130,0 Q 1145,26 1158,60 Q 1172,82 1200,95" />
                  <path d="M 1050,0 Q 1075,58 1105,125 Q 1142,175 1200,195" />
                  <path d="M 955,0 Q 995,90 1045,190 Q 1110,270 1200,315" />
                  <path d="M 850,0 Q 905,130 975,275 Q 1070,385 1200,445" />
                </g>
              </g>

              <!-- LAYER 3: HANGING CATENARY SUSPENSION WEB STRINGS -->
              <g class="hanging-cables-group">
                <!-- Shadow base paths (pitch black cord) -->
                <g stroke="#000000" stroke-width="4.2" stroke-opacity="0.98" fill="none">
                  <path d="M 0,30 Q 310,225 600,195 T 1200,45" />
                  <path d="M 0,115 Q 380,335 745,290 T 1200,125" />
                  <path d="M 120,0 Q 455,490 840,430 T 1200,210" />
                  <path d="M 265,0 Q 610,635 1010,550 T 1200,335" />

                  <!-- Diagonal bracing filaments -->
                  <path d="M 300,220 Q 430,320 565,395" />
                  <path d="M 695,240 Q 805,360 935,420" />
                  <path d="M 215,145 Q 370,350 455,490" />
                  <path d="M 815,190 Q 910,335 1045,455" />
                  <path d="M 480,310 Q 600,445 730,515" />
                </g>

                <!-- Glossy wet white/chrome highlight spine -->
                <g stroke="url(#webSheen)" stroke-width="1.5" fill="none">
                  <path d="M 0,30 Q 310,225 600,195 T 1200,45" />
                  <path d="M 0,115 Q 380,335 745,290 T 1200,125" />
                  <path d="M 120,0 Q 455,490 840,430 T 1200,210" />
                  <path d="M 265,0 Q 610,635 1010,550 T 1200,335" />

                  <path d="M 300,220 Q 430,320 565,395" />
                  <path d="M 695,240 Q 805,360 935,420" />
                  <path d="M 215,145 Q 370,350 455,490" />
                  <path d="M 815,190 Q 910,335 1045,455" />
                  <path d="M 480,310 Q 600,445 730,515" />
                </g>
              </g>

              <!-- LAYER 4: DANGLING VERTICAL DRIP FILAMENTS & VENOM DROPLETS -->
              <g class="hanging-droplets-group">
                <g stroke="#000000" stroke-width="3" stroke-opacity="0.95" fill="none">
                  <line x1="290" y1="0" x2="290" y2="185" />
                  <line x1="430" y1="0" x2="430" y2="290" />
                  <line x1="575" y1="0" x2="575" y2="150" />
                  <line x1="710" y1="0" x2="710" y2="245" />
                  <line x1="850" y1="0" x2="850" y2="335" />
                  <line x1="995" y1="0" x2="995" y2="170" />
                  <line x1="600" y1="195" x2="600" y2="275" />
                  <line x1="745" y1="290" x2="745" y2="370" />
                  <line x1="840" y1="430" x2="840" y2="535" />
                </g>
                <g stroke="rgba(255,255,255,0.45)" stroke-width="1.1" fill="none">
                  <line x1="290" y1="0" x2="290" y2="185" />
                  <line x1="430" y1="0" x2="430" y2="290" />
                  <line x1="575" y1="0" x2="575" y2="150" />
                  <line x1="710" y1="0" x2="710" y2="245" />
                  <line x1="850" y1="0" x2="850" y2="335" />
                  <line x1="995" y1="0" x2="995" y2="170" />
                  <line x1="600" y1="195" x2="600" y2="275" />
                  <line x1="745" y1="290" x2="745" y2="370" />
                  <line x1="840" y1="430" x2="840" y2="535" />
                </g>

                <!-- Glossy Hanging Venom Pearls / Droplet Beads -->
                <g>
                  <circle cx="290" cy="188" r="5" fill="url(#dropletGrad)" stroke="#ffffff" stroke-width="0.9" />
                  <circle cx="430" cy="295" r="6.5" fill="url(#dropletGrad)" stroke="#ffffff" stroke-width="0.9" />
                  <circle cx="575" cy="153" r="4" fill="url(#dropletGrad)" stroke="#ffffff" stroke-width="0.8" />
                  <circle cx="710" cy="250" r="5.5" fill="url(#dropletGrad)" stroke="#ffffff" stroke-width="0.9" />
                  <circle cx="850" cy="341" r="7" fill="url(#dropletGrad)" stroke="#ffffff" stroke-width="0.9" />
                  <circle cx="995" cy="173" r="4.5" fill="url(#dropletGrad)" stroke="#ffffff" stroke-width="0.8" />
                  <circle cx="600" cy="279" r="6" fill="url(#dropletGrad)" stroke="#ffffff" stroke-width="0.9" />
                  <circle cx="745" cy="376" r="6.5" fill="url(#dropletGrad)" stroke="#ffffff" stroke-width="0.9" />
                  <circle cx="840" cy="542" r="7.5" fill="url(#dropletGrad)" stroke="#ffffff" stroke-width="1" />
                </g>
              </g>
            </svg>
          </div>

          <!-- Modal Header Bar -->
          <div class="modal-header-bar flex items-center justify-between px-6 py-5 border-b border-white/10 bg-black/60 relative z-10 backdrop-blur-md">
            <div class="flex items-center gap-3">
              <span class="w-2.5 h-2.5 rounded-full bg-white shadow-[0_0_10px_white]"></span>
              <span class="font-mono text-sm tracking-wider uppercase text-neutral-200 font-semibold">
                {{ 
                  activeModal === 'console' ? 'Simulation Console' :
                  activeModal === 'workflow' ? 'Swarm Workflow Architecture' :
                  activeModal === 'history' ? 'Simulation History Database' :
                  'System Status & Architecture'
                }}
              </span>
            </div>
            <button 
              @click="activeModal = null"
              class="modal-close-btn w-8 h-8 rounded-full flex items-center justify-center text-lg transition-all cursor-pointer"
              aria-label="Close"
            >
              &times;
            </button>
          </div>

          <!-- Modal Scrollable Body -->
          <div class="relative z-10 overflow-y-auto p-6 sm:p-8 space-y-6">
            <!-- Modal Content 1: Simulation Console -->
            <div v-if="activeModal === 'console'" class="console-box">
              <!-- Upload Area -->
              <div class="console-section">
                <div class="console-header">
                  <span class="console-label">{{ $t('home.realitySeed') }}</span>
                  <span class="console-meta">{{ $t('home.supportedFormats') }}</span>
                </div>
                
                <div 
                  class="upload-zone"
                  :class="{ 'drag-over': isDragOver, 'has-files': files.length > 0 }"
                  @dragover.prevent="handleDragOver"
                  @dragleave.prevent="handleDragLeave"
                  @drop.prevent="handleDrop"
                  @click="triggerFileInput"
                >
                  <input
                    ref="fileInput"
                    type="file"
                    multiple
                    accept=".pdf,.md,.txt"
                    @change="handleFileSelect"
                    style="display: none"
                    :disabled="loading"
                  />
                  
                  <div v-if="files.length === 0" class="upload-placeholder">
                    <div class="upload-icon">&uarr;</div>
                    <div class="upload-title">{{ $t('home.dragToUpload') }}</div>
                    <div class="upload-hint">{{ $t('home.orBrowse') }}</div>
                  </div>
                  
                  <div v-else class="file-list">
                    <div v-for="(file, index) in files" :key="index" class="file-item">
                      <span class="file-icon">&#128196;</span>
                      <span class="file-name">{{ file.name }}</span>
                      <button @click.stop="removeFile(index)" class="remove-btn">&times;</button>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Divider -->
              <div class="console-divider">
                <span>{{ $t('home.inputParams') }}</span>
              </div>

              <!-- Input Area -->
              <div class="console-section">
                <div class="console-header">
                  <span class="console-label">{{ $t('home.simulationPrompt') }}</span>
                </div>
                <div class="input-wrapper">
                  <textarea
                    v-model="formData.simulationRequirement"
                    class="code-input"
                    :placeholder="$t('home.promptPlaceholder')"
                    rows="5"
                    :disabled="loading"
                  ></textarea>
                  <div class="model-badge">{{ $t('home.engineBadge') }}</div>
                </div>
              </div>

              <!-- Start Button -->
              <div class="console-section btn-section flex flex-col gap-3">
                <button 
                  class="start-engine-btn"
                  @click="startSimulation"
                  :disabled="!canSubmit || loading"
                >
                  <span v-if="!loading">{{ $t('home.startEngine') }}</span>
                  <span v-else>{{ $t('home.initializing') }}</span>
                  <span class="btn-arrow">&rarr;</span>
                </button>

                <button 
                  v-if="!files.length"
                  type="button"
                  class="quick-demo-btn"
                  @click="quickDemoSimulation"
                >
                  <span>⚡ Quick Demo: Launch Venom Reality Seed</span>
                </button>
              </div>
            </div>

            <!-- Modal Content 2: Workflow Sequence -->
            <div v-if="activeModal === 'workflow'" class="steps-container">
              <div class="steps-header">
                <span class="diamond-icon">&#9671;</span> {{ $t('home.workflowSequence') }}
              </div>
              <div class="workflow-list">
                <div class="workflow-item">
                  <span class="step-num">01</span>
                  <div class="step-info">
                    <div class="step-title">{{ $t('home.step01Title') }}</div>
                    <div class="step-desc">{{ $t('home.step01Desc') }}</div>
                  </div>
                </div>
                <div class="workflow-item">
                  <span class="step-num">02</span>
                  <div class="step-info">
                    <div class="step-title">{{ $t('home.step02Title') }}</div>
                    <div class="step-desc">{{ $t('home.step02Desc') }}</div>
                  </div>
                </div>
                <div class="workflow-item">
                  <span class="step-num">03</span>
                  <div class="step-info">
                    <div class="step-title">{{ $t('home.step03Title') }}</div>
                    <div class="step-desc">{{ $t('home.step03Desc') }}</div>
                  </div>
                </div>
                <div class="workflow-item">
                  <span class="step-num">04</span>
                  <div class="step-info">
                    <div class="step-title">{{ $t('home.step04Title') }}</div>
                    <div class="step-desc">{{ $t('home.step04Desc') }}</div>
                  </div>
                </div>
                <div class="workflow-item">
                  <span class="step-num">05</span>
                  <div class="step-info">
                    <div class="step-title">{{ $t('home.step05Title') }}</div>
                    <div class="step-desc">{{ $t('home.step05Desc') }}</div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Modal Content 3: History Database -->
            <div v-if="activeModal === 'history'" class="pt-2">
              <HistoryDatabase />
            </div>

            <!-- Modal Content 4: System Architecture & Status -->
            <div v-if="activeModal === 'status'" class="space-y-6">
              <div class="panel-header">
                <span class="status-dot">&#9632;</span> {{ $t('home.systemStatus') }}
              </div>
              <h2 class="section-title">{{ $t('home.systemReady') }}</h2>
              <p class="section-desc">
                {{ $t('home.systemReadyDesc') }}
              </p>
              
              <!-- Data Metrics Card -->
              <div class="metrics-row">
                <div class="metric-card">
                  <div class="metric-value">{{ $t('home.metricLowCost') }}</div>
                  <div class="metric-label">{{ $t('home.metricLowCostDesc') }}</div>
                </div>
                <div class="metric-card">
                  <div class="metric-value">{{ $t('home.metricHighAvail') }}</div>
                  <div class="metric-label">{{ $t('home.metricHighAvailDesc') }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import HistoryDatabase from '../components/HistoryDatabase.vue'
import VenomIntro from '../components/VenomIntro.vue'

const router = useRouter()
const route = useRoute()

// Intro opening state (appears as soon as page is opened on /)
const showIntro = ref(route.path === '/' || route.query.intro === '1')

const handleEnterHomepage = () => {
  showIntro.value = false
  if (route.path !== '/home' || route.query.intro) {
    router.push({ path: '/home', query: {} })
  }
  startHeroAnimations()
}

const handleLogoClick = () => {
  if (activeModal.value) {
    activeModal.value = null
  } else {
    heroAnimationsStarted.value = false
    typewriterDone.value = false
    displayedText.value = ''
    showPills.value = false
    router.push('/')
  }
}

watch(() => [route.path, route.query.intro], ([newPath, introQuery]) => {
  if (newPath === '/' || introQuery === '1') {
    showIntro.value = true
  } else if (newPath === '/home') {
    showIntro.value = false
    startHeroAnimations()
  }
})

// UI state
const activeModal = ref(null)
const showPills = ref(false)

// Interactive Head Rotation Canvas Engine (0-latency preloaded WebP sequence)
const canvasRef = ref(null)
const TOTAL_FRAMES = 97
const frameImages = []
let loadedFrames = 0
let currentFrame = 48
let targetFrame = 48
let animId = null
let hasDrawnInitial = false

// Typewriter state
const fullTypewriterText = 'Auto-Generate Parallel World. Million-Scale Agents. God\'s-Eye View. Optimal Solution in Complex Dynamics.'
const displayedText = ref('')
const typewriterDone = ref(false)

const drawFrame = (index) => {
  const canvas = canvasRef.value
  if (!canvas) return
  const ctx = canvas.getContext('2d', { alpha: false })
  if (!ctx) return

  const idx = Math.max(0, Math.min(TOTAL_FRAMES - 1, Math.round(index)))
  const img = frameImages[idx]
  if (img && img.complete && img.naturalWidth > 0) {
    ctx.drawImage(img, 0, 0, canvas.width, canvas.height)
  }
}

const preloadFrames = () => {
  for (let i = 0; i < TOTAL_FRAMES; i++) {
    const img = new Image()
    img.src = `/frames/f_${String(i).padStart(3, '0')}.webp`
    img.onload = () => {
      loadedFrames++
      if ((i === Math.round(currentFrame) || !hasDrawnInitial) && canvasRef.value) {
        drawFrame(i)
        hasDrawnInitial = true
      }
    }
    frameImages.push(img)
  }
}

const startRenderLoop = () => {
  const render = () => {
    const diff = targetFrame - currentFrame
    if (Math.abs(diff) > 0.02) {
      const factor = Math.abs(diff) > 15 ? 0.45 : 0.28
      currentFrame += diff * factor
      drawFrame(currentFrame)
    }
    animId = requestAnimationFrame(render)
  }
  animId = requestAnimationFrame(render)
}

const handleMouseMove = (e) => {
  if (showIntro.value) return
  const ratio = Math.max(0, Math.min(1, e.clientX / window.innerWidth))
  targetFrame = ratio * (TOTAL_FRAMES - 1)
}

const handleTouchMove = (e) => {
  if (showIntro.value) return
  if (e.touches && e.touches.length > 0) {
    const ratio = Math.max(0, Math.min(1, e.touches[0].clientX / window.innerWidth))
    targetFrame = ratio * (TOTAL_FRAMES - 1)
  }
}

const handleMouseLeave = () => {
  // Preserve current position
}

// Form and file upload logic
const formData = ref({
  simulationRequirement: ''
})
const files = ref([])
const loading = ref(false)
const error = ref('')
const isDragOver = ref(false)
const fileInput = ref(null)

const canSubmit = computed(() => {
  return formData.value.simulationRequirement.trim() !== '' && files.value.length > 0
})

const triggerFileInput = () => {
  if (!loading.value) {
    fileInput.value?.click()
  }
}

const handleFileSelect = (event) => {
  const selectedFiles = Array.from(event.target.files)
  addFiles(selectedFiles)
}

const handleDragOver = (e) => {
  if (!loading.value) {
    isDragOver.value = true
  }
}

const handleDragLeave = (e) => {
  isDragOver.value = false
}

const handleDrop = (e) => {
  isDragOver.value = false
  if (loading.value) return
  const droppedFiles = Array.from(e.dataTransfer.files)
  addFiles(droppedFiles)
}

const addFiles = (newFiles) => {
  const validFiles = newFiles.filter(file => {
    const ext = file.name.split('.').pop().toLowerCase()
    return ['pdf', 'md', 'txt'].includes(ext)
  })
  files.value.push(...validFiles)
}

const removeFile = (index) => {
  files.value.splice(index, 1)
}

const quickDemoSimulation = () => {
  formData.value.simulationRequirement = 'Simulate autonomous swarm agent reaction to anomalous bio-tech volatility and divergent sentiment trajectories.'
  const mockBlob = new Blob(['# Venom Reality Blueprint\n\nBio-tech market volatility and swarm multi-agent consensus dynamics.'], { type: 'text/markdown' })
  const mockFile = new File([mockBlob], 'venom_reality_seed.md', { type: 'text/markdown' })
  files.value = [mockFile]
  startSimulation()
}

const startSimulation = () => {
  if (!canSubmit.value || loading.value) return
  
  import('../store/pendingUpload.js').then(({ setPendingUpload }) => {
    setPendingUpload(files.value, formData.value.simulationRequirement)
    router.push({
      name: 'Process',
      params: { projectId: 'new' }
    })
  })
}

// Hero section text animations (trigger when homepage is entered)
let typewriterTimer = null
let typewriterInterval = null
const heroAnimationsStarted = ref(false)

const startHeroAnimations = () => {
  if (heroAnimationsStarted.value) return
  heroAnimationsStarted.value = true

  setTimeout(() => {
    showPills.value = true
  }, 350)

  if (typewriterTimer) clearTimeout(typewriterTimer)
  if (typewriterInterval) clearInterval(typewriterInterval)

  typewriterTimer = setTimeout(() => {
    let currentIndex = 0
    typewriterInterval = setInterval(() => {
      if (currentIndex < fullTypewriterText.length) {
        displayedText.value = fullTypewriterText.slice(0, currentIndex + 1)
        currentIndex++
      } else {
        typewriterDone.value = true
        if (typewriterInterval) clearInterval(typewriterInterval)
      }
    }, 35)
  }, 450)
}

// Lifecycle hooks
onMounted(() => {
  // Initialize canvas frame sequence & render loop
  preloadFrames()
  startRenderLoop()

  // Attach mouse and touch scrub listeners to window
  window.addEventListener('mousemove', handleMouseMove, { passive: true })
  window.addEventListener('touchmove', handleTouchMove, { passive: true })
  window.addEventListener('mouseleave', handleMouseLeave)

  // Start hero animations immediately if not showing intro
  if (!showIntro.value) {
    startHeroAnimations()
  }

  onUnmounted(() => {
    if (typewriterTimer) clearTimeout(typewriterTimer)
    if (typewriterInterval) clearInterval(typewriterInterval)
    if (animId) cancelAnimationFrame(animId)
    window.removeEventListener('mousemove', handleMouseMove)
    window.removeEventListener('touchmove', handleTouchMove)
    window.removeEventListener('mouseleave', handleMouseLeave)
  })
})
</script>

<style scoped>
:root {
  --black: #000000;
  --white: #FFFFFF;
  --accent: #171717;
  --gray-light: #121212;
  --gray-text: #a3a3a3;
  --border: rgba(255, 255, 255, 0.12);
  --font-mono: 'JetBrains Mono', monospace;
  --font-sans: 'Space Grotesk', 'Noto Sans SC', system-ui, sans-serif;
}

.home-container {
  position: fixed;
  inset: 0;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  background: radial-gradient(circle at 45% 42%, #0e0e0e 0%, #050505 55%, #000000 100%);
  color: #f5f5f5;
}

/* --- Venom Symbiote Badge --- */
.venom-badge-wrap {
  display: flex;
  align-items: center;
}

.venom-symbiote-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 16px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.12);
  font-family: var(--font-mono);
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.14em;
  color: #e2e8f0;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.12);
}

.symbiote-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #ffffff;
  box-shadow: 0 0 10px #ffffff, 0 0 18px rgba(255, 255, 255, 0.85);
  animation: symbiote-pulse 2s ease-in-out infinite;
}

@keyframes symbiote-pulse {
  0%, 100% { opacity: 0.5; transform: scale(0.9); }
  50% { opacity: 1; transform: scale(1.25); }
}

/* --- Bold Unique Hero Highlight Line --- */
.hero-highlight-wrap {
  position: relative;
  user-select: none;
}

.hero-highlight-title {
  font-family: var(--font-display, 'Syne', 'ClashDisplay', sans-serif);
  font-size: clamp(34px, 5.4vw, 64px);
  font-weight: 800;
  line-height: 1.05;
  letter-spacing: -0.038em;
  display: flex;
  flex-direction: column;
  gap: 0.08em;
  margin: 0;
}

.hero-text-white {
  color: #ffffff;
  text-shadow: 0 0 35px rgba(0, 0, 0, 0.95), 0 2px 4px rgba(0, 0, 0, 0.9);
}

.hero-text-venom-chrome {
  background: linear-gradient(
    135deg,
    #52525b 0%,
    #a1a1aa 16%,
    #f4f4f5 34%,
    #ffffff 50%,
    #e4e4e7 66%,
    #71717a 84%,
    #3f3f46 100%
  );
  background-size: 220% auto;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  animation: silver-shimmer 7s cubic-bezier(0.4, 0, 0.2, 1) infinite;
  filter: drop-shadow(0 0 25px rgba(255, 255, 255, 0.28)) drop-shadow(0 2px 14px rgba(0, 0, 0, 0.9));
  display: inline-block;
}

@keyframes silver-shimmer {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}

/* --- Signature Venom Symbiote Action Buttons --- */
.venom-pill-btn-primary {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: clamp(14px, 1.8vw, 17px) clamp(28px, 3.5vw, 42px);
  border-radius: 999px;
  border: none;
  outline: none;
  cursor: pointer;
  background:
    radial-gradient(120% 95% at 50% 12%, rgba(255, 255, 255, 0.42) 0%, rgba(255, 255, 255, 0.08) 34%, rgba(0, 0, 0, 0) 60%),
    linear-gradient(180deg, #222222 0%, #0d0d0d 54%, #000000 100%);
  color: #ffffff;
  font-size: clamp(15px, 1.8vw, 18px);
  font-weight: 600;
  letter-spacing: -0.01em;
  white-space: nowrap;
  box-shadow:
    0 22px 38px -10px rgba(0, 0, 0, 0.85),
    0 10px 18px -4px rgba(0, 0, 0, 0.6),
    0 0 22px rgba(255, 255, 255, 0.12),
    inset 0 2px 3px rgba(255, 255, 255, 0.45),
    inset 0 -3px 6px rgba(255, 255, 255, 0.14),
    inset 0 0 16px rgba(0, 0, 0, 0.95);
  transform-style: preserve-3d;
  transition: transform 0.2s ease, box-shadow 0.25s ease;
  user-select: none;
  touch-action: manipulation;
}

.venom-pill-btn-primary::before {
  content: "";
  position: absolute;
  top: 4px;
  left: 12%;
  right: 12%;
  height: 38%;
  border-radius: 999px;
  background: linear-gradient(
    180deg,
    rgba(255, 255, 255, 0.45) 0%,
    rgba(255, 255, 255, 0.08) 65%,
    rgba(255, 255, 255, 0) 100%
  );
  pointer-events: none;
  filter: blur(0.5px);
}

.venom-pill-btn-primary::after {
  content: "";
  position: absolute;
  bottom: 4px;
  left: 18%;
  right: 18%;
  height: 20%;
  border-radius: 999px;
  background: linear-gradient(
    0deg,
    rgba(255, 255, 255, 0.22) 0%,
    rgba(255, 255, 255, 0) 100%
  );
  pointer-events: none;
  filter: blur(0.8px);
}

.venom-pill-btn-primary:hover {
  transform: translateY(-2px) scale(1.02);
  box-shadow:
    0 26px 48px -10px rgba(0, 0, 0, 0.92),
    0 14px 24px -4px rgba(0, 0, 0, 0.65),
    0 0 30px rgba(255, 255, 255, 0.25),
    inset 0 2px 4px rgba(255, 255, 255, 0.55),
    inset 0 -3px 6px rgba(255, 255, 255, 0.18),
    inset 0 0 20px rgba(0, 0, 0, 0.95);
}

.venom-pill-btn-primary:active {
  transform: translateY(0) scale(0.98);
}

/* Secondary Smoked Obsidian Glass Pills */
.venom-pill-btn-secondary {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: clamp(13px, 1.7vw, 16px) clamp(22px, 2.8vw, 32px);
  border-radius: 999px;
  background: rgba(12, 12, 12, 0.75);
  border: 1px solid rgba(255, 255, 255, 0.16);
  color: #e5e5e5;
  font-size: clamp(14px, 1.7vw, 17px);
  font-weight: 500;
  letter-spacing: -0.01em;
  white-space: nowrap;
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  box-shadow:
    0 10px 25px -6px rgba(0, 0, 0, 0.8),
    inset 0 1px 1px rgba(255, 255, 255, 0.14);
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  user-select: none;
  touch-action: manipulation;
}

.venom-pill-btn-secondary:hover {
  background: rgba(24, 24, 24, 0.95);
  border-color: rgba(255, 255, 255, 0.4);
  color: #ffffff;
  transform: translateY(-2px);
  box-shadow:
    0 16px 32px -8px rgba(0, 0, 0, 0.9),
    0 0 20px rgba(255, 255, 255, 0.12),
    inset 0 1px 2px rgba(255, 255, 255, 0.25);
}

.venom-pill-btn-secondary:active {
  transform: translateY(0) scale(0.98);
}

/* Intro dissolve animation */
.intro-dissolve-leave-active {
  transition: opacity 0.25s ease-out, transform 0.25s ease-out;
  pointer-events: none;
}
.intro-dissolve-leave-to {
  opacity: 0;
  transform: scale(1.04);
}

/* Modal fade animation */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: all 0.25s ease-out;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
  transform: scale(0.97);
}

/* ===== Pitch-Black Obsidian Symbiote Modal Styling with Venom Web Theme ===== */
.modal-dialog {
  background: radial-gradient(circle at 50% 0%, #111111 0%, #050505 50%, #000000 100%) !important;
  border: 1px solid rgba(255, 255, 255, 0.14) !important;
  border-radius: 24px !important;
  box-shadow:
    0 40px 100px -20px rgba(0, 0, 0, 1),
    0 0 60px rgba(0, 0, 0, 0.95),
    inset 0 1px 0 rgba(255, 255, 255, 0.18) !important;
  color: #f5f5f5 !important;
}

.modal-header-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(0, 0, 0, 0.65);
  backdrop-filter: blur(12px);
  position: relative;
  z-index: 10;
}

.modal-close-btn {
  width: 32px;
  height: 32px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.14);
  color: #e5e5e5;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  line-height: 1;
  transition: all 0.2s ease;
  cursor: pointer;
}

.modal-close-btn:hover {
  background: #ffffff;
  color: #000000;
  border-color: #ffffff;
  box-shadow: 0 0 15px rgba(255, 255, 255, 0.7);
}

/* Venom Web and Crack animations */
.modal-venom-web-bg {
  opacity: 0.92;
}

.hanging-cables-group {
  animation: web-breathe 9s ease-in-out infinite alternate;
  transform-origin: 50% 0%;
}

.hanging-droplets-group {
  animation: web-drip-sway 7s ease-in-out infinite alternate;
  transform-origin: 50% 0%;
}

.fissure-cracks-group {
  animation: crack-pulse 5s ease-in-out infinite alternate;
}

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
  0%, 100% { opacity: 0.85; filter: drop-shadow(0 0 2px rgba(255, 255, 255, 0.1)); }
  50% { opacity: 1; filter: drop-shadow(0 0 8px rgba(255, 255, 255, 0.28)); }
}

/* Left panel / System Status */
.panel-header {
  font-family: var(--font-mono);
  font-size: 0.8rem;
  color: #a3a3a3;
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 20px;
}

.status-dot {
  color: #ffffff;
  text-shadow: 0 0 8px #ffffff;
  font-size: 0.8rem;
}

.section-title {
  font-size: 2rem;
  font-weight: 600;
  margin: 0 0 15px 0;
  color: #ffffff;
}

.section-desc {
  color: #a3a3a3;
  margin-bottom: 25px;
  line-height: 1.6;
}

.metrics-row {
  display: flex;
  gap: 20px;
  margin-bottom: 15px;
}

.metric-card {
  border: 1px solid rgba(255, 255, 255, 0.12);
  padding: 20px 30px;
  min-width: 150px;
  background: rgba(10, 10, 10, 0.72);
  backdrop-filter: blur(8px);
  border-radius: 14px;
}

.metric-value {
  font-family: var(--font-mono);
  font-size: 1.8rem;
  font-weight: 600;
  margin-bottom: 5px;
  color: #ffffff;
  text-shadow: 0 0 15px rgba(255, 255, 255, 0.25);
}

.metric-label {
  font-size: 0.85rem;
  color: #737373;
}

/* Workflow step items */
.steps-container {
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 26px;
  position: relative;
  z-index: 10;
  background: rgba(8, 8, 8, 0.65);
  backdrop-filter: blur(10px);
  border-radius: 18px;
}

.steps-header {
  font-family: var(--font-mono);
  font-size: 0.8rem;
  color: #a3a3a3;
  margin-bottom: 22px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.diamond-icon {
  font-size: 1.2rem;
  line-height: 1;
  color: #ffffff;
}

.workflow-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.workflow-item {
  display: flex;
  align-items: flex-start;
  gap: 20px;
  background: rgba(12, 12, 12, 0.7);
  backdrop-filter: blur(6px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 14px;
  padding: 16px 20px;
  transition: all 0.25s ease;
}

.workflow-item:hover {
  border-color: rgba(255, 255, 255, 0.35);
  background: rgba(22, 22, 22, 0.88);
  transform: translateX(4px);
}

.step-num {
  font-family: var(--font-mono);
  font-weight: 700;
  color: #737373;
  font-size: 1.1rem;
}

.step-info {
  flex: 1;
}

.step-title {
  font-weight: 600;
  font-size: 1rem;
  margin-bottom: 4px;
  color: #ffffff;
}

.step-desc {
  font-size: 0.85rem;
  color: #a3a3a3;
  line-height: 1.5;
}

/* Console Box */
.console-box {
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 12px;
  background: rgba(8, 8, 8, 0.65);
  backdrop-filter: blur(10px);
  border-radius: 18px;
  position: relative;
  z-index: 10;
}

.console-section {
  padding: 18px;
}

.console-section.btn-section {
  padding-top: 0;
}

.console-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 14px;
  font-family: var(--font-mono);
  font-size: 0.75rem;
  color: #a3a3a3;
}

.console-label {
  color: #f5f5f5;
  font-weight: 600;
}

.console-meta {
  color: #737373;
}

.upload-zone {
  border: 1px dashed rgba(255, 255, 255, 0.2);
  height: 180px;
  overflow-y: auto;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background: rgba(10, 10, 10, 0.65);
  backdrop-filter: blur(6px);
  border-radius: 14px;
}

.upload-zone.has-files {
  align-items: flex-start;
}

.upload-zone:hover, .upload-zone.drag-over {
  background: rgba(20, 20, 20, 0.85);
  border-color: rgba(255, 255, 255, 0.5);
  box-shadow: 0 0 30px rgba(255, 255, 255, 0.08), inset 0 0 20px rgba(255, 255, 255, 0.04);
}

.upload-placeholder {
  text-align: center;
}

.upload-icon {
  width: 44px;
  height: 44px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  background: rgba(255, 255, 255, 0.04);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 12px;
  color: #ffffff;
  font-size: 1.2rem;
  box-shadow: 0 0 15px rgba(255, 255, 255, 0.1);
}

.upload-title {
  font-weight: 600;
  font-size: 0.95rem;
  margin-bottom: 4px;
  color: #ffffff;
}

.upload-hint {
  font-family: var(--font-mono);
  font-size: 0.75rem;
  color: #a3a3a3;
}

.file-list {
  width: 100%;
  padding: 15px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.file-item {
  display: flex;
  align-items: center;
  background: rgba(16, 16, 16, 0.85);
  padding: 10px 14px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 8px;
  font-family: var(--font-mono);
  font-size: 0.85rem;
  color: #f5f5f5;
}

.file-name {
  flex: 1;
  margin: 0 10px;
}

.remove-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.2rem;
  color: #a3a3a3;
  transition: color 0.2s;
}

.remove-btn:hover {
  color: #ffffff;
  text-shadow: 0 0 8px #ffffff;
}

.console-divider {
  display: flex;
  align-items: center;
  margin: 10px 0;
}

.console-divider::before,
.console-divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: rgba(255, 255, 255, 0.08);
}

.console-divider span {
  padding: 0 15px;
  font-family: var(--font-mono);
  font-size: 0.7rem;
  color: #737373;
  letter-spacing: 1px;
}

.input-wrapper {
  position: relative;
  border: 1px solid rgba(255, 255, 255, 0.14);
  background: rgba(10, 10, 10, 0.75);
  backdrop-filter: blur(8px);
  border-radius: 14px;
  transition: all 0.3s ease;
}

.input-wrapper:focus-within {
  border-color: rgba(255, 255, 255, 0.45);
  box-shadow: 0 0 25px rgba(255, 255, 255, 0.08);
}

.code-input {
  width: 100%;
  border: none;
  background: transparent;
  padding: 20px;
  font-family: var(--font-mono);
  font-size: 0.9rem;
  line-height: 1.6;
  resize: vertical;
  outline: none;
  min-height: 130px;
  color: #f5f5f5;
}

.code-input::placeholder {
  color: rgba(163, 163, 163, 0.5);
}

.model-badge {
  position: absolute;
  bottom: 12px;
  right: 15px;
  font-family: var(--font-mono);
  font-size: 0.7rem;
  color: #a3a3a3;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 6px;
  padding: 3px 8px;
}

.start-engine-btn {
  width: 100%;
  background:
    radial-gradient(120% 95% at 50% 12%, rgba(255, 255, 255, 0.38) 0%, rgba(255, 255, 255, 0.07) 34%, rgba(0, 0, 0, 0) 60%),
    linear-gradient(180deg, #222222 0%, #0d0d0d 54%, #000000 100%) !important;
  color: #ffffff !important;
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  border-radius: 12px !important;
  padding: 18px;
  font-family: var(--font-mono);
  font-weight: 700;
  font-size: 1.1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  transition: all 0.3s ease;
  letter-spacing: 1px;
  position: relative;
  overflow: hidden;
  box-shadow:
    0 16px 32px -8px rgba(0, 0, 0, 0.95),
    inset 0 1px 2px rgba(255, 255, 255, 0.35);
}

.start-engine-btn:not(:disabled) {
  animation: pulse-border 2.5s infinite;
}

.start-engine-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow:
    0 22px 40px -8px rgba(0, 0, 0, 1),
    0 0 25px rgba(255, 255, 255, 0.2),
    inset 0 1px 2px rgba(255, 255, 255, 0.45);
}

.start-engine-btn:disabled {
  background: rgba(255, 255, 255, 0.05) !important;
  color: #737373;
  cursor: not-allowed;
  transform: none;
  border: 1px solid rgba(255, 255, 255, 0.08) !important;
  box-shadow: none;
}

@keyframes pulse-border {
  0% { box-shadow: 0 0 0 0 rgba(255, 255, 255, 0.15); }
  70% { box-shadow: 0 0 0 8px rgba(255, 255, 255, 0); }
  100% { box-shadow: 0 0 0 0 rgba(255, 255, 255, 0); }
}

.quick-demo-btn {
  background: rgba(255, 87, 34, 0.12);
  border: 1px dashed rgba(255, 87, 34, 0.4);
  color: #ff7043;
  padding: 10px 18px;
  border-radius: 999px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.25s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.quick-demo-btn:hover {
  background: rgba(255, 87, 34, 0.22);
  border-color: #ff5722;
  color: #ffffff;
  box-shadow: 0 0 16px rgba(255, 87, 34, 0.4);
  transform: translateY(-1px);
}

</style>
