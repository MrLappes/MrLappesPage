<script setup>
import { ref, reactive, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { api } from '../../wiki/api.js';
import RichTextEditor from '../../components/wiki/RichTextEditor.vue';
import ImageUpload from '../../components/wiki/ImageUpload.vue';
import IngredientPicker from '../../components/wiki/IngredientPicker.vue';

const props = defineProps({ id: { type: [String, Number], default: null } });
const router = useRouter();
const { t } = useI18n();

const LOCALES = [
  { code: 'en', label: 'English' },
  { code: 'de', label: 'Deutsch' },
  { code: 'cs', label: 'Čeština' },
  { code: 'jp', label: '日本語' },
];

const activeLocale = ref('en');
const loading = ref(!!props.id);
const saving = ref(false);
const error = ref('');

const form = reactive({
  servings: 2,
  image_id: null,
  published: true,
  ingredients: [],
});

const translations = reactive({});
LOCALES.forEach((l) => {
  translations[l.code] = { title: '', summary: '', instructions_html: '' };
});

const missingLocales = computed(() =>
  LOCALES.filter((l) => !translations[l.code].title.trim()).map((l) => l.code)
);

async function load() {
  if (!props.id) return;
  try {
    const data = await api.adminGetRecipe(props.id);
    form.servings = data.servings;
    form.image_id = data.image_id;
    form.published = data.published;
    form.ingredients = data.ingredients.map((i) => ({ ingredient_id: i.ingredient_id, grams: i.grams }));
    for (const tr of data.translations) {
      if (translations[tr.locale]) {
        translations[tr.locale] = {
          title: tr.title, summary: tr.summary, instructions_html: tr.instructions_html,
        };
      }
    }
  } catch (e) {
    error.value = e.message;
  } finally {
    loading.value = false;
  }
}

async function save() {
  error.value = '';
  if (missingLocales.value.length) {
    error.value = t('wiki.admin.editor.missingTitles', { locales: missingLocales.value.join(', ') });
    return;
  }
  saving.value = true;
  try {
    const payload = {
      servings: Number(form.servings),
      image_id: form.image_id,
      published: form.published,
      ingredients: form.ingredients.map((i) => ({ ingredient_id: i.ingredient_id, grams: Number(i.grams) })),
      translations: LOCALES.map((l) => ({
        locale: l.code,
        title: translations[l.code].title.trim(),
        summary: translations[l.code].summary.trim(),
        instructions_html: translations[l.code].instructions_html,
      })),
    };
    if (props.id) await api.updateRecipe(props.id, payload);
    else await api.createRecipe(payload);
    router.replace({ name: 'WikiAdminDashboard' });
  } catch (e) {
    error.value = e.message;
  } finally {
    saving.value = false;
  }
}

onMounted(load);
</script>

<template>
  <div class="max-w-3xl mx-auto">
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold gradient-text">
        {{ props.id ? t('wiki.admin.editor.editRecipe') : t('wiki.admin.editor.newRecipe') }}
      </h1>
      <button @click="router.back()" class="text-sm text-gray-500 hover:text-primary transition">
        <i class="fas fa-arrow-left mr-1"></i>{{ t('wiki.admin.editor.cancel') }}
      </button>
    </div>

    <div v-if="loading" class="space-y-4">
      <div class="wiki-skeleton h-48 w-full rounded-2xl"></div>
      <div class="wiki-skeleton h-32 w-full rounded-2xl"></div>
    </div>

    <div v-else class="space-y-6">
      <div class="bg-white dark:bg-dark-surface rounded-2xl shadow-md p-5">
        <h2 class="font-semibold mb-3">{{ t('wiki.admin.editor.image') }}</h2>
        <ImageUpload v-model="form.image_id" />
      </div>

      <div class="bg-white dark:bg-dark-surface rounded-2xl shadow-md p-5 flex flex-wrap items-center gap-6">
        <div>
          <label class="block text-sm font-medium mb-1">{{ t('wiki.admin.editor.servings') }}</label>
          <input v-model="form.servings" type="number" min="1" step="1"
            class="w-28 px-3 py-2 rounded-lg border border-gray-200 dark:border-dark-elevated bg-white dark:bg-dark-bg focus:ring-2 focus:ring-primary focus:outline-none" />
        </div>
        <label class="flex items-center gap-2 cursor-pointer mt-5">
          <input v-model="form.published" type="checkbox" class="w-4 h-4 accent-primary" />
          <span class="text-sm font-medium">{{ t('wiki.admin.editor.published') }}</span>
        </label>
      </div>

      <div class="bg-white dark:bg-dark-surface rounded-2xl shadow-md p-5">
        <h2 class="font-semibold mb-3">{{ t('wiki.recipe.ingredients') }}</h2>
        <IngredientPicker v-model="form.ingredients" />
      </div>

      <div class="bg-white dark:bg-dark-surface rounded-2xl shadow-md p-5">
        <div class="flex gap-1 mb-4 border-b border-gray-100 dark:border-dark-elevated">
          <button v-for="l in LOCALES" :key="l.code" type="button"
            @click="activeLocale = l.code"
            class="px-3 py-2 text-sm font-medium border-b-2 transition -mb-px"
            :class="activeLocale === l.code ? 'border-primary text-primary' : 'border-transparent text-gray-400 hover:text-gray-600'">
            {{ l.label }}
            <span v-if="!translations[l.code].title.trim()" class="text-red-400 ml-0.5">•</span>
          </button>
        </div>

        <div v-for="l in LOCALES" v-show="activeLocale === l.code" :key="l.code" class="space-y-3">
          <div>
            <label class="block text-sm font-medium mb-1">{{ t('wiki.admin.editor.title') }} *</label>
            <input v-model="translations[l.code].title" type="text"
              class="w-full px-4 py-2.5 rounded-xl border border-gray-200 dark:border-dark-elevated bg-white dark:bg-dark-bg focus:ring-2 focus:ring-primary focus:outline-none" />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">{{ t('wiki.admin.editor.summary') }}</label>
            <input v-model="translations[l.code].summary" type="text"
              class="w-full px-4 py-2.5 rounded-xl border border-gray-200 dark:border-dark-elevated bg-white dark:bg-dark-bg focus:ring-2 focus:ring-primary focus:outline-none" />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">{{ t('wiki.recipe.instructions') }}</label>
            <RichTextEditor v-model="translations[l.code].instructions_html" :placeholder="t('wiki.admin.editor.instructionsPlaceholder')" />
          </div>
        </div>
      </div>

      <p v-if="error" class="text-sm text-red-500">{{ error }}</p>

      <div class="flex justify-end gap-2">
        <button @click="router.back()" class="px-4 py-2.5 rounded-xl border border-gray-200 dark:border-dark-elevated hover:bg-gray-50 dark:hover:bg-dark-bg transition font-medium">
          {{ t('wiki.admin.editor.cancel') }}
        </button>
        <button @click="save" :disabled="saving"
          class="px-6 py-2.5 rounded-xl gradient-bg text-white font-semibold hover:opacity-90 transition disabled:opacity-50">
          <i v-if="saving" class="fas fa-spinner fa-spin mr-2"></i>{{ t('wiki.admin.editor.save') }}
        </button>
      </div>
    </div>
  </div>
</template>
