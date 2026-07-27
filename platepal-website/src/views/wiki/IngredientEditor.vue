<script setup>
import { ref, reactive, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { api } from '../../wiki/api.js';
import RichTextEditor from '../../components/wiki/RichTextEditor.vue';
import ImageUpload from '../../components/wiki/ImageUpload.vue';

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
  kcal: 0, protein: 0, carbs: 0, fat: 0,
  fiber: null, sugar: null, salt: null,
  image_id: null,
});

const translations = reactive({});
LOCALES.forEach((l) => {
  translations[l.code] = { name: '', description_html: '' };
});

const NUTRIENTS = [
  { key: 'kcal', unit: 'kcal', required: true },
  { key: 'protein', unit: 'g', required: true },
  { key: 'carbs', unit: 'g', required: true },
  { key: 'fat', unit: 'g', required: true },
  { key: 'fiber', unit: 'g', required: false },
  { key: 'sugar', unit: 'g', required: false },
  { key: 'salt', unit: 'g', required: false },
];

const missingLocales = computed(() =>
  LOCALES.filter((l) => !translations[l.code].name.trim()).map((l) => l.code)
);

async function load() {
  if (!props.id) return;
  try {
    const data = await api.adminGetIngredient(props.id);
    Object.assign(form, {
      kcal: data.kcal, protein: data.protein, carbs: data.carbs, fat: data.fat,
      fiber: data.fiber, sugar: data.sugar, salt: data.salt, image_id: data.image_id,
    });
    for (const tr of data.translations) {
      if (translations[tr.locale]) {
        translations[tr.locale] = { name: tr.name, description_html: tr.description_html };
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
    error.value = t('wiki.admin.editor.missingNames', { locales: missingLocales.value.join(', ') });
    return;
  }
  saving.value = true;
  try {
    const payload = {
      kcal: Number(form.kcal), protein: Number(form.protein),
      carbs: Number(form.carbs), fat: Number(form.fat),
      fiber: form.fiber === null || form.fiber === '' ? null : Number(form.fiber),
      sugar: form.sugar === null || form.sugar === '' ? null : Number(form.sugar),
      salt: form.salt === null || form.salt === '' ? null : Number(form.salt),
      image_id: form.image_id,
      translations: LOCALES.map((l) => ({
        locale: l.code,
        name: translations[l.code].name.trim(),
        description_html: translations[l.code].description_html,
      })),
    };
    if (props.id) await api.updateIngredient(props.id, payload);
    else await api.createIngredient(payload);
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
        {{ props.id ? t('wiki.admin.editor.editIngredient') : t('wiki.admin.editor.newIngredient') }}
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

      <div class="bg-white dark:bg-dark-surface rounded-2xl shadow-md p-5">
        <h2 class="font-semibold mb-3">{{ t('wiki.admin.editor.nutritionPer100') }}</h2>
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div v-for="n in NUTRIENTS" :key="n.key">
            <label class="block text-xs font-medium mb-1 text-gray-500">
              {{ t(`wiki.nutrients.${n.key}`) }} ({{ n.unit }})<span v-if="n.required" class="text-primary">*</span>
            </label>
            <input v-model="form[n.key]" type="number" min="0" step="0.1"
              class="w-full px-3 py-2 rounded-lg border border-gray-200 dark:border-dark-elevated bg-white dark:bg-dark-bg focus:ring-2 focus:ring-primary focus:outline-none" />
          </div>
        </div>
      </div>

      <div class="bg-white dark:bg-dark-surface rounded-2xl shadow-md p-5">
        <div class="flex gap-1 mb-4 border-b border-gray-100 dark:border-dark-elevated">
          <button v-for="l in LOCALES" :key="l.code" type="button"
            @click="activeLocale = l.code"
            class="px-3 py-2 text-sm font-medium border-b-2 transition -mb-px"
            :class="activeLocale === l.code ? 'border-primary text-primary' : 'border-transparent text-gray-400 hover:text-gray-600'">
            {{ l.label }}
            <span v-if="!translations[l.code].name.trim()" class="text-red-400 ml-0.5">•</span>
          </button>
        </div>

        <div v-for="l in LOCALES" v-show="activeLocale === l.code" :key="l.code" class="space-y-3">
          <div>
            <label class="block text-sm font-medium mb-1">{{ t('wiki.admin.editor.name') }} *</label>
            <input v-model="translations[l.code].name" type="text"
              class="w-full px-4 py-2.5 rounded-xl border border-gray-200 dark:border-dark-elevated bg-white dark:bg-dark-bg focus:ring-2 focus:ring-primary focus:outline-none" />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">{{ t('wiki.admin.editor.description') }}</label>
            <RichTextEditor v-model="translations[l.code].description_html" :placeholder="t('wiki.admin.editor.descriptionPlaceholder')" />
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
