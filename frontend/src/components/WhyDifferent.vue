<template>
  <div class="why-different-container space-y-6 text-neutral-100">
    <!-- Header Hero Banner -->
    <div class="why-header-box relative p-6 sm:p-8 rounded-2xl bg-black/70 border border-white/12 backdrop-blur-xl overflow-hidden shadow-[0_8px_32px_rgba(0,0,0,0.85)]">
      <!-- Ambient Backlight Gradient -->
      
      
      
      <div class="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div class="space-y-3 max-w-2xl">
          <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/8 border border-white/15 text-[11px] font-mono tracking-wider uppercase text-neutral-300">
            <span class="w-1.5 h-1.5 rounded-full bg-white animate-pulse"></span>
            System Architecture &bull; Technical Differentiation
          </div>

          <h2 class="text-2xl sm:text-3xl md:text-4xl font-extrabold tracking-tight text-white leading-tight font-display">
            LOKĀNTRA <span class="text-neutral-400 font-normal">&mdash;</span> The technology behind the intelligence
          </h2>

          <p class="text-xs sm:text-sm text-neutral-300/90 leading-relaxed font-body">
            An architectural breakdown of the 7 specialized engines powering parallel-world simulations. 
            From GraphRAG ontology and neuromorphic reflex routing to multi-agent social interrogation and token-aware grounding.
          </p>
        </div>

        <!-- Metric Badges Column -->
        <div class="flex flex-row md:flex-col gap-3 shrink-0">
          <div class="px-4 py-2.5 rounded-xl bg-neutral-950/80 border border-white/10 flex items-center gap-3">
            <span class="text-xl font-bold font-mono text-white">07</span>
            <div class="text-[11px] font-mono text-neutral-400 leading-tight">
              <span class="block text-white font-medium">Core Pillars</span>
              Engine Architecture
            </div>
          </div>
          <div class="px-4 py-2.5 rounded-xl bg-neutral-950/80 border border-white/10 flex items-center gap-3">
            <span class="text-xl font-bold font-mono text-white">&infin;</span>
            <div class="text-[11px] font-mono text-neutral-400 leading-tight">
              <span class="block text-white font-medium">Parallel States</span>
              Swarm Dynamics
            </div>
          </div>
        </div>
      </div>

      <!-- Quick Category Filter Bar & Search -->
      <div class="mt-6 pt-5 border-t border-white/10 flex flex-wrap items-center justify-between gap-3 relative z-10">
        <div class="flex flex-wrap items-center gap-1.5 sm:gap-2">
          <button
            v-for="cat in categories"
            :key="cat.id"
            @click="activeCategory = cat.id"
            type="button"
            :class="[
              'px-3 py-1.5 rounded-lg text-xs font-mono transition-all duration-200 cursor-pointer flex items-center gap-1.5',
              activeCategory === cat.id
                ? 'bg-white text-black font-bold shadow-md shadow-black/80'
                : 'bg-black/50 text-neutral-400 hover:text-white hover:bg-neutral-900 border border-white/10'
            ]"
          >
            <span>{{ cat.label }}</span>
            <span 
              :class="[
                'text-[10px] px-1.5 py-0.2 rounded-full font-bold',
                activeCategory === cat.id ? 'bg-black text-white' : 'bg-white/10 text-neutral-300'
              ]"
            >
              {{ cat.count }}
            </span>
          </button>
        </div>

        <!-- Search Input -->
        <div class="relative w-full sm:w-64">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search technology, model, paper..."
            class="w-full pl-8 pr-3 py-1.5 rounded-lg bg-black/60 border border-white/15 focus:border-white/50 text-xs text-white placeholder-neutral-500 font-mono transition-colors outline-none"
          />
          <svg class="w-3.5 h-3.5 text-neutral-400 absolute left-2.5 top-1/2 -translate-y-1/2 pointer-events-none" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="8"/>
            <line x1="21" y1="21" x2="16.65" y2="16.65"/>
          </svg>
          <button 
            v-if="searchQuery" 
            @click="searchQuery = ''" 
            class="absolute right-2.5 top-1/2 -translate-y-1/2 text-neutral-400 hover:text-white text-xs"
          >
            &times;
          </button>
        </div>
      </div>
    </div>

    <!-- The 7 Architecture Pillars Cards List -->
    <div class="space-y-4">
      <div
        v-for="item in filteredItems"
        :key="item.id"
        class="pillar-card group relative p-6 rounded-2xl bg-black/75 border border-white/12 hover:border-white/35 transition-all duration-300 backdrop-blur-md overflow-hidden shadow-[0_4px_24px_rgba(0,0,0,0.6)]"
      >
        <!-- Subtle corner notch viewfinder decoration -->
        <div class="absolute top-0 right-0 w-8 h-8 pointer-events-none overflow-hidden">
          <div class="absolute top-0 right-0 w-4 h-4 border-t border-r border-white/20 group-hover:border-white/60 transition-colors"></div>
        </div>

        <!-- Card Top Bar: Number, Category, Status Tag & External Links -->
        <div class="flex flex-wrap items-center justify-between gap-3 mb-4 pb-3 border-b border-white/8">
          <div class="flex items-center gap-3">
            <span class="pillar-num font-mono text-base font-bold text-white px-2.5 py-0.5 rounded-md bg-white/10 border border-white/20 ">
              {{ item.number }}
            </span>
            <span class="text-[11px] font-mono tracking-widest uppercase text-neutral-400">
              {{ item.category }}
            </span>
          </div>

          <div class="flex items-center gap-2 flex-wrap">
            <!-- External Links if any -->
            <a
              v-for="link in item.links"
              :key="link.url"
              :href="link.url"
              target="_blank"
              rel="noopener noreferrer"
              class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-white/5 hover:bg-white/15 border border-white/15 text-[11px] font-mono text-neutral-300 hover:text-white transition-all cursor-pointer group/link"
              :title="`Open ${link.label}`"
            >
              <!-- Github or External Icon -->
              <svg v-if="link.icon === 'github'" class="w-3 h-3 fill-current" viewBox="0 0 24 24">
                <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/>
              </svg>
              <svg v-else class="w-2.5 h-2.5 stroke-current" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/>
              </svg>
              <span>{{ link.label }}</span>
              <span class="text-neutral-500 group-hover/link:translate-x-0.5 transition-transform">&rarr;</span>
            </a>

            <!-- Status Indicator Pill -->
            <span 
              :class="[
                'inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-mono tracking-wide uppercase font-semibold border',
                item.statusType === 'active'
                  ? 'bg-white/10 text-neutral-200 border-white/20'
                  : item.statusType === 'notice'
                  ? 'bg-amber-400/10 text-amber-300 border-amber-400/25'
                  : 'bg-blue-400/10 text-blue-300 border-blue-400/25'
              ]"
            >
              <span 
                :class="[
                  'w-1.5 h-1.5 rounded-full',
                  item.statusType === 'active'
                    ? 'bg-white '
                    : item.statusType === 'notice'
                    ? 'bg-amber-400 '
                    : 'bg-blue-400 '
                ]"
              ></span>
              {{ item.statusBadge }}
            </span>
          </div>
        </div>

        <!-- Pillar Title -->
        <h3 class="text-xl sm:text-2xl font-bold text-white mb-4 tracking-tight flex items-center gap-2 font-display">
          <span>{{ item.title }}</span>
        </h3>

        <!-- Core Two-Column Info Layout -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6 mb-4">
          <!-- "What it is" Block -->
          <div class="info-block p-4 rounded-xl bg-black/50 border border-white/8 space-y-1.5">
            <div class="text-[11px] font-mono uppercase tracking-wider text-neutral-400 font-semibold flex items-center gap-1.5">
              <span class="w-1 h-1 rounded-full bg-neutral-400"></span>
              What it is
            </div>
            <p class="text-xs sm:text-sm text-neutral-200 leading-relaxed font-body">
              {{ item.whatItIs }}
            </p>
          </div>

          <!-- "How LOKĀNTRA uses it" Block -->
          <div class="info-block p-4 rounded-xl bg-black/50 border border-white/8 space-y-1.5">
            <div class="text-[11px] font-mono uppercase tracking-wider text-neutral-400 font-semibold flex items-center gap-1.5">
              <span class="w-1 h-1 rounded-full bg-white"></span>
              {{ item.usageHeading || 'How LOKĀNTRA uses it' }}
            </div>
            <p class="text-xs sm:text-sm text-neutral-200 leading-relaxed font-body">
              {{ item.howLokantraUsesIt }}
            </p>
          </div>
        </div>

        <!-- Technology Stack Chips (if provided) -->
        <div v-if="item.technology" class="mb-3.5 flex flex-wrap items-center gap-2">
          <span class="text-[11px] font-mono text-neutral-400 uppercase tracking-wider mr-1">
            Technology:
          </span>
          <span 
            v-for="(tech, tIdx) in item.technology" 
            :key="tIdx"
            class="px-2.5 py-1 rounded-md bg-neutral-900 border border-white/12 text-xs font-mono text-neutral-200 flex items-center gap-1.5"
          >
            <span class="w-1 h-1 rounded-full bg-white/70"></span>
            {{ tech }}
          </span>
        </div>

        <!-- THE KEY IDEA Callout (for Item 6) -->
        <div v-if="item.keyIdea" class="key-idea-box p-4 rounded-xl bg-gradient-to-r from-white/8 via-white/5 to-transparent border-l-2 border-white border-y border-r border-white/10 my-3">
          <div class="text-[10px] font-mono uppercase tracking-widest text-neutral-300 mb-1 flex items-center gap-1.5">
            <span class="text-white font-bold">&bull;</span>
            The Key Idea
          </div>
          <p class="text-sm sm:text-base font-semibold text-white tracking-tight italic font-display">
            &ldquo;{{ item.keyIdea }}&rdquo;
          </p>
        </div>

        <!-- WHY IT MATTERS Callout (for Item 7) -->
        <div v-if="item.whyItMatters" class="why-matters-box p-4 rounded-xl bg-neutral-950/90 border border-white/15 my-3 space-y-1.5">
          <div class="text-[10px] font-mono uppercase tracking-widest text-neutral-300 flex items-center gap-1.5 font-bold">
            <span class="w-1.5 h-1.5 rounded-full bg-white "></span>
            Why it matters
          </div>
          <p class="text-xs sm:text-sm text-neutral-300 leading-relaxed font-body">
            {{ item.whyItMatters }}
          </p>
        </div>

        <!-- Status / Transparency Notice Banner (for LAYA, BrainChip Akida, etc.) -->
        <div 
          v-if="item.statusNotice" 
          :class="[
            'status-notice-box p-3.5 rounded-xl border flex items-start gap-3 my-2 text-xs font-mono',
            item.statusType === 'notice'
              ? 'bg-amber-950/20 border-amber-400/30 text-amber-200/90'
              : 'bg-neutral-950/80 border-white/20 text-neutral-300'
          ]"
        >
          <div class="shrink-0 mt-0.5">
            <svg v-if="item.statusType === 'notice'" class="w-4 h-4 text-amber-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
            </svg>
            <svg v-else class="w-4 h-4 text-blue-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/>
              <line x1="12" y1="16" x2="12" y2="12"/>
              <line x1="12" y1="8" x2="12.01" y2="8"/>
            </svg>
          </div>
          <div class="space-y-1">
            <div class="font-bold uppercase tracking-wider text-[11px]" :class="item.statusType === 'notice' ? 'text-amber-300' : 'text-white'">
              Status &bull; Architectural Verification Note
            </div>
            <p class="leading-relaxed">
              {{ item.statusNotice }}
            </p>
          </div>
        </div>

        <!-- Technical Capabilities Tags -->
        <div class="pt-3 border-t border-white/6 flex flex-wrap items-center gap-1.5">
          <span 
            v-for="(cap, cIdx) in item.capabilities" 
            :key="cIdx"
            class="text-[10px] font-mono px-2 py-0.5 rounded bg-white/5 hover:bg-white/10 text-neutral-400 border border-white/8 transition-colors"
          >
            #{{ cap }}
          </span>
        </div>
      </div>
    </div>

    <!-- Bottom Architectural Summary Footer -->
    <div class="p-6 rounded-2xl bg-black/60 border border-white/10 text-center space-y-3">
      <div class="text-xs font-mono tracking-widest uppercase text-neutral-400">
        Empirical Rigor &bull; Architectural Integrity
      </div>
      <p class="text-xs sm:text-sm text-neutral-300 max-w-2xl mx-auto leading-relaxed">
        LOKĀNTRA replaces conversational guessing with multi-agent consensus dynamics, verifiable knowledge graphs, and empirical interrogation.
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const searchQuery = ref('')
const activeCategory = ref('all')

const categories = [
  { id: 'all', label: 'All 7 Pillars', count: 7 },
  { id: 'graph', label: 'Graph & Memory', count: 2 },
  { id: 'swarm', label: 'Agent Swarm', count: 2 },
  { id: 'reflex', label: 'Reflex & Neuromorphic', count: 2 },
  { id: 'grounding', label: 'Token & Evidence', count: 1 }
]

const pillars = [
  {
    id: 'graphrag',
    number: '01',
    title: 'GraphRAG & Ontology Engineering',
    category: 'Knowledge Representation',
    catGroup: 'graph',
    statusBadge: 'Active Engine',
    statusType: 'active',
    whatItIs: 'Graph-based knowledge representation combined with retrieval-augmented generation.',
    howLokantraUsesIt: 'Extracts entities, relationships, and domain-specific structures from uploaded documents to build a knowledge graph that provides context for simulations.',
    usageHeading: 'How LOKĀNTRA uses it',
    technology: ['Ontology generation', 'TigerGraph', 'Zep Cloud'],
    capabilities: [
      'entity-relationship-extraction',
      'ontology-induction',
      'subgraph-retrieval',
      'semantic-grounding'
    ],
    links: [
      { label: 'TigerGraph', url: 'https://www.tigergraph.com/', icon: 'external' },
      { label: 'Zep Cloud', url: 'https://www.getzep.com/', icon: 'external' }
    ]
  },
  {
    id: 'camel-oasis',
    number: '02',
    title: 'CAMEL-AI & OASIS',
    category: 'Multi-Agent Simulation Framework',
    catGroup: 'swarm',
    statusBadge: 'Core Swarm Runtime',
    statusType: 'active',
    whatItIs: 'CAMEL-AI is an open-source multi-agent AI framework; OASIS is its social simulation framework for creating AI-driven social media users and interactions.',
    howLokantraUsesIt: 'Creates simulated personas that post, react, comment, and interact in Reddit-style and Twitter-style environments to explore how scenarios may develop.',
    usageHeading: 'How LOKĀNTRA uses it',
    capabilities: [
      'persona-synthesis',
      'reddit-thread-simulation',
      'twitter-feed-dynamics',
      'emergent-consensus',
      'parallel-conversations'
    ],
    links: [
      { label: 'GitHub: CAMEL-AI / OASIS', url: 'https://github.com/camel-ai/oasis', icon: 'github' }
    ]
  },
  {
    id: 'laya',
    number: '03',
    title: 'LAYA — System 1 Decision Intelligence',
    category: 'Fast Reflex Routing & Classification',
    catGroup: 'reflex',
    statusBadge: 'Configured in Repo',
    statusType: 'notice',
    whatItIs: 'A non-autoregressive AI decision model that classifies inputs and answers structured decision questions with probability estimates, rather than generating a conversational response.',
    howLokantraUsesIt: 'Quickly classify simulation states or route decisions before invoking a larger language model for complex reasoning.',
    usageHeading: 'Potential role in LOKĀNTRA',
    statusNotice: 'The model is configured in the repository; confirm that it is actually loaded and used at runtime before claiming this capability is active.',
    capabilities: [
      'non-autoregressive',
      'probability-estimates',
      'system-1-fast-reflex',
      'decision-router'
    ],
    links: [
      { label: 'Hugging Face', url: 'https://huggingface.co/models?search=laya', icon: 'external' }
    ]
  },
  {
    id: 'brainchip-akida',
    number: '04',
    title: 'BrainChip Akida — Neuromorphic Computing',
    category: 'Event-Driven Neuromorphic Architecture',
    catGroup: 'reflex',
    statusBadge: 'Experimental Path',
    statusType: 'notice',
    whatItIs: 'A brain-inspired neural processor designed for low-power, event-driven AI processing, particularly on edge devices.',
    howLokantraUsesIt: 'Explore a lightweight reflex gate that could handle suitable decisions before more expensive reasoning is engaged.',
    usageHeading: 'Research direction for LOKĀNTRA',
    statusNotice: 'Experimental integration path. The repository\'s example configuration defaults to a heuristic gate, so don\'t claim actual Akida hardware acceleration yet.',
    capabilities: [
      'neuromorphic-spiking-neural-nets',
      'event-driven-reflex-gate',
      'low-power-edge-inference',
      'spiking-heuristics'
    ],
    links: [
      { label: 'BrainChip Akida', url: 'https://brainchip.com/', icon: 'external' }
    ]
  },
  {
    id: 'graph-memory',
    number: '05',
    title: 'Graph-Backed Memory',
    category: 'Relational & Temporal Memory Architecture',
    catGroup: 'graph',
    statusBadge: 'Active Memory Tier',
    statusType: 'active',
    whatItIs: 'A memory architecture that represents information through connected entities and relationships, making relevant context retrievable.',
    howLokantraUsesIt: 'Connects agent activity and simulation context to graph services for memory updates, report investigation, and follow-up questions.',
    usageHeading: 'How LOKĀNTRA uses it',
    technology: ['Zep Cloud', 'TigerGraph-backed services'],
    capabilities: [
      'connected-entities',
      'temporal-memory-updates',
      'state-persistence',
      'relational-recall'
    ],
    links: [
      { label: 'TigerGraph', url: 'https://www.tigergraph.com/', icon: 'external' },
      { label: 'Zep Memory', url: 'https://www.getzep.com/', icon: 'external' }
    ]
  },
  {
    id: 'agent-interrogation',
    number: '06',
    title: 'Agent Interrogation & Report Intelligence',
    category: 'Interactive Audit & Empirical Investigation',
    catGroup: 'swarm',
    statusBadge: 'Interactive Audit Suite',
    statusType: 'active',
    whatItIs: 'Interactive investigation through agent interviews and a tool-using report agent.',
    howLokantraUsesIt: 'After a simulation, users can ask specific agents about their decisions and reactions, investigate the simulated world, ask the report agent follow-up questions, and export findings as PDFs.',
    usageHeading: 'How LOKĀNTRA uses it',
    keyIdea: 'The report tells you what happened. The agents help you explore why.',
    capabilities: [
      'agent-1-on-1-interrogation',
      'tool-using-report-agent',
      'cross-entity-tracing',
      'pdf-intelligence-export'
    ]
  },
  {
    id: 'evidence-grounded',
    number: '07',
    title: 'Evidence-Grounded & Token-Aware AI',
    category: 'Token Efficiency & Anti-Hallucination Rigor',
    catGroup: 'grounding',
    statusBadge: 'Empirical Grounding',
    statusType: 'active',
    whatItIs: 'A combination of retrieval, selective context construction, structured outputs, and validation.',
    howLokantraUsesIt: 'Selects representative document chunks, limits context passed into certain generation stages, and instructs the report agent to retrieve evidence before producing analysis.',
    usageHeading: 'How LOKĀNTRA uses it',
    whyItMatters: 'These mechanisms are designed to reduce unnecessary token usage and unsupported claims. Actual cost savings and hallucination rates must be measured; neither is guaranteed by the architecture alone.',
    capabilities: [
      'selective-chunk-sampling',
      'token-budget-enforcement',
      'evidence-before-analysis',
      'schema-validation'
    ]
  }
]

const filteredItems = computed(() => {
  let list = pillars

  if (activeCategory.value !== 'all') {
    list = list.filter(item => item.catGroup === activeCategory.value)
  }

  if (searchQuery.value.trim()) {
    const q = searchQuery.value.toLowerCase().trim()
    list = list.filter(item => {
      return (
        item.title.toLowerCase().includes(q) ||
        item.category.toLowerCase().includes(q) ||
        item.whatItIs.toLowerCase().includes(q) ||
        item.howLokantraUsesIt.toLowerCase().includes(q) ||
        (item.keyIdea && item.keyIdea.toLowerCase().includes(q)) ||
        (item.whyItMatters && item.whyItMatters.toLowerCase().includes(q)) ||
        (item.technology && item.technology.some(t => t.toLowerCase().includes(q))) ||
        (item.capabilities && item.capabilities.some(c => c.toLowerCase().includes(q)))
      )
    })
  }

  return list
})
</script>

<style scoped>
.pillar-card {
  box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.85);
}

.pillar-card:hover {
  box-shadow: 0 8px 32px -4px rgba(0, 0, 0, 0.98);
}

.key-idea-box {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.6);
}
</style>
