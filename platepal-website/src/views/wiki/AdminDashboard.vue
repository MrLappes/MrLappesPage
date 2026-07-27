<script setup>
import { ref, onMounted } from 'vue';
import { useRouter, RouterLink } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { api } from '../../wiki/api.js';
import { auth, logout } from '../../wiki/auth.js';

const router = useRouter();
const { t } = useI18n();

const recipes = ref([]);
const ingredients = ref([]);
const loading = ref(true);
const error = ref('');
const recoveryCodes = ref([]);
const showRecovery = ref(false);

async function load() {
  loading.value = true;
  error.value = '';
  try {
    const [r, i] = await Promise.all([api.adminListRecipes(), api.adminListIngredients()]);
    recipes.value = r;
    ingredients.value = i;
  } catch (e) {
    error.value = e.message;
  } finally {
    loading.value = false;
  }
}

async function onLogout() {
  await logout();
  router.replace({ name: 'WikiAdminLogin' });
}

async function deleteRecipe(id) {
  if (!confirm(t('wiki.admin.dashboard.confirmDelete'))) return;
  try {
    await api.deleteRecipe(id);
    recipes.value = recipes.value.filter((r) => r.id !== id);
  } catch (e) {
    alert(e.message);
  }
}

async function deleteIngredient(id) {
  if (!confirm(t('wiki.admin.dashboard.confirmDelete'))) return;
  try {
    await api.deleteIngredient(id);
    ingredients.value = ingredients.value.filter((i) => i.id !== id);
  } catch (e) {
    alert(e.message);
  }
}

async function regenerateRecovery() {
  if (!confirm(t('wiki.admin.dashboard.confirmRegenerate'))) return;
  try {
    const res = await api.regenerateRecovery();
    recoveryCodes.value = res.recovery_codes;
    showRecovery.value = true;
  } catch (e) {
    alert(e.message);
  }
}

onMounted(load);
</script>

<template>
  <div class="max-w-5xl mx-auto">
    <div class="flex flex-wrap items-center justify-between gap-4 mb-8">
      <div>
        <h1 class="text-2xl md:text-3xl font-bold gradient-text">{{ t('wiki.admin.dashboard.title') }}</h1>
        <p class="text-sm text-gray-500 dark:text-gray-400">{{ t('wiki.admin.dashboard.welcome', { name: auth.username }) }}</p>
      </div>
      <div class="flex gap-2">
        <button @click="regenerateRecovery"
          class="px-3 py-2 rounded-xl border border-gray-200 dark:border-dark-elevated hover:bg-gray-50 dark:hover:bg-dark-bg transition text-sm font-medium">
          <i class="fas fa-shield-halved mr-1"></i>{{ t('wiki.admin.dashboard.recovery') }}
        </button>
        <button @click="onLogout"
          class="px-3 py-2 rounded-xl border border-gray-200 dark:border-dark-elevated hover:bg-gray-50 dark:hover:bg-dark-bg transition text-sm font-medium">
          <i class="fas fa-right-from-bracket mr-1"></i>{{ t('wiki.admin.dashboard.logout') }}
        </button>
      </div>
    </div>

    <div v-if="showRecovery" class="mb-8 bg-white dark:bg-dark-surface rounded-2xl shadow-lg p-6">
      <h2 class="font-bold mb-2"><i class="fas fa-shield-halved text-primary mr-1"></i>{{ t('wiki.admin.login.recoveryTitle') }}</h2>
      <p class="text-sm text-gray-500 dark:text-gray-400 mb-3">{{ t('wiki.admin.login.recoveryWarning') }}</p>
      <div class="grid grid-cols-2 gap-2 bg-gray-50 dark:bg-dark-bg rounded-xl p-4 font-mono text-sm mb-3">
        <span v-for="c in recoveryCodes" :key="c" class="select-all">{{ c }}</span>
      </div>
      <button @click="showRecovery = false" class="text-sm text-primary font-medium">{{ t('wiki.admin.login.savedContinue') }}</button>
    </div>

    <p v-if="error" class="text-red-500 mb-4">{{ error }}</p>

    <div class="grid md:grid-cols-2 gap-8">
      <!-- Recipes -->
      <section>
        <div class="flex items-center justify-between mb-3">
          <h2 class="text-xl font-bold">{{ t('wiki.recipes.title') }}</h2>
          <RouterLink :to="{ name: 'WikiAdminRecipeNew' }"
            class="px-3 py-1.5 rounded-lg gradient-bg text-white text-sm font-medium hover:opacity-90 transition">
            <i class="fas fa-plus mr-1"></i>{{ t('wiki.admin.dashboard.new') }}
          </RouterLink>
        </div>
        <div v-if="loading" class="space-y-2">
          <div v-for="n in 3" :key="n" class="wiki-skeleton h-12 w-full"></div>
        </div>
        <div v-else-if="recipes.length === 0" class="text-sm text-gray-400 py-6 text-center">{{ t('wiki.recipes.empty') }}</div>
        <ul v-else class="space-y-2">
          <li v-for="r in recipes" :key="r.id"
            class="flex items-center gap-3 bg-white dark:bg-dark-surface rounded-xl px-3 py-2 shadow-sm">
            <span class="flex-1 truncate font-medium">{{ r.title }}</span>
            <span v-if="!r.published" class="text-xs px-2 py-0.5 rounded-full bg-gray-100 dark:bg-dark-elevated text-gray-500">
              {{ t('wiki.admin.dashboard.draft') }}
            </span>
            <RouterLink :to="{ name: 'WikiAdminRecipeEdit', params: { id: r.id } }" class="text-gray-400 hover:text-primary transition">
              <i class="fas fa-pen"></i>
            </RouterLink>
            <button @click="deleteRecipe(r.id)" class="text-gray-400 hover:text-red-500 transition">
              <i class="fas fa-trash"></i>
            </button>
          </li>
        </ul>
      </section>

      <!-- Ingredients -->
      <section>
        <div class="flex items-center justify-between mb-3">
          <h2 class="text-xl font-bold">{{ t('wiki.ingredients.title') }}</h2>
          <RouterLink :to="{ name: 'WikiAdminIngredientNew' }"
            class="px-3 py-1.5 rounded-lg gradient-bg text-white text-sm font-medium hover:opacity-90 transition">
            <i class="fas fa-plus mr-1"></i>{{ t('wiki.admin.dashboard.new') }}
          </RouterLink>
        </div>
        <div v-if="loading" class="space-y-2">
          <div v-for="n in 3" :key="n" class="wiki-skeleton h-12 w-full"></div>
        </div>
        <div v-else-if="ingredients.length === 0" class="text-sm text-gray-400 py-6 text-center">{{ t('wiki.ingredients.empty') }}</div>
        <ul v-else class="space-y-2">
          <li v-for="i in ingredients" :key="i.id"
            class="flex items-center gap-3 bg-white dark:bg-dark-surface rounded-xl px-3 py-2 shadow-sm">
            <span class="flex-1 truncate font-medium">{{ i.name }}</span>
            <RouterLink :to="{ name: 'WikiAdminIngredientEdit', params: { id: i.id } }" class="text-gray-400 hover:text-primary transition">
              <i class="fas fa-pen"></i>
            </RouterLink>
            <button @click="deleteIngredient(i.id)" class="text-gray-400 hover:text-red-500 transition">
              <i class="fas fa-trash"></i>
            </button>
          </li>
        </ul>
      </section>
    </div>
  </div>
</template>
