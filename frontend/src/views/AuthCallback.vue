<template>
  <div class="fixed inset-0 w-screen h-screen flex flex-col items-center justify-center bg-black text-white select-none">
    <!-- Ambient Venom Glow -->
    <div class="fixed inset-0 pointer-events-none bg-radial-at-c from-transparent via-[#080808]/80 to-[#000000]/98"></div>

    <div class="relative z-10 flex flex-col items-center gap-6 p-8 rounded-2xl bg-neutral-950/80 border border-white/10 shadow-2xl backdrop-blur-xl max-w-sm text-center">
      <!-- Animated Spinner -->
      <div class="relative w-14 h-14">
        <div class="absolute inset-0 rounded-full border-2 border-white/20"></div>
        <div class="absolute inset-0 rounded-full border-2 border-transparent border-t-white animate-spin"></div>
      </div>

      <div class="space-y-2">
        <h2 class="text-lg font-semibold tracking-wide text-neutral-100">Authenticating</h2>
        <p class="text-xs text-neutral-400">Syncing user session with Supabase...</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/store/auth'

const router = useRouter()
const { initAuth, getAndClearAuthRedirect } = useAuth()

onMounted(async () => {
  try {
    await initAuth()
  } catch (err) {
    console.error('Auth callback error:', err)
  } finally {
    // Check if there was a saved redirect before auth
    const target = getAndClearAuthRedirect() || '/home'
    // Brief timeout for smooth UX transition
    setTimeout(() => {
      router.replace(target)
    }, 600)
  }
})
</script>
