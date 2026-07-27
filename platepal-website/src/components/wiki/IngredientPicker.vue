<script setup>
import { ref, computed, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { api } from '../../wiki/api.js';

// modelValue: array of { ingredient_id, grams }
const props = defineProps({
  modelValue: { type: Array, default: () => [] },
});
const emit = defineEmits(['update:modelValue']);
const { t } = useI18n();

const available = ref([]);
const loading = ref(true);
const selectId = ref('');

onMounted(async () => {
  try {
    available.value = await api.adminListIngredients();
  } finally {
    loading.value = false;
  }
});

const nameById = computed(() => {
  const map = {};
  for (const i of available.value) map[i.id] = i.name;
  return map;
});

const selectable = computed(() =>
  available.value.filter((i) => !props.modelValue.some((r) => r.ingredient_id === i.id))
);

function addIngredient() {
  if (!selectId.value) return;
  const next = [...props.modelValue, { ingredient_id: Number(selectId.value), grams: 100 }];
  emit('update:modelValue', next);
  selectId.value = '';
}

function updateGrams(index, value) {
  const next = props.modelValue.map((row, i) =>
    i === index ? { ...row, grams: Number(value) || 0 } : row
  );
  emit('update:modelValue', next);
}

function remove(index) {
  emit('update:modelValue', props.modelValue.filter((_, i) => i !== index));
}
</script>

<template>
  <div class="space-y-3">
    <div v-if="loading" class="wiki-skeleton h-10 w-full"></div>

    <template v-else>
      <div
        v-for="(row, index) in modelValue"
        :key="row.ingredient_id"
        class="flex items-center gap-3 bg-gray-50 dark:bg-dark-bg rounded-xl px-3 py-2"
      >
        <span class="flex-1 font-medium">{{ nameById[row.ingredient_id] || '#' + row.ingredient_id }}</span>
        <div class="flex items-center gap-1">
          <input
            type="number"
            min="1"
            step="1"
            :value="row.grams"
            class="w-20 px-2 py-1 rounded-lg border border-gray-200 dark:border-dark-elevated bg-white dark:bg-dark-surface text-right"
            @input="updateGrams(index, $event.target.value)"
          />
          <span class="text-gray-400 text-sm">g</span>
        </div>
        <button type="button" class="text-gray-400 hover:text-red-500 transition" @click="remove(index)">
          <i class="fas fa-times"></i>
        </button>
      </div>

      <div class="flex items-center gap-2">
        <select
          v-model="selectId"
          class="flex-1 px-3 py-2 rounded-xl border border-gray-200 dark:border-dark-elevated bg-white dark:bg-dark-surface"
        >
          <option value="">{{ t('wiki.picker.select') }}</option>
          <option v-for="i in selectable" :key="i.id" :value="i.id">{{ i.name }}</option>
        </select>
        <button
          type="button"
          class="px-3 py-2 rounded-xl gradient-bg text-white font-medium hover:opacity-90 transition disabled:opacity-40"
          :disabled="!selectId"
          @click="addIngredient"
        >
          <i class="fas fa-plus mr-1"></i>{{ t('wiki.picker.add') }}
        </button>
      </div>

      <p v-if="available.length === 0" class="text-sm text-gray-400">
        {{ t('wiki.picker.empty') }}
      </p>
    </template>
  </div>
</template>
