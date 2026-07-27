<script setup>
import { ref, watch, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { RouterLink } from 'vue-router';
import { api } from '../../wiki/api.js';

const { t, locale } = useI18n();

const ingredients = ref([]);
const loading = ref(true);
const error = ref('');
const search = ref('');
let debounce;

async function load() {
  loading.value = true;
  error.value = '';
  try {
    ingredients.value = await api.listIngredients(locale.value, search.value.trim());
  } catch (e) {
    error.value = e.message || 'Failed to load ingredients';
  } finally {
    loading.value = false;
  }
}

function onSearch() {
  clearTimeout(debounce);
  debounce = setTimeout(load, 250);
}

watch(locale, load);
onMounted(load);
</script>

<template>
  <div class="max-w-6xl mx-auto">
    <div class="text-center mb-8">
      <h1 class="text-3xl md:text-4xl font-bold gradient-text mb-2">{{ t('wiki.ingredients.title') }}</h1>
      <p class="text-gray-500 dark:text-gray-400">{{ t('wiki.ingredients.subtitle') }}</p>
    </div>

    <div class="max-w-md mx-auto mb-8">
      <div class="relative">
        <i class="fas fa-search absolute left-4 top-1/2 -translate-y-1/2 text-gray-400"></i>
        <input
          v-model="search"
          type="text"
          :placeholder="t('wiki.ingredients.searchPlaceholder')"
          class="w-full pl-11 pr-4 py-3 rounded-full border border-gray-200 dark:border-dark-elevated bg-white dark:bg-dark-surface focus:ring-2 focus:ring-primary focus:outline-none transition"
          @input="onSearch"
        />
      </div>
    </div>

    <div v-if="loading" class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
      <div v-for="n in 8" :key="n" class="bg-white dark:bg-dark-surface rounded-2xl shadow-md p-4">
        <div class="wiki-skeleton h-24 w-full mb-3"></div>
        <div class="wiki-skeleton h-4 w-2/3 mx-auto"></div>
      </div>
    </div>

    <p v-else-if="error" class="text-center text-red-500 py-10">{{ error }}</p>

    <div v-else-if="ingredients.length === 0" class="text-center py-16 text-gray-400">
      <i class="fas fa-leaf text-4xl mb-3"></i>
      <p>{{ t('wiki.ingredients.empty') }}</p>
    </div>

    <div v-else class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
      <RouterLink
        v-for="ing in ingredients"
        :key="ing.slug"
        :to="{ name: 'WikiIngredient', params: { slug: ing.slug } }"
        class="wiki-fade-in group bg-white dark:bg-dark-surface rounded-2xl shadow-md hover:shadow-xl overflow-hidden transition-all duration-300 hover:-translate-y-1"
      >
        <div class="h-28 bg-gray-100 dark:bg-dark-bg overflow-hidden">
          <img
            v-if="ing.image_id"
            :src="api.imageUrl(ing.image_id)"
            :alt="ing.name"
            loading="lazy"
            class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
          />
          <div v-else class="w-full h-full flex items-center justify-center text-gray-300">
            <i class="fas fa-leaf text-2xl"></i>
          </div>
        </div>
        <div class="p-3 text-center">
          <h3 class="font-semibold text-sm mb-1 group-hover:text-primary transition-colors truncate">{{ ing.name }}</h3>
          <span class="text-xs text-gray-400">{{ ing.kcal }} kcal / 100 g</span>
        </div>
      </RouterLink>
    </div>
  </div>
</template>
