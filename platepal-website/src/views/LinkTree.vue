<script setup>
import { ref, computed } from 'vue';
import { useI18n } from 'vue-i18n';
import { links, categories } from '../data/links.js';

const { t } = useI18n();

const search = ref('');
const activeCategory = ref(null);

const filtered = computed(() => {
  const q = search.value.trim().toLowerCase();
  return links.filter((link) => {
    const matchesSearch =
      !q ||
      link.title.toLowerCase().includes(q) ||
      link.description.toLowerCase().includes(q) ||
      link.url.toLowerCase().includes(q);
    const matchesCategory =
      !activeCategory.value || link.category === activeCategory.value;
    return matchesSearch && matchesCategory;
  });
});

const setCategory = (cat) => {
  activeCategory.value = activeCategory.value === cat ? null : cat;
};

const imgError = (e) => {
  e.target.src = '/icon.png';
};
</script>

<template>
  <div class="min-h-screen bg-transparent">
    <div class="max-w-4xl mx-auto px-4 py-12">
      <div
        class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 md:p-8 relative z-10 backdrop-blur-sm bg-opacity-90 dark:bg-opacity-90 animate-fade-in"
      >
        <!-- Title -->
        <h1
          class="text-3xl font-bold mb-2 bg-clip-text text-transparent bg-gradient-to-r from-[#e384c7] to-[#9e6593] animate-fade-in"
        >
          {{ t('linktree.title') }}
        </h1>
        <p class="text-gray-500 dark:text-gray-400 mb-6 animate-fade-in">
          {{ t('linktree.subtitle') }}
        </p>

        <!-- Search -->
        <div class="relative mb-4 animate-fade-in">
          <span class="absolute inset-y-0 left-3 flex items-center pointer-events-none text-gray-400">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M21 21l-4.35-4.35M17 11A6 6 0 1 1 5 11a6 6 0 0 1 12 0z" />
            </svg>
          </span>
          <input
            v-model="search"
            type="text"
            :placeholder="t('linktree.searchPlaceholder')"
            class="w-full pl-10 pr-4 py-2 rounded-lg border border-gray-200 dark:border-gray-600 bg-gray-50 dark:bg-gray-700 text-gray-800 dark:text-gray-100 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-[#e384c7] transition-all duration-200"
          />
          <button
            v-if="search"
            @click="search = ''"
            class="absolute inset-y-0 right-3 flex items-center text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 transition-colors duration-200"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Category chips -->
        <div class="flex flex-wrap gap-2 mb-6 animate-fade-in">
          <button
            @click="activeCategory = null"
            :class="[
              'px-3 py-1 rounded-full text-sm font-medium transition-all duration-200',
              activeCategory === null
                ? 'bg-gradient-to-r from-[#e384c7] to-[#9e6593] text-white shadow'
                : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600',
            ]"
          >
            {{ t('linktree.all') }}
          </button>
          <button
            v-for="cat in categories"
            :key="cat"
            @click="setCategory(cat)"
            :class="[
              'px-3 py-1 rounded-full text-sm font-medium transition-all duration-200',
              activeCategory === cat
                ? 'bg-gradient-to-r from-[#e384c7] to-[#9e6593] text-white shadow'
                : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600',
            ]"
          >
            {{ t('linktree.categories.' + cat) }}
          </button>
        </div>

        <!-- Link cards -->
        <transition-group
          name="card"
          tag="div"
          class="grid grid-cols-1 sm:grid-cols-2 gap-4"
        >
          <a
            v-for="link in filtered"
            :key="link.id"
            :href="link.url"
            target="_blank"
            rel="noopener noreferrer"
            class="group flex items-center gap-4 p-4 rounded-lg border border-gray-100 dark:border-gray-700 bg-gray-50 dark:bg-gray-700/50 hover:border-[#e384c7] dark:hover:border-[#e384c7] hover:shadow-md transition-all duration-200"
          >
            <!-- Thumbnail -->
            <div class="flex-shrink-0 w-14 h-14 rounded-lg overflow-hidden bg-white dark:bg-gray-600 flex items-center justify-center shadow-sm">
              <!-- Inline SVG icon (e.g. Printables) -->
              <svg
                v-if="link.iconSvg"
                :viewBox="link.iconViewBox || '0 0 24 24'"
                class="w-8 h-8 fill-[#e384c7]"
                xmlns="http://www.w3.org/2000/svg"
                aria-hidden="true"
              >
                <path :d="link.iconSvg" />
              </svg>
              <!-- Image icon -->
              <img
                v-else
                :src="link.image"
                :alt="link.title"
                @error="imgError"
                class="w-full h-full object-contain p-1"
              />
            </div>

            <!-- Text -->
            <div class="min-w-0 flex-1">
              <div class="flex items-center gap-2 flex-wrap">
                <span class="font-semibold text-gray-800 dark:text-gray-100 group-hover:text-[#e384c7] transition-colors duration-200 truncate">
                  {{ link.title }}
                </span>
                <span class="text-xs px-2 py-0.5 rounded-full bg-[#e384c7]/15 text-[#9e6593] dark:text-[#e384c7] font-medium whitespace-nowrap">
                  {{ t('linktree.categories.' + link.category) }}
                </span>
              </div>
              <p class="text-sm text-gray-500 dark:text-gray-400 truncate mt-0.5">{{ link.description }}</p>
              <p class="text-xs text-gray-400 dark:text-gray-500 truncate mt-0.5">{{ link.url }}</p>
            </div>

            <!-- Arrow -->
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-4 w-4 flex-shrink-0 text-gray-300 dark:text-gray-500 group-hover:text-[#e384c7] transition-colors duration-200"
              fill="none" viewBox="0 0 24 24" stroke="currentColor"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </a>
        </transition-group>

        <!-- Empty state -->
        <div
          v-if="filtered.length === 0"
          class="flex flex-col items-center justify-center py-16 text-gray-400 dark:text-gray-500"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mb-3 opacity-40" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
              d="M21 21l-4.35-4.35M17 11A6 6 0 1 1 5 11a6 6 0 0 1 12 0z" />
          </svg>
          <p class="text-sm">{{ t('linktree.empty') }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.5s ease-in-out forwards;
  opacity: 0;
}

.animate-fade-in:nth-child(2) { animation-delay: 0.05s; }
.animate-fade-in:nth-child(3) { animation-delay: 0.10s; }
.animate-fade-in:nth-child(4) { animation-delay: 0.15s; }
.animate-fade-in:nth-child(5) { animation-delay: 0.20s; }

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(16px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* Card transition-group animations */
.card-enter-active,
.card-leave-active {
  transition: all 0.25s ease;
}
.card-enter-from,
.card-leave-to {
  opacity: 0;
  transform: translateY(10px) scale(0.97);
}
.card-move {
  transition: transform 0.25s ease;
}
</style>
