<script setup>
import { onMounted } from 'vue';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();

// Animation for content
onMounted(() => {
  const elements = document.querySelectorAll('.animate-fade-in');
  elements.forEach((element, index) => {
    element.style.animationDelay = `${index * 0.1}s`;
  });
});
</script>

<template>
  <!-- Remove the solid background so the AnimatedBackground from App.vue shows through -->
  <div class="min-h-screen bg-transparent">
    <!-- Policy content with animations -->
    <div class="max-w-4xl mx-auto px-4 py-12">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 md:p-8 relative z-10 backdrop-blur-sm bg-opacity-90 dark:bg-opacity-90">
        <h1 class="text-3xl font-bold mb-6 bg-clip-text text-transparent bg-gradient-to-r from-[#e384c7] to-[#9e6593] animate-fade-in">
          {{ t('privacy.title') }}
        </h1>
        
        <p class="text-gray-600 dark:text-gray-300 mb-8 italic animate-fade-in">
          {{ t('privacy.effective') }}
        </p>

        <section class="mb-8 animate-fade-in">
          <h2 class="text-2xl font-semibold mb-4 text-gray-800 dark:text-gray-100">
            {{ t('privacy.intro.title') }}
          </h2>
          <p class="text-gray-600 dark:text-gray-300 mb-4">
            {{ t('privacy.intro.content') }}
          </p>
        </section>

        <section class="mb-8 animate-fade-in">
          <h2 class="text-2xl font-semibold mb-4 text-gray-800 dark:text-gray-100">
            {{ t('privacy.data.title') }}
          </h2>
          
          <h3 class="text-xl font-medium mb-2 text-gray-800 dark:text-gray-100">
            {{ t('privacy.data.camera.title') }}
          </h3>
          <p class="text-gray-600 dark:text-gray-300 mb-4">
            {{ t('privacy.data.camera.content') }}
          </p>

          <h3 class="text-xl font-medium mb-2 text-gray-800 dark:text-gray-100">
            {{ t('privacy.data.processing.title') }}
          </h3>
          <p class="text-gray-600 dark:text-gray-300 mb-2">
            {{ t('privacy.data.processing.intro') }}
          </p>
          <ul class="list-disc pl-6 mb-4 text-gray-600 dark:text-gray-300">
            <li class="mb-1">{{ t('privacy.data.processing.account') }}</li>
            <li class="mb-1">{{ t('privacy.data.processing.custom') }}</li>
          </ul>
          <p class="text-gray-600 dark:text-gray-300 mb-4">
            {{ t('privacy.data.processing.purpose') }}
          </p>

          <h3 class="text-xl font-medium mb-2 text-gray-800 dark:text-gray-100">
            {{ t('privacy.data.local.title') }}
          </h3>
          <p class="text-gray-600 dark:text-gray-300 mb-2">
            {{ t('privacy.data.local.intro') }}
          </p>
          <ul class="list-disc pl-6 mb-4 text-gray-600 dark:text-gray-300">
            <li class="mb-1">{{ t('privacy.data.local.images') }}</li>
            <li class="mb-1">{{ t('privacy.data.local.nutrition') }}</li>
            <li class="mb-1">{{ t('privacy.data.local.logs') }}</li>
            <li class="mb-1">{{ t('privacy.data.local.prefs') }}</li>
          </ul>
          <p class="text-gray-600 dark:text-gray-300 mb-4">
            {{ t('privacy.data.local.storage') }}
          </p>
        </section>

        <!-- More sections would continue here, following the same pattern -->
        
        <section class="mb-8 animate-fade-in">
          <h2 class="text-2xl font-semibold mb-4 text-gray-800 dark:text-gray-100">
            {{ t('privacy.contact.title') }}
          </h2>
          <p class="text-gray-600 dark:text-gray-300">
            {{ t('privacy.contact.content') }}
          </p>
        </section>

        <p class="text-gray-500 dark:text-gray-400 italic mt-12 animate-fade-in">
          {{ t('privacy.lastUpdated') }}
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.6s ease-in-out forwards;
  opacity: 0;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
