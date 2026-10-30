<template>
  <div class="viasocket-governance-container">
    <!-- Floating Trigger Pill Button -->
    <button 
      class="viasocket-trigger-btn"
      :class="{ 'has-pending': pendingCount > 0 }"
      @click="toggleDrawer"
      title="viaSocket Action Execution & Governance Hub"
    >
      <div class="trigger-pulse" :class="{ 'pulse-amber': pendingCount > 0, 'pulse-green': pendingCount === 0 }"></div>
      <span class="trigger-icon">⚡</span>
      <span class="trigger-label">viaSocket</span>
      <span class="trigger-badge" v-if="pendingCount > 0">{{ pendingCount }} Pending</span>
      <span class="trigger-status" v-else>Governed</span>
    </button>

    <!-- Slide-over Drawer / Modal -->
    <div v-if="isOpen" class="governance-overlay" @click.self="toggleDrawer">
      <div class="governance-drawer">
        <!-- Header -->
        <div class="drawer-header">
          <div class="header-branding">
            <span class="hub-tag">ENTERPRISE GOVERNANCE</span>
            <h2 class="hub-title">
              <span class="accent-text">viaSocket</span> Action Execution Service
            </h2>
            <p class="hub-subtitle">
              Role-Based Scoping Registry • Default-Deny Firewall • Human-in-the-Loop Gateway
            </p>
          </div>
          <button class="close-btn" @click="toggleDrawer" title="Close">✕</button>
        </div>

        <!-- Connection & Metric Status Bar -->
        <div class="status-metric-strip">
          <div class="metric-box">
            <span class="metric-label">Connection Mode</span>
            <div class="metric-val">
              <span class="status-indicator-dot" :class="statusData.configured ? 'live' : 'mock'"></span>
              <span>{{ statusData.configured ? 'Live MCP SSE' : 'Enterprise Sandbox' }}</span>
            </div>
          </div>
          <div class="metric-box">
            <span class="metric-label">Integrations</span>
            <div class="metric-val font-mono">2,300+ Tools</div>
          </div>
          <div class="metric-box">
            <span class="metric-label">Policy Status</span>
            <div class="metric-val text-cyan">Default-Deny Active</div>
          </div>
          <div class="metric-box">
            <span class="metric-label">Pending HITL</span>
            <div class="metric-val" :class="pendingCount > 0 ? 'text-amber' : 'text-green'">
              {{ pendingCount }} Actions
            </div>
          </div>
        </div>

        <!-- Navigation Tabs -->
        <div class="hub-tabs">
          <button 
            class="tab-btn" 
            :class="{ active: activeTab === 'audit' }" 
            @click="activeTab = 'audit'"
          >
            🛡️ Live Audit Stream
            <span class="tab-badge" v-if="auditLogs.length">{{ auditLogs.length }}</span>
          </button>
          <button 
            class="tab-btn" 
            :class="{ active: activeTab === 'hitl' }" 
            @click="activeTab = 'hitl'"
          >
            ✋ Human-in-the-Loop Queue
            <span class="tab-badge-amber" v-if="pendingCount">{{ pendingCount }}</span>
          </button>
          <button 
            class="tab-btn" 
            :class="{ active: activeTab === 'registry' }" 
            @click="activeTab = 'registry'"
          >
            📜 Scoping Registry
          </button>
          <button 
            class="tab-btn" 
            :class="{ active: activeTab === 'sandbox' }" 
            @click="activeTab = 'sandbox'"
          >
            🧪 Tool Sandbox
          </button>
        </div>

        <!-- Tab Body -->
        <div class="drawer-body">
          <!-- TAB 1: Live Security Audit Stream -->
          <div v-if="activeTab === 'audit'" class="tab-content">
            <div class="toolbar-strip">
              <div class="filter-group">
                <button 
                  v-for="filter in ['ALL', 'DENIED', 'ALLOWED', 'PENDING_APPROVAL', 'CACHED']" 
                  :key="filter"
                  class="filter-pill"
                  :class="{ active: auditFilter === filter }"
                  @click="auditFilter = filter"
                >
                  {{ filter }}
                </button>
              </div>
              <div class="toolbar-actions">
                <button class="demo-attack-btn" @click="runRogueAttackDemo" :disabled="demoLoading">
                  <span v-if="demoLoading">Simulating...</span>
                  <span v-else>🚨 Simulate Rogue Agent Attack</span>
                </button>
                <button class="refresh-btn" @click="fetchAuditLogs" title="Refresh">↻</button>
              </div>
            </div>

            <!-- Demo Attack Banner Alert -->
            <div v-if="demoAlert" class="demo-alert-banner">
              <div class="alert-icon">🛡️</div>
              <div class="alert-text">
                <div class="alert-title">{{ demoAlert.demonstration }}</div>
                <div class="alert-desc">
                  Intercepted unauthorized <code>{{ demoAlert.attempted_by.unauthorized_tool }}</code> from 
                  <code>{{ demoAlert.attempted_by.role }}</code> in <strong>{{ demoAlert.governance_verdict.latency_ms }}ms</strong>.
                  Verdict: <span class="badge-denied">{{ demoAlert.governance_verdict.decision }}</span>
                </div>
              </div>
              <button class="alert-close" @click="demoAlert = null">×</button>
            </div>

            <!-- Audit Stream List -->
            <div class="audit-stream">
              <div v-if="filteredAuditLogs.length === 0" class="empty-state">
                No audit events recorded yet. Trigger a simulation or run the rogue agent test!
              </div>
              <div 
                v-for="log in filteredAuditLogs" 
                :key="log.audit_id" 
                class="audit-card"
                :class="'decision-' + log.decision.toLowerCase()"
              >
                <div class="card-top">
                  <div class="card-badges">
                    <span class="decision-badge" :class="'badge-' + log.decision.toLowerCase()">
                      {{ log.decision }}
                    </span>
                    <span class="tool-badge">{{ log.tool_name }}</span>
                    <span class="action-type-badge" :class="log.action_type">{{ log.action_type.toUpperCase() }}</span>
                  </div>
                  <div class="card-meta">
                    <span class="latency-pill">{{ log.latency_ms }}ms</span>
                    <span class="time-label">{{ formatTime(log.timestamp) }}</span>
                  </div>
                </div>

                <div class="card-body">
                  <div class="agent-info">
                    <span class="agent-label">Agent:</span>
                    <code class="agent-val">{{ log.agent_id }}</code>
                    <span class="role-label">Role:</span>
                    <span class="role-pill">{{ log.agent_role }}</span>
                  </div>
                  <p class="decision-reason">{{ log.reason }}</p>
                </div>

                <div class="card-footer" v-if="log.arguments && Object.keys(log.arguments).length">
                  <span class="payload-label">Arguments:</span>
                  <code class="payload-code">{{ JSON.stringify(log.arguments) }}</code>
                </div>
              </div>
            </div>
          </div>

          <!-- TAB 2: Human-in-the-Loop Action Queue -->
          <div v-if="activeTab === 'hitl'" class="tab-content">
            <div class="hitl-header-box">
              <div class="hitl-banner-text">
                <h3>Autonomous Swarm Action Execution Barrier</h3>
                <p>
                  Destructive write tools (e.g. sending real Slack messages, dispatching customer emails, or publishing tweets)
                  are paused in this review gate. An authorized operator must approve them before viaSocket executes.
                </p>
              </div>
            </div>

            <div class="hitl-queue">
              <div v-if="pendingActions.length === 0" class="empty-hitl">
                <div class="empty-icon">✅</div>
                <h4>No Pending Actions</h4>
                <p>All agent action requests have been processed or approved.</p>
              </div>

              <div 
                v-for="action in pendingActions" 
                :key="action.action_id" 
                class="hitl-card"
              >
                <div class="hitl-card-header">
                  <div class="hitl-title-row">
                    <span class="risk-badge" :class="'risk-' + action.risk_level.toLowerCase()">
                      {{ action.risk_level }} RISK
                    </span>
                    <span class="hitl-tool-title">{{ action.tool_name }}</span>
                    <span class="hitl-id font-mono">{{ action.action_id }}</span>
                  </div>
                  <span class="hitl-time">{{ formatTime(action.created_at) }}</span>
                </div>

                <div class="hitl-content">
                  <div class="proposer-row">
                    <span>Proposed by:</span>
                    <strong>{{ action.agent_role }}</strong>
                    <code class="font-mono">({{ action.agent_id }})</code>
                  </div>
                  <div class="outcome-box">
                    <strong>Predicted Impact:</strong> {{ action.predicted_outcome }}
                  </div>
                  <div class="payload-box">
                    <strong>Payload:</strong>
                    <pre>{{ JSON.stringify(action.arguments, null, 2) }}</pre>
                  </div>
                </div>

                <!-- Approval Actions -->
                <div class="hitl-actions" v-if="action.status === 'PENDING_APPROVAL'">
                  <button 
                    class="btn-approve" 
                    @click="approveAction(action.action_id)"
                    :disabled="actionLoading === action.action_id"
                  >
                    ⚡ Approve & Execute via viaSocket
                  </button>
                  <button 
                    class="btn-reject" 
                    @click="rejectAction(action.action_id)"
                    :disabled="actionLoading === action.action_id"
                  >
                    Reject Action
                  </button>
                </div>

                <div class="hitl-result" v-else-if="action.status === 'EXECUTED'">
                  <span class="status-executed">✓ Executed via viaSocket</span>
                  <pre class="result-box">{{ JSON.stringify(action.execution_result, null, 2) }}</pre>
                </div>

                <div class="hitl-result" v-else-if="action.status === 'REJECTED'">
                  <span class="status-rejected">✕ Rejected by Operator</span>
                </div>
              </div>
            </div>
          </div>

          <!-- TAB 3: Scoping Registry (Least Privilege Matrix) -->
          <div v-if="activeTab === 'registry'" class="tab-content">
            <div class="registry-intro">
              <div>
                <h3>Role-Based Tool Scoping Registry</h3>
                <p>Governs which viaSocket integrations each agent archetype is permitted to invoke. Unmapped actions are denied by default.</p>
              </div>
              <button class="btn-secondary" @click="resetPolicies">Reset to Enterprise Baselines</button>
            </div>

            <div class="scoping-table-wrapper">
              <table class="scoping-table">
                <thead>
                  <tr>
                    <th>Agent Archetype</th>
                    <th>Allowed viaSocket Tools</th>
                    <th>Rate Limit / Rd</th>
                    <th>Write Permissions</th>
                    <th>Security Boundary</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(policy, role) in scopingMatrix" :key="role">
                    <td class="role-cell">
                      <strong>{{ role }}</strong>
                      <span class="role-desc">{{ policy.description }}</span>
                    </td>
                    <td>
                      <div class="tool-tag-list" v-if="policy.allowed_tools.length">
                        <span v-for="t in policy.allowed_tools" :key="t" class="tool-tag">
                          {{ t }}
                        </span>
                      </div>
                      <span v-else class="text-muted italic">None (Default Deny)</span>
                    </td>
                    <td class="font-mono text-center">
                      {{ policy.max_calls_per_round }} calls
                    </td>
                    <td class="text-center">
                      <span class="perm-badge" :class="policy.can_request_write ? 'perm-yes' : 'perm-no'">
                        {{ policy.can_request_write ? 'HITL Staged' : 'Denied' }}
                      </span>
                    </td>
                    <td>
                      <span class="boundary-badge" :class="policy.allowed_tools.length > 0 ? 'boundary-scoped' : 'boundary-isolated'">
                        {{ policy.allowed_tools.length > 0 ? 'Least-Privilege' : 'Strict Isolation' }}
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- TAB 4: Tool Sandbox & Test Execution -->
          <div v-if="activeTab === 'sandbox'" class="tab-content">
            <div class="sandbox-container">
              <div class="sandbox-sidebar">
                <h4>Available viaSocket Tools</h4>
                <div class="tool-catalog-list">
                  <div 
                    v-for="t in toolsList" 
                    :key="t.name" 
                    class="tool-catalog-item"
                    :class="{ selected: selectedTool?.name === t.name }"
                    @click="selectToolForTest(t)"
                  >
                    <div class="tool-name-row">
                      <span class="name">{{ t.name }}</span>
                      <span class="type-pill" :class="t.type">{{ t.type }}</span>
                    </div>
                    <p class="tool-desc-short">{{ t.description }}</p>
                  </div>
                </div>
              </div>

              <div class="sandbox-main">
                <h4>Execute Tool via Governance Layer</h4>
                <div class="sandbox-form" v-if="selectedTool">
                  <div class="form-row">
                    <label>Agent Role:</label>
                    <select v-model="testRole" class="form-select">
                      <option value="market_research_agent">market_research_agent (Allowed read)</option>
                      <option value="financial_agent">financial_agent (Allowed DB & read)</option>
                      <option value="report_agent">report_agent (Allowed all + write HITL)</option>
                      <option value="public_persona">public_persona (Strict Default Deny)</option>
                    </select>
                  </div>

                  <div class="form-row">
                    <label>Selected Tool:</label>
                    <input type="text" class="form-input" :value="selectedTool.name" disabled />
                  </div>

                  <div class="form-row">
                    <label>Tool Arguments (JSON):</label>
                    <textarea v-model="testArgsJson" rows="4" class="form-textarea"></textarea>
                  </div>

                  <button class="btn-execute" @click="executeTestTool" :disabled="testRunning">
                    <span v-if="testRunning">Evaluating & Routing...</span>
                    <span v-else>⚡ Run Intercepted Execution</span>
                  </button>

                  <div class="test-result-box" v-if="testResult">
                    <div class="result-header">
                      <span>Governance Verdict:</span>
                      <span class="decision-badge" :class="'badge-' + (testResult.decision || '').toLowerCase()">
                        {{ testResult.decision }}
                      </span>
                      <span class="latency-pill" v-if="testResult.latency_ms">{{ testResult.latency_ms }}ms</span>
                    </div>
                    <p class="result-reason">{{ testResult.reason }}</p>
                    <pre class="result-json">{{ JSON.stringify(testResult.result || testResult.staged_action || testResult, null, 2) }}</pre>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { viasocketApi } from '../api/viasocket'

const isOpen = ref(false)
const activeTab = ref('audit')
const statusData = ref({
  configured: false,
  total_tools_available: 0,
  mode: 'demo'
})

const auditLogs = ref([])
const auditFilter = ref('ALL')
const pendingActions = ref([])
const scopingMatrix = ref({})
const toolsList = ref([])

const demoLoading = ref(false)
const demoAlert = ref(null)
const actionLoading = ref(null)

const selectedTool = ref(null)
const testRole = ref('market_research_agent')
const testArgsJson = ref('{"query": "green hydrogen policy subsidies"}')
const testRunning = ref(false)
const testResult = ref(null)

let pollInterval = null

const pendingCount = computed(() => {
  return pendingActions.value.filter(a => a.status === 'PENDING_APPROVAL').length
})

const filteredAuditLogs = computed(() => {
  if (auditFilter.value === 'ALL') return auditLogs.value
  return auditLogs.value.filter(l => l.decision === auditFilter.value)
})

function toggleDrawer() {
  isOpen.value = !isOpen.value
  if (isOpen.value) {
    refreshAll()
  }
}

async function refreshAll() {
  await Promise.allSettled([
    fetchStatus(),
    fetchAuditLogs(),
    fetchPendingActions(),
    fetchPolicies(),
    fetchTools()
  ])
}

async function fetchStatus() {
  try {
    const res = await viasocketApi.getStatus()
    if (res.success) {
      statusData.value = res
    }
  } catch (e) {
    console.debug('viaSocket status error', e)
  }
}

async function fetchAuditLogs() {
  try {
    const res = await viasocketApi.getAuditLogs(50)
    if (res.success) {
      auditLogs.value = res.logs || []
    }
  } catch (e) {
    console.debug('viaSocket audit error', e)
  }
}

async function fetchPendingActions() {
  try {
    const res = await viasocketApi.getPendingActions()
    if (res.success) {
      pendingActions.value = res.actions || []
    }
  } catch (e) {
    console.debug('viaSocket pending error', e)
  }
}

async function fetchPolicies() {
  try {
    const res = await viasocketApi.getPolicies()
    if (res.success) {
      scopingMatrix.value = res.matrix || {}
    }
  } catch (e) {
    console.debug('viaSocket policies error', e)
  }
}

async function fetchTools() {
  try {
    const res = await viasocketApi.getTools()
    if (res.success) {
      toolsList.value = res.tools || []
      if (!selectedTool.value && toolsList.value.length > 0) {
        selectToolForTest(toolsList.value[0])
      }
    }
  } catch (e) {
    console.debug('viaSocket tools error', e)
  }
}

async function runRogueAttackDemo() {
  demoLoading.value = true
  try {
    const res = await viasocketApi.simulateRogueAttack()
    if (res.success) {
      demoAlert.value = res
      await fetchAuditLogs()
      auditFilter.value = 'ALL'
    }
  } catch (e) {
    console.error('Demo error', e)
  } finally {
    demoLoading.value = false
  }
}

async function approveAction(actionId) {
  actionLoading.value = actionId
  try {
    await viasocketApi.approveAction(actionId)
    await Promise.all([fetchPendingActions(), fetchAuditLogs()])
  } catch (e) {
    console.error('Approve error', e)
  } finally {
    actionLoading.value = null
  }
}

async function rejectAction(actionId) {
  actionLoading.value = actionId
  try {
    await viasocketApi.rejectAction(actionId, 'Operator rejected from Governance Hub')
    await Promise.all([fetchPendingActions(), fetchAuditLogs()])
  } catch (e) {
    console.error('Reject error', e)
  } finally {
    actionLoading.value = null
  }
}

async function resetPolicies() {
  try {
    const res = await viasocketApi.resetPolicies()
    if (res.success) {
      scopingMatrix.value = res.matrix
    }
  } catch (e) {
    console.error('Reset policies error', e)
  }
}

function selectToolForTest(tool) {
  selectedTool.value = tool
  testResult.value = null
  if (tool.name === 'scrape_webpage') {
    testArgsJson.value = '{"url": "https://competitor.com/pricing"}'
  } else if (tool.name === 'search_serp_google') {
    testArgsJson.value = '{"query": "quarterly policy shift tax reforms"}'
  } else if (tool.name === 'query_postgres') {
    testArgsJson.value = '{"sql": "SELECT indicator, value FROM metrics WHERE id = 101"}'
  } else if (tool.name === 'send_slack_message') {
    testArgsJson.value = '{"channel": "#announcements", "message": "Simulated forecast milestone reached."}'
  } else {
    testArgsJson.value = '{}'
  }
}

async function executeTestTool() {
  if (!selectedTool.value) return
  testRunning.value = true
  testResult.value = null

  let parsedArgs = {}
  try {
    parsedArgs = JSON.parse(testArgsJson.value)
  } catch (e) {
    parsedArgs = { raw: testArgsJson.value }
  }

  try {
    const res = await viasocketApi.executeTool({
      agent_id: 'test_operator_agent',
      agent_role: testRole.value,
      tool_name: selectedTool.value.name,
      arguments: parsedArgs,
      phase: 'simulation',
      round_num: 1
    })
    testResult.value = res
  } catch (err) {
    testResult.value = err.response?.data || { error: err.message, decision: 'DENIED', reason: err.message }
  } finally {
    testRunning.value = false
    await Promise.all([fetchAuditLogs(), fetchPendingActions()])
  }
}

function formatTime(isoStr) {
  if (!isoStr) return ''
  try {
    const d = new Date(isoStr)
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
  } catch {
    return isoStr
  }
}

onMounted(() => {
  fetchStatus()
  fetchPendingActions()
  // Periodic poll
  pollInterval = setInterval(() => {
    fetchStatus()
    fetchPendingActions()
    if (isOpen.value && activeTab.value === 'audit') {
      fetchAuditLogs()
    }
  }, 4000)
})

onUnmounted(() => {
  if (pollInterval) clearInterval(pollInterval)
})
</script>

<style scoped>
.viasocket-governance-container {
  position: relative;
  z-index: 9999;
}

/* Floating Trigger Button */
.viasocket-trigger-btn {
  position: fixed;
  bottom: 24px;
  right: 28px;
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(15, 17, 26, 0.88);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(139, 92, 246, 0.4);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4), 0 0 16px rgba(139, 92, 246, 0.25);
  color: #fff;
  padding: 10px 18px;
  border-radius: 9999px;
  cursor: pointer;
  font-family: inherit;
  font-size: 13px;
  font-weight: 600;
  transition: all 0.25s ease;
  z-index: 9999;
}

.viasocket-trigger-btn:hover {
  border-color: rgba(139, 92, 246, 0.8);
  transform: translateY(-2px);
  box-shadow: 0 12px 36px rgba(0, 0, 0, 0.5), 0 0 24px rgba(139, 92, 246, 0.4);
}

.trigger-pulse {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.pulse-green {
  background: #10b981;
  box-shadow: 0 0 8px #10b981;
}

.pulse-amber {
  background: #f59e0b;
  box-shadow: 0 0 8px #f59e0b;
  animation: pulse-glow 1.5s infinite;
}

@keyframes pulse-glow {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(1.2); }
}

.trigger-icon {
  font-size: 14px;
  color: #fbbf24;
}

.trigger-label {
  letter-spacing: 0.5px;
  color: #e2e8f0;
}

.trigger-status {
  font-size: 11px;
  background: rgba(139, 92, 246, 0.25);
  color: #c4b5fd;
  padding: 2px 8px;
  border-radius: 12px;
}

.trigger-badge {
  font-size: 11px;
  background: rgba(245, 158, 11, 0.25);
  color: #fbbf24;
  border: 1px solid rgba(245, 158, 11, 0.5);
  padding: 2px 8px;
  border-radius: 12px;
}

/* Modal Overlay & Drawer */
.governance-overlay {
  position: fixed;
  inset: 0;
  background: rgba(5, 7, 13, 0.75);
  backdrop-filter: blur(8px);
  display: flex;
  justify-content: flex-end;
  z-index: 10000;
}

.governance-drawer {
  width: 760px;
  max-width: 95vw;
  height: 100vh;
  background: #0b0d17;
  border-left: 1px solid rgba(139, 92, 246, 0.35);
  box-shadow: -16px 0 64px rgba(0, 0, 0, 0.85);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  animation: slide-in 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes slide-in {
  from { transform: translateX(100%); }
  to { transform: translateX(0); }
}

/* Drawer Header */
.drawer-header {
  padding: 20px 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  background: rgba(15, 18, 30, 0.6);
}

.hub-tag {
  font-size: 10px;
  letter-spacing: 1.5px;
  color: #a78bfa;
  font-weight: 700;
  display: block;
  margin-bottom: 4px;
}

.hub-title {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  color: #f8fafc;
}

.accent-text {
  color: #38bdf8;
  background: linear-gradient(135deg, #38bdf8, #a855f7);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.hub-subtitle {
  margin: 4px 0 0 0;
  font-size: 12px;
  color: #94a3b8;
}

.close-btn {
  background: transparent;
  border: none;
  color: #94a3b8;
  font-size: 20px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 6px;
  transition: all 0.2s;
}

.close-btn:hover {
  color: #fff;
  background: rgba(255, 255, 255, 0.1);
}

/* Metric Strip */
.status-metric-strip {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  padding: 14px 24px;
  background: rgba(18, 22, 38, 0.4);
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.metric-box {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.metric-label {
  font-size: 11px;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.metric-val {
  font-size: 13px;
  font-weight: 600;
  color: #e2e8f0;
  display: flex;
  align-items: center;
  gap: 6px;
}

.status-indicator-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.status-indicator-dot.live {
  background: #10b981;
  box-shadow: 0 0 6px #10b981;
}

.status-indicator-dot.mock {
  background: #38bdf8;
  box-shadow: 0 0 6px #38bdf8;
}

.text-cyan { color: #38bdf8; }
.text-amber { color: #fbbf24; }
.text-green { color: #34d399; }

/* Hub Navigation Tabs */
.hub-tabs {
  display: flex;
  background: rgba(13, 16, 28, 0.95);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  padding: 0 16px;
}

.tab-btn {
  background: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  color: #94a3b8;
  font-size: 13px;
  font-weight: 600;
  padding: 12px 16px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
}

.tab-btn:hover {
  color: #e2e8f0;
}

.tab-btn.active {
  color: #a855f7;
  border-bottom-color: #a855f7;
}

.tab-badge {
  background: rgba(255, 255, 255, 0.1);
  color: #cbd5e1;
  font-size: 11px;
  padding: 1px 6px;
  border-radius: 10px;
}

.tab-badge-amber {
  background: rgba(245, 158, 11, 0.25);
  color: #fbbf24;
  font-size: 11px;
  padding: 1px 6px;
  border-radius: 10px;
}

/* Drawer Body */
.drawer-body {
  flex: 1;
  overflow-y: auto;
  padding: 20px 24px;
}

/* Audit Tab */
.toolbar-strip {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  gap: 12px;
}

.filter-group {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.filter-pill {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #94a3b8;
  font-size: 11px;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.filter-pill.active {
  background: rgba(168, 85, 247, 0.25);
  border-color: #a855f7;
  color: #c4b5fd;
}

.toolbar-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.demo-attack-btn {
  background: rgba(239, 68, 68, 0.15);
  border: 1px solid rgba(239, 68, 68, 0.4);
  color: #f87171;
  font-size: 12px;
  font-weight: 600;
  padding: 6px 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.demo-attack-btn:hover {
  background: rgba(239, 68, 68, 0.25);
  border-color: #ef4444;
}

.refresh-btn {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #94a3b8;
  font-size: 14px;
  padding: 4px 10px;
  border-radius: 6px;
  cursor: pointer;
}

.demo-alert-banner {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.35);
  border-radius: 8px;
  padding: 12px 16px;
  margin-bottom: 16px;
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.alert-icon { font-size: 18px; }
.alert-title { font-weight: 700; color: #f87171; font-size: 13px; }
.alert-desc { font-size: 12px; color: #e2e8f0; margin-top: 2px; }
.alert-close { background: none; border: none; color: #f87171; cursor: pointer; font-size: 16px; }

/* Audit Cards */
.audit-stream {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.audit-card {
  background: rgba(18, 22, 38, 0.55);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px;
  padding: 14px;
  transition: border-color 0.2s;
}

.audit-card.decision-allowed {
  border-left: 3px solid #10b981;
}

.audit-card.decision-denied {
  border-left: 3px solid #ef4444;
  background: rgba(35, 16, 22, 0.4);
}

.audit-card.decision-cached {
  border-left: 3px solid #38bdf8;
}

.audit-card.decision-pending_approval {
  border-left: 3px solid #f59e0b;
}

.card-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.card-badges {
  display: flex;
  align-items: center;
  gap: 8px;
}

.decision-badge {
  font-size: 10px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 4px;
  letter-spacing: 0.5px;
}

.badge-allowed { background: rgba(16, 185, 129, 0.2); color: #34d399; }
.badge-denied { background: rgba(239, 68, 68, 0.2); color: #f87171; }
.badge-cached { background: rgba(56, 189, 248, 0.2); color: #38bdf8; }
.badge-pending_approval { background: rgba(245, 158, 11, 0.2); color: #fbbf24; }

.tool-badge {
  font-family: monospace;
  font-size: 12px;
  color: #f1f5f9;
  background: rgba(255, 255, 255, 0.08);
  padding: 2px 6px;
  border-radius: 4px;
}

.action-type-badge {
  font-size: 10px;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 4px;
}

.action-type-badge.read { color: #38bdf8; background: rgba(56, 189, 248, 0.1); }
.action-type-badge.write { color: #f43f5e; background: rgba(244, 63, 94, 0.1); }

.card-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}

.latency-pill {
  font-size: 11px;
  font-family: monospace;
  color: #a78bfa;
}

.time-label {
  font-size: 11px;
  color: #64748b;
}

.agent-info {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #94a3b8;
  margin-bottom: 6px;
}

.agent-val {
  color: #e2e8f0;
}

.role-pill {
  background: rgba(139, 92, 246, 0.15);
  color: #c4b5fd;
  padding: 1px 6px;
  border-radius: 4px;
  font-size: 11px;
}

.decision-reason {
  margin: 0;
  font-size: 12px;
  color: #cbd5e1;
  line-height: 1.4;
}

.card-footer {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  font-size: 11px;
  color: #94a3b8;
}

.payload-code {
  font-family: monospace;
  color: #a5b4fc;
}

/* HITL Tab */
.hitl-header-box {
  background: rgba(245, 158, 11, 0.08);
  border: 1px solid rgba(245, 158, 11, 0.25);
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
}

.hitl-header-box h3 {
  margin: 0 0 6px 0;
  font-size: 15px;
  color: #fbbf24;
}

.hitl-header-box p {
  margin: 0;
  font-size: 12px;
  color: #cbd5e1;
  line-height: 1.4;
}

.hitl-card {
  background: rgba(18, 22, 38, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 14px;
}

.hitl-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.hitl-title-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.risk-badge {
  font-size: 10px;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 4px;
}

.risk-critical { background: #ef4444; color: #fff; }
.risk-high { background: #f97316; color: #fff; }
.risk-medium { background: #eab308; color: #000; }
.risk-low { background: #10b981; color: #fff; }

.hitl-tool-title {
  font-size: 14px;
  font-weight: 600;
  color: #f1f5f9;
}

.hitl-id {
  font-size: 11px;
  color: #64748b;
}

.hitl-time {
  font-size: 11px;
  color: #64748b;
}

.hitl-content {
  font-size: 13px;
  color: #cbd5e1;
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 14px;
}

.outcome-box {
  background: rgba(255, 255, 255, 0.03);
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 12px;
  color: #e2e8f0;
}

.payload-box pre {
  margin: 4px 0 0 0;
  background: #060810;
  padding: 10px;
  border-radius: 6px;
  font-size: 11px;
  color: #38bdf8;
  overflow-x: auto;
}

.hitl-actions {
  display: flex;
  gap: 10px;
}

.btn-approve {
  background: linear-gradient(135deg, #059669, #10b981);
  color: #fff;
  border: none;
  font-size: 13px;
  font-weight: 600;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-approve:hover {
  background: linear-gradient(135deg, #047857, #059669);
}

.btn-reject {
  background: rgba(239, 68, 68, 0.15);
  border: 1px solid rgba(239, 68, 68, 0.4);
  color: #f87171;
  font-size: 13px;
  font-weight: 600;
  padding: 8px 14px;
  border-radius: 6px;
  cursor: pointer;
}

.status-executed {
  color: #10b981;
  font-weight: 600;
  font-size: 12px;
}

.status-rejected {
  color: #ef4444;
  font-weight: 600;
  font-size: 12px;
}

.result-box {
  margin-top: 6px;
  background: #060810;
  padding: 10px;
  border-radius: 6px;
  font-size: 11px;
  color: #a7f3d0;
  overflow-x: auto;
}

/* Scoping Registry Tab */
.registry-intro {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.registry-intro h3 {
  margin: 0 0 4px 0;
  font-size: 15px;
  color: #f1f5f9;
}

.registry-intro p {
  margin: 0;
  font-size: 12px;
  color: #94a3b8;
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: #e2e8f0;
  font-size: 12px;
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
}

.scoping-table-wrapper {
  overflow-x: auto;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px;
}

.scoping-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
  color: #cbd5e1;
}

.scoping-table th {
  background: rgba(18, 22, 38, 0.8);
  padding: 10px 14px;
  text-align: left;
  font-weight: 600;
  color: #94a3b8;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.scoping-table td {
  padding: 12px 14px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
}

.role-cell strong {
  display: block;
  color: #f1f5f9;
  font-size: 13px;
}

.role-desc {
  font-size: 11px;
  color: #64748b;
}

.tool-tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.tool-tag {
  background: rgba(139, 92, 246, 0.15);
  color: #c4b5fd;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 11px;
  font-family: monospace;
}

.perm-badge {
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 4px;
}

.perm-yes { background: rgba(245, 158, 11, 0.2); color: #fbbf24; }
.perm-no { background: rgba(239, 68, 68, 0.15); color: #f87171; }

.boundary-badge {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 4px;
}

.boundary-scoped { color: #38bdf8; background: rgba(56, 189, 248, 0.1); }
.boundary-isolated { color: #ef4444; background: rgba(239, 68, 68, 0.1); }

/* Sandbox Tab */
.sandbox-container {
  display: grid;
  grid-template-columns: 260px 1fr;
  gap: 16px;
}

.sandbox-sidebar h4, .sandbox-main h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #f1f5f9;
}

.tool-catalog-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 500px;
  overflow-y: auto;
}

.tool-catalog-item {
  background: rgba(18, 22, 38, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 6px;
  padding: 10px;
  cursor: pointer;
  transition: all 0.2s;
}

.tool-catalog-item:hover, .tool-catalog-item.selected {
  border-color: #a855f7;
  background: rgba(168, 85, 247, 0.1);
}

.tool-name-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.tool-name-row .name {
  font-weight: 600;
  font-size: 12px;
  color: #f1f5f9;
}

.type-pill {
  font-size: 9px;
  padding: 1px 4px;
  border-radius: 3px;
  text-transform: uppercase;
}

.type-pill.read { background: rgba(56, 189, 248, 0.2); color: #38bdf8; }
.type-pill.write { background: rgba(244, 63, 94, 0.2); color: #f43f5e; }

.tool-desc-short {
  margin: 0;
  font-size: 11px;
  color: #94a3b8;
  line-height: 1.3;
}

.sandbox-form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.form-row {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.form-row label {
  font-size: 12px;
  color: #94a3b8;
}

.form-select, .form-input, .form-textarea {
  background: #060810;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 6px;
  color: #f1f5f9;
  padding: 8px 10px;
  font-size: 12px;
  font-family: inherit;
}

.form-textarea {
  font-family: monospace;
}

.btn-execute {
  background: linear-gradient(135deg, #7c3aed, #a855f7);
  color: #fff;
  border: none;
  padding: 10px 16px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-execute:hover {
  background: linear-gradient(135deg, #6d28d9, #9333ea);
}

.test-result-box {
  margin-top: 14px;
  background: #060810;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  padding: 12px;
}

.result-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  font-weight: 600;
  color: #f1f5f9;
  margin-bottom: 6px;
}

.result-reason {
  margin: 0 0 8px 0;
  font-size: 12px;
  color: #cbd5e1;
}

.result-json {
  margin: 0;
  font-size: 11px;
  color: #38bdf8;
  max-height: 200px;
  overflow-y: auto;
}

.empty-state, .empty-hitl {
  text-align: center;
  padding: 40px 20px;
  color: #64748b;
  font-size: 13px;
}

.empty-icon {
  font-size: 32px;
  margin-bottom: 8px;
}
</style>
