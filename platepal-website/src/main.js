import { createApp } from 'vue'
import { createI18n } from 'vue-i18n'
import './style.css'
import App from './App.vue'
import de from './locales/de.json?raw'
import en from './locales/en.json?raw'
import cs from './locales/cs.json?raw'

const parseJSON = (jsonString) => {
  try {
    return JSON.parse(jsonString)
  } catch (e) {
    console.error('Error parsing JSON locale file:', e)
    return {}
  }
}

const messages = {
  de: parseJSON(de),
  en: parseJSON(en),
  cs: parseJSON(cs)
}

const savedLocale = localStorage.getItem('locale') || navigator.language.split('-')[0]
const locale = ['de', 'en', 'cs'].includes(savedLocale) ? savedLocale : 'de'

const i18n = createI18n({
  legacy: false,
  locale: locale,
  fallbackLocale: 'en',
  globalInjection: true,
  messages,
  missing: (locale, key) => {
    console.warn(`Missing translation: [${locale}] ${key}`)
    return key
  }
})

const app = createApp(App)
app.use(i18n)
app.mount('#app')
