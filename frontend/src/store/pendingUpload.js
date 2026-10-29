/**
 * Temporarily store files, direct text notes, and requirements to be uploaded
 * Used for instant redirect when starting engine on home page, deferring API calls to Process page
 */
import { reactive } from 'vue'

const state = reactive({
  files: [],
  simulationRequirement: '',
  directText: '',
  isPending: false
})

export function setPendingUpload(files, requirement, directText = '') {
  state.files = files || []
  state.simulationRequirement = requirement || ''
  state.directText = directText || ''
  state.isPending = true
}

export function getPendingUpload() {
  return {
    files: state.files,
    simulationRequirement: state.simulationRequirement,
    directText: state.directText,
    isPending: state.isPending
  }
}

export function clearPendingUpload() {
  state.files = []
  state.simulationRequirement = ''
  state.directText = ''
  state.isPending = false
}

export default state
