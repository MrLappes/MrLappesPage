import { createApp } from 'vue'
import { createI18n } from 'vue-i18n'
import './style.css'
import App from './App.vue'
import en from './locales/en'
import de from './locales/de'
import cs from './locales/cs'

// Get the browser language or saved preference
const savedLocale = localStorage.getItem('locale');
const browserLocale = navigator.language.split('-')[0];
const availableLocales = ['de', 'en', 'cs'];
const defaultLocale = (savedLocale && availableLocales.includes(savedLocale)) ? 
                      savedLocale : 
                      (availableLocales.includes(browserLocale) ? browserLocale : 'en');

// Create i18n instance
const i18n = createI18n({
  legacy: false, // You must set `false`, to use Composition API
  globalInjection: true, // If you want to use $t in template
  locale: defaultLocale,
  fallbackLocale: 'en',
  messages: {
    "en": en,
    "de": de,
    "cs": cs
  }
})

// Mount app with i18n
const app = createApp(App)
app.use(i18n)
app.mount('#app')
