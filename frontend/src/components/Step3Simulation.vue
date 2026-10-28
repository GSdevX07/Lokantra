<template>
    <div class="simulation-panel relative overflow-hidden">
    <!-- Venom Cyber Grid & Web Strings Background Patterns Layer (Pure Glass Backing) -->
    <div class="workbench-venom-bg pointer-events-none select-none absolute inset-0 z-0 overflow-hidden">
      <!-- 1. Cyber Perspective Ceiling & Floor Plane Grid Lines -->
      <svg class="cyber-grid-svg absolute inset-0 w-full h-full" viewBox="0 0 800 1200" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <linearGradient id="gridLineFade3" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stop-color="#ffffff" stop-opacity="0.4" />
            <stop offset="30%" stop-color="#ffffff" stop-opacity="0.2" />
            <stop offset="70%" stop-color="#ffffff" stop-opacity="0.15" />
            <stop offset="100%" stop-color="#ffffff" stop-opacity="0.3" />
          </linearGradient>
        </defs>
        <!-- Horizontal grid lines across all card zones -->
        <line x1="0" y1="40" x2="800" y2="40" stroke="url(#gridLineFade3)" stroke-width="1" />
        <line x1="0" y1="120" x2="800" y2="120" stroke="url(#gridLineFade3)" stroke-width="1.2" />
        <line x1="0" y1="220" x2="800" y2="220" stroke="url(#gridLineFade3)" stroke-width="1" />
        <line x1="0" y1="360" x2="800" y2="360" stroke="url(#gridLineFade3)" stroke-width="1.2" />
        <line x1="0" y1="520" x2="800" y2="520" stroke="url(#gridLineFade3)" stroke-width="1" />
        <line x1="0" y1="680" x2="800" y2="680" stroke="url(#gridLineFade3)" stroke-width="1.2" />
        <line x1="0" y1="840" x2="800" y2="840" stroke="url(#gridLineFade3)" stroke-width="1" />
        <line x1="0" y1="1020" x2="800" y2="1020" stroke="url(#gridLineFade3)" stroke-width="1.2" />
        <line x1="0" y1="1160" x2="800" y2="1160" stroke="url(#gridLineFade3)" stroke-width="1" />
        <!-- Vertical grid lines -->
        <line x1="40" y1="0" x2="40" y2="1200" stroke="url(#gridLineFade3)" stroke-width="1.2" />
        <line x1="160" y1="0" x2="160" y2="1200" stroke="url(#gridLineFade3)" stroke-width="1" />
        <line x1="320" y1="0" x2="320" y2="1200" stroke="url(#gridLineFade3)" stroke-width="1.2" />
        <line x1="480" y1="0" x2="480" y2="1200" stroke="url(#gridLineFade3)" stroke-width="1" />
        <line x1="640" y1="0" x2="640" y2="1200" stroke="url(#gridLineFade3)" stroke-width="1.2" />
        <line x1="760" y1="0" x2="760" y2="1200" stroke="url(#gridLineFade3)" stroke-width="1" />
        <!-- Perspective converging lines -->
        <line x1="0" y1="0" x2="400" y2="600" stroke="url(#gridLineFade3)" stroke-width="0.8" />
        <line x1="800" y1="0" x2="400" y2="600" stroke="url(#gridLineFade3)" stroke-width="0.8" />
        <line x1="0" y1="1200" x2="400" y2="600" stroke="url(#gridLineFade3)" stroke-width="0.8" />
        <line x1="800" y1="1200" x2="400" y2="600" stroke="url(#gridLineFade3)" stroke-width="0.8" />
      </svg>

      <!-- 2. Venomous Web Strands, Fissure Cracks & Suspension Cables -->
      <svg class="venom-webs-svg absolute inset-0 w-full h-full" viewBox="0 0 800 1200" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <linearGradient id="wbSheen3" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#ffffff" stop-opacity="0.95" />
            <stop offset="25%" stop-color="#d4d4d8" stop-opacity="0.75" />
            <stop offset="60%" stop-color="#71717a" stop-opacity="0.5" />
            <stop offset="100%" stop-color="#ffffff" stop-opacity="0.9" />
          </linearGradient>
          <linearGradient id="fisGrad3" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#ffffff" stop-opacity="1" />
            <stop offset="50%" stop-color="#e4e4e7" stop-opacity="0.75" />
            <stop offset="100%" stop-color="#a1a1aa" stop-opacity="0.45" />
          </linearGradient>
        </defs>

        <!-- SPREADING FRACTURE CRACKS -->
        <g class="fissure-cracks-group">
          <g stroke="url(#fisGrad3)" stroke-linecap="round" stroke-linejoin="bevel">
            <path d="M 0,40 L 90,95 L 140,80 L 210,175 L 270,230 L 350,265 L 430,360 L 390,440 L 460,520 L 520,610 L 490,700 L 570,810 L 630,920 L 720,1050 L 800,1110" stroke-width="2.2" fill="none" />
            <path d="M 140,80 L 190,35 L 250,20" stroke-width="1.3" fill="none" />
            <path d="M 270,230 L 330,205 L 400,210" stroke-width="1.3" fill="none" />
            <path d="M 430,360 L 490,410 L 530,475" stroke-width="1.4" fill="none" />
            <path d="M 520,610 L 580,570 L 640,560" stroke-width="1.3" fill="none" />
            <path d="M 570,810 L 640,830 L 700,790" stroke-width="1.4" fill="none" />
            <path d="M 800,320 L 710,380 L 660,360 L 580,450 L 530,520 L 440,550 L 370,640 L 320,720 L 250,760 L 180,870 L 110,910 L 0,980" stroke-width="2" fill="none" />
            <path d="M 660,360 L 620,310 L 580,290" stroke-width="1.2" fill="none" />
            <path d="M 440,550 L 390,520 L 340,530" stroke-width="1.2" fill="none" />
            <path d="M 320,720 L 270,690 L 220,700" stroke-width="1.2" fill="none" />
          </g>
        </g>

        <!-- CORNER & EDGE SPIDERWEBS -->
        <g class="corner-webs-group">
          <g stroke="rgba(255,255,255,0.6)" stroke-width="1.2" fill="none">
            <line x1="0" y1="0" x2="320" y2="70" />
            <line x1="0" y1="0" x2="260" y2="190" />
            <line x1="0" y1="0" x2="160" y2="300" />
            <line x1="0" y1="0" x2="50" y2="380" />
          </g>
          <g stroke="url(#wbSheen3)" stroke-width="1.8" fill="none">
            <path d="M 85,0 Q 68,32 50,74 Q 34,100 0,116" />
            <path d="M 180,0 Q 152,70 114,152 Q 70,212 0,238" />
            <path d="M 295,0 Q 250,108 188,232 Q 108,328 0,382" />
            <path d="M 425,0 Q 355,158 272,334 Q 158,464 0,538" />
          </g>

          <g stroke="rgba(255,255,255,0.6)" stroke-width="1.2" fill="none">
            <line x1="800" y1="0" x2="480" y2="70" />
            <line x1="800" y1="0" x2="540" y2="190" />
            <line x1="800" y1="0" x2="640" y2="300" />
            <line x1="800" y1="0" x2="750" y2="380" />
          </g>
          <g stroke="url(#wbSheen3)" stroke-width="1.8" fill="none">
            <path d="M 715,0 Q 732,32 750,74 Q 766,100 800,116" />
            <path d="M 620,0 Q 648,70 686,152 Q 730,212 800,238" />
            <path d="M 505,0 Q 550,108 612,232 Q 692,328 800,382" />
            <path d="M 375,0 Q 445,158 528,334 Q 642,464 800,538" />
          </g>
        </g>
      </svg>
    </div>
    <!-- Top Control Bar -->
    <div class="control-bar">
      <div class="status-group">
        <!-- Twitter Platform Progress -->
        <div class="platform-status twitter" :class="{ active: runStatus.twitter_running, completed: runStatus.twitter_completed }">
          <div class="platform-header">
            <svg class="platform-icon" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"></circle><line x1="2" y1="12" x2="22" y2="12"></line><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path>
            </svg>
            <span class="platform-name">Info Plaza</span>
            <span v-if="runStatus.twitter_completed" class="status-badge">
              <svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="3">
                <polyline points="20 6 9 17 4 12"></polyline>
              </svg>
            </span>
          </div>
          <div class="platform-stats">
            <span class="stat">
              <span class="stat-label">ROUND</span>
              <span class="stat-value mono">{{ runStatus.twitter_current_round || 0 }}<span class="stat-total">/{{ runStatus.total_rounds || maxRounds || '-' }}</span></span>
            </span>
            <span class="stat">
              <span class="stat-label">TIME</span>
              <span class="stat-value mono">{{ twitterElapsedTime }}</span>
            </span>
            <span class="stat">
              <span class="stat-label">ACTS</span>
              <span class="stat-value mono">{{ runStatus.twitter_actions_count || 0 }}</span>
            </span>
          </div>
          <!-- Available Actions Hint -->
          <div class="actions-tooltip">
            <div class="tooltip-title">Available Actions</div>
            <div class="tooltip-actions">
              <span class="tooltip-action">POST</span>
              <span class="tooltip-action">LIKE</span>
              <span class="tooltip-action">REPOST</span>
              <span class="tooltip-action">QUOTE</span>
              <span class="tooltip-action">FOLLOW</span>
              <span class="tooltip-action">IDLE</span>
            </div>
          </div>
        </div>
        
        <!-- Reddit Platform Progress -->
        <div class="platform-status reddit" :class="{ active: runStatus.reddit_running, completed: runStatus.reddit_completed }">
          <div class="platform-header">
            <svg class="platform-icon" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path>
            </svg>
            <span class="platform-name">Topic Community</span>
            <span v-if="runStatus.reddit_completed" class="status-badge">
              <svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="3">
                <polyline points="20 6 9 17 4 12"></polyline>
              </svg>
            </span>
          </div>
          <div class="platform-stats">
            <span class="stat">
              <span class="stat-label">ROUND</span>
              <span class="stat-value mono">{{ runStatus.reddit_current_round || 0 }}<span class="stat-total">/{{ runStatus.total_rounds || maxRounds || '-' }}</span></span>
            </span>
            <span class="stat">
              <span class="stat-label">TIME</span>
              <span class="stat-value mono">{{ redditElapsedTime }}</span>
            </span>
            <span class="stat">
              <span class="stat-label">ACTS</span>
              <span class="stat-value mono">{{ runStatus.reddit_actions_count || 0 }}</span>
            </span>
          </div>
          <!-- Available Actions Hint -->
          <div class="actions-tooltip">
            <div class="tooltip-title">Available Actions</div>
            <div class="tooltip-actions">
              <span class="tooltip-action">POST</span>
              <span class="tooltip-action">COMMENT</span>
              <span class="tooltip-action">LIKE</span>
              <span class="tooltip-action">DISLIKE</span>
              <span class="tooltip-action">SEARCH</span>
              <span class="tooltip-action">TREND</span>
              <span class="tooltip-action">FOLLOW</span>
              <span class="tooltip-action">MUTE</span>
              <span class="tooltip-action">REFRESH</span>
              <span class="tooltip-action">IDLE</span>
            </div>
          </div>
        </div>
      </div>

      <div class="action-controls">
        <button 
          v-if="phase === 1"
          class="action-btn secondary stop-btn"
          :disabled="isStopping"
          @click="handleStopSimulation"
        >
          <span v-if="isStopping" class="loading-spinner-small"></span>
          {{ isStopping ? 'STOPPING...' : 'STOP' }}
        </button>

        <button 
          class="action-btn primary"
          :disabled="phase !== 2 || isGeneratingReport"
          @click="handleNextStep"
        >
          <span v-if="isGeneratingReport" class="loading-spinner-small"></span>
          {{ isGeneratingReport ? $t('step3.generatingReportBtn') : $t('step3.startGenerateReportBtn') }}
          <span v-if="!isGeneratingReport" class="arrow-icon">→</span>
        </button>
      </div>
    </div>

    <!-- Main Content: Dual Timeline -->
    <div class="main-content-area" ref="scrollContainer">
      <!-- Timeline Header -->
      <div class="timeline-header" v-if="allActions.length > 0">
        <div class="timeline-stats">
          <span class="total-count">TOTAL EVENTS: <span class="mono">{{ allActions.length }}</span></span>
          <span class="platform-breakdown">
            <span class="breakdown-item twitter">
              <svg class="mini-icon" viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="2" y1="12" x2="22" y2="12"></line><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path></svg>
              <span class="mono">{{ twitterActionsCount }}</span>
            </span>
            <span class="breakdown-divider">/</span>
            <span class="breakdown-item reddit">
              <svg class="mini-icon" viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path></svg>
              <span class="mono">{{ redditActionsCount }}</span>
            </span>
          </span>
        </div>
      </div>
      
      <!-- Timeline Feed -->
      <div class="timeline-feed">
        <div class="timeline-axis"></div>
        
        <TransitionGroup name="timeline-item">
          <div 
            v-for="action in chronologicalActions" 
            :key="action._uniqueId || action.id || `${action.timestamp}-${action.agent_id}`" 
            class="timeline-item"
            :class="action.platform"
          >
            <div class="timeline-marker">
              <div class="marker-dot"></div>
            </div>
            
            <div class="timeline-card">
              <div class="card-header">
                <div class="agent-info">
                  <div class="avatar-placeholder">{{ (action.agent_name || 'A')[0] }}</div>
                  <span class="agent-name">{{ action.agent_name }}</span>
                </div>
                
                <div class="header-meta">
                  <div class="platform-indicator">
                    <svg v-if="action.platform === 'twitter'" viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="2" y1="12" x2="22" y2="12"></line><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path></svg>
                    <svg v-else viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path></svg>
                  </div>
                  <div class="action-badge" :class="getActionTypeClass(action.action_type)">
                    {{ getActionTypeLabel(action.action_type) }}
                  </div>
                </div>
              </div>
              
              <div class="card-body">
                <!-- CREATE_POST: Create Post -->
                <div v-if="action.action_type === 'CREATE_POST' && action.action_args?.content" class="content-text main-text">
                  {{ action.action_args.content }}
                </div>

                <!-- QUOTE_POST: Quote Post -->
                <template v-if="action.action_type === 'QUOTE_POST'">
                  <div v-if="action.action_args?.quote_content" class="content-text">
                    {{ action.action_args.quote_content }}
                  </div>
                  <div v-if="action.action_args?.original_content" class="quoted-block">
                    <div class="quote-header">
                      <svg class="icon-small" viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path></svg>
                      <span class="quote-label">@{{ action.action_args.original_author_name || 'User' }}</span>
                    </div>
                    <div class="quote-text">
                      {{ truncateContent(action.action_args.original_content, 150) }}
                    </div>
                  </div>
                </template>

                <!-- REPOST: Repost -->
                <template v-if="action.action_type === 'REPOST'">
                  <div class="repost-info">
                    <svg class="icon-small" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><polyline points="17 1 21 5 17 9"></polyline><path d="M3 11V9a4 4 0 0 1 4-4h14"></path><polyline points="7 23 3 19 7 15"></polyline><path d="M21 13v2a4 4 0 0 1-4 4H3"></path></svg>
                    <span class="repost-label">Reposted from @{{ action.action_args?.original_author_name || 'User' }}</span>
                  </div>
                  <div v-if="action.action_args?.original_content" class="repost-content">
                    {{ truncateContent(action.action_args.original_content, 200) }}
                  </div>
                </template>

                <!-- LIKE_POST: Like Post -->
                <template v-if="action.action_type === 'LIKE_POST'">
                  <div class="like-info">
                    <svg class="icon-small filled" viewBox="0 0 24 24" width="14" height="14" fill="currentColor"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path></svg>
                    <span class="like-label">Liked @{{ action.action_args?.post_author_name || 'User' }}'s post</span>
                  </div>
                  <div v-if="action.action_args?.post_content" class="liked-content">
                    "{{ truncateContent(action.action_args.post_content, 120) }}"
                  </div>
                </template>

                <!-- CREATE_COMMENT: Create Comment -->
                <template v-if="action.action_type === 'CREATE_COMMENT'">
                  <div v-if="action.action_args?.content" class="content-text">
                    {{ action.action_args.content }}
                  </div>
                  <div v-if="action.action_args?.post_id" class="comment-context">
                    <svg class="icon-small" viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path></svg>
                    <span>Reply to post #{{ action.action_args.post_id }}</span>
                  </div>
                </template>

                <!-- SEARCH_POSTS: Search Posts -->
                <template v-if="action.action_type === 'SEARCH_POSTS'">
                  <div class="search-info">
                    <svg class="icon-small" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
                    <span class="search-label">Search Query:</span>
                    <span class="search-query">"{{ action.action_args?.query || '' }}"</span>
                  </div>
                </template>

                <!-- FOLLOW: Follow User -->
                <template v-if="action.action_type === 'FOLLOW'">
                  <div class="follow-info">
                    <svg class="icon-small" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="8.5" cy="7" r="4"></circle><line x1="20" y1="8" x2="20" y2="14"></line><line x1="23" y1="11" x2="17" y2="11"></line></svg>
                    <span class="follow-label">Followed @{{ action.action_args?.target_user || action.action_args?.user_id || 'User' }}</span>
                  </div>
                </template>

                <!-- UPVOTE / DOWNVOTE -->
                <template v-if="action.action_type === 'UPVOTE_POST' || action.action_type === 'DOWNVOTE_POST'">
                  <div class="vote-info">
                    <svg v-if="action.action_type === 'UPVOTE_POST'" class="icon-small" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><polyline points="18 15 12 9 6 15"></polyline></svg>
                    <svg v-else class="icon-small" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"></polyline></svg>
                    <span class="vote-label">{{ action.action_type === 'UPVOTE_POST' ? 'Upvoted' : 'Downvoted' }} Post</span>
                  </div>
                  <div v-if="action.action_args?.post_content" class="voted-content">
                    "{{ truncateContent(action.action_args.post_content, 120) }}"
                  </div>
                </template>

                <!-- DO_NOTHING: No Operation (Silent) -->
                <template v-if="action.action_type === 'DO_NOTHING'">
                  <div class="idle-info">
                    <svg class="icon-small" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
                    <span class="idle-label">Action Skipped</span>
                  </div>
                </template>

                <!-- General fallback: unknown type or has content not handled above -->
                <div v-if="!['CREATE_POST', 'QUOTE_POST', 'REPOST', 'LIKE_POST', 'CREATE_COMMENT', 'SEARCH_POSTS', 'FOLLOW', 'UPVOTE_POST', 'DOWNVOTE_POST', 'DO_NOTHING'].includes(action.action_type) && action.action_args?.content" class="content-text">
                  {{ action.action_args.content }}
                </div>
              </div>

              <div class="card-footer">
                <span class="time-tag">R{{ action.round_num }} • {{ formatActionTime(action.timestamp) }}</span>
                <!-- Platform tag removed as it is in header now -->
              </div>
            </div>
          </div>
        </TransitionGroup>

        <div v-if="allActions.length === 0" class="waiting-state">
          <div class="pulse-ring"></div>
          <span>Waiting for agent actions...</span>
        </div>
      </div>
    </div>

    <!-- Floating Windows Terminal Component -->
    <FloatingTerminal
      title="SIMULATION MONITOR"
      :sub-id="simulationId || 'NO_SIMULATION'"
      :logs="systemLogs"
      :is-active="runStatus.is_running || isGeneratingReport"
    />
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import {
  startSimulation,
  stopSimulation,
  getRunStatus,
  getRunStatusDetail
} from '../api/simulation'
import { generateReport } from '../api/report'
import FloatingTerminal from './FloatingTerminal.vue'

const { t } = useI18n()

const props = defineProps({
  simulationId: String,
  maxRounds: Number, // Max rounds passed from Step 2
  minutesPerRound: {
    type: Number,
    default: 30 // Default 30 minutes per round
  },
  projectData: Object,
  graphData: Object,
  systemLogs: Array
})

const emit = defineEmits(['go-back', 'next-step', 'add-log', 'update-status'])

const router = useRouter()

// State
const isGeneratingReport = ref(false)
const phase = ref(0) // 0: Not started, 1: Running, 2: Completed
const isStarting = ref(false)
const isStopping = ref(false)
const startError = ref(null)
const runStatus = ref({})
const allActions = ref([]) // All actions (incrementally accumulated)
const actionIds = ref(new Set()) // Action ID set for deduplication
const scrollContainer = ref(null)

// Computed
// Display actions in chronological order (newest at bottom)
const chronologicalActions = computed(() => {
  return allActions.value
})

// Action count per platform
const twitterActionsCount = computed(() => {
  return allActions.value.filter(a => a.platform === 'twitter').length
})

const redditActionsCount = computed(() => {
  return allActions.value.filter(a => a.platform === 'reddit').length
})

// Format simulated elapsed time (calculated from rounds and minutes per round)
const formatElapsedTime = (currentRound) => {
  if (!currentRound || currentRound <= 0) return '0h 0m'
  const totalMinutes = currentRound * props.minutesPerRound
  const hours = Math.floor(totalMinutes / 60)
  const minutes = totalMinutes % 60
  return `${hours}h ${minutes}m`
}

// Simulated elapsed time for Twitter platform
const twitterElapsedTime = computed(() => {
  return formatElapsedTime(runStatus.value.twitter_current_round || 0)
})

// Simulated elapsed time for Reddit platform
const redditElapsedTime = computed(() => {
  return formatElapsedTime(runStatus.value.reddit_current_round || 0)
})

// Methods
const addLog = (msg) => {
  emit('add-log', msg)
}

// Reset all state (used when restarting simulation)
const resetAllState = () => {
  phase.value = 0
  runStatus.value = {}
  allActions.value = []
  actionIds.value = new Set()
  prevTwitterRound.value = 0
  prevRedditRound.value = 0
  startError.value = null
  isStarting.value = false
  isStopping.value = false
  stopPolling()  // Stop any previous polling
}

// Start simulation
const doStartSimulation = async () => {
  if (!props.simulationId) {
    addLog(t('log.errorMissingSimId'))
    return
  }

  // Reset all state first to avoid interference from previous runs
  resetAllState()
  
  isStarting.value = true
  startError.value = null
  addLog(t('log.startingDualSim'))
  emit('update-status', 'processing')
  
  try {
    const params = {
      simulation_id: props.simulationId,
      platform: 'parallel',
      force: true,  // Force restart
      enable_graph_memory_update: true  // Enable dynamic graph update
    }
    
    if (props.maxRounds) {
      params.max_rounds = props.maxRounds
      addLog(t('log.setMaxRounds', { rounds: props.maxRounds }))
    }
    
    addLog(t('log.graphMemoryUpdateEnabled'))
    
    const res = await startSimulation(params)
    
    if (res.success && res.data) {
      if (res.data.force_restarted) {
        addLog(t('log.oldSimCleared'))
      }
      addLog(t('log.engineStarted'))
      addLog(`  ├─ PID: ${res.data.process_pid || '-'}`)
      
      phase.value = 1
      runStatus.value = res.data
      
      startStatusPolling()
      startDetailPolling()
    } else {
      startError.value = res.error || 'Failed to start'
      addLog(t('log.startFailed', { error: res.error || t('common.unknownError') }))
      emit('update-status', 'error')
    }
  } catch (err) {
    startError.value = err.message
    addLog(t('log.startException', { error: err.message }))
    emit('update-status', 'error')
  } finally {
    isStarting.value = false
  }
}

// Stop simulation
const handleStopSimulation = async () => {
  if (!props.simulationId) return
  
  isStopping.value = true
  addLog(t('log.stoppingSim'))
  
  try {
    const res = await stopSimulation({ simulation_id: props.simulationId })
    
    if (res.success) {
      addLog(t('log.simStoppedSuccess'))
      phase.value = 2
      stopPolling()
      emit('update-status', 'completed')
    } else {
      addLog(t('log.stopFailed', { error: res.error || t('common.unknownError') }))
    }
  } catch (err) {
    addLog(t('log.stopException', { error: err.message }))
  } finally {
    isStopping.value = false
  }
}

// Poll status
let statusTimer = null
let detailTimer = null

const startStatusPolling = () => {
  statusTimer = setInterval(fetchRunStatus, 2000)
}

const startDetailPolling = () => {
  detailTimer = setInterval(fetchRunStatusDetail, 3000)
}

const stopPolling = () => {
  if (statusTimer) {
    clearInterval(statusTimer)
    statusTimer = null
  }
  if (detailTimer) {
    clearInterval(detailTimer)
    detailTimer = null
  }
}

// Track last round per platform to detect changes and log
const prevTwitterRound = ref(0)
const prevRedditRound = ref(0)

const fetchRunStatus = async () => {
  if (!props.simulationId) return
  
  try {
    const res = await getRunStatus(props.simulationId)
    
    if (res.success && res.data) {
      const data = res.data
      
      runStatus.value = data
      
      // Detect round changes per platform separately and log
      if (data.twitter_current_round > prevTwitterRound.value) {
        addLog(`[Plaza] R${data.twitter_current_round}/${data.total_rounds} | T:${data.twitter_simulated_hours || 0}h | A:${data.twitter_actions_count}`)
        prevTwitterRound.value = data.twitter_current_round
      }
      
      if (data.reddit_current_round > prevRedditRound.value) {
        addLog(`[Community] R${data.reddit_current_round}/${data.total_rounds} | T:${data.reddit_simulated_hours || 0}h | A:${data.reddit_actions_count}`)
        prevRedditRound.value = data.reddit_current_round
      }
      
      // Detect if simulation completed (determined by runner_status or platform completion status)
      const isCompleted = data.runner_status === 'completed' || data.runner_status === 'stopped'
      const isFailed = data.runner_status === 'failed'
      
      // runner_status is authoritative because the backend only publishes a
      // terminal state after the Zep ingestion barrier has completed.
      if (isFailed) {
        addLog(t('log.simFailed') + (data.error ? `: ${data.error}` : ''))
        phase.value = 2
        stopPolling()
        emit('update-status', 'error')
      } else if (isCompleted) {
        addLog(t('log.simCompleted'))
        phase.value = 2
        stopPolling()
        emit('update-status', 'completed')
      }
    }
  } catch (err) {
    console.warn('Failed to get running status:', err)
  }
}

// Check if all enabled platforms have completed
const checkPlatformsCompleted = (data) => {
  // Return false if no platform data exists
  if (!data) return false
  
  // Check completion status per platform
  const twitterCompleted = data.twitter_completed === true
  const redditCompleted = data.reddit_completed === true
  
  // If at least one platform completed, check if all enabled platforms completed
  // Determine if platform is enabled via actions_count (if count > 0 or running was true)
  const twitterEnabled = (data.twitter_actions_count > 0) || data.twitter_running || twitterCompleted
  const redditEnabled = (data.reddit_actions_count > 0) || data.reddit_running || redditCompleted
  
  // Return false if no platform was enabled
  if (!twitterEnabled && !redditEnabled) return false
  
  // Check if all enabled platforms are complete
  if (twitterEnabled && !twitterCompleted) return false
  if (redditEnabled && !redditCompleted) return false
  
  return true
}

const fetchRunStatusDetail = async () => {
  if (!props.simulationId) return
  
  try {
    const res = await getRunStatusDetail(props.simulationId)
    
    if (res.success && res.data) {
      // Use all_actions to get full action list
      const serverActions = res.data.all_actions || []
      
      // Incrementally add new actions (deduplicated)
      let newActionsAdded = 0
      serverActions.forEach(action => {
        // Generate unique ID
        const actionId = action.id || `${action.timestamp}-${action.platform}-${action.agent_id}-${action.action_type}`
        
        if (!actionIds.value.has(actionId)) {
          actionIds.value.add(actionId)
          allActions.value.push({
            ...action,
            _uniqueId: actionId
          })
          newActionsAdded++
        }
      })
      
      // Do not auto-scroll, allow user to freely inspect timeline
      // New actions will append to the bottom
    }
  } catch (err) {
    console.warn('Failed to get detailed status:', err)
  }
}

// Helpers
const getActionTypeLabel = (type) => {
  const labels = {
    'CREATE_POST': 'POST',
    'REPOST': 'REPOST',
    'LIKE_POST': 'LIKE',
    'CREATE_COMMENT': 'COMMENT',
    'LIKE_COMMENT': 'LIKE',
    'DO_NOTHING': 'IDLE',
    'FOLLOW': 'FOLLOW',
    'SEARCH_POSTS': 'SEARCH',
    'QUOTE_POST': 'QUOTE',
    'UPVOTE_POST': 'UPVOTE',
    'DOWNVOTE_POST': 'DOWNVOTE'
  }
  return labels[type] || type || 'UNKNOWN'
}

const getActionTypeClass = (type) => {
  const classes = {
    'CREATE_POST': 'badge-post',
    'REPOST': 'badge-action',
    'LIKE_POST': 'badge-action',
    'CREATE_COMMENT': 'badge-comment',
    'LIKE_COMMENT': 'badge-action',
    'QUOTE_POST': 'badge-post',
    'FOLLOW': 'badge-meta',
    'SEARCH_POSTS': 'badge-meta',
    'UPVOTE_POST': 'badge-action',
    'DOWNVOTE_POST': 'badge-action',
    'DO_NOTHING': 'badge-idle'
  }
  return classes[type] || 'badge-default'
}

const truncateContent = (content, maxLength = 100) => {
  if (!content) return ''
  if (content.length > maxLength) return content.substring(0, maxLength) + '...'
  return content
}

const formatActionTime = (timestamp) => {
  if (!timestamp) return ''
  try {
    return new Date(timestamp).toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' })
  } catch {
    return ''
  }
}

const handleNextStep = async () => {
  if (!props.simulationId) {
    addLog(t('log.errorMissingSimId'))
    return
  }

  if (isGeneratingReport.value) {
    addLog(t('log.reportRequestSent'))
    return
  }
  
  isGeneratingReport.value = true
  addLog(t('log.startingReportGen'))
  
  try {
    const res = await generateReport({
      simulation_id: props.simulationId,
      force_regenerate: true
    })
    
    if (res.success && res.data) {
      const reportId = res.data.report_id
      addLog(t('log.reportGenTaskStarted', { reportId }))
      
      // Navigate to report page
      router.push({ name: 'Report', params: { reportId } })
    } else {
      addLog(t('log.reportGenFailed', { error: res.error || t('common.unknownError') }))
      isGeneratingReport.value = false
    }
  } catch (err) {
    addLog(t('log.reportGenException', { error: err.message }))
    isGeneratingReport.value = false
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
  addLog(t('log.step3Init'))
  if (props.simulationId) {
    doStartSimulation()
  }
})

onUnmounted(() => {
  stopPolling()
})
</script>

<style scoped>
.simulation-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: radial-gradient(circle at 85% 15%, #0e0e14 0%, #060608 60%, #020203 100%);
  color: #f5f5f7;
  font-family: var(--font-body, system-ui, sans-serif);
  position: relative;
  overflow: hidden;
}

/* Background Cyber Patterns */
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

/* --- Control Bar --- */
.control-bar {
  background: rgba(12, 12, 16, 0.85);
  backdrop-filter: blur(12px);
  padding: 12px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  z-index: 10;
  height: 64px;
}

.status-group {
  display: flex;
  gap: 12px;
}

/* Platform Status Cards */
.platform-status {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 6px 14px;
  border-radius: 8px;
  background: rgba(18, 18, 24, 0.85);
  border: 1px solid rgba(255, 255, 255, 0.12);
  transition: all 0.25s ease;
  min-width: 140px;
  position: relative;
  cursor: pointer;
}

.platform-status:hover {
  border-color: rgba(255, 255, 255, 0.35);
  background: rgba(24, 24, 32, 0.9);
}

.platform-status.active {
  border-color: #FFFFFF;
  background: rgba(24, 24, 32, 0.95);
}

.platform-status.completed {
  border-color: #94A3B8;
  background: rgba(20, 20, 26, 0.9);
}

/* Actions Tooltip */
.actions-tooltip {
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  margin-top: 8px;
  padding: 10px 14px;
  background: rgba(10, 10, 14, 0.96);
  color: #FFF;
  border-radius: 6px;
  border: 1px solid rgba(255, 255, 255, 0.18);
  opacity: 0;
  visibility: hidden;
  transition: all 0.2s ease;
  z-index: 100;
  min-width: 180px;
  pointer-events: none;
}

.actions-tooltip::before {
  content: '';
  position: absolute;
  top: -6px;
  left: 50%;
  transform: translateX(-50%);
  border-left: 6px solid transparent;
  border-right: 6px solid transparent;
  border-bottom: 6px solid rgba(255, 255, 255, 0.18);
}

.platform-status:hover .actions-tooltip {
  opacity: 1;
  visibility: visible;
}

.tooltip-title {
  font-family: 'JetBrains Mono', monospace;
  font-size: 10px;
  font-weight: 700;
  color: #94A3B8;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-bottom: 8px;
}

.tooltip-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.tooltip-action {
  font-family: 'JetBrains Mono', monospace;
  font-size: 9px;
  font-weight: 600;
  padding: 3px 8px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 4px;
  color: #e4e4e7;
  letter-spacing: 0.03em;
}

.platform-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 2px;
}

.platform-name {
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  font-weight: 700;
  color: #FFFFFF;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.platform-icon {
  color: #94A3B8;
}

.platform-status.active .platform-icon {
  color: #FFFFFF;
}

.platform-stats {
  display: flex;
  gap: 10px;
}

.stat {
  display: flex;
  align-items: baseline;
  gap: 3px;
}

.stat-label {
  font-family: 'JetBrains Mono', monospace;
  font-size: 8px;
  color: #71717a;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.stat-value {
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  font-weight: 700;
  color: #FFFFFF;
}

.stat-total, .stat-unit {
  font-size: 9px;
  color: #71717a;
  font-weight: 400;
}

.status-badge {
  margin-left: auto;
  color: #94A3B8;
  display: flex;
  align-items: center;
}

/* Action Controls & Buttons */
.action-controls {
  display: flex;
  align-items: center;
  gap: 10px;
}

.action-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 22px;
  font-size: 12px;
  font-weight: 700;
  border-radius: 999px;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-family: 'JetBrains Mono', monospace;
}

.action-btn.primary {
  background: #FFFFFF;
  color: #000000;
  border: 1px solid #FFFFFF;
}

.action-btn.primary:hover:not(:disabled) {
  background: #000000;
  color: #FFFFFF;
  border-color: #FFFFFF;
  transform: translateY(-1px);
}

.action-btn.secondary {
  background: rgba(22, 22, 30, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #FFFFFF;
}

.action-btn.secondary:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.12);
  border-color: rgba(255, 255, 255, 0.4);
  transform: translateY(-1px);
}

.action-btn:disabled {
  background: rgba(255, 255, 255, 0.04);
  color: #52525b;
  border: 1px solid rgba(255, 255, 255, 0.08);
  cursor: not-allowed;
  opacity: 0.6;
}

/* --- Main Content Area --- */
.main-content-area {
  flex: 1;
  overflow-y: auto;
  position: relative;
  background: transparent;
  z-index: 1;
}

.main-content-area::-webkit-scrollbar {
  width: 6px;
}

.main-content-area::-webkit-scrollbar-track {
  background: transparent;
}

.main-content-area::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.12);
  border-radius: 999px;
}

.main-content-area::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.25);
}

/* Timeline Header */
.timeline-header {
  position: sticky;
  top: 0;
  background: rgba(12, 12, 16, 0.85);
  backdrop-filter: blur(12px);
  padding: 12px 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  z-index: 5;
  display: flex;
  justify-content: center;
}

.timeline-stats {
  display: flex;
  align-items: center;
  gap: 16px;
  font-size: 11px;
  color: #a1a1aa;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.12);
  padding: 5px 16px;
  border-radius: 20px;
}

.total-count {
  font-family: 'JetBrains Mono', monospace;
  font-weight: 700;
  color: #FFFFFF;
}

.platform-breakdown {
  display: flex;
  align-items: center;
  gap: 8px;
}

.breakdown-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-family: 'JetBrains Mono', monospace;
  font-weight: 600;
  color: #94A3B8;
}

.breakdown-divider {
  color: rgba(255, 255, 255, 0.2);
}

/* --- Timeline Feed --- */
.timeline-feed {
  padding: 24px 0;
  position: relative;
  min-height: 100%;
  max-width: 900px;
  margin: 0 auto;
}

.timeline-axis {
  position: absolute;
  left: 50%;
  top: 0;
  bottom: 0;
  width: 1px;
  background: rgba(255, 255, 255, 0.12);
  transform: translateX(-50%);
}

.timeline-item {
  display: flex;
  justify-content: center;
  margin-bottom: 32px;
  position: relative;
  width: 100%;
}

.timeline-marker {
  position: absolute;
  left: 50%;
  top: 24px;
  width: 10px;
  height: 10px;
  background: #08080c;
  border: 1px solid rgba(255, 255, 255, 0.4);
  border-radius: 50%;
  transform: translateX(-50%);
  z-index: 2;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.marker-dot {
  width: 4px;
  height: 4px;
  background: #FFFFFF;
  border-radius: 50%;
}

.timeline-item:hover .timeline-marker {
  border-color: #FFFFFF;
  transform: translateX(-50%) scale(1.2);
}

/* Card Layout */
.timeline-card {
  width: calc(100% - 48px);
  background: rgba(14, 14, 18, 0.85);
  border-radius: 12px;
  padding: 16px 20px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  position: relative;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.timeline-card:hover {
  border-color: rgba(255, 255, 255, 0.38);
  background: rgba(20, 20, 26, 0.95);
  transform: translateY(-1px);
}

/* Left side (Twitter) */
.timeline-item.twitter {
  justify-content: flex-start;
  padding-right: 50%;
}
.timeline-item.twitter .timeline-card {
  margin-left: auto;
  margin-right: 32px;
}

/* Right side (Reddit) */
.timeline-item.reddit {
  justify-content: flex-end;
  padding-left: 50%;
}
.timeline-item.reddit .timeline-card {
  margin-right: auto;
  margin-left: 32px;
}

/* Card Content Styles */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.agent-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.avatar-placeholder {
  width: 24px;
  height: 24px;
  background: #FFFFFF;
  color: #000000;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  font-weight: 800;
  text-transform: uppercase;
}

.agent-name {
  font-size: 13px;
  font-weight: 700;
  color: #FFFFFF;
}

.header-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}

.platform-indicator {
  color: #94A3B8;
  display: flex;
  align-items: center;
}

.action-badge {
  font-family: 'JetBrains Mono', monospace;
  font-size: 9px;
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border: 1px solid transparent;
}

/* Monochromatic Badges */
.badge-post {
  background: rgba(255, 255, 255, 0.12);
  color: #FFFFFF;
  border: 1px solid #FFFFFF;
}

.badge-comment {
  background: rgba(255, 255, 255, 0.08);
  color: #e4e4e7;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.badge-action {
  background: rgba(255, 255, 255, 0.05);
  color: #94A3B8;
  border: 1px solid rgba(255, 255, 255, 0.15);
}

.badge-meta {
  background: rgba(255, 255, 255, 0.03);
  color: #71717a;
  border: 1px dashed rgba(255, 255, 255, 0.15);
}

.badge-idle {
  background: transparent;
  color: #52525b;
  border: 1px dashed rgba(255, 255, 255, 0.08);
  opacity: 0.6;
}

.content-text {
  font-size: 13px;
  line-height: 1.6;
  color: #d4d4d8;
  margin-bottom: 10px;
}

.content-text.main-text {
  font-size: 14px;
  color: #FFFFFF;
}

/* Info Blocks (Quote, Repost, etc) */
.quoted-block, .repost-content {
  background: rgba(24, 24, 32, 0.85);
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 10px 14px;
  border-radius: 8px;
  margin-top: 8px;
  font-size: 12px;
  color: #d4d4d8;
}

.quote-header, .repost-info, .like-info, .search-info, .follow-info, .vote-info, .idle-info, .comment-context {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 6px;
  font-size: 11px;
  color: #a1a1aa;
}

.icon-small {
  color: #94A3B8;
}
.icon-small.filled {
  color: #FFFFFF;
}

.search-query {
  font-family: 'JetBrains Mono', monospace;
  background: rgba(255, 255, 255, 0.08);
  padding: 1px 6px;
  border-radius: 4px;
  color: #FFFFFF;
}

.card-footer {
  margin-top: 12px;
  display: flex;
  justify-content: flex-end;
  font-size: 10px;
  color: #71717a;
  font-family: 'JetBrains Mono', monospace;
}

/* Waiting State */
.waiting-state {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  color: #71717a;
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.pulse-ring {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 1px solid rgba(255, 255, 255, 0.25);
  animation: ripple 2s infinite;
}

@keyframes ripple {
  0% { transform: scale(0.8); opacity: 1; border-color: #FFFFFF; }
  100% { transform: scale(2.5); opacity: 0; border-color: rgba(255, 255, 255, 0.1); }
}

/* Animation */
.timeline-item-enter-active,
.timeline-item-leave-active {
  transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
}

.timeline-item-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.timeline-item-leave-to {
  opacity: 0;
}

/* Logs */
.system-logs {
  background: #000;
  color: #DDD;
  padding: 16px;
  font-family: 'JetBrains Mono', monospace;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
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
  height: 100px;
  overflow-y: auto;
  padding-right: 4px;
}

.log-content::-webkit-scrollbar { width: 4px; }
.log-content::-webkit-scrollbar-thumb { background: rgba(255, 255, 255, 0.15); border-radius: 2px; }

.log-line {
  font-size: 11px;
  display: flex;
  gap: 12px;
  line-height: 1.5;
}

.log-time { color: #71717a; min-width: 75px; }
.log-msg { color: #e4e4e7; word-break: break-all; }
.mono { font-family: 'JetBrains Mono', monospace; }

/* Loading spinner for button */
.loading-spinner-small {
  display: inline-block;
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #FFF;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-right: 6px;
}
</style>
