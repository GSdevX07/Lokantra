import { useAuth } from '@/store/auth'

/**
 * Get the localStorage key scoped to the current user
 *
 * @param {string} [userId]
 * @returns {string}
 */
function getStorageKey(userId) {
  if (userId) {
    return `lokantra_simulations_${userId}`
  }
  const { user } = useAuth()
  if (user.value?.id) {
    return `lokantra_simulations_${user.value.id}`
  }
  return 'lokantra_simulations_guest'
}

/**
 * Load raw simulation array for the current user from localStorage
 *
 * @param {string} [userId]
 * @returns {Array}
 */
function loadSimulationsArray(userId) {
  try {
    const key = getStorageKey(userId)
    const raw = localStorage.getItem(key)
    if (!raw) return []
    const parsed = JSON.parse(raw)
    return Array.isArray(parsed) ? parsed : []
  } catch (err) {
    console.warn('[LocalSimHistory] Error reading localStorage:', err)
    return []
  }
}

/**
 * Save array of simulations to localStorage
 *
 * @param {Array} list
 * @param {string} [userId]
 */
function saveSimulationsArray(list, userId) {
  try {
    const key = getStorageKey(userId)
    localStorage.setItem(key, JSON.stringify(list))
  } catch (err) {
    console.warn('[LocalSimHistory] Error saving to localStorage:', err)
  }
}

/**
 * Save or insert a simulation record into the current user's localStorage
 *
 * @param {Object} data
 * @param {string} data.simulation_id
 * @param {string} [data.project_id]
 * @param {string} [data.project_name]
 * @param {string} [data.simulation_requirement]
 * @param {string} [data.status]
 * @param {Array}  [data.files]
 * @param {number} [data.entities_count]
 * @param {number} [data.profiles_count]
 * @param {number} [data.total_rounds]
 * @param {number} [data.current_round]
 * @param {string} [data.report_id]
 * @param {Array}  [data.entity_types]
 * @returns {Object}
 */
export function saveLocalSimulation(data) {
  if (!data || !data.simulation_id) return null

  const list = loadSimulationsArray()
  const existingIndex = list.findIndex(item => item.simulation_id === data.simulation_id)

  const now = new Date().toISOString()
  const record = {
    simulation_id: data.simulation_id,
    project_id: data.project_id || (existingIndex >= 0 ? list[existingIndex].project_id : null),
    project_name: data.project_name || (existingIndex >= 0 ? list[existingIndex].project_name : 'Swarm Reality Seed'),
    simulation_requirement: data.simulation_requirement || (existingIndex >= 0 ? list[existingIndex].simulation_requirement : ''),
    status: data.status || (existingIndex >= 0 ? list[existingIndex].status : 'created'),
    entities_count: data.entities_count !== undefined ? data.entities_count : (existingIndex >= 0 ? list[existingIndex].entities_count : 0),
    profiles_count: data.profiles_count !== undefined ? data.profiles_count : (existingIndex >= 0 ? list[existingIndex].profiles_count : 0),
    total_rounds: data.total_rounds !== undefined ? data.total_rounds : (existingIndex >= 0 ? list[existingIndex].total_rounds : 0),
    current_round: data.current_round !== undefined ? data.current_round : (existingIndex >= 0 ? list[existingIndex].current_round : 0),
    report_id: data.report_id || (existingIndex >= 0 ? list[existingIndex].report_id : null),
    entity_types: data.entity_types || (existingIndex >= 0 ? list[existingIndex].entity_types : []),
    files: data.files || (existingIndex >= 0 ? list[existingIndex].files : []),
    created_at: existingIndex >= 0 ? list[existingIndex].created_at : now,
    updated_at: now
  }

  if (existingIndex >= 0) {
    list[existingIndex] = { ...list[existingIndex], ...record }
  } else {
    list.unshift(record)
  }

  // Cap at 100 entries per user
  if (list.length > 100) {
    list.splice(100)
  }

  saveSimulationsArray(list)
  return record
}

/**
 * Update an existing simulation record in localStorage
 *
 * @param {string} simulationId
 * @param {Object} updates
 * @returns {Object|null}
 */
export function updateLocalSimulation(simulationId, updates) {
  if (!simulationId) return null

  const list = loadSimulationsArray()
  const index = list.findIndex(item => item.simulation_id === simulationId)

  if (index >= 0) {
    list[index] = {
      ...list[index],
      ...updates,
      updated_at: new Date().toISOString()
    }
    saveSimulationsArray(list)
    return list[index]
  }

  // If not found yet, create new entry with updates
  return saveLocalSimulation({ simulation_id: simulationId, ...updates })
}

/**
 * Fetch simulations for the current user from localStorage
 *
 * @param {number} [limit=20]
 * @returns {Array}
 */
export function getLocalUserSimulations(limit = 20) {
  const { user, isAuthenticated } = useAuth()
  if (!isAuthenticated.value || !user.value?.id) {
    return []
  }

  const list = loadSimulationsArray(user.value.id)
  return list.slice(0, limit)
}
