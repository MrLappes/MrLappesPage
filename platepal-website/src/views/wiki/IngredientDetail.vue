<script setup>
import { ref, watch, computed, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { RouterLink } from 'vue-router';
import { api } from '../../wiki/api.js';
import RichTextView from '../../components/wiki/RichTextView.vue';

const props = defineProps({ slug: { type: String, required: true } });
const { t, locale } = useI18n();

const ingredient = ref(null);
const loading = ref(true);
const error = ref('');

async function load() {
  loading.value = true;
  error.value = '';
  try {
    ingredient.value = await api.getIngredient(props.slug, locale.value);
  } catch (e) {
    error.value = e.status === 404 ? t('wiki.ingredient.notFound') : e.message;
    ingredient.value = null;
  } finally {
    loading.value = false;
  }
}

const macros = computed(() => {
  if (!ingredient.value) return [];
  const i = ingredient.value;
  return [
    { key: 'kcal', value: i.kcal, unit: 'kcal' },
    { key: 'protein', value: i.protein, unit: 'g' },
    { key: 'carbs', value: i.carbs, unit: 'g' },
    { key: 'fat', value: i.fat, unit: 'g' },
    { key: 'fiber', value: i.fiber, unit: 'g' },
    { key: 'sugar', value: i.sugar, unit: 'g' },
    { key: 'salt', value: i.salt, unit: 'g' },
  ].filter((m) => m.value !== null && m.value !== undefined);
});

watch(locale, load);
watch(() => props.slug, load);
onMounted(load);
</script>

<template>
  <div class="max-w-3xl mx-auto">
    <RouterLink
      :to="{ name: 'WikiIngredients' }"
      class="inline-flex items-center gap-2 text-sm text-gray-500 hover:text-primary transition mb-6"
    >
      <i class="fas fa-arrow-left"></i>{{ t('wiki.ingredient.back') }}
    </RouterLink>

    <div v-if="loading" class="space-y-6">
      <div class="wiki-skeleton h-56 w-full rounded-2xl"></div>
      <div class="wiki-skeleton h-8 w-1/2"></div>
      <div class="wiki-skeleton h-24 w-full"></div>
    </div>

    <div v-else-if="error" class="text-center py-16 text-gray-400">
      <i class="fas fa-circle-exclamation text-4xl mb-3"></i>
      <p>{{ error }}</p>
    </div>

    <article v-else-if="ingredient" class="wiki-fade-in">
      <div class="flex flex-col sm:flex-row gap-6 mb-8">
        <div class="w-full sm:w-48 h-48 rounded-2xl overflow-hidden shadow-lg bg-gray-100 dark:bg-dark-bg flex-shrink-0">
          <img v-if="ingredient.image_id" :src="api.imageUrl(ingredient.image_id)" :alt="ingredient.name" class="w-full h-full object-cover" />
          <div v-else class="w-full h-full flex items-center justify-center text-gray-300">
            <i class="fas fa-leaf text-4xl"></i>
          </div>
        </div>
        <div class="flex-1">
          <h1 class="text-3xl font-bold gradient-text mb-3">{{ ingredient.name }}</h1>
          <p class="text-sm text-gray-400 mb-3">{{ t('wiki.ingredient.per100g') }}</p>
          <div class="grid grid-cols-2 sm:grid-cols-3 gap-2">
            <div
              v-for="m in macros"
              :key="m.key"
              class="bg-white dark:bg-dark-surface rounded-xl px-3 py-2 shadow-sm"
            >
              <div class="text-xs text-gray-400">{{ t(`wiki.nutrients.${m.key}`) }}</div>
              <div class="font-semibold tabular-nums">{{ m.value }} {{ m.unit }}</div>
            </div>
          </div>
        </div>
      </div>

      <section v-if="ingredient.description_html" class="mb-8">
        <h2 class="text-xl font-bold mb-3">{{ t('wiki.ingredient.about') }}</h2>
        <RichTextView :html="ingredient.description_html" />
      </section>

      <section v-if="ingredient.used_in && ingredient.used_in.length">
        <h2 class="text-xl font-bold mb-3 flex items-center gap-2">
          <i class="fas fa-utensils text-primary"></i>{{ t('wiki.ingredient.usedIn') }}
        </h2>
        <div class="flex flex-wrap gap-2">
          <RouterLink
            v-for="r in ingredient.used_in"
            :key="r.slug"
            :to="{ name: 'WikiRecipe', params: { slug: r.slug } }"
            class="px-3 py-1.5 rounded-full bg-primary-light text-secondary dark:text-primary text-sm font-medium hover:opacity-80 transition"
          >
            {{ r.title }}
          </RouterLink>
        </div>
      </section>
    </article>
  </div>
</template>
