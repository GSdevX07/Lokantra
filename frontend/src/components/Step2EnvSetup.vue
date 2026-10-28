<template>
  <div class="env-setup-panel relative overflow-hidden">
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
        <!-- Horizontal grid lines across all card zones -->
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

        <!-- SPREADING FRACTURE CRACKS (running through Step cards) -->
        <g class="fissure-cracks-group">
          <g stroke="url(#fisGrad)" stroke-linecap="round" stroke-linejoin="bevel">
            <!-- Crack 1: Top-left down through cards -->
            <path d="M 0,40 L 90,95 L 140,80 L 210,175 L 270,230 L 350,265 L 430,360 L 390,440 L 460,520 L 520,610 L 490,700 L 570,810 L 630,920 L 720,1050 L 800,1110" stroke-width="2.2" fill="none" />
            <path d="M 140,80 L 190,35 L 250,20" stroke-width="1.3" fill="none" />
            <path d="M 270,230 L 330,205 L 400,210" stroke-width="1.3" fill="none" />
            <path d="M 430,360 L 490,410 L 530,475" stroke-width="1.4" fill="none" />
            <path d="M 520,610 L 580,570 L 640,560" stroke-width="1.3" fill="none" />
            <path d="M 570,810 L 640,830 L 700,790" stroke-width="1.4" fill="none" />
            <!-- Crack 2: Right edge through cards -->
            <path d="M 800,320 L 710,380 L 660,360 L 580,450 L 530,520 L 440,550 L 370,640 L 320,720 L 250,760 L 180,870 L 110,910 L 0,980" stroke-width="2" fill="none" />
            <path d="M 660,360 L 620,310 L 580,290" stroke-width="1.2" fill="none" />
            <path d="M 440,550 L 390,520 L 340,530" stroke-width="1.2" fill="none" />
            <path d="M 320,720 L 270,690 L 220,700" stroke-width="1.2" fill="none" />
          </g>
        </g>

        <!-- CORNER & EDGE SPIDERWEBS -->
        <g class="corner-webs-group">
          <!-- Top-Left Radial Web Spokes & Drooping Arcs -->
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

          <!-- Bottom-Left Radial Web Spokes & Arcs -->
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

        <!-- HANGING CATENARY SUSPENSION WEB STRINGS -->
        <g class="hanging-cables-group">
          <g stroke="url(#wbSheen)" stroke-width="2" fill="none">
            <path d="M 0,80 Q 400,240 800,90" />
            <path d="M 0,180 Q 420,380 800,190" />
            <path d="M 0,310 Q 380,510 800,320" />
            <path d="M 0,460 Q 440,680 800,470" />
            <path d="M 0,610 Q 400,810 800,620" />
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
      <!-- Step 01: Simulation Instance -->
      <div class="step-card" :class="{ 'active': phase === 0, 'completed': phase > 0 }">
        <div class="card-header">
          <div class="step-info">
            <span class="step-num">01</span>
            <span class="step-title">{{ $t('step2.simInstanceInit') }}</span>
          </div>
          <div class="step-status">
            <span v-if="phase > 0" class="badge success">{{ $t('common.completed') }}</span>
            <span v-else class="badge processing">{{ $t('step2.initializing') }}</span>
          </div>
        </div>
        
        <div class="card-content">
          <p class="api-note">POST /api/simulation/create</p>
          <p class="description">
            {{ $t('step2.simInstanceDesc') }}
          </p>

          <div v-if="simulationId" class="info-card">
            <div class="info-row">
              <span class="info-label">Project ID</span>
              <span class="info-value mono">{{ projectData?.project_id }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Graph ID</span>
              <span class="info-value mono">{{ projectData?.graph_id }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Simulation ID</span>
              <span class="info-value mono">{{ simulationId }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Task ID</span>
              <span class="info-value mono">{{ taskId || $t('step2.asyncTaskDone') }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Step 02: Generate Agent Profiles -->
      <div class="step-card" :class="{ 'active': phase === 1, 'completed': phase > 1 }">
        <div class="card-header">
          <div class="step-info">
            <span class="step-num">02</span>
            <span class="step-title">{{ $t('step2.generateAgentPersona') }}</span>
          </div>
          <div class="step-status">
            <span v-if="phase > 1" class="badge success">{{ $t('common.completed') }}</span>
            <span v-else-if="phase === 1" class="badge processing">{{ prepareProgress }}%</span>
            <span v-else class="badge pending">{{ $t('common.pending') }}</span>
          </div>
        </div>

        <div class="card-content">
          <p class="api-note">POST /api/simulation/prepare</p>
          <p class="description">
            {{ $t('step2.generateAgentPersonaDesc') }}
          </p>

          <!-- Profiles Stats -->
          <div v-if="profiles.length > 0" class="stats-grid">
            <div class="stat-card">
              <span class="stat-value">{{ profiles.length }}</span>
              <span class="stat-label">{{ $t('step2.currentAgentCount') }}</span>
            </div>
            <div class="stat-card">
              <span class="stat-value">{{ expectedTotal || '-' }}</span>
              <span class="stat-label">{{ $t('step2.expectedAgentTotal') }}</span>
            </div>
            <div class="stat-card">
              <span class="stat-value">{{ totalTopicsCount }}</span>
              <span class="stat-label">{{ $t('step2.relatedTopicsCount') }}</span>
            </div>
          </div>

          <!-- Profiles List Preview -->
          <div v-if="profiles.length > 0" class="profiles-preview">
            <div class="preview-header">
              <span class="preview-title">{{ $t('step2.generatedAgentPersonas') }}</span>
            </div>
            <div class="profiles-list">
              <div 
                v-for="(profile, idx) in profiles" 
                :key="idx" 
                class="profile-card"
                @click="selectProfile(profile)"
              >
                <div class="profile-header">
                  <span class="profile-realname">{{ profile.username || 'Unknown' }}</span>
                  <span class="profile-username">@{{ profile.name || `agent_${idx}` }}</span>
                </div>
                <div class="profile-meta">
                  <span class="profile-profession">{{ profile.profession || $t('step2.unknownProfession') }}</span>
                </div>
                <p class="profile-bio">{{ profile.bio || $t('step2.noBio') }}</p>
                <div v-if="profile.interested_topics?.length" class="profile-topics">
                  <span 
                    v-for="topic in profile.interested_topics.slice(0, 3)" 
                    :key="topic" 
                    class="topic-tag"
                  >{{ topic }}</span>
                  <span v-if="profile.interested_topics.length > 3" class="topic-more">
                    +{{ profile.interested_topics.length - 3 }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Step 03: Generate Dual-Platform Simulation Config -->
      <div class="step-card" :class="{ 'active': phase === 2, 'completed': phase > 2 }">
        <div class="card-header">
          <div class="step-info">
            <span class="step-num">03</span>
            <span class="step-title">{{ $t('step2.dualPlatformConfig') }}</span>
          </div>
          <div class="step-status">
            <span v-if="phase > 2" class="badge success">{{ $t('common.completed') }}</span>
            <span v-else-if="phase === 2" class="badge processing">{{ $t('step2.generating') }}</span>
            <span v-else class="badge pending">{{ $t('common.pending') }}</span>
          </div>
        </div>

        <div class="card-content">
          <p class="api-note">POST /api/simulation/prepare</p>
          <p class="description">
            {{ $t('step2.dualPlatformConfigDesc') }}
          </p>
          
          <!-- Config Preview -->
          <div v-if="simulationConfig" class="config-detail-panel">
            <!-- Time Configuration -->
            <div class="config-block">
              <div class="config-grid">
                <div class="config-item">
                  <span class="config-item-label">{{ $t('step2.simulationDuration') }}</span>
                  <span class="config-item-value">{{ simulationConfig.time_config?.total_simulation_hours || '-' }} {{ $t('common.hours') }}</span>
                </div>
                <div class="config-item">
                  <span class="config-item-label">{{ $t('step2.roundDuration') }}</span>
                  <span class="config-item-value">{{ simulationConfig.time_config?.minutes_per_round || '-' }} {{ $t('common.minutes') }}</span>
                </div>
                <div class="config-item">
                  <span class="config-item-label">{{ $t('step2.totalRounds') }}</span>
                  <span class="config-item-value">{{ Math.floor((simulationConfig.time_config?.total_simulation_hours * 60 / simulationConfig.time_config?.minutes_per_round)) || '-' }} {{ $t('common.rounds') }}</span>
                </div>
                <div class="config-item">
                  <span class="config-item-label">{{ $t('step2.activePerHour') }}</span>
                  <span class="config-item-value">{{ simulationConfig.time_config?.agents_per_hour_min }}-{{ simulationConfig.time_config?.agents_per_hour_max }}</span>
                </div>
              </div>
              <div class="time-periods">
                <div class="period-item">
                  <span class="period-label">{{ $t('step2.peakHours') }}</span>
                  <span class="period-hours">{{ simulationConfig.time_config?.peak_hours?.join(':00, ') }}:00</span>
                  <span class="period-multiplier">×{{ simulationConfig.time_config?.peak_activity_multiplier }}</span>
                </div>
                <div class="period-item">
                  <span class="period-label">{{ $t('step2.workHours') }}</span>
                  <span class="period-hours">{{ simulationConfig.time_config?.work_hours?.[0] }}:00-{{ simulationConfig.time_config?.work_hours?.slice(-1)[0] }}:00</span>
                  <span class="period-multiplier">×{{ simulationConfig.time_config?.work_activity_multiplier }}</span>
                </div>
                <div class="period-item">
                  <span class="period-label">{{ $t('step2.morningHours') }}</span>
                  <span class="period-hours">{{ simulationConfig.time_config?.morning_hours?.[0] }}:00-{{ simulationConfig.time_config?.morning_hours?.slice(-1)[0] }}:00</span>
                  <span class="period-multiplier">×{{ simulationConfig.time_config?.morning_activity_multiplier }}</span>
                </div>
                <div class="period-item">
                  <span class="period-label">{{ $t('step2.offPeakHours') }}</span>
                  <span class="period-hours">{{ simulationConfig.time_config?.off_peak_hours?.[0] }}:00-{{ simulationConfig.time_config?.off_peak_hours?.slice(-1)[0] }}:00</span>
                  <span class="period-multiplier">×{{ simulationConfig.time_config?.off_peak_activity_multiplier }}</span>
                </div>
              </div>
            </div>

            <!-- Agent Configuration -->
            <div class="config-block">
              <div class="config-block-header">
                <span class="config-block-title">{{ $t('step2.agentConfig') }}</span>
                <span class="config-block-badge">{{ simulationConfig.agent_configs?.length || 0 }} {{ $t('common.items') }}</span>
              </div>
              <div class="agents-cards">
                <div 
                  v-for="agent in simulationConfig.agent_configs" 
                  :key="agent.agent_id" 
                  class="agent-card"
                >
                  <!-- Card Header -->
                  <div class="agent-card-header">
                    <div class="agent-identity">
                      <span class="agent-id">Agent {{ agent.agent_id }}</span>
                      <span class="agent-name">{{ agent.entity_name }}</span>
                    </div>
                    <div class="agent-tags">
                      <span class="agent-type">{{ agent.entity_type }}</span>
                      <span class="agent-stance" :class="'stance-' + agent.stance">{{ agent.stance }}</span>
                    </div>
                  </div>
                  
                  <!-- Active Timeline -->
                  <div class="agent-timeline">
                    <span class="timeline-label">{{ $t('step2.activeTimePeriod') }}</span>
                    <div class="mini-timeline">
                      <div 
                        v-for="hour in 24" 
                        :key="hour - 1" 
                        class="timeline-hour"
                        :class="{ 'active': agent.active_hours?.includes(hour - 1) }"
                        :title="`${hour - 1}:00`"
                      ></div>
                    </div>
                    <div class="timeline-marks">
                      <span>0</span>
                      <span>6</span>
                      <span>12</span>
                      <span>18</span>
                      <span>24</span>
                    </div>
                  </div>

                  <!-- Behavior Parameters -->
                  <div class="agent-params">
                    <div class="param-group">
                      <div class="param-item">
                        <span class="param-label">{{ $t('step2.postsPerHour') }}</span>
                        <span class="param-value">{{ agent.posts_per_hour }}</span>
                      </div>
                      <div class="param-item">
                        <span class="param-label">{{ $t('step2.commentsPerHour') }}</span>
                        <span class="param-value">{{ agent.comments_per_hour }}</span>
                      </div>
                      <div class="param-item">
                        <span class="param-label">{{ $t('step2.responseDelay') }}</span>
                        <span class="param-value">{{ agent.response_delay_min }}-{{ agent.response_delay_max }}min</span>
                      </div>
                    </div>
                    <div class="param-group">
                      <div class="param-item">
                        <span class="param-label">{{ $t('step2.activityLevel') }}</span>
                        <span class="param-value with-bar">
                          <span class="mini-bar" :style="{ width: (agent.activity_level * 100) + '%' }"></span>
                          {{ (agent.activity_level * 100).toFixed(0) }}%
                        </span>
                      </div>
                      <div class="param-item">
                        <span class="param-label">{{ $t('step2.sentimentBias') }}</span>
                        <span class="param-value" :class="agent.sentiment_bias > 0 ? 'positive' : agent.sentiment_bias < 0 ? 'negative' : 'neutral'">
                          {{ agent.sentiment_bias > 0 ? '+' : '' }}{{ agent.sentiment_bias?.toFixed(1) }}
                        </span>
                      </div>
                      <div class="param-item">
                        <span class="param-label">{{ $t('step2.influenceWeight') }}</span>
                        <span class="param-value highlight">{{ agent.influence_weight?.toFixed(1) }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Platform Configuration -->
            <div class="config-block">
              <div class="config-block-header">
                <span class="config-block-title">{{ $t('step2.recommendAlgoConfig') }}</span>
              </div>
              <div class="platforms-grid">
                <div v-if="simulationConfig.twitter_config" class="platform-card">
                  <div class="platform-card-header">
                    <span class="platform-name">{{ $t('step2.platform1Name') }}</span>
                  </div>
                  <div class="platform-params">
                    <div class="param-row">
                      <span class="param-label">{{ $t('step2.recencyWeight') }}</span>
                      <span class="param-value">{{ simulationConfig.twitter_config.recency_weight }}</span>
                    </div>
                    <div class="param-row">
                      <span class="param-label">{{ $t('step2.popularityWeight') }}</span>
                      <span class="param-value">{{ simulationConfig.twitter_config.popularity_weight }}</span>
                    </div>
                    <div class="param-row">
                      <span class="param-label">{{ $t('step2.relevanceWeight') }}</span>
                      <span class="param-value">{{ simulationConfig.twitter_config.relevance_weight }}</span>
                    </div>
                    <div class="param-row">
                      <span class="param-label">{{ $t('step2.viralThreshold') }}</span>
                      <span class="param-value">{{ simulationConfig.twitter_config.viral_threshold }}</span>
                    </div>
                    <div class="param-row">
                      <span class="param-label">{{ $t('step2.echoChamberStrength') }}</span>
                      <span class="param-value">{{ simulationConfig.twitter_config.echo_chamber_strength }}</span>
                    </div>
                  </div>
                </div>
                <div v-if="simulationConfig.reddit_config" class="platform-card">
                  <div class="platform-card-header">
                    <span class="platform-name">{{ $t('step2.platform2Name') }}</span>
                  </div>
                  <div class="platform-params">
                    <div class="param-row">
                      <span class="param-label">{{ $t('step2.recencyWeight') }}</span>
                      <span class="param-value">{{ simulationConfig.reddit_config.recency_weight }}</span>
                    </div>
                    <div class="param-row">
                      <span class="param-label">{{ $t('step2.popularityWeight') }}</span>
                      <span class="param-value">{{ simulationConfig.reddit_config.popularity_weight }}</span>
                    </div>
                    <div class="param-row">
                      <span class="param-label">{{ $t('step2.relevanceWeight') }}</span>
                      <span class="param-value">{{ simulationConfig.reddit_config.relevance_weight }}</span>
                    </div>
                    <div class="param-row">
                      <span class="param-label">{{ $t('step2.viralThreshold') }}</span>
                      <span class="param-value">{{ simulationConfig.reddit_config.viral_threshold }}</span>
                    </div>
                    <div class="param-row">
                      <span class="param-label">{{ $t('step2.echoChamberStrength') }}</span>
                      <span class="param-value">{{ simulationConfig.reddit_config.echo_chamber_strength }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- LLM Configuration Reasoning -->
            <div v-if="simulationConfig.generation_reasoning" class="config-block">
              <div class="config-block-header">
                <span class="config-block-title">{{ $t('step2.llmConfigReasoning') }}</span>
              </div>
              <div class="reasoning-content">
                <div 
                  v-for="(reason, idx) in simulationConfig.generation_reasoning.split('|').slice(0, 2)" 
                  :key="idx" 
                  class="reasoning-item"
                >
                  <p class="reasoning-text">{{ reason.trim() }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Step 04: Initial Activation Orchestration -->
      <div class="step-card" :class="{ 'active': phase === 3, 'completed': phase > 3 }">
        <div class="card-header">
          <div class="step-info">
            <span class="step-num">04</span>
            <span class="step-title">{{ $t('step2.initialActivation') }}</span>
          </div>
          <div class="step-status">
            <span v-if="phase > 3" class="badge success">{{ $t('common.completed') }}</span>
            <span v-else-if="phase === 3" class="badge processing">{{ $t('step2.orchestrating') }}</span>
            <span v-else class="badge pending">{{ $t('common.pending') }}</span>
          </div>
        </div>

        <div class="card-content">
          <p class="api-note">POST /api/simulation/prepare</p>
          <p class="description">
            {{ $t('step2.initialActivationDesc') }}
          </p>

          <div v-if="simulationConfig?.event_config" class="orchestration-content">
            <!-- Narrative Direction -->
            <div class="narrative-box">
              <span class="box-label narrative-label">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="special-icon">
                  <path d="M12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2C6.47715 2 2 6.47715 2 12C2 17.5228 6.47715 22 12 22Z" stroke="url(#paint0_linear)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                  <path d="M16.24 7.76L14.12 14.12L7.76 16.24L9.88 9.88L16.24 7.76Z" fill="url(#paint0_linear)" stroke="url(#paint0_linear)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                  <defs>
                    <linearGradient id="paint0_linear" x1="2" y1="2" x2="22" y2="22" gradientUnits="userSpaceOnUse">
                      <stop stop-color="#ffffff"/>
                      <stop offset="1" stop-color="#71717a"/>
                    </linearGradient>
                  </defs>
                </svg>
                {{ $t('step2.narrativeDirection') }}
              </span>
              <p class="narrative-text">{{ simulationConfig.event_config.narrative_direction }}</p>
            </div>

            <!-- Trending Topics -->
            <div class="topics-section">
              <span class="box-label">{{ $t('step2.initialHotTopics') }}</span>
              <div class="hot-topics-grid">
                <span v-for="topic in simulationConfig.event_config.hot_topics" :key="topic" class="hot-topic-tag">
                  # {{ topic }}
                </span>
              </div>
            </div>

            <!-- Initial Post Feed -->
            <div class="initial-posts-section">
              <span class="box-label">{{ $t('step2.initialActivationSeq', { count: simulationConfig.event_config.initial_posts.length }) }}</span>
              <div class="posts-timeline">
                <div v-for="(post, idx) in simulationConfig.event_config.initial_posts" :key="idx" class="timeline-item">
                  <div class="timeline-marker"></div>
                  <div class="timeline-content">
                    <div class="post-header">
                      <span class="post-role">{{ post.poster_type }}</span>
                      <span class="post-agent-info">
                        <span class="post-id">Agent {{ post.poster_agent_id }}</span>
                        <span class="post-username">@{{ getAgentUsername(post.poster_agent_id) }}</span>
                      </span>
                    </div>
                    <p class="post-text">{{ post.content }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Step 05: Preparation Complete -->
      <div class="step-card" :class="{ 'active': phase === 4 }">
        <div class="card-header">
          <div class="step-info">
            <span class="step-num">05</span>
            <span class="step-title">{{ $t('step2.setupComplete') }}</span>
          </div>
          <div class="step-status">
            <span v-if="phase >= 4" class="badge processing">{{ $t('step1.inProgress') }}</span>
            <span v-else class="badge pending">{{ $t('common.pending') }}</span>
          </div>
        </div>

        <div class="card-content">
          <p class="api-note">POST /api/simulation/start</p>
          <p class="description">{{ $t('step2.setupCompleteDesc') }}</p>
          
          <!-- Simulation rounds configuration - only shown after config is generated and rounds calculated -->
          <div v-if="simulationConfig && autoGeneratedRounds" class="rounds-config-section">
            <div class="rounds-header">
              <div class="header-left">
                <span class="section-title">{{ $t('step2.roundsConfig') }}</span>
                <span class="section-desc">{{ $t('step2.roundsConfigDesc', { hours: simulationConfig?.time_config?.total_simulation_hours || '-', minutesPerRound: simulationConfig?.time_config?.minutes_per_round || '-' }) }}</span>
              </div>
              <label class="switch-control">
                <input type="checkbox" v-model="useCustomRounds">
                <span class="switch-track"></span>
                <span class="switch-label">{{ $t('step2.customToggle') }}</span>
              </label>
            </div>
            
            <Transition name="fade" mode="out-in">
              <div v-if="useCustomRounds" class="rounds-content custom" key="custom">
                <div class="slider-display">
                  <div class="slider-main-value">
                    <span class="val-num">{{ customMaxRounds }}</span>
                    <span class="val-unit">{{ $t('step2.roundsUnit') }}</span>
                  </div>
                  <div class="slider-meta-info">
                    <span>{{ $t('step2.estimatedDuration', { minutes: Math.round(customMaxRounds * 0.6) }) }}</span>
                  </div>
                </div>

                <div class="range-wrapper">
                  <input 
                    type="range" 
                    v-model.number="customMaxRounds" 
                    min="10" 
                    :max="autoGeneratedRounds"
                    step="5"
                    class="minimal-slider"
                    :style="{ '--percent': ((customMaxRounds - 10) / (autoGeneratedRounds - 10)) * 100 + '%' }"
                  />
                  <div class="range-marks">
                    <span>10</span>
                    <span 
                      class="mark-recommend" 
                      :class="{ active: customMaxRounds === 40 }"
                      @click="customMaxRounds = 40"
                      :style="{ position: 'absolute', left: `calc(${(40 - 10) / (autoGeneratedRounds - 10) * 100}% - 30px)` }"
                    >{{ $t('step2.recommendedRounds', { rounds: 40 }) }}</span>
                    <span>{{ autoGeneratedRounds }}</span>
                  </div>
                </div>
              </div>
              
              <div v-else class="rounds-content auto" key="auto">
                <div class="auto-info-card">
                  <div class="auto-value">
                    <span class="val-num">{{ autoGeneratedRounds }}</span>
                    <span class="val-unit">{{ $t('step2.roundsUnit') }}</span>
                  </div>
                  <div class="auto-content">
                    <div class="auto-meta-row">
                      <span class="duration-badge">
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                          <circle cx="12" cy="12" r="10"></circle>
                          <polyline points="12 6 12 12 16 14"></polyline>
                        </svg>
                        {{ $t('step2.estimatedDurationFull', { minutes: Math.round(autoGeneratedRounds * 0.6) }) }}
                      </span>
                    </div>
                    <div class="auto-desc">
                      <p class="highlight-tip" @click="useCustomRounds = true">{{ $t('step2.customTip') }} ➝</p>
                    </div>
                  </div>
                </div>
              </div>
            </Transition>
          </div>

          <div class="action-group dual">
            <button 
              class="action-btn secondary"
              @click="$emit('go-back')"
            >
              ← {{ $t('step2.backToGraphBuild') }}
            </button>
            <button 
              class="action-btn primary"
              :disabled="phase < 4"
              @click="handleStartSimulation"
            >
              {{ $t('step2.startDualWorldSim') }} ➝
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Profile Detail Modal -->
    <Transition name="modal">
      <div v-if="selectedProfile" class="profile-modal-overlay" @click.self="selectedProfile = null">
        <div class="profile-modal">
          <div class="modal-header">
          <div class="modal-header-info">
            <div class="modal-name-row">
              <span class="modal-realname">{{ selectedProfile.username }}</span>
              <span class="modal-username">@{{ selectedProfile.name }}</span>
            </div>
            <span class="modal-profession">{{ selectedProfile.profession }}</span>
          </div>
          <button class="close-btn" @click="selectedProfile = null">×</button>
        </div>
        
        <div class="modal-body">
          <!-- Basic Information -->
          <div class="modal-info-grid">
            <div class="info-item">
              <span class="info-label">{{ $t('step2.profileModalAge') }}</span>
              <span class="info-value">{{ selectedProfile.age || '-' }} {{ $t('step2.yearsOld') }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">{{ $t('step2.profileModalGender') }}</span>
              <span class="info-value">{{ { male: $t('step2.genderMale'), female: $t('step2.genderFemale'), other: $t('step2.genderOther') }[selectedProfile.gender] || selectedProfile.gender }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">{{ $t('step2.profileModalCountry') }}</span>
              <span class="info-value">{{ selectedProfile.country || '-' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">{{ $t('step2.profileModalMbti') }}</span>
              <span class="info-value mbti">{{ selectedProfile.mbti || '-' }}</span>
            </div>
          </div>

          <!-- Bio / Summary -->
          <div class="modal-section">
            <span class="section-label">{{ $t('step2.profileModalBio') }}</span>
            <p class="section-bio">{{ selectedProfile.bio || $t('step2.noBio') }}</p>
          </div>

          <!-- Followed Topics -->
          <div class="modal-section" v-if="selectedProfile.interested_topics?.length">
            <span class="section-label">{{ $t('step2.profileModalTopics') }}</span>
            <div class="topics-grid">
              <span 
                v-for="topic in selectedProfile.interested_topics" 
                :key="topic" 
                class="topic-item"
              >{{ topic }}</span>
            </div>
          </div>

          <!-- Detailed Persona -->
          <div class="modal-section" v-if="selectedProfile.persona">
            <span class="section-label">{{ $t('step2.profileModalPersona') }}</span>
            
            <!-- Persona Dimension Overview -->
            <div class="persona-dimensions">
              <div class="dimension-card">
                <span class="dim-title">{{ $t('step2.personaDimExperience') }}</span>
                <span class="dim-desc">{{ $t('step2.personaDimExperienceDesc') }}</span>
              </div>
              <div class="dimension-card">
                <span class="dim-title">{{ $t('step2.personaDimBehavior') }}</span>
                <span class="dim-desc">{{ $t('step2.personaDimBehaviorDesc') }}</span>
              </div>
              <div class="dimension-card">
                <span class="dim-title">{{ $t('step2.personaDimMemory') }}</span>
                <span class="dim-desc">{{ $t('step2.personaDimMemoryDesc') }}</span>
              </div>
              <div class="dimension-card">
                <span class="dim-title">{{ $t('step2.personaDimSocial') }}</span>
                <span class="dim-desc">{{ $t('step2.personaDimSocialDesc') }}</span>
              </div>
            </div>

            <div class="persona-content">
              <p class="section-persona">{{ selectedProfile.persona }}</p>
            </div>
          </div>
        </div>
      </div>
      </div>
    </Transition>

    <!-- Floating Windows Terminal Component -->
    <FloatingTerminal
      title="SYSTEM DASHBOARD"
      :sub-id="simulationId || 'ENV_SETUP'"
      :logs="systemLogs"
      :is-active="phase === 1 || phase === 2"
    />
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import FloatingTerminal from './FloatingTerminal.vue'
import {
  prepareSimulation,
  getPrepareStatus,
  getSimulationProfilesRealtime,
  getSimulationConfig,
  getSimulationConfigRealtime
} from '../api/simulation'

const { t } = useI18n()

const props = defineProps({
  simulationId: String,  // Passed from parent component
  projectData: Object,
  graphData: Object,
  systemLogs: Array
})

const emit = defineEmits(['go-back', 'next-step', 'add-log', 'update-status'])

// State
const phase = ref(0) // 0: Initialize, 1: Generate Profiles, 2: Generate Config, 3: Complete
const taskId = ref(null)
const prepareProgress = ref(0)
const currentStage = ref('')
const progressMessage = ref('')
const profiles = ref([])
const entityTypes = ref([])
const expectedTotal = ref(null)
const simulationConfig = ref(null)
const selectedProfile = ref(null)
const showProfilesDetail = ref(true)

// Log deduplication: record key info of last output
let lastLoggedMessage = ''
let lastLoggedProfileCount = 0
let lastLoggedConfigStage = ''

// Simulation rounds configuration
const useCustomRounds = ref(false) // Default to automatic configured rounds
const customMaxRounds = ref(40)   // Default recommended 40 rounds

// Watch stage to update phase
watch(currentStage, (newStage) => {
  if (newStage === 'generating_profiles' || newStage === 'Generating Agent Profiles') {
    phase.value = 1
  } else if (newStage === 'generating_config' || newStage === 'Generating Simulation Config') {
    phase.value = 2
    // Enter config generation phase, start polling config
    if (!configTimer) {
      addLog(t('log.startGeneratingConfig'))
      startConfigPolling()
    }
  } else if (newStage === 'copying_scripts' || newStage === 'Preparing Simulation Scripts') {
    phase.value = 2 // Still belongs to configuration phase
  }
})

// Calculate auto-generated rounds from config (no hardcoded default)
const autoGeneratedRounds = computed(() => {
  if (!simulationConfig.value?.time_config) {
    return null // Returns null when config is not generated
  }
  const totalHours = simulationConfig.value.time_config.total_simulation_hours
  const minutesPerRound = simulationConfig.value.time_config.minutes_per_round
  if (!totalHours || !minutesPerRound) {
    return null // Returns null when config data is incomplete
  }
  const calculatedRounds = Math.floor((totalHours * 60) / minutesPerRound)
  // Ensure max rounds not less than 40 (recommended) to prevent abnormal slider range
  return Math.max(calculatedRounds, 40)
})

// Polling timer
let pollTimer = null
let profilesTimer = null
let configTimer = null

// Computed
const displayProfiles = computed(() => {
  if (showProfilesDetail.value) {
    return profiles.value
  }
  return profiles.value.slice(0, 6)
})

// Get username corresponding to agent_id
const getAgentUsername = (agentId) => {
  if (profiles.value && profiles.value.length > agentId && agentId >= 0) {
    const profile = profiles.value[agentId]
    return profile?.username || `agent_${agentId}`
  }
  return `agent_${agentId}`
}

// Calculate total associated topics across all personas
const totalTopicsCount = computed(() => {
  return profiles.value.reduce((sum, p) => {
    return sum + (p.interested_topics?.length || 0)
  }, 0)
})

// Methods
const addLog = (msg) => {
  emit('add-log', msg)
}

const handlePrepareFailure = (message) => {
  stopPolling()
  stopProfilesPolling()
  stopConfigPolling()
  addLog(t('log.prepareFailedWithError', { error: message || t('common.unknownError') }))
  emit('update-status', 'error')
}

// Handle start simulation button click
const handleStartSimulation = () => {
  // Construct parameters passed to parent component
  const params = {}
  
  if (useCustomRounds.value) {
    // User custom rounds, pass max_rounds parameter
    params.maxRounds = customMaxRounds.value
    addLog(t('log.startSimCustomRounds', { rounds: customMaxRounds.value }))
  } else {
    // User keeps auto-generated rounds, do not pass max_rounds
    addLog(t('log.startSimAutoRounds', { rounds: autoGeneratedRounds.value }))
  }
  
  emit('next-step', params)
}

const truncateBio = (bio) => {
  if (bio.length > 80) {
    return bio.substring(0, 80) + '...'
  }
  return bio
}

const selectProfile = (profile) => {
  selectedProfile.value = profile
}

// Automatically start simulation preparation
const startPrepareSimulation = async () => {
  if (!props.simulationId) {
    addLog(t('log.errorMissingSimId'))
    emit('update-status', 'error')
    return
  }
  
  // Mark step 1 completed, start step 2
  phase.value = 1
  addLog(t('log.simInstanceCreated', { id: props.simulationId }))
  addLog(t('log.preparingSimEnv'))
  emit('update-status', 'processing')
  
  try {
    const res = await prepareSimulation({
      simulation_id: props.simulationId,
      use_llm_for_profiles: true,
      parallel_profile_count: 5
    })
    
    if (res.success && res.data) {
      if (res.data.already_prepared) {
        addLog(t('log.detectedExistingPrep'))
        await loadPreparedData()
        return
      }
      
      taskId.value = res.data.task_id
      addLog(t('log.prepareTaskStarted'))
      addLog(t('log.prepareTaskId', { taskId: res.data.task_id }))
      
      // Set expected total agents immediately (from prepare API return value)
      if (res.data.expected_entities_count) {
        expectedTotal.value = res.data.expected_entities_count
        addLog(t('log.zepEntitiesFound', { count: res.data.expected_entities_count }))
        if (res.data.entity_types && res.data.entity_types.length > 0) {
          addLog(t('log.entityTypes', { types: res.data.entity_types.join(', ') }))
        }
      }
      
      addLog(t('log.startPollingProgress'))
      // Start polling progress
      startPolling()
      // Start real-time profile fetching
      startProfilesPolling()
    } else {
      addLog(t('log.prepareFailed', { error: res.error || t('common.unknownError') }))
      emit('update-status', 'error')
    }
  } catch (err) {
    addLog(t('log.prepareException', { error: err.message }))
    emit('update-status', 'error')
  }
}

const startPolling = () => {
  pollTimer = setInterval(pollPrepareStatus, 2000)
}

const stopPolling = () => {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

const startProfilesPolling = () => {
  profilesTimer = setInterval(fetchProfilesRealtime, 3000)
}

const stopProfilesPolling = () => {
  if (profilesTimer) {
    clearInterval(profilesTimer)
    profilesTimer = null
  }
}

const pollPrepareStatus = async () => {
  if (!taskId.value && !props.simulationId) return
  
  try {
    const res = await getPrepareStatus({
      task_id: taskId.value,
      simulation_id: props.simulationId
    })
    
    if (res.success && res.data) {
      const data = res.data
      
      // Update progress
      prepareProgress.value = data.progress || 0
      progressMessage.value = data.message || ''
      
      // Parse phase info and output detailed logs
      if (data.progress_detail) {
        currentStage.value = data.progress_detail.current_stage_name || ''
        
        // Output detailed progress logs (avoiding duplicates)
        const detail = data.progress_detail
        const logKey = `${detail.current_stage}-${detail.current_item}-${detail.total_items}`
        if (logKey !== lastLoggedMessage && detail.item_description) {
          lastLoggedMessage = logKey
          const stageInfo = `[${detail.stage_index}/${detail.total_stages}]`
          if (detail.total_items > 0) {
            addLog(`${stageInfo} ${detail.current_stage_name}: ${detail.current_item}/${detail.total_items} - ${detail.item_description}`)
          } else {
            addLog(`${stageInfo} ${detail.current_stage_name}: ${detail.item_description}`)
          }
        }
      } else if (data.message) {
        // Extract phase from message
        const match = data.message.match(/\[(\d+)\/(\d+)\]\s*([^:]+)/)
        if (match) {
          currentStage.value = match[3].trim()
        }
        // Output message logs (avoiding duplicates)
        if (data.message !== lastLoggedMessage) {
          lastLoggedMessage = data.message
          addLog(data.message)
        }
      }
      
      // Check if completed
      if (data.status === 'completed' || data.status === 'ready' || data.already_prepared) {
        addLog(t('log.prepareComplete'))
        stopPolling()
        stopProfilesPolling()
        await loadPreparedData()
      } else if (data.status === 'failed') {
        handlePrepareFailure(data.error)
      }
    }
  } catch (err) {
    console.warn('Failed to poll status:', err)
  }
}

const fetchProfilesRealtime = async () => {
  if (!props.simulationId) return
  
  try {
    const res = await getSimulationProfilesRealtime(props.simulationId)
    
    if (res.success && res.data) {
      const prevCount = profiles.value.length
      profiles.value = res.data.profiles || []
      // Only update when API returns valid values to avoid overwriting existing valid values
      if (res.data.total_expected) {
        expectedTotal.value = res.data.total_expected
      }
      
      // Extract entity types
      const types = new Set()
      profiles.value.forEach(p => {
        if (p.entity_type) types.add(p.entity_type)
      })
      entityTypes.value = Array.from(types)
      
      // Output Profile generation progress logs (only when count changes)
      const currentCount = profiles.value.length
      if (currentCount > 0 && currentCount !== lastLoggedProfileCount) {
        lastLoggedProfileCount = currentCount
        const total = expectedTotal.value || '?'
        const latestProfile = profiles.value[currentCount - 1]
        const profileName = latestProfile?.name || latestProfile?.username || `Agent_${currentCount}`
        if (currentCount === 1) {
          addLog(t('log.startGeneratingAgentProfiles'))
        }
        addLog(t('log.agentProfile', { current: currentCount, total: total, name: profileName, profession: latestProfile?.profession || t('step2.unknownProfession') }))

        // If all generated completely
        if (expectedTotal.value && currentCount >= expectedTotal.value) {
          addLog(t('log.allProfilesComplete', { count: currentCount }))
        }
      }
    }
  } catch (err) {
    console.warn('Failed to get Profiles:', err)
  }
}

// Config polling
const startConfigPolling = () => {
  configTimer = setInterval(fetchConfigRealtime, 2000)
}

const stopConfigPolling = () => {
  if (configTimer) {
    clearInterval(configTimer)
    configTimer = null
  }
}

const fetchConfigRealtime = async () => {
  if (!props.simulationId) return
  
  try {
    const res = await getSimulationConfigRealtime(props.simulationId)
    
    if (res.success && res.data) {
      const data = res.data

      if (data.status === 'failed' || data.error) {
        handlePrepareFailure(data.error)
        return
      }
      
      // Output config generation phase logs (avoiding duplicates)
      if (data.generation_stage && data.generation_stage !== lastLoggedConfigStage) {
        lastLoggedConfigStage = data.generation_stage
        if (data.generation_stage === 'generating_profiles') {
          addLog(t('log.generatingAgentProfileConfig'))
        } else if (data.generation_stage === 'generating_config') {
          addLog(t('log.generatingLLMConfig'))
        }
      }
      
      // If config is already generated
      if (data.config_generated && data.config) {
        simulationConfig.value = data.config
        addLog(t('log.configComplete'))

        // Display detailed config summary
        if (data.summary) {
          addLog(t('log.configSummaryAgents', { count: data.summary.total_agents }))
          addLog(t('log.configSummaryHours', { hours: data.summary.simulation_hours }))
          addLog(t('log.configSummaryPosts', { count: data.summary.initial_posts_count }))
          addLog(t('log.configSummaryTopics', { count: data.summary.hot_topics_count }))
          addLog(t('log.configSummaryPlatforms', { twitter: data.summary.has_twitter_config ? '✓' : '✗', reddit: data.summary.has_reddit_config ? '✓' : '✗' }))
        }
        
        // Display time config details
        if (data.config.time_config) {
          const tc = data.config.time_config
          addLog(t('log.timeConfigDetail', { minutes: tc.minutes_per_round, rounds: Math.floor((tc.total_simulation_hours * 60) / tc.minutes_per_round) }))
        }
        
        // Display event config
        if (data.config.event_config?.narrative_direction) {
          const narrative = data.config.event_config.narrative_direction
          addLog(t('log.narrativeDirection', { direction: narrative.length > 50 ? narrative.substring(0, 50) + '...' : narrative }))
        }
        
        stopConfigPolling()
        phase.value = 4
        addLog(t('log.envSetupComplete'))
        emit('update-status', 'completed')
      }
    }
  } catch (err) {
    console.warn('Failed to get Config:', err)
  }
}

const loadPreparedData = async () => {
  phase.value = 2
  addLog(t('log.loadingExistingConfig'))

  // Fetch Profiles one last time
  await fetchProfilesRealtime()
  addLog(t('log.loadedAgentProfiles', { count: profiles.value.length }))

  // Get config (using real-time API)
  try {
    const res = await getSimulationConfigRealtime(props.simulationId)
    if (res.success && res.data) {
      const configState = res.data

      if (configState.status === 'failed' || configState.error) {
        handlePrepareFailure(configState.error)
        return
      }

      if (configState.config_generated && configState.config) {
        simulationConfig.value = configState.config
        addLog(t('log.configLoadSuccess'))

        // Display detailed config summary
        if (configState.summary) {
          addLog(t('log.configSummaryAgents', { count: configState.summary.total_agents }))
          addLog(t('log.configSummaryHours', { hours: configState.summary.simulation_hours }))
          addLog(t('log.configSummaryPostsAlt', { count: configState.summary.initial_posts_count }))
        }

        addLog(t('log.envSetupComplete'))
        phase.value = 4
        emit('update-status', 'completed')
      } else if (configState.is_generating) {
        addLog(t('log.configGenerating'))
        startConfigPolling()
      } else {
        handlePrepareFailure(t('log.configNotGenerating'))
      }
    }
  } catch (err) {
    handlePrepareFailure(t('log.loadConfigFailed', { error: err.message }))
  }
}

// Scroll log to bottom
const logContent = ref(null)
watch(() => props.systemLogs?.length, () => {
  nextTick(() => {
    if (logContent.value) {
      logContent.value.scrollTop = logContent.value.scrollHeight
    }
  })
})

onMounted(() => {
  // Automatically start preparation process
  if (props.simulationId) {
    addLog(t('log.step2Init'))
    startPrepareSimulation()
  }
})

onUnmounted(() => {
  stopPolling()
  stopProfilesPolling()
  stopConfigPolling()
})
</script>

<style scoped>
.env-setup-panel {
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

@keyframes web-breathe {
  0% { transform: translateY(0px) scaleY(1); opacity: 0.85; }
  100% { transform: translateY(4px) scaleY(1.015); opacity: 1; }
}

@keyframes web-drip-sway {
  0% { transform: rotate(0deg); }
  50% { transform: rotate(0.4deg); }
  100% { transform: rotate(-0.35deg); }
}

.scroll-container {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.scroll-container::-webkit-scrollbar {
  width: 6px;
}
.scroll-container::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.12);
  border-radius: 999px;
}

/* Step Card */
.step-card {
  background: rgba(12, 12, 16, 0.78);
  border-radius: 18px;
  padding: 24px;
  border: 1px solid rgba(255, 255, 255, 0.13);
transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  position: relative;
  color: #f5f5f7;
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

.badge {
  font-family: 'JetBrains Mono', monospace;
  font-size: 10px;
  padding: 4px 12px;
  border-radius: 999px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.6px;
  transition: all 0.25s ease;
}

.badge.success {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.45);
  color: #FFFFFF;
}

.badge.processing,
.badge.accent {
  background: rgba(255, 255, 255, 0.12);
  border: 1px solid #FFFFFF;
  color: #FFFFFF;
}

.badge.pending {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #71717a;
}

.card-content {
}

.api-note {
  font-family: 'JetBrains Mono', monospace;
  font-size: 10px;
  color: #71717a;
  margin-bottom: 8px;
}

.description {
  font-size: 12px;
  color: #a1a1aa;
  line-height: 1.5;
  margin-bottom: 16px;
}

/* Action Section */
.action-section {
  margin-top: 16px;
}

.action-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 24px;
  font-size: 14px;
  font-weight: 600;
  border-radius: 999px;
  cursor: pointer;
  transition: all 0.2s ease;
  user-select: none;
}

.action-btn.primary {
  background: #FFFFFF;
  border: 1px solid #FFFFFF;
  color: #000000;
  font-weight: 700;
}

.action-btn.primary:hover:not(:disabled) {
  background: #000000;
  color: #FFFFFF;
  border-color: #FFFFFF;
  transform: translateY(-1px);
}

.action-btn.primary:active:not(:disabled) {
  transform: translateY(0);
}

.action-btn.secondary {
  background: rgba(22, 22, 30, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #FFFFFF;
}

.action-btn.secondary:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.12);
  border-color: rgba(255, 255, 255, 0.4);
  color: #FFFFFF;
  transform: translateY(-1px);
}

.action-btn:disabled {
  background: rgba(255, 255, 255, 0.04);
  color: #52525b;
  border: 1px solid rgba(255, 255, 255, 0.08);
  cursor: not-allowed;
  opacity: 0.6;
}

.action-group {
  display: flex;
  gap: 12px;
  margin-top: 16px;
}

.action-group.dual {
  display: grid;
  grid-template-columns: 1fr 1fr;
}

.action-group.dual .action-btn {
  width: 100%;
}

/* Info Card */
.info-card {
  background: rgba(8, 8, 12, 0.65);
  border: 1px solid rgba(255, 255, 255, 0.08);
border-radius: 12px;
  padding: 16px;
  margin-top: 16px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px dashed rgba(255, 255, 255, 0.1);
}

.info-row:last-child {
  border-bottom: none;
}

.info-label {
  font-size: 11px;
  color: #71717a;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-family: 'JetBrains Mono', monospace;
}

.info-value {
  font-size: 13px;
  font-weight: 500;
  color: #FFFFFF;
}

.info-value.mono {
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  color: #FFFFFF;
}

/* Stats Grid */
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

/* Profiles Preview */
.profiles-preview {
  margin-top: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  padding-top: 16px;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.preview-title {
  font-size: 12px;
  font-weight: 600;
  color: #a1a1aa;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.profiles-list {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  max-height: 320px;
  overflow-y: auto;
  padding-right: 4px;
}

.profiles-list::-webkit-scrollbar {
  width: 4px;
}

.profiles-list::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.15);
  border-radius: 2px;
}

.profiles-list::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}

.profile-card {
  background: rgba(14, 14, 18, 0.85);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.profile-card:hover {
  border-color: rgba(255, 255, 255, 0.35);
  background: rgba(22, 22, 30, 0.95);
  transform: translateY(-2px);
}

.profile-header {
  display: flex;
  align-items: baseline;
  gap: 8px;
  margin-bottom: 6px;
}

.profile-realname {
  font-size: 14px;
  font-weight: 700;
  color: #FFFFFF;
}

.profile-username {
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  color: #71717a;
}

.profile-meta {
  margin-bottom: 8px;
}

.profile-profession {
  font-size: 11px;
  color: #e4e4e7;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 2px 8px;
  border-radius: 4px;
}

.profile-bio {
  font-size: 12px;
  color: #a1a1aa;
  line-height: 1.6;
  margin: 0 0 10px 0;
  display:box;
line-clamp: 3;
box-orient: vertical;
  overflow: hidden;
}

.profile-topics {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.topic-tag {
  font-size: 10px;
  color: #ffffff;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  padding: 2px 8px;
  border-radius: 999px;
}

.topic-more {
  font-size: 10px;
  color: #71717a;
  padding: 2px 6px;
}

/* Config Detail Panel */
.config-detail-panel {
  margin-top: 16px;
}

.config-block {
  margin-top: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  padding-top: 12px;
}

.config-block:first-child {
  margin-top: 0;
  border-top: none;
  padding-top: 0;
}

.config-block-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.config-block-title {
  font-size: 12px;
  font-weight: 600;
  color: #a1a1aa;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.config-block-badge {
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: #e4e4e7;
  padding: 2px 8px;
  border-radius: 10px;
}

/* Config Grid */
.config-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.config-item {
  background: rgba(14, 14, 18, 0.85);
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 12px 14px;
  border-radius: 10px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.config-item-label {
  font-size: 11px;
  color: #71717a;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.config-item-value {
  font-family: 'JetBrains Mono', monospace;
  font-size: 16px;
  font-weight: 700;
  color: #FFFFFF;
}

/* Time Periods */
.time-periods {
  margin-top: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.period-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  background: rgba(14, 14, 18, 0.85);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px;
}

.period-label {
  font-size: 12px;
  font-weight: 500;
  color: #a1a1aa;
  min-width: 70px;
}

.period-hours {
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  color: #ffffff;
  flex: 1;
}

.period-multiplier {
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  font-weight: 600;
  color: #ffffff;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  padding: 2px 6px;
  border-radius: 4px;
}

/* Agents Cards */
.agents-cards {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  max-height: 400px;
  overflow-y: auto;
  padding-right: 4px;
}

.agents-cards::-webkit-scrollbar {
  width: 4px;
}

.agents-cards::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.15);
  border-radius: 2px;
}

.agents-cards::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}

.agent-card {
  background: rgba(14, 14, 18, 0.85);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 14px;
  transition: all 0.2s ease;
}

.agent-card:hover {
  border-color: rgba(255, 255, 255, 0.35);
  background: rgba(22, 22, 30, 0.95);
}

/* Agent Card Header */
.agent-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 14px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.agent-identity {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.agent-id {
  font-family: 'JetBrains Mono', monospace;
  font-size: 10px;
  color: #71717a;
}

.agent-name {
  font-size: 14px;
  font-weight: 600;
  color: #FFFFFF;
}

.agent-tags {
  display: flex;
  gap: 6px;
}

.agent-type {
  font-size: 10px;
  color: #a1a1aa;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 2px 8px;
  border-radius: 4px;
}

.agent-stance {
  font-size: 10px;
  font-weight: 500;
  text-transform: uppercase;
  padding: 2px 8px;
  border-radius: 4px;
}

.stance-neutral {
  background: rgba(255, 255, 255, 0.05);
  color: #a1a1aa;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.stance-supportive {
  background: rgba(255, 255, 255, 0.15);
  color: #ffffff;
  border: 1px solid rgba(255, 255, 255, 0.4);
  font-weight: 700;
}

.stance-opposing {
  background: rgba(255, 255, 255, 0.08);
  color: #d4d4d8;
  border: 1px dashed rgba(255, 255, 255, 0.25);
}

.stance-observer {
  background: rgba(255, 255, 255, 0.04);
  color: #71717a;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

/* Agent Timeline */
.agent-timeline {
  margin-bottom: 14px;
}

.timeline-label {
  display: block;
  font-size: 10px;
  color: #71717a;
  margin-bottom: 6px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.mini-timeline {
  display: flex;
  gap: 2px;
  height: 16px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 4px;
  padding: 3px;
}

.timeline-hour {
  flex: 1;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
  transition: all 0.2s;
}

.timeline-hour.active {
  background: #ffffff;
}

.timeline-marks {
  display: flex;
  justify-content: space-between;
  margin-top: 4px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 9px;
  color: #71717a;
}

/* Agent Params */
.agent-params {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.param-group {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
}

.param-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.param-item .param-label {
  font-size: 10px;
  color: #71717a;
}

.param-item .param-value {
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  font-weight: 600;
  color: #ffffff;
}

.param-value.with-bar {
  display: flex;
  align-items: center;
  gap: 6px;
}

.mini-bar {
  height: 4px;
  background: linear-gradient(90deg, #ffffff, #71717a);
  border-radius: 2px;
  min-width: 4px;
  max-width: 40px;
}

.param-value.positive {
  color: #ffffff;
}

.param-value.negative {
  color: #a1a1aa;
}

.param-value.neutral {
  color: #71717a;
}

.param-value.highlight {
  color: #ffffff;
  font-weight: 700;
}

/* Platforms Grid */
.platforms-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.platform-card {
  background: rgba(14, 14, 18, 0.85);
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 14px;
  border-radius: 12px;
}

.platform-card-header {
  margin-bottom: 10px;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.platform-name {
  font-size: 13px;
  font-weight: 600;
  color: #ffffff;
}

.platform-params {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.param-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.param-label {
  font-size: 12px;
  color: #71717a;
}

.param-value {
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  font-weight: 600;
  color: #ffffff;
}

/* Reasoning Content */
.reasoning-content {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.reasoning-item {
  padding: 12px 14px;
  background: rgba(14, 14, 18, 0.85);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
}

.reasoning-text {
  font-size: 13px;
  color: #d4d4d8;
  line-height: 1.7;
  margin: 0;
}

/* Profile Modal */
.profile-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  }

.profile-modal {
  background: #0c0c10;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  width: 90%;
  max-width: 600px;
  max-height: 85vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 24px;
  background: rgba(18, 18, 24, 0.95);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.modal-header-info {
  flex: 1;
}

.modal-name-row {
  display: flex;
  align-items: baseline;
  gap: 10px;
  margin-bottom: 8px;
}

.modal-realname {
  font-size: 20px;
  font-weight: 700;
  color: #FFFFFF;
}

.modal-username {
  font-family: 'JetBrains Mono', monospace;
  font-size: 13px;
  color: #71717a;
}

.modal-profession {
  font-size: 12px;
  color: #e4e4e7;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  padding: 4px 10px;
  border-radius: 4px;
  display: inline-block;
  font-weight: 500;
}

.close-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: none;
  color: #71717a;
  border-radius: 50%;
  font-size: 24px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
  transition: color 0.2s;
  padding: 0;
}

.close-btn:hover {
  color: #ffffff;
}

.modal-body {
  padding: 24px;
  overflow-y: auto;
  flex: 1;
}

/* Basic info grid */
.modal-info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px 16px;
  margin-bottom: 32px;
  padding: 0;
  background: transparent;
  border-radius: 0;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-label {
  font-size: 11px;
  color: #71717a;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 600;
}

.info-value {
  font-size: 15px;
  font-weight: 600;
  color: #ffffff;
}

.info-value.mbti {
  font-family: 'JetBrains Mono', monospace;
  color: #ffffff;
}

/* Module area */
.modal-section {
  margin-bottom: 28px;
}

.section-label {
  display: block;
  font-size: 11px;
  font-weight: 600;
  color: #71717a;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 12px;
}

.section-bio {
  font-size: 14px;
  color: #d4d4d8;
  line-height: 1.6;
  margin: 0;
  padding: 16px;
  background: rgba(14, 14, 18, 0.85);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-left: 3px solid #ffffff;
}

/* Topic tags */
.topics-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.topic-item {
  font-size: 11px;
  color: #ffffff;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  padding: 4px 10px;
  border-radius: 12px;
  transition: all 0.2s;
}

.topic-item:hover {
  background: rgba(255, 255, 255, 0.18);
  border-color: #ffffff;
}

/* Detailed persona */
.persona-dimensions {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-bottom: 16px;
}

.dimension-card {
  background: rgba(14, 14, 18, 0.85);
  border: 1px solid rgba(255, 255, 255, 0.08);
  padding: 12px;
  border-radius: 8px;
  border-left: 3px solid rgba(255, 255, 255, 0.4);
  transition: all 0.2s;
}

.dimension-card:hover {
  background: rgba(22, 22, 30, 0.95);
  border-left-color: #ffffff;
}

.dim-title {
  display: block;
  font-size: 12px;
  font-weight: 700;
  color: #ffffff;
  margin-bottom: 4px;
}

.dim-desc {
  display: block;
  font-size: 10px;
  color: #a1a1aa;
  line-height: 1.4;
}

.persona-content {
  max-height: none;
  overflow: visible;
  padding: 0;
  background: transparent;
  border: none;
  border-radius: 0;
}

.persona-content::-webkit-scrollbar {
  width: 4px;
}

.persona-content::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.15);
  border-radius: 2px;
}

.section-persona {
  font-size: 13px;
  color: #d4d4d8;
  line-height: 1.8;
  margin: 0;
  text-align: justify;
}

/* System Logs */
.system-logs {
  background: #000;
  color: #DDD;
  padding: 16px;
  font-family: 'JetBrains Mono', monospace;
  border-top: 1px solid rgba(255, 255, 255, 0.12);
  flex-shrink: 0;
}

.log-header {
  display: flex;
  justify-content: space-between;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding-bottom: 8px;
  margin-bottom: 8px;
  font-size: 10px;
  color: #71717a;
}

.log-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
  height: 80px;
  overflow-y: auto;
  padding-right: 4px;
}

.log-content::-webkit-scrollbar {
  width: 4px;
}

.log-content::-webkit-scrollbar-thumb {
  background: #333;
  border-radius: 2px;
}

.log-line {
  font-size: 11px;
  display: flex;
  gap: 12px;
  line-height: 1.5;
}

.log-time {
  color: #71717a;
  min-width: 75px;
}

.log-msg {
  color: #CCC;
  word-break: break-all;
}

/* Spinner */
.spinner-sm {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-top-color: #FFFFFF;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Orchestration Content */
.orchestration-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-top: 16px;
}

.box-label {
  display: block;
  font-size: 12px;
  font-weight: 600;
  color: #a1a1aa;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 12px;
}

.narrative-box {
  background: rgba(14, 14, 18, 0.85);
  padding: 20px 24px;
  border-radius: 14px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  transition: all 0.3s ease;
}

.narrative-box .box-label {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #ffffff;
  font-size: 13px;
  letter-spacing: 0.5px;
  margin-bottom: 12px;
  font-weight: 600;
}

.special-icon {
  transition: transform 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.narrative-box:hover .special-icon {
  transform: rotate(180deg);
}

.narrative-text {
  font-family: 'Inter', 'Noto Sans SC', system-ui, sans-serif;
  font-size: 14px;
  color: #d4d4d8;
  line-height: 1.8;
  margin: 0;
  text-align: justify;
  letter-spacing: 0.01em;
}

.topics-section {
  background: transparent;
}

.hot-topics-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.hot-topic-tag {
  font-size: 12px;
  color: #ffffff;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  padding: 4px 10px;
  border-radius: 12px;
  font-weight: 500;
}

.hot-topic-more {
  font-size: 11px;
  color: #71717a;
  padding: 4px 6px;
}

.initial-posts-section {
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  padding-top: 16px;
}

.posts-timeline {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding-left: 8px;
  border-left: 2px solid rgba(255, 255, 255, 0.15);
  margin-top: 12px;
}

.timeline-item {
  position: relative;
  padding-left: 20px;
}

.timeline-marker {
  position: absolute;
  left: 0;
  top: 14px;
  width: 12px;
  height: 2px;
  background: #ffffff;
}

.timeline-content {
  background: rgba(14, 14, 18, 0.85);
  padding: 12px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.post-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 6px;
}

.post-role {
  font-size: 11px;
  font-weight: 700;
  color: #ffffff;
  text-transform: uppercase;
}

.post-agent-info {
  display: flex;
  align-items: center;
  gap: 6px;
}

.post-id,
.post-username {
  font-family: 'JetBrains Mono', monospace;
  font-size: 10px;
  color: #71717a;
  line-height: 1;
  vertical-align: baseline;
}

.post-username {
  margin-right: 6px;
}

.post-text {
  font-size: 12px;
  color: #d4d4d8;
  line-height: 1.5;
  margin: 0;
}

/* Simulation rounds configuration styles */
.rounds-config-section {
  margin: 24px 0;
  padding-top: 24px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.rounds-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-left {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: #ffffff;
}

.section-desc {
  font-size: 12px;
  color: #71717a;
}

.desc-highlight {
  font-family: 'JetBrains Mono', monospace;
  font-weight: 600;
  color: #ffffff;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.15);
  padding: 1px 6px;
  border-radius: 4px;
  margin: 0 2px;
}

/* Switch Control - Minimal, monochrome, understated Slate grey (Accent: #94A3B8) */
.switch-control {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 8px 4px 4px;
  border-radius: 20px;
  transition: background 0.2s ease;
}

.switch-control:hover {
  background: rgba(148, 163, 184, 0.08);
}

.switch-control input {
  display: none;
}

.switch-track {
  width: 36px;
  height: 20px;
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 10px;
  position: relative;
  transition: all 0.25s ease;
}

.switch-track::after {
  content: '';
  position: absolute;
  left: 2px;
  top: 2px;
  width: 14px;
  height: 14px;
  background: #64748b;
  border-radius: 50%;
  transition: transform 0.25s ease, background-color 0.25s ease;
}

.switch-control input:checked + .switch-track {
  background: #94A3B8;
  border-color: #94A3B8;
}

.switch-control input:checked + .switch-track::after {
  transform: translateX(16px);
  background: #0f172a;
}

.switch-label {
  font-size: 12px;
  font-weight: 500;
  color: #64748b;
  transition: color 0.2s ease;
}

.switch-control input:checked ~ .switch-label {
  color: #94A3B8;
}

/* Slider Content */
.rounds-content {
  animation: fadeIn 0.3s ease;
}

.slider-display {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 16px;
}

.slider-main-value {
  display: flex;
  align-items: baseline;
  gap: 4px;
}

.val-num {
  font-family: 'JetBrains Mono', monospace;
  font-size: 24px;
  font-weight: 700;
  color: #ffffff;
}

.val-unit {
  font-size: 12px;
  color: #71717a;
  font-weight: 500;
}

.slider-meta-info {
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  color: #a1a1aa;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.12);
  padding: 4px 8px;
  border-radius: 4px;
}

.range-wrapper {
  position: relative;
  padding: 0 2px;
}

.minimal-slider {
appearance: none;
  width: 100%;
  height: 4px;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 2px;
  outline: none;
  background-image: linear-gradient(#ffffff, #ffffff);
  background-size: var(--percent, 0%) 100%;
  background-repeat: no-repeat;
  cursor: pointer;
}

.minimal-slider::slider-thumb {
appearance: none;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: #000000;
  border: 2px solid #ffffff;
  cursor: pointer;
  transition: transform 0.1s;
  margin-top: -6px;
}

.minimal-slider::slider-thumb:hover {
  transform: scale(1.15);
  background: #ffffff;
  border-color: #000000;
}

.minimal-slider::slider-runnable-track {
  height: 4px;
  border-radius: 2px;
}

.range-marks {
  display: flex;
  justify-content: space-between;
  margin-top: 8px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 10px;
  color: #71717a;
  position: relative;
}

.mark-recommend {
  cursor: pointer;
  transition: color 0.2s;
  position: relative;
}

.mark-recommend:hover {
  color: #ffffff;
}

.mark-recommend.active {
  color: #ffffff;
  font-weight: 600;
}

.mark-recommend::after {
  content: '';
  position: absolute;
  top: -12px;
  left: 50%;
  transform: translateX(-50%);
  width: 1px;
  height: 4px;
  background: rgba(255, 255, 255, 0.3);
}

/* Auto Info */
.auto-info-card {
  display: flex;
  align-items: center;
  gap: 24px;
  background: rgba(14, 14, 18, 0.85);
  border: 1px solid rgba(255, 255, 255, 0.12);
  padding: 16px 20px;
  border-radius: 12px;
}

.auto-value {
  display: flex;
  flex-direction: row;
  align-items: baseline;
  gap: 4px;
  padding-right: 24px;
  border-right: 1px solid rgba(255, 255, 255, 0.1);
}

.auto-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
  justify-content: center;
}

.auto-meta-row {
  display: flex;
  align-items: center;
}

.duration-badge {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  font-weight: 500;
  color: #ffffff;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  padding: 3px 8px;
  border-radius: 6px;
}

.auto-desc {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.auto-desc p {
  margin: 0;
  font-size: 13px;
  color: #a1a1aa;
  line-height: 1.5;
}

.highlight-tip {
  margin-top: 4px !important;
  font-size: 12px !important;
  color: #ffffff !important;
  font-weight: 500;
  cursor: pointer;
  text-decoration: underline;
}

.highlight-tip:hover {
  color: #e4e4e7 !important;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(4px); }
  to { opacity: 1; transform: translateY(0); }
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Modal Transition */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active .profile-modal {
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.modal-leave-active .profile-modal {
  transition: all 0.3s ease-in;
}

.modal-enter-from .profile-modal,
.modal-leave-to .profile-modal {
  transform: scale(0.95) translateY(10px);
  opacity: 0;
}
</style>