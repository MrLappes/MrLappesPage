import { createApp } from 'vue'
import { createI18n } from 'vue-i18n'
import './style.css'
import App from './App.vue'
import en from './locales/en'
import de from './locales/de'
import cs from './locales/cs'
import jp from './locales/jp'


const savedLocale = localStorage.getItem('locale');
const browserLocale = navigator.language.split('-')[0];
const availableLocales = ['de', 'en', 'cs', 'jp'];
const defaultLocale = (savedLocale && availableLocales.includes(savedLocale)) ? 
                      savedLocale : 
                      (availableLocales.includes(browserLocale) ? browserLocale : 'en');


const i18n = createI18n({
  legacy: false, 
  globalInjection: true, 
  locale: defaultLocale,
  fallbackLocale: 'en',
  messages: {
    "en": en,
    "de": de,
    "cs": cs,
    "jp": jp
  }
})


const app = createApp(App)
app.use(i18n)
app.mount('#app')
