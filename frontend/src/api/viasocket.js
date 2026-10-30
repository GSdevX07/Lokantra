import request from './index'

export const viasocketApi = {
  // Get connection status, mode, and summary metrics
  getStatus() {
    return request({
      url: '/api/viasocket/status',
      method: 'get'
    })
  },

  // Get available viaSocket tool catalog
  getTools() {
    return request({
      url: '/api/viasocket/tools',
      method: 'get'
    })
  },

  // Get active scoping matrix
  getPolicies() {
    return request({
      url: '/api/viasocket/policies',
      method: 'get'
    })
  },

  // Update role policy
  updatePolicy(data) {
    return request({
      url: '/api/viasocket/policies',
      method: 'post',
      data
    })
  },

  // Reset policies to default-deny baselines
  resetPolicies() {
    return request({
      url: '/api/viasocket/policies/reset',
      method: 'post'
    })
  },

  // Get live security audit trail
  getAuditLogs(limit = 50) {
    return request({
      url: '/api/viasocket/audit-logs',
      method: 'get',
      params: { limit }
    })
  },

  // Get pending actions requiring HITL review
  getPendingActions(status = 'PENDING_APPROVAL') {
    return request({
      url: '/api/viasocket/pending-actions',
      method: 'get',
      params: { status }
    })
  },

  // Operator approves a staged write action
  approveAction(actionId, operatorId = 'human_operator') {
    return request({
      url: '/api/viasocket/approve-action',
      method: 'post',
      data: {
        action_id: actionId,
        operator_id: operatorId
      }
    })
  },

  // Operator rejects a proposed action
  rejectAction(actionId, reason = 'Rejected by human operator', operatorId = 'human_operator') {
    return request({
      url: '/api/viasocket/reject-action',
      method: 'post',
      data: {
        action_id: actionId,
        reason,
        operator_id: operatorId
      }
    })
  },

  // Test execute through governance
  executeTool(payload) {
    return request({
      url: '/api/viasocket/execute-tool',
      method: 'post',
      data: payload
    })
  },

  // Demo trigger: simulate rogue attack
  simulateRogueAttack() {
    return request({
      url: '/api/viasocket/simulate-rogue-attack',
      method: 'post'
    })
  }
}

export default viasocketApi
