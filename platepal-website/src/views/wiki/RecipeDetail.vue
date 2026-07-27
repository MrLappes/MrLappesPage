<script setup>
import { ref, watch, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { RouterLink } from 'vue-router';
import { api } from '../../wiki/api.js';
import RichTextView from '../../components/wiki/RichTextView.vue';
import NutritionTable from '../../components/wiki/NutritionTable.vue';

const props = defineProps({ slug: { type: String, required: true } });
const { t, locale } = useI18n();

const recipe = ref(null);
const loading = ref(true);
const error = ref('');

async function load() {
  loading.value = true;
  error.value = '';
  try {
    recipe.value = await api.getRecipe(props.slug, locale.value);
  } catch (e) {
    error.value = e.status === 404 ? t('wiki.recipe.notFound') : e.message;
    recipe.value = null;
  } finally {
    loading.value = false;
  }
}

watch(locale, load);
watch(() => props.slug, load);
onMounted(load);

// --- PlatePal Tracker export ---------------------------------------------
const exportOpen = ref(false);
const exportPortion = ref('serving');
const exportMsg = ref('');
let exportMsgTimer;

function flashExport(msg) {
  exportMsg.value = msg;
  clearTimeout(exportMsgTimer);
  exportMsgTimer = setTimeout(() => {
    exportMsg.value = '';
  }, 2500);
}

async function fetchDish() {
  const dish = await api.exportRecipe(props.slug, locale.value, exportPortion.value);
  if (recipe.value?.image_id) {
    const url = api.absoluteImageUrl(recipe.value.image_id);
    dish.imageUrl = url;
    dish.imageUri = url;
  }
  return dish;
}

async function copyForTracker() {
  try {
    const dish = await fetchDish();
    await navigator.clipboard.writeText(JSON.stringify(dish, null, 2));
    flashExport(t('wiki.recipe.export.copied'));
  } catch {
    flashExport(t('wiki.recipe.export.failed'));
  }
}

async function downloadForTracker() {
  try {
    const dish = await fetchDish();
    const payload = { dishes: [dish], dishLogs: [] };
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `platepal_${props.slug}.json`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
    flashExport(t('wiki.recipe.export.downloaded'));
  } catch {
    flashExport(t('wiki.recipe.export.failed'));
  }
}

</script>

<template>
  <div class="max-w-4xl mx-auto">
    <RouterLink
      :to="{ name: 'WikiRecipes' }"
      class="inline-flex items-center gap-2 text-sm text-gray-500 hover:text-primary transition mb-6"
    >
      <i class="fas fa-arrow-left"></i>{{ t('wiki.recipe.back') }}
    </RouterLink>

    <div v-if="loading" class="space-y-6">
      <div class="wiki-skeleton h-64 w-full rounded-2xl"></div>
      <div class="wiki-skeleton h-8 w-2/3"></div>
      <div class="wiki-skeleton h-4 w-full"></div>
      <div class="wiki-skeleton h-4 w-5/6"></div>
    </div>

    <div v-else-if="error" class="text-center py-16 text-gray-400">
      <i class="fas fa-circle-exclamation text-4xl mb-3"></i>
      <p>{{ error }}</p>
    </div>

    <article v-else-if="recipe" class="wiki-fade-in">
      <div
        v-if="recipe.image_id"
        class="h-64 md:h-80 rounded-2xl overflow-hidden shadow-lg mb-6 bg-gray-100 dark:bg-dark-bg"
      >
        <img :src="api.imageUrl(recipe.image_id)" :alt="recipe.title" class="w-full h-full object-cover" />
      </div>

      <h1 class="text-3xl md:text-4xl font-bold gradient-text mb-2">{{ recipe.title }}</h1>
      <p v-if="recipe.summary" class="text-lg text-gray-500 dark:text-gray-400 mb-4">{{ recipe.summary }}</p>

      <div class="flex flex-wrap gap-2 mb-8 text-sm">
        <span class="px-3 py-1.5 rounded-full bg-primary-light text-secondary dark:text-primary font-medium">
          <i class="fas fa-users mr-1"></i>{{ t('wiki.recipe.servings', { count: recipe.servings }) }}
        </span>
        <span class="px-3 py-1.5 rounded-full bg-gray-100 dark:bg-dark-elevated text-gray-600 dark:text-gray-300 font-medium">
          <i class="fas fa-fire mr-1"></i>{{ recipe.nutrition.per_serving.kcal }} kcal / {{ t('wiki.recipe.perServing') }}
        </span>
      </div>

      <div class="mb-8">
        <button
          type="button"
          class="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-primary text-white text-sm font-semibold shadow-sm hover:bg-secondary transition"
          @click="exportOpen = !exportOpen"
        >
          <i class="fas fa-mobile-screen-button"></i>{{ t('wiki.recipe.export.button') }}
          <i class="fas fa-chevron-down text-xs transition-transform" :class="{ 'rotate-180': exportOpen }"></i>
        </button>

        <div
          v-if="exportOpen"
          class="mt-3 p-4 rounded-2xl bg-white dark:bg-dark-surface shadow-sm border border-gray-100 dark:border-dark-elevated max-w-lg"
        >
          <p class="text-sm text-gray-500 dark:text-gray-400 mb-3">{{ t('wiki.recipe.export.hint') }}</p>

          <div class="flex gap-2 mb-4">
            <button
              type="button"
              class="flex-1 px-3 py-1.5 rounded-lg text-sm font-medium border transition"
              :class="exportPortion === 'serving'
                ? 'bg-primary-light text-secondary dark:text-primary border-primary'
                : 'border-gray-200 dark:border-dark-elevated text-gray-500'"
              @click="exportPortion = 'serving'"
            >
              {{ t('wiki.recipe.export.perServing') }}
            </button>
            <button
              type="button"
              class="flex-1 px-3 py-1.5 rounded-lg text-sm font-medium border transition"
              :class="exportPortion === 'whole'
                ? 'bg-primary-light text-secondary dark:text-primary border-primary'
                : 'border-gray-200 dark:border-dark-elevated text-gray-500'"
              @click="exportPortion = 'whole'"
            >
              {{ t('wiki.recipe.export.wholeRecipe') }}
            </button>
          </div>

          <div class="flex flex-wrap gap-2">
            <button
              type="button"
              class="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-gray-100 dark:bg-dark-elevated text-gray-700 dark:text-gray-200 text-sm font-medium hover:bg-gray-200 dark:hover:bg-dark-bg transition"
              @click="copyForTracker"
            >
              <i class="fas fa-copy"></i>{{ t('wiki.recipe.export.copy') }}
            </button>
            <button
              type="button"
              class="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-gray-100 dark:bg-dark-elevated text-gray-700 dark:text-gray-200 text-sm font-medium hover:bg-gray-200 dark:hover:bg-dark-bg transition"
              @click="downloadForTracker"
            >
              <i class="fas fa-download"></i>{{ t('wiki.recipe.export.download') }}
            </button>
            <span v-if="exportMsg" class="inline-flex items-center gap-1 text-sm text-green-600 dark:text-green-400">
              <i class="fas fa-check"></i>{{ exportMsg }}
            </span>
          </div>

          <p class="text-xs text-gray-400 mt-3">{{ t('wiki.recipe.export.usage') }}</p>
        </div>
      </div>

      <div class="grid md:grid-cols-5 gap-8">
        <div class="md:col-span-3 space-y-8">
          <section>
            <h2 class="text-xl font-bold mb-3 flex items-center gap-2">
              <i class="fas fa-carrot text-primary"></i>{{ t('wiki.recipe.ingredients') }}
            </h2>
            <ul class="space-y-2">
              <li
                v-for="ing in recipe.ingredients"
                :key="ing.ingredient_id"
                class="flex items-center gap-3 bg-white dark:bg-dark-surface rounded-xl px-4 py-2.5 shadow-sm"
              >
                <div class="w-9 h-9 rounded-lg bg-gray-100 dark:bg-dark-bg overflow-hidden flex-shrink-0">
                  <img v-if="ing.image_id" :src="api.imageUrl(ing.image_id)" :alt="ing.name" class="w-full h-full object-cover" />
                  <div v-else class="w-full h-full flex items-center justify-center text-gray-300 text-xs">
                    <i class="fas fa-leaf"></i>
                  </div>
                </div>
                <RouterLink
                  :to="{ name: 'WikiIngredient', params: { slug: ing.slug } }"
                  class="flex-1 font-medium hover:text-primary transition"
                >
                  {{ ing.name }}
                </RouterLink>
                <span class="text-sm text-gray-500 tabular-nums">{{ ing.grams }} g</span>
                <span class="text-xs text-gray-400 tabular-nums w-16 text-right">{{ ing.kcal }} kcal</span>
              </li>
            </ul>
          </section>

          <section v-if="recipe.instructions_html">
            <h2 class="text-xl font-bold mb-3 flex items-center gap-2">
              <i class="fas fa-list-ol text-primary"></i>{{ t('wiki.recipe.instructions') }}
            </h2>
            <RichTextView :html="recipe.instructions_html" />
          </section>
        </div>

        <div class="md:col-span-2">
          <div class="sticky top-24">
            <NutritionTable :nutrition="recipe.nutrition" :servings="recipe.servings" />
          </div>
        </div>
      </div>
    </article>
  </div>
</template>
