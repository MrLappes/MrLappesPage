<script setup>
import { ref, watch, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { RouterLink } from 'vue-router';
import { api } from '../../wiki/api.js';
import SkeletonCard from '../../components/wiki/SkeletonCard.vue';

const { t, locale } = useI18n();

const recipes = ref([]);
const loading = ref(true);
const error = ref('');
const search = ref('');
let debounce;

async function load() {
  loading.value = true;
  error.value = '';
  try {
    recipes.value = await api.listRecipes(locale.value, search.value.trim());
  } catch (e) {
    error.value = e.message || 'Failed to load recipes';
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
      <h1 class="text-3xl md:text-4xl font-bold gradient-text mb-2">{{ t('wiki.recipes.title') }}</h1>
      <p class="text-gray-500 dark:text-gray-400">{{ t('wiki.recipes.subtitle') }}</p>
    </div>

    <div class="max-w-md mx-auto mb-8">
      <div class="relative">
        <i class="fas fa-search absolute left-4 top-1/2 -translate-y-1/2 text-gray-400"></i>
        <input
          v-model="search"
          type="text"
          :placeholder="t('wiki.recipes.searchPlaceholder')"
          class="w-full pl-11 pr-4 py-3 rounded-full border border-gray-200 dark:border-dark-elevated bg-white dark:bg-dark-surface focus:ring-2 focus:ring-primary focus:outline-none transition"
          @input="onSearch"
        />
      </div>
    </div>

    <SkeletonCard v-if="loading" :count="6" />

    <p v-else-if="error" class="text-center text-red-500 py-10">{{ error }}</p>

    <div v-else-if="recipes.length === 0" class="text-center py-16 text-gray-400">
      <i class="fas fa-utensils text-4xl mb-3"></i>
      <p>{{ t('wiki.recipes.empty') }}</p>
    </div>

    <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
      <RouterLink
        v-for="recipe in recipes"
        :key="recipe.slug"
        :to="{ name: 'WikiRecipe', params: { slug: recipe.slug } }"
        class="wiki-fade-in group bg-white dark:bg-dark-surface rounded-2xl shadow-md hover:shadow-xl overflow-hidden transition-all duration-300 hover:-translate-y-1"
      >
        <div class="h-44 bg-gray-100 dark:bg-dark-bg overflow-hidden">
          <img
            v-if="recipe.image_id"
            :src="api.imageUrl(recipe.image_id)"
            :alt="recipe.title"
            loading="lazy"
            class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
          />
          <div v-else class="w-full h-full flex items-center justify-center text-gray-300">
            <i class="fas fa-utensils text-3xl"></i>
          </div>
        </div>
        <div class="p-4">
          <h3 class="font-bold text-lg mb-1 group-hover:text-primary transition-colors">{{ recipe.title }}</h3>
          <p class="text-sm text-gray-500 dark:text-gray-400 line-clamp-2 mb-3">{{ recipe.summary }}</p>
          <div class="flex items-center gap-2 text-xs">
            <span class="px-2.5 py-1 rounded-full bg-primary-light text-secondary dark:text-primary font-medium">
              <i class="fas fa-fire mr-1"></i>{{ recipe.kcal_per_serving }} kcal
            </span>
            <span class="px-2.5 py-1 rounded-full bg-gray-100 dark:bg-dark-elevated text-gray-500 dark:text-gray-300 font-medium">
              <i class="fas fa-users mr-1"></i>{{ recipe.servings }}
            </span>
          </div>
        </div>
      </RouterLink>
    </div>
  </div>
</template>
