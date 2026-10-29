<template>
  <div class="user-auth-wrapper relative inline-block text-left" ref="dropdownRef">
    <!-- 1. LOADING STATE -->
    <div
      v-if="loading"
      class="auth-loading-pill flex items-center gap-2 px-3 py-1.5 rounded-full bg-black/60 border border-white/10 text-xs text-neutral-400 backdrop-blur-md"
    >
      <span class="inline-block w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
      <span class="tracking-wide text-[11px] uppercase">Connecting...</span>
    </div>

    <!-- 2. AUTHENTICATED STATE: User Avatar & Dropdown Trigger -->
    <div v-else-if="isAuthenticated && user" class="relative">
      <button
        @click="toggleDropdown"
        type="button"
        class="user-profile-btn flex items-center gap-2.5 px-3 py-1.5 rounded-full bg-neutral-950/80 hover:bg-neutral-900 border border-white/15 hover:border-white/35 transition-all duration-300 shadow-[0_2px_12px_rgba(0,0,0,0.7)] group cursor-pointer backdrop-blur-md"
        :aria-expanded="isDropdownOpen"
      >
        <!-- Avatar Ring -->
        <div class="avatar-ring relative w-7 h-7 rounded-full overflow-hidden border border-white/25 shadow-sm shadow-black/80 transition-all">
          <img
            v-if="userAvatar"
            :src="userAvatar"
            :alt="userName"
            class="w-full h-full object-cover"
            referrerpolicy="no-referrer"
          />
          <div
            v-else
            class="w-full h-full bg-gradient-to-tr from-[#1a1a1a] via-[#333333] to-[#777777] flex items-center justify-center font-bold text-xs text-white uppercase"
          >
            {{ userInitial }}
          </div>
        </div>

        <!-- User Name -->
        <span class="text-xs font-medium text-neutral-200 group-hover:text-white max-w-[110px] truncate tracking-tight">
          {{ userName }}
        </span>

        <!-- Chevron Icon -->
        <svg
          class="w-3.5 h-3.5 text-neutral-400 group-hover:text-neutral-200 transition-transform duration-300"
          :class="{ 'rotate-180': isDropdownOpen }"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      <!-- DROPDOWN MENU -->
      <Transition name="auth-popover">
        <div
          v-if="isDropdownOpen"
          class="absolute right-0 mt-2.5 w-72 rounded-xl bg-[#090909]/95 backdrop-blur-xl border border-white/15 shadow-[0_16px_40px_rgba(0,0,0,0.95)] p-4 z-50 text-neutral-200 text-left select-none"
        >
          <!-- User Info Header -->
          <div class="flex items-center gap-3 pb-3 border-b border-white/10">
            <div class="w-10 h-10 rounded-full overflow-hidden border border-white/20 shrink-0">
              <img
                v-if="userAvatar"
                :src="userAvatar"
                :alt="userName"
                class="w-full h-full object-cover"
                referrerpolicy="no-referrer"
              />
              <div
                v-else
                class="w-full h-full bg-[#222] flex items-center justify-center font-bold text-white text-sm"
              >
                {{ userInitial }}
              </div>
            </div>
            <div class="overflow-hidden">
              <div class="font-semibold text-sm text-white truncate">{{ userName }}</div>
              <div class="text-[11px] text-neutral-400 truncate">{{ user?.email }}</div>
            </div>
          </div>

          <!-- Metadata & Connection Badge -->
          <div class="py-3 border-b border-white/10 space-y-2">
            <div class="flex items-center justify-between text-[11px]">
              <span class="text-neutral-400">Auth Provider</span>
              <span class="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-white/10 text-neutral-200 border border-white/15">
                <svg class="w-3 h-3" viewBox="0 0 24 24">
                  <path fill="#4285F4" d="M23.745 12.27c0-.7-.06-1.4-.19-2.07H12v4.51h6.6c-.29 1.52-1.14 2.8-2.4 3.68v3.05h3.88c2.27-2.09 3.66-5.17 3.66-9.17z"/>
                  <path fill="#34A853" d="M12 24c3.24 0 5.95-1.08 7.93-2.91l-3.88-3.05c-1.08.72-2.45 1.16-4.05 1.16-3.12 0-5.77-2.1-6.72-4.93H1.25v3.15C3.26 21.36 7.35 24 12 24z"/>
                  <path fill="#FBBC05" d="M5.28 14.27c-.25-.72-.38-1.49-.38-2.27s.13-1.55.38-2.27V6.58H1.25C.45 8.18 0 9.99 0 12s.45 3.82 1.25 5.42l4.03-3.15z"/>
                  <path fill="#EA4335" d="M12 4.75c1.77 0 3.35.61 4.6 1.8l3.42-3.42C17.95 1.19 15.24 0 12 0 7.35 0 3.26 2.64 1.25 6.58l4.03 3.15c.95-2.83 3.6-4.98 6.72-4.98z"/>
                </svg>
                Google (Supabase)
              </span>
            </div>

            <div class="flex items-center justify-between text-[11px]">
              <span class="text-neutral-400">Database Sync</span>
              <span class="text-emerald-400 flex items-center gap-1 font-mono">
                <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 shadow-[0_0_6px_#34d399]"></span>
                Connected
              </span>
            </div>

            <div v-if="lastSignInFormatted" class="flex items-center justify-between text-[11px]">
              <span class="text-neutral-400">Last Login</span>
              <span class="text-neutral-300 font-mono text-[10px]">{{ lastSignInFormatted }}</span>
            </div>
          </div>

          <!-- Sign Out Action -->
          <div class="pt-3">
            <button
              @click="handleSignOut"
              type="button"
              class="w-full flex items-center justify-center gap-2 px-3 py-2 rounded-lg bg-neutral-900/80 hover:bg-red-950/40 text-neutral-300 hover:text-red-400 border border-white/10 hover:border-red-500/30 text-xs font-medium transition-all duration-200 cursor-pointer"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
              Sign Out
            </button>
          </div>
        </div>
      </Transition>
    </div>

    <!-- 3. UNAUTHENTICATED STATE: Sign In with Google Button -->
    <div v-else class="relative">
      <button
        @click="handleSignIn"
        type="button"
        :disabled="isSigningIn"
        class="google-signin-btn group relative flex items-center gap-2.5 px-3.5 py-1.5 sm:px-4 sm:py-2 rounded-full bg-neutral-950/85 hover:bg-neutral-900 border border-white/20 hover:border-white/50 text-neutral-100 transition-all duration-300 shadow-[0_4px_16px_rgba(0,0,0,0.8)] hover:shadow-[0_8px_24px_rgba(0,0,0,0.95)] cursor-pointer backdrop-blur-md"
        title="Sign in with Google"
      >
        <!-- Google Logo SVG -->
        <span class="flex items-center justify-center w-4 h-4 shrink-0 transition-transform duration-300 group-hover:scale-110">
          <svg class="w-full h-full" viewBox="0 0 24 24">
            <path fill="#4285F4" d="M23.745 12.27c0-.7-.06-1.4-.19-2.07H12v4.51h6.6c-.29 1.52-1.14 2.8-2.4 3.68v3.05h3.88c2.27-2.09 3.66-5.17 3.66-9.17z"/>
            <path fill="#34A853" d="M12 24c3.24 0 5.95-1.08 7.93-2.91l-3.88-3.05c-1.08.72-2.45 1.16-4.05 1.16-3.12 0-5.77-2.1-6.72-4.93H1.25v3.15C3.26 21.36 7.35 24 12 24z"/>
            <path fill="#FBBC05" d="M5.28 14.27c-.25-.72-.38-1.49-.38-2.27s.13-1.55.38-2.27V6.58H1.25C.45 8.18 0 9.99 0 12s.45 3.82 1.25 5.42l4.03-3.15z"/>
            <path fill="#EA4335" d="M12 4.75c1.77 0 3.35.61 4.6 1.8l3.42-3.42C17.95 1.19 15.24 0 12 0 7.35 0 3.26 2.64 1.25 6.58l4.03 3.15c.95-2.83 3.6-4.98 6.72-4.98z"/>
          </svg>
        </span>

        <span class="text-xs font-semibold tracking-wide text-neutral-200 group-hover:text-white">
          <span v-if="isSigningIn">Redirecting...</span>
          <span v-else>Sign in with Google</span>
        </span>
      </button>

      <!-- Warning Toast if Supabase Keys are Missing -->
      <Transition name="auth-popover">
        <div
          v-if="showConfigNotice"
          class="absolute right-0 top-full mt-2 w-72 p-3.5 rounded-xl bg-[#141414] border border-amber-500/40 shadow-2xl text-xs text-neutral-200 z-50 backdrop-blur-xl"
        >
          <div class="flex items-start gap-2.5">
            <span class="text-amber-400 text-base leading-none">⚠️</span>
            <div class="flex-1">
              <div class="font-semibold text-amber-300 text-xs mb-1">Supabase Setup Required</div>
              <p class="text-[11px] text-neutral-300 leading-relaxed">
                Add <code class="px-1 py-0.5 rounded bg-black/60 text-white font-mono text-[10px]">VITE_SUPABASE_URL</code> and <code class="px-1 py-0.5 rounded bg-black/60 text-white font-mono text-[10px]">VITE_SUPABASE_ANON_KEY</code> to your <code class="text-white font-mono">.env</code> file.
              </p>
            </div>
            <button
              @click="showConfigNotice = false"
              class="text-neutral-400 hover:text-white text-xs leading-none"
            >
              &times;
            </button>
          </div>
        </div>
      </Transition>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useAuth } from '@/store/auth'

const {
  user,
  profile,
  loading,
  isAuthenticated,
  isConfigured,
  initAuth,
  signInWithGoogle,
  signOut
} = useAuth()

const isDropdownOpen = ref(false)
const isSigningIn = ref(false)
const showConfigNotice = ref(false)
const dropdownRef = ref(null)

const userName = computed(() => {
  return (
    profile.value?.full_name ||
    user.value?.user_metadata?.full_name ||
    user.value?.user_metadata?.name ||
    user.value?.email?.split('@')[0] ||
    'Explorer'
  )
})

const userAvatar = computed(() => {
  return (
    profile.value?.avatar_url ||
    user.value?.user_metadata?.avatar_url ||
    user.value?.user_metadata?.picture ||
    null
  )
})

const userInitial = computed(() => {
  const name = userName.value || 'U'
  return name.charAt(0).toUpperCase()
})

const lastSignInFormatted = computed(() => {
  const time = profile.value?.last_sign_in_at || user.value?.last_sign_in_at
  if (!time) return null
  try {
    const d = new Date(time)
    return d.toLocaleDateString(undefined, {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch {
    return null
  }
})

function toggleDropdown() {
  isDropdownOpen.value = !isDropdownOpen.value
}

async function handleSignIn() {
  if (!isConfigured) {
    showConfigNotice.value = true
    return
  }

  try {
    isSigningIn.value = true
    await signInWithGoogle()
  } catch (err) {
    console.error('Sign-in failed:', err)
  } finally {
    isSigningIn.value = false
  }
}

async function handleSignOut() {
  isDropdownOpen.value = false
  await signOut()
}

function handleOutsideClick(e) {
  if (dropdownRef.value && !dropdownRef.value.contains(e.target)) {
    isDropdownOpen.value = false
    showConfigNotice.value = false
  }
}

onMounted(() => {
  initAuth()
  if (typeof document !== 'undefined') {
    document.addEventListener('click', handleOutsideClick)
  }
})

onUnmounted(() => {
  if (typeof document !== 'undefined') {
    document.removeEventListener('click', handleOutsideClick)
  }
})
</script>

<style scoped>
.auth-popover-enter-active,
.auth-popover-leave-active {
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.auth-popover-enter-from,
.auth-popover-leave-to {
  opacity: 0;
  transform: translateY(-6px) scale(0.96);
}
</style>
