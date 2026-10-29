import { createApp } from 'vue'
import './index.css'
import App from './App.vue'
import router from './router'
import i18n from './i18n'
import { initAuth } from './store/auth'

// Initialize Supabase auth session early
initAuth().catch(err => console.warn('[Lokantra Auth] Initial session load notice:', err))

const app = createApp(App)

app.use(router)
app.use(i18n)

app.mount('#app')
