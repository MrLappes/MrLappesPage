<script setup>
import { ref, computed, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';


const { t, locale } = useI18n();

const props = defineProps({
  darkMode: Boolean
});


const calculateAge = () => {
  const birthdate = new Date(2003, 6, 9); 
  const today = new Date();
  let age = today.getFullYear() - birthdate.getFullYear();
  const monthDifference = today.getMonth() - birthdate.getMonth();
  
  if (monthDifference < 0 || (monthDifference === 0 && today.getDate() < birthdate.getDate())) {
    age--;
  }
  
  return age;
};

const age = calculateAge();


const calculateGymYears = () => {
  const startDate = new Date(2022, 6, 1); 
  const today = new Date();
  
  let years = today.getFullYear() - startDate.getFullYear();
  const monthDiff = today.getMonth() - startDate.getMonth();
  
  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < startDate.getDate())) {
    years--;
  }
  
  return years;
};

const gymYears = calculateGymYears();


const gymYearsText = computed(() => {
  if (gymYears === 0) {
    return t('home.about.year');
  } else {
    return t('home.about.years', { count: gymYears });
  }
});


const bachelorStatus = computed(() => {
  const today = new Date();
  const finishDate = new Date(2025, 9, 1); 
  
  if (today >= finishDate) {
    const formattedDate = new Intl.DateTimeFormat(locale.value, { 
      month: 'long', 
      year: 'numeric' 
    }).format(finishDate);
    
    return t('home.about.bachelor.completed', { date: formattedDate });
  } else {
    return t('home.about.bachelor.inProgress');
  }
});


const animated = ref(false);
const skillsVisible = ref(false);


const skills = [
{ name: 'home.skills.vue', icon: 'fab fa-solid fa-vuejs', color: 'text-green-500' },
{ name: 'home.skills.flutter', icon: 'fa-solid fa-mobile-alt', color: 'text-blue-500' },
{ name: 'home.skills.godot', icon: 'fa-solid fa-gamepad', color: 'text-purple-500' },
{ name: 'home.skills.unity', icon: 'fa-solid fa-vr-cardboard', color: 'text-red-500' },
{ name: 'home.skills.ai', icon: 'fa-solid fa-brain', color: 'text-orange-500' },
{ name: 'home.skills.arch', icon: 'fab fa-solid fa-linux', color: 'text-teal-500' },
{ name: 'home.skills.design', icon: 'fa-solid fa-palette', color: 'text-pink-500' },
{ name: 'home.skills.pixel', icon: 'fa-solid fa-pen-fancy', color: 'text-yellow-500' },
{ name: 'home.skills.editor', icon: 'fa-solid fa-code', color: 'text-cyan-500' },
{ name: 'home.skills.dark', icon: 'fa-solid fa-moon', color: 'text-indigo-400' },
{ name: 'home.skills.backend', icon: 'fa-solid fa-server', color: 'text-blue-600' },
{ name: 'home.skills.discordbots', icon: 'fab fa-discord', color: 'text-indigo-500' },
];


const socialLinks = [
  { name: 'home.social.steam', icon: 'fab fa-steam', color: 'text-gray-500', url: 'https://steamcommunity.com/id/dergottderherr/' },
  { name: 'home.social.discord', icon: 'fab fa-discord', color: 'text-indigo-500', url: 'https://discordapp.com/users/mrlappes' },
  { name: 'home.social.instagram', icon: 'fab fa-instagram', color: 'text-pink-500', url: 'https://www.instagram.com/mrlappes/channel/' },
  { name: 'home.social.youtube', icon: 'fab fa-youtube', color: 'text-red-500', url: 'https://www.youtube.com/@MrLappes' },
  { name: 'home.social.twitch', icon: 'fab fa-twitch', color: 'text-purple-500', url: 'https://www.twitch.tv/kinglappes' },
  { name: 'home.social.itch', icon: 'fab fa-itch-io', color: 'text-red-500', url: 'https://mrlappes.itch.io/casual-day'}
];

onMounted(() => {
  setTimeout(() => {
    animated.value = true;
    setTimeout(() => {
      skillsVisible.value = true;
    }, 500);
  }, 300);
});

</script>

<template>
  <div class="max-w-4xl mx-auto no-select">
    <!-- Hero Section -->
    <section class="py-10 mb-16">
      <div class="flex flex-col md:flex-row items-center justify-between gap-8">
        <div class="w-full md:w-1/2 text-center md:text-left">
          <h1 
            class="text-4xl md:text-5xl font-bold mb-4 transition-transform duration-700"
            :class="animated ? 'translate-x-0 opacity-100' : '-translate-x-10 opacity-0'"
          >
            <span class="bg-clip-text text-transparent bg-gradient-to-r from-[#e384c7] to-[#9e6593]">
              {{ t('home.title') }}
            </span>
          </h1>
          <p 
            class="text-xl text-gray-600 dark:text-gray-300 mb-6 transition-transform duration-700 delay-100"
            :class="animated ? 'translate-x-0 opacity-100' : '-translate-x-10 opacity-0'"
          >
            {{ t('home.subtitle') }} <br> {{ t('home.subtitle2') }}
          </p>
          <div 
            class="flex flex-col sm:flex-row gap-4 justify-center md:justify-start transition-all duration-700 delay-200"
            :class="animated ? 'translate-y-0 opacity-100' : 'translate-y-10 opacity-0'"
          >
            <a 
              href="https://github.com/MrLappes" 
              target="_blank" 
              class="flex items-center justify-center gap-2 bg-gradient-to-r from-[#e384c7] to-[#9e6593] hover:from-[#9e6593] hover:to-[#e384c7] text-white py-3 px-6 rounded-lg shadow-lg transform hover:scale-105 transition-all duration-300"
            >
              <i class="fab fa-solid fa-github"></i>
              {{ t('home.buttons.github') }}
            </a>
            <a 
              href="#skills" 
              class="flex items-center justify-center gap-2 bg-white dark:bg-gray-800 text-[#e384c7] border-2 border-[#e384c7] py-3 px-6 rounded-lg shadow-lg transform hover:scale-105 transition-all duration-300"
            >
              <i class="fas fa-solid fa-code"></i>
              {{ t('home.buttons.skills') }}
            </a>
          </div>
        </div>
        <div 
          class="w-full md:w-1/2 flex justify-center transition-transform duration-700 delay-300"
          :class="animated ? 'translate-x-0 opacity-100' : 'translate-x-10 opacity-0'"
        >
          <div class="relative w-64 h-64 rounded-full overflow-hidden border-4 border-[#e384c7] shadow-xl transform hover:rotate-6 transition-transform duration-500">
            <video src="../assets/loop.mp4" class="w-full h-full object-cover" autoplay loop muted alt="Mike Busam" />
          </div>
          <!-- Media Attribution Disclaimer -->
          <div class="absolute -bottom-20 left-1/2 transform -translate-x-1/2 w-64 text-center">
            <p class="text-xs text-gray-500 dark:text-gray-400 mt-2 px-2 py-1 bg-white/50 dark:bg-gray-800/50 backdrop-blur-sm rounded-md">
              {{ t('home.mediaAttr.generated') }}<br>{{ t('home.mediaAttr.video') }}
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- About Section -->
    <section class="py-10 mb-16 scroll-mt-20" id="about">
      <div 
        class="bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-2xl shadow-xl p-8 transform transition-all duration-500 hover:shadow-2xl"
        :class="animated ? 'translate-y-0 opacity-100' : 'translate-y-10 opacity-0'"
      >
        <h2 class="text-3xl font-bold mb-6 inline-block relative">
          <span class="bg-clip-text text-transparent bg-gradient-to-r from-[#e384c7] to-[#9e6593]">
            {{ t('home.about.title') }}
          </span>
          <span class="absolute bottom-0 left-0 w-full h-1 bg-gradient-to-r from-[#e384c7] to-[#9e6593] rounded-full"></span>
        </h2>
        
        <div class="space-y-6 text-gray-700 dark:text-gray-300">
          <div class="flex items-start gap-3">
            <i class="fas fa-solid fa-user-graduate text-2xl text-[#e384c7] mt-1"></i>
            <p class="text-lg">
              {{ t('home.about.age', { age, status: bachelorStatus }) }}
            </p>
          </div>
          
          <div class="flex items-start gap-3">
            <i class="fas fa-solid fa-map-marker-alt text-2xl text-[#e384c7] mt-1"></i>
            <p class="text-lg">
              {{ t('home.about.location') }}
            </p>
          </div>

          <div class="flex items-start gap-3">
            <i class="fas fa-solid fa-dumbbell text-2xl text-[#e384c7] mt-1"></i>
            <p class="text-lg">
              {{ t('home.about.gym', { years: gymYearsText }) }}
            </p>
          </div>

          <div class="flex items-start gap-3">
            <i class="fas fa-solid fa-laptop-code text-2xl text-[#e384c7] mt-1"></i>
            <p class="text-lg">
              {{ t('home.about.developer') }}
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- Social Media Section -->
    <section class="py-10 mb-16 scroll-mt-20" id="social">
      <div 
        class="bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-2xl shadow-xl p-8 transform transition-all duration-500 hover:shadow-2xl"
        :class="animated ? 'translate-y-0 opacity-100' : 'translate-y-10 opacity-0'"
      >
        <h2 class="text-3xl font-bold mb-6 inline-block relative">
          <span class="bg-clip-text text-transparent bg-gradient-to-r from-[#e384c7] to-[#9e6593]">
            {{ t('home.social.title') }}
          </span>
          <span class="absolute bottom-0 left-0 w-full h-1 bg-gradient-to-r from-[#e384c7] to-[#9e6593] rounded-full"></span>
        </h2>
        
        <p class="text-lg mb-6 text-gray-700 dark:text-gray-300 italic">{{ t('home.social.note') }}</p>
        
        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
          <!-- Fix: Changed the v-for logic to avoid duplicate key issues -->
          <template v-for="(social, index) in socialLinks" :key="index">
            <!-- URL based links -->
            <a 
              :href="social.url" 
              target="_blank" 
              class="flex items-center gap-4 bg-white dark:bg-gray-700 p-4 rounded-lg shadow hover:shadow-md transition-all duration-300 hover:-translate-y-1"
            >
              <i :class="[social.icon, social.color, 'text-2xl']"></i>
              <span class="text-gray-800 dark:text-white">{{ t(social.name) }}</span>
            </a>
            </template>
        </div>
      </div>
    </section>

    <!-- Skills Section -->
    <section class="py-10 mb-16 scroll-mt-20" id="skills">
      <h2 class="text-3xl font-bold mb-10 inline-block relative">
        <span class="bg-clip-text text-transparent bg-gradient-to-r from-[#e384c7] to-[#9e6593]">
          {{ t('home.skills.title') }}
        </span>
        <span class="absolute bottom-0 left-0 w-full h-1 bg-gradient-to-r from-[#e384c7] to-[#9e6593] rounded-full"></span>
      </h2>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div 
          v-for="(skill, index) in skills" 
          :key="index"
          class="bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-xl shadow-lg p-6 flex items-center gap-4 transform transition-all duration-500 hover:scale-105 hover:shadow-xl"
          :class="[
            skillsVisible ? 'translate-y-0 opacity-100' : 'translate-y-10 opacity-0',
            {'delay-100': index % 4 === 0, 'delay-200': index % 4 === 1, 'delay-300': index % 4 === 2, 'delay-400': index % 4 === 3}
          ]"
        >
          <div class="w-12 h-12 flex items-center justify-center rounded-full bg-gray-100 dark:bg-gray-700">
            <i :class="[skill.icon, skill.color, 'text-xl']"></i>
          </div>
          <div>
            <h3 class="text-lg font-semibold text-gray-800 dark:text-white">{{ t(skill.name) }}</h3>
          </div>
        </div>
      </div>
    </section>

    <!-- Project Preview Section -->
    <section class="py-10 mb-16">
      <div 
        class="bg-gradient-to-br from-[#e384c7]/95 to-[#9e6593]/95 backdrop-blur-sm rounded-2xl shadow-xl p-8 text-white transition-all duration-500 hover:shadow-2xl transform hover:scale-[1.01]"
        :class="animated ? 'translate-y-0 opacity-100' : 'translate-y-10 opacity-0'"
      >
        <div class="flex flex-col md:flex-row items-center gap-8">
          <div class="w-full md:w-1/2">
            <h2 class="text-3xl font-bold mb-4">{{ t('home.project.title') }}</h2>
            <p class="text-lg mb-6">
              {{ t('home.project.description') }}
            </p>
            <div class="flex flex-wrap gap-3">
              <span class="inline-block bg-white bg-opacity-20 px-4 py-2 rounded-full text-sm font-medium text-[#e384c7]">{{ t('home.project.tags.flutter') }}</span>
              <span class="inline-block bg-white bg-opacity-20 px-4 py-2 rounded-full text-sm font-medium text-[#e384c7]">{{ t('home.project.tags.social') }}</span>
              <span class="inline-block bg-white bg-opacity-20 px-4 py-2 rounded-full text-sm font-medium text-[#e384c7]">{{ t('home.project.tags.coming') }}</span>
            </div>
          </div>
          <div class="w-full md:w-1/2 flex justify-center">
            <div class="relative w-64 h-64 flex items-center justify-center bg-white bg-opacity-10 rounded-2xl backdrop-blur-sm border border-white border-opacity-20">
              <img src="../assets/logo_color_no.svg" class="w-48 h-48 object-contain animate-pulse" alt="PlatePal Logo" />
              <div class="absolute -bottom-4 left-1/2 transform -translate-x-1/2 bg-white px-4 py-1 rounded-full text-sm font-medium text-[#e384c7]">
                {{ t('home.project.soon') }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css');

/* Make text unselectable */
.no-select {
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
  user-select: none;
}

/* Smooth scrolling */
html {
  scroll-behavior: smooth;
}

/* Animation for elements */
.animate-float {
  animation: float 6s ease-in-out infinite;
}

@keyframes float {
  0% { transform: translateY(0px); }
  50% { transform: translateY(-20px); }
  100% { transform: translateY(0px); }
}

/* Animated underlines for links */
.animated-underline {
  position: relative;
}

.animated-underline::after {
  content: '';
  position: absolute;
  width: 100%;
  height: 2px;
  bottom: 0;
  left: 0;
  background-color: #e384c7;
  transform: scaleX(0);
  transform-origin: bottom right;
  transition: transform 0.3s;
}

.animated-underline:hover::after {
  transform: scaleX(1);
  transform-origin: bottom left;
}

/* Cursor trail effect, will be activated via JS */
.cursor-trail {
  position: absolute;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #e384c7;
  opacity: 0.7;
  pointer-events: none;
  transform: translate(-50%, -50%);
}

/* Animation for skills icons */
.skills-icon {
  transition: all 0.3s;
}

.skills-icon:hover {
  transform: scale(1.1) rotate(10deg);
}
</style>
