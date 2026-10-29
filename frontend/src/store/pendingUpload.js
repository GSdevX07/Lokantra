/**
 * Temporarily store files, direct text notes, and requirements to be uploaded
 * Used for instant redirect when starting engine on home page, deferring API calls to Process page
 */
import { reactive } from 'vue'

const state = reactive({
  files: [],
  simulationRequirement: '',
  directText: '',
  superSpeed: false,
  isPending: false
})

export function setPendingUpload(files, requirement, directText = '', superSpeed = false) {
  state.files = files || []
  state.simulationRequirement = requirement || ''
  state.directText = directText || ''
  state.superSpeed = !!superSpeed
  state.isPending = true
}

export function getPendingUpload() {
  return {
    files: state.files,
    simulationRequirement: state.simulationRequirement,
    directText: state.directText,
    superSpeed: state.superSpeed,
    isPending: state.isPending
  }
}

export function clearPendingUpload() {
  state.files = []
  state.simulationRequirement = ''
  state.directText = ''
  state.superSpeed = false
  state.isPending = false
}

export default state
