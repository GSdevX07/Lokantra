import { reactive, ref, computed } from 'vue'
import { supabase, isSupabaseConfigured } from '@/lib/supabase'

const user = ref(null)
const profile = ref(null)
const session = ref(null)
const loading = ref(true)
const authError = ref(null)
const loginHistory = ref([])
let isInitialized = false
let initPromise = null

// Check if user is authenticated
const isAuthenticated = computed(() => !!user.value)

/**
 * Record a login event directly in public.login_history
 */
async function recordLogin(userData) {
  if (!supabase || !userData) return

  try {
    const userAgent = typeof navigator !== 'undefined' ? navigator.userAgent : 'Unknown'
    const payload = {
      user_id: userData.id,
      email: userData.email,
      provider: userData.app_metadata?.provider || 'google',
      logged_in_at: new Date().toISOString(),
      user_agent: userAgent,
      metadata: {
        last_sign_in_at: userData.last_sign_in_at,
        user_metadata: userData.user_metadata
      }
    }

    const { error } = await supabase.from('login_history').insert(payload)
    if (error) {
      console.warn('[Lokantra Auth] Note on recording login_history:', error.message)
    }
  } catch (err) {
    console.warn('[Lokantra Auth] Failed to record login history:', err)
  }
}

/**
 * Sync user profile to public.profiles table
 */
async function syncUserProfile(userData) {
  if (!supabase || !userData) return null

  try {
    const meta = userData.user_metadata || {}
    const fullName = meta.full_name || meta.name || userData.email?.split('@')[0] || 'Swarm Explorer'
    const avatarUrl = meta.avatar_url || meta.picture || ''
    const provider = userData.app_metadata?.provider || 'google'

    const profileData = {
      id: userData.id,
      email: userData.email,
      full_name: fullName,
      avatar_url: avatarUrl,
      provider: provider,
      last_sign_in_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    }

    const { data, error } = await supabase
      .from('profiles')
      .upsert(profileData, { onConflict: 'id' })
      .select()
      .single()

    if (error) {
      console.warn('[Lokantra Auth] Note on syncing profile:', error.message)
      // Fallback in-memory profile
      profile.value = profileData
      return profileData
    }

    profile.value = data || profileData
    return profile.value
  } catch (err) {
    console.warn('[Lokantra Auth] Failed to sync profile:', err)
    return null
  }
}

/**
 * Fetch profile from public.profiles
 */
async function fetchProfile(userId) {
  if (!supabase || !userId) return null

  try {
    const { data, error } = await supabase
      .from('profiles')
      .select('*')
      .eq('id', userId)
      .maybeSingle()

    if (!error && data) {
      profile.value = data
      return data
    }
  } catch (err) {
    console.warn('[Lokantra Auth] Error fetching profile:', err)
  }
  return null
}

/**
 * Fetch recent login history for the current user
 */
async function fetchLoginHistory(userId, limit = 5) {
  if (!supabase || !userId) return []

  try {
    const { data, error } = await supabase
      .from('login_history')
      .select('*')
      .eq('user_id', userId)
      .order('logged_in_at', { ascending: false })
      .limit(limit)

    if (!error && data) {
      loginHistory.value = data
      return data
    }
  } catch (err) {
    console.warn('[Lokantra Auth] Error fetching login history:', err)
  }
  return []
}

/**
 * Clean OAuth redirect URL parameters (e.g. hash fragments / query codes)
 */
function cleanAuthUrl() {
  if (typeof window === 'undefined') return
  if (window.location.hash && (window.location.hash.includes('access_token') || window.location.hash.includes('error'))) {
    const cleanUrl = window.location.pathname + window.location.search
    window.history.replaceState(null, '', cleanUrl)
  }
}

/**
 * Initialize Authentication: session check & state listener
 */
export function initAuth() {
  if (initPromise) return initPromise
  initPromise = (async () => {
    if (isInitialized) return
    isInitialized = true

    if (!isSupabaseConfigured() || !supabase) {
      loading.value = false
      return
    }

    try {
      loading.value = true

      // 1. Get initial session
      const { data: { session: initialSession }, error } = await supabase.auth.getSession()
      if (error) {
        console.warn('[Lokantra Auth] getSession error:', error.message)
      }

      if (initialSession?.user) {
        session.value = initialSession
        user.value = initialSession.user
        await syncUserProfile(initialSession.user)
        await fetchLoginHistory(initialSession.user.id)
        cleanAuthUrl()
      }

      // 2. Listen for auth changes
      supabase.auth.onAuthStateChange(async (event, newSession) => {
        session.value = newSession
        user.value = newSession?.user || null
        authError.value = null

        if (event === 'SIGNED_IN' && newSession?.user) {
          await syncUserProfile(newSession.user)
          await recordLogin(newSession.user)
          await fetchLoginHistory(newSession.user.id)
          cleanAuthUrl()
        } else if (event === 'SIGNED_OUT') {
          user.value = null
          profile.value = null
          session.value = null
          loginHistory.value = []
        } else if (event === 'USER_UPDATED' && newSession?.user) {
          await fetchProfile(newSession.user.id)
        }
      })
    } catch (err) {
      console.error('[Lokantra Auth] Initialization error:', err)
      authError.value = err.message
    } finally {
      loading.value = false
    }
  })()
  return initPromise
}

/**
 * Ensure authentication has finished initial session retrieval
 */
export async function ensureAuthInitialized() {
  if (isInitialized && !loading.value) return
  await initAuth()
}

/**
 * Store target route to redirect to after successful sign-in
 */
export function setAuthRedirect(path) {
  try {
    if (path && path !== '/' && path !== '/home') {
      localStorage.setItem('lokantra_auth_redirect', path)
    }
  } catch (e) {}
}

/**
 * Get and clear the post-sign-in redirect route
 */
export function getAndClearAuthRedirect() {
  try {
    const path = localStorage.getItem('lokantra_auth_redirect')
    if (path) {
      localStorage.removeItem('lokantra_auth_redirect')
      return path
    }
  } catch (e) {}
  return null
}

/**
 * Initiate Google Sign-In via Supabase OAuth
 */
async function signInWithGoogle() {
  authError.value = null

  if (!isSupabaseConfigured() || !supabase) {
    const msg = 'Supabase credentials are not configured. Please add VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY to your environment (.env).'
    authError.value = msg
    throw new Error(msg)
  }

  try {
    loading.value = true
    const redirectTo = window.location.origin

    const { data, error } = await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: {
        redirectTo,
        queryParams: {
          access_type: 'offline',
          prompt: 'consent'
        }
      }
    })

    if (error) {
      authError.value = error.message
      throw error
    }

    return data
  } catch (err) {
    console.error('[Lokantra Auth] Google sign-in failed:', err)
    authError.value = err.message
    throw err
  } finally {
    loading.value = false
  }
}

/**
 * Sign out user
 */
async function signOut() {
  if (!supabase) {
    user.value = null
    profile.value = null
    session.value = null
    loginHistory.value = []
    return
  }

  try {
    loading.value = true
    const { error } = await supabase.auth.signOut()
    if (error) {
      console.warn('[Lokantra Auth] Sign out error:', error.message)
    }
    user.value = null
    profile.value = null
    session.value = null
    loginHistory.value = []
  } catch (err) {
    console.error('[Lokantra Auth] SignOut exception:', err)
  } finally {
    loading.value = false
  }
}

export function useAuth() {
  return {
    user,
    profile,
    session,
    loading,
    authError,
    loginHistory,
    isAuthenticated,
    isConfigured: isSupabaseConfigured(),
    initAuth,
    ensureAuthInitialized,
    setAuthRedirect,
    getAndClearAuthRedirect,
    signInWithGoogle,
    signOut,
    syncUserProfile,
    recordLogin,
    fetchProfile,
    fetchLoginHistory
  }
}
