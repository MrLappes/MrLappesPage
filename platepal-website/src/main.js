import { createApp } from 'vue'
import { createI18n } from 'vue-i18n'
import App from './App.vue'
import router from './router'
import en from './locales/en'
import de from './locales/de'
import cs from './locales/cs'
import jp from './locales/jp'
import './style.css'

const savedLocale = localStorage.getItem('locale')
const browserLocale = navigator.language.split('-')[0]
const availableLocales = ['de', 'en', 'cs', 'jp']
const defaultLocale =
  savedLocale && availableLocales.includes(savedLocale)
    ? savedLocale
    : availableLocales.includes(browserLocale)
    ? browserLocale
    : 'en'

const i18n = createI18n({
  legacy: false,
  globalInjection: true,
  locale: defaultLocale,
  fallbackLocale: 'en',
  messages: {
    en,
    de,
    cs,
    jp
  }
})

const app = createApp(App)
app.use(router)
app.use(i18n)
app.mount('#app')
