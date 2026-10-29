/**
 * Audio Recorder & Transcriber
 * Records single-channel 16kHz 16-bit PCM WAV
 * Handles Base64 conversion and browser SpeechRecognition fallback.
 */

import axios from 'axios'

/**
 * Resample audio buffer from input sample rate to target sample rate (16kHz)
 * @param {Float32Array} audioBuffer
 * @param {number} inputSampleRate
 * @param {number} targetSampleRate
 * @returns {Float32Array}
 */
function downsampleTo16k(audioBuffer, inputSampleRate, targetSampleRate = 16000) {
  if (inputSampleRate === targetSampleRate) {
    return audioBuffer
  }
  const ratio = inputSampleRate / targetSampleRate
  const newLength = Math.round(audioBuffer.length / ratio)
  const result = new Float32Array(newLength)
  let offsetResult = 0
  let offsetBuffer = 0
  while (offsetResult < result.length) {
    const nextOffsetBuffer = Math.round((offsetResult + 1) * ratio)
    let accum = 0
    let count = 0
    for (let i = offsetBuffer; i < nextOffsetBuffer && i < audioBuffer.length; i++) {
      accum += audioBuffer[i]
    }
    result[offsetResult] = count > 0 ? accum / count : 0
    offsetResult++
    offsetBuffer = nextOffsetBuffer
  }
  return result
}

/**
 * Encode 16kHz PCM Float32 samples into standard 16-bit mono WAV binary ArrayBuffer
 * @param {Float32Array} samples
 * @param {number} sampleRate
 * @returns {ArrayBuffer}
 */
function encodeWAV(samples, sampleRate = 16000) {
  const buffer = new ArrayBuffer(44 + samples.length * 2)
  const view = new DataView(buffer)

  const writeString = (view, offset, string) => {
    for (let i = 0; i < string.length; i++) {
      view.setUint8(offset + i, string.charCodeAt(i))
    }
  }

  /* RIFF identifier */
  writeString(view, 0, 'RIFF')
  /* file length */
  view.setUint32(4, 36 + samples.length * 2, true)
  /* RIFF type */
  writeString(view, 8, 'WAVE')
  /* format chunk identifier */
  writeString(view, 12, 'fmt ')
  /* format chunk length */
  view.setUint32(16, 16, true)
  /* sample format (raw PCM) */
  view.setUint16(20, 1, true)
  /* channel count (1 = mono) */
  view.setUint16(22, 1, true)
  /* sample rate (16000 Hz) */
  view.setUint32(24, sampleRate, true)
  /* byte rate (sample rate * block align) */
  view.setUint32(28, sampleRate * 2, true)
  /* block align (channels * bytes per sample) */
  view.setUint16(32, 2, true)
  /* bits per sample (16-bit PCM) */
  view.setUint16(34, 16, true)
  /* data chunk identifier */
  writeString(view, 36, 'data')
  /* data chunk length */
  view.setUint32(40, samples.length * 2, true)

  // Write PCM samples (convert float -1..+1 to 16-bit signed integer -32768..32767)
  let offset = 44
  for (let i = 0; i < samples.length; i++, offset += 2) {
    const s = Math.max(-1, Math.min(1, samples[i]))
    view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7fff, true)
  }

  return buffer
}

/**
 * Convert ArrayBuffer to Base64
 * @param {ArrayBuffer} buffer
 * @returns {string}
 */
function arrayBufferToBase64(buffer) {
  let binary = ''
  const bytes = new Uint8Array(buffer)
  const len = bytes.byteLength
  for (let i = 0; i < len; i++) {
    binary += String.fromCharCode(bytes[i])
  }
  return window.btoa(binary)
}

/**
 * Start recording 16kHz mono audio from user's microphone
 * @returns {Promise<{ stop: () => Promise<{ base64: string, blob: Blob, duration: number }> }>}
 */
export async function start16kHzRecording() {
  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    throw new Error('Microphone access is not supported by your browser')
  }

  const stream = await navigator.mediaDevices.getUserMedia({
    audio: {
      channelCount: 1,
      echoCancellation: true,
      noiseSuppression: true,
      autoGainControl: true
    }
  })

  warmupVoiceEngine()

  const AudioContextClass = window.AudioContext || window.webkitAudioContext
  const audioContext = new AudioContextClass()
  const inputSampleRate = audioContext.sampleRate

  const source = audioContext.createMediaStreamSource(stream)
  const bufferSize = 4096
  const processor = audioContext.createScriptProcessor(bufferSize, 1, 1)

  const audioChunks = []
  const startTime = Date.now()

  processor.onaudioprocess = (e) => {
    const channelData = e.inputBuffer.getChannelData(0)
    audioChunks.push(new Float32Array(channelData))
  }

  source.connect(processor)
  processor.connect(audioContext.destination)

  return {
    async stop() {
      processor.disconnect()
      source.disconnect()
      
      stream.getTracks().forEach(t => t.stop())
      await audioContext.close()

      const duration = (Date.now() - startTime) / 1000

      let totalLength = 0
      for (const chunk of audioChunks) {
        totalLength += chunk.length
      }

      const mergedAudio = new Float32Array(totalLength)
      let offset = 0
      for (const chunk of audioChunks) {
        mergedAudio.set(chunk, offset)
        offset += chunk.length
      }

      const downsampled16k = downsampleTo16k(mergedAudio, inputSampleRate, 16000)
      const wavBuffer = encodeWAV(downsampled16k, 16000)
      const base64Audio = arrayBufferToBase64(wavBuffer)
      const wavBlob = new Blob([wavBuffer], { type: 'audio/wav' })

      return {
        base64: base64Audio,
        blob: wavBlob,
        duration
      }
    }
  }
}

/**
 * Send audio base64 to backend /api/voice/transcribe
 * @param {string} audioBase64
 * @param {string} [language='en-IN']
 * @param {string} [mode='transcribe']
 * @returns {Promise<{ success: boolean, text: string, detected_language?: string, error?: string }>}
 */
export async function transcribeAudio(audioBase64, language = 'en-IN', mode = 'transcribe') {
  try {
    const res = await axios.post('/api/voice/transcribe', {
      audio: audioBase64,
      language,
      mode
    }, {
      headers: { 'Content-Type': 'application/json' },
      timeout: 45000
    })
    return res.data
  } catch (err) {
    const errMsg = err.response?.data?.error || err.message || 'Voice transcription request failed'
    return {
      success: false,
      error: errMsg,
      status_code: err.response?.status
    }
  }
}


/**
 * Pre-warm or check voice engine status
 */
export async function warmupVoiceEngine() {
  try {
    await axios.get('/api/voice/status', { timeout: 3000 })
  } catch {
    // Ignore warmup network failures
  }
}


/**
 * Start Browser Native SpeechRecognition for live preview while speaking
 * @param {Function} onTranscript - callback receiving live string
 * @returns {{ stop: () => void, isSupported: boolean, getFinalText: () => string }}
 */
export function startLiveSpeechPreview(onTranscript) {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
  if (!SpeechRecognition) {
    return { stop: () => {}, isSupported: false, getFinalText: () => '' }
  }

  let finalTranscript = ''
  let recognition = null
  try {
    recognition = new SpeechRecognition()
    recognition.continuous = true
    recognition.interimResults = true
    recognition.lang = 'en-US'

    recognition.onresult = (event) => {
      let interim = ''
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const text = event.results[i][0].transcript
        if (event.results[i].isFinal) {
          finalTranscript += (finalTranscript ? ' ' : '') + text.trim()
        } else {
          interim += text
        }
      }
      const combined = (finalTranscript + ' ' + interim).trim()
      if (onTranscript && combined) {
        onTranscript(combined)
      }
    }

    recognition.onerror = () => {}
    recognition.start()
  } catch {
    // Ignore mic errors in live preview
  }

  return {
    stop: () => {
      if (recognition) {
        try {
          recognition.stop()
        } catch {}
      }
    },
    getFinalText: () => finalTranscript.trim(),
    isSupported: true
  }
}
