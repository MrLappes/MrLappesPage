<script setup>
import { ref, onMounted, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import HomePage from './components/HomePage.vue';
import AnimatedBackground from './components/AnimatedBackground.vue';

// Use the i18n composition API
const { t, locale } = useI18n();

const darkMode = ref(localStorage.getItem('darkMode') === 'true' || window.matchMedia('(prefers-color-scheme: dark)').matches);
const showParticles = ref(localStorage.getItem('showParticles') !== 'false');
const maxParticles = ref(parseInt(localStorage.getItem('maxParticles')) || 500);
const mobileMenuOpen = ref(false);

const languages = [
  { code: 'de', name: 'Deutsch', flag: '🇩🇪' },
  { code: 'en', name: 'English', flag: '🇬🇧' },
  { code: 'cs', name: 'Čeština', flag: '🇨🇿' }
];

const langDropdownOpen = ref(false);

watch(darkMode, (newValue) => {
  localStorage.setItem('darkMode', newValue);
  if (newValue) {
    document.documentElement.classList.add('dark');
  } else {
    document.documentElement.classList.remove('dark');
  }
});

watch(showParticles, (newValue) => {
  localStorage.setItem('showParticles', newValue);
});

watch(maxParticles, (newValue) => {
  localStorage.setItem('maxParticles', newValue);
});

watch(locale, (newValue) => {
  localStorage.setItem('locale', newValue);
  document.querySelector('html').setAttribute('lang', newValue);
});

onMounted(() => {
  if (darkMode.value) {
    document.documentElement.classList.add('dark');
  } else {
    document.documentElement.classList.remove('dark');
  }
    document.querySelector('html').setAttribute('lang', locale.value);
});

const toggleDarkMode = () => {
  darkMode.value = !darkMode.value;
};

const toggleParticles = () => {
  showParticles.value = !showParticles.value;
};

const updateMaxParticles = (event) => {
  maxParticles.value = parseInt(event.target.value);
};

const changeLanguage = (langCode) => {
  locale.value = langCode;
  langDropdownOpen.value = false;
  mobileMenuOpen.value = false;
};

const toggleLangDropdown = () => {
  langDropdownOpen.value = !langDropdownOpen.value;
};

const toggleMobileMenu = (event) => {
  // Stop event propagation to prevent immediate closing
  if (event) {
    event.stopPropagation();
  }
  mobileMenuOpen.value = !mobileMenuOpen.value;
  // Close language dropdown if it's open
  if (langDropdownOpen.value) {
    langDropdownOpen.value = false;
  }
};

const handleClickOutside = (event) => {
  // Don't close the mobile menu if clicking the menu button
  if (event.target.closest('.mobile-menu-button')) {
    return;
  }
  
  if (langDropdownOpen.value && !event.target.closest('.lang-dropdown')) {
    langDropdownOpen.value = false;
  }
  
  if (mobileMenuOpen.value && !event.target.closest('.mobile-menu')) {
    mobileMenuOpen.value = false;
  }
};

onMounted(() => {
  document.addEventListener('click', handleClickOutside);
});
</script>

<template>
  <div class="min-h-screen transition-colors duration-300 bg-gray-50 dark:bg-gray-900">
    <!-- Animated background -->
    <AnimatedBackground 
      :darkMode="darkMode" 
      :showParticles="showParticles"
      :maxParticles="maxParticles"
    />
    
    <header class="sticky top-0 z-50 bg-white dark:bg-gray-800 shadow-md transition-all duration-300 bg-opacity-90 dark:bg-opacity-90 backdrop-blur-sm">
      <div class="container mx-auto px-4 py-3 flex justify-between items-center">
        <div class="flex items-center space-x-3">
          <img src="/icon.png" class="h-12 w-12 transition-transform duration-300 transform hover:rotate-12" alt="PlatePal logo" />
          <h1 class="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-[#e384c7] to-[#9e6593] dark:from-[#e384c7] dark:to-[#9e6593]">
            PlatePal
          </h1>
        </div>
        
        <!-- Desktop Controls - Hidden on mobile -->
        <div class="hidden md:flex items-center space-x-4">
          <!-- Language Selector -->
          <div class="relative lang-dropdown">
            <button 
              @click="toggleLangDropdown" 
              class="flex items-center space-x-1 p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors duration-200"
            >
              <span class="text-xl">{{ languages.find(l => l.code === locale)?.flag }}</span>
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-gray-600 dark:text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </button>
            
            <div v-if="langDropdownOpen" class="absolute right-0 mt-2 w-40 bg-white dark:bg-gray-800 rounded-md shadow-lg py-1 z-50">
              <button
                v-for="lang in languages"
                :key="lang.code"
                @click="changeLanguage(lang.code)"
                class="flex items-center w-full px-4 py-2 text-left text-sm hover:bg-gray-100 dark:hover:bg-gray-700"
                :class="{ 'bg-gray-100 dark:bg-gray-700': locale === lang.code }"
              >
                <span class="text-lg mr-2">{{ lang.flag }}</span>
                <span>{{ lang.name }}</span>
              </button>
            </div>
          </div>
          
          <!-- Particles Toggle -->
          <div class="flex items-center">
            <button 
              @click="toggleParticles" 
              class="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors duration-200"
              :title="showParticles ? t('header.particlesToggle.disable') : t('header.particlesToggle.enable')"
            >
              <svg v-if="showParticles" xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-[#e384c7]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
              </svg>
              <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
              </svg>
            </button>
          </div>
          
          <!-- Particles Count Dropdown -->
          <div class="relative">
            <select 
              v-if="showParticles"
              v-model="maxParticles" 
              @change="updateMaxParticles"
              class="appearance-none bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md py-1 pl-3 pr-8 text-sm leading-tight focus:outline-none focus:ring-2 focus:ring-[#e384c7] transition-colors duration-200"
            >
              <option value="100">{{ t('header.particleCount.100') }}</option>
              <option value="200">{{ t('header.particleCount.200') }}</option>
              <option value="300">{{ t('header.particleCount.300') }}</option>
              <option value="500">{{ t('header.particleCount.500') }}</option>
              <option value="750">{{ t('header.particleCount.750') }}</option>
              <option value="1000">{{ t('header.particleCount.1000') }}</option>
              <option value="1500">{{ t('header.particleCount.1500') }}</option>
              <option value="2000">{{ t('header.particleCount.2000') }}</option>
            </select>
            <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-700 dark:text-gray-300">
              <svg class="fill-current h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">
                <path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z"/>
              </svg>
            </div>
          </div>
          
          <!-- Dark Mode Toggle -->
          <button @click="toggleDarkMode" aria-label="Toggle dark mode" class="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors duration-200">
            <svg v-if="darkMode" xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-yellow-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-gray-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
            </svg>
          </button>
        </div>
        
        <!-- Mobile Menu Button - Only visible on mobile -->
        <button 
          @click.stop="toggleMobileMenu" 
          class="mobile-menu-button md:hidden p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors duration-200"
          aria-label="Toggle mobile menu"
        >
          <svg v-if="!mobileMenuOpen" xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-gray-700 dark:text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
          <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-gray-700 dark:text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
      
      <!-- Mobile Menu Drawer -->
      <div 
        v-if="mobileMenuOpen" 
        class="mobile-menu md:hidden bg-white dark:bg-gray-800 shadow-lg border-t dark:border-gray-700 p-4 pt-6 transition-all duration-300"
        @click.stop
      >
        <div class="space-y-5">
          <!-- Dark Mode Toggle in Mobile Menu -->
          <div class="flex justify-between items-center">
            <span class="text-gray-700 dark:text-gray-300 pt-4 font-medium">{{ !darkMode ? '☀️ Light Mode' : '🌙 Dark Mode' }}</span>
            <button 
              @click="toggleDarkMode" 
              class="relative inline-flex h-6 w-11 items-center rounded-full bg-gray-200 dark:bg-gray-600 transition-colors duration-200"
            >
              <span
                :class="!darkMode ? 'translate-x-6 bg-yellow-400' : 'translate-x-1 bg-white'"
                class="inline-block h-4 w-4 transform rounded-full transition-transform duration-200"
              />
            </button>
          </div>
          
          <!-- Particles Toggle in Mobile Menu -->
          <div class="flex justify-between items-center">
            <span class="text-gray-700 dark:text-gray-300 font-medium">{{ t('header.particles') }}</span>
            <button 
              @click="toggleParticles" 
              class="relative inline-flex h-6 w-11 items-center rounded-full bg-gray-200 dark:bg-gray-600 transition-colors duration-200"
            >
              <span
                :class="showParticles ? 'translate-x-6 bg-[#e384c7]' : 'translate-x-1 bg-white'"
                class="inline-block h-4 w-4 transform rounded-full transition-transform duration-200"
              />
            </button>
          </div>
          
          <!-- Particles Count in Mobile Menu -->
          <div v-if="showParticles" class="flex flex-col space-y-2">
            <span class="text-gray-700 dark:text-gray-300 font-medium">{{ t('header.particles') }} {{ maxParticles }}</span>
            <input 
              type="range" 
              min="100" 
              max="2000" 
              step="100" 
              v-model="maxParticles"
              class="w-full h-2 bg-gray-200 dark:bg-gray-600 rounded-lg appearance-none cursor-pointer accent-[#e384c7]"
            />
            <div class="flex justify-between text-xs text-gray-500 dark:text-gray-400">
              <span>100</span>
              <span>1000</span>
              <span>2000</span>
            </div>
          </div>
          
          <!-- Language Selector in Mobile Menu -->
          <div class="pt-2 border-t dark:border-gray-700">
            <div class="grid grid-cols-1 gap-2">
              <button
                v-for="lang in languages"
                :key="lang.code"
                @click="changeLanguage(lang.code)"
                class="flex items-center space-x-2 p-3 rounded-md text-left relative"
                :class="locale === lang.code 
                  ? 'bg-[#e384c7] bg-opacity-15 text-whitefont-medium' 
                  : 'hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300'"
              >
                <span class="text-lg">{{ lang.flag }}</span>
                <span>{{ lang.name }}</span>
                <span 
                  v-if="locale === lang.code" 
                  class="absolute right-3 text-[#e384c7]"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                  </svg>
                </span>
              </button>
            </div>
          </div>
        </div>
      </div>
      
    </header>
    
    <main class="container mx-auto px-4 py-8 relative z-10">
      <HomePage :darkMode="darkMode" />
    </main>
    
    <footer class="py-6 bg-white dark:bg-gray-800 shadow-inner transition-colors duration-300 bg-opacity-90 dark:bg-opacity-90 backdrop-blur-sm relative z-10">
      <div class="container mx-auto px-4 text-center text-gray-600 dark:text-gray-300">
        <p>{{ t('footer.copyright', { year: new Date().getFullYear() }) }}</p>
      </div>
    </footer>
  </div>
</template>

<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

:root {
  --primary: #e384c7;
  --secondary: #9e6593;
  --primary-light: rgba(227, 132, 199, 0.15);
  --primary-dark: rgba(227, 132, 199, 0.9);
}

* {
  font-family: 'Poppins', sans-serif;
}

.logo {
  height: 6em;
  padding: 1.5em;
  will-change: filter;
  transition: filter 300ms;
}

.logo:hover {
  filter: drop-shadow(0 0 2em rgba(227, 132, 199, 0.8));
}

.page-enter-active,
.page-leave-active {
  transition: opacity 0.3s, transform 0.3s;
}

.page-enter-from,
.page-leave-to {
  opacity: 0;
  transform: translateY(20px);
}

:root {
  color-scheme: light;
}

html.dark {
  color-scheme: dark;
}

.dark body {
  background-color: var(--color-dark-bg);
  color: white;
}
</style>
