<script setup>
import { computed } from 'vue';
import { useI18n } from 'vue-i18n';

const props = defineProps({
  nutrition: { type: Object, required: true }, // { total, per_serving }
  servings: { type: Number, default: 1 },
});

const { t } = useI18n();

const rows = computed(() => {
  const keys = ['kcal', 'protein', 'carbs', 'fat', 'fiber', 'sugar', 'salt'];
  const unit = (k) => (k === 'kcal' ? 'kcal' : 'g');
  return keys
    .filter((k) => props.nutrition.total[k] !== undefined)
    .map((k) => ({
      key: k,
      label: t(`wiki.nutrients.${k}`),
      unit: unit(k),
      total: props.nutrition.total[k],
      perServing: props.nutrition.per_serving[k],
    }));
});
</script>

<template>
  <div class="bg-white dark:bg-dark-surface rounded-2xl shadow-md overflow-hidden">
    <div class="gradient-bg px-5 py-3">
      <h3 class="text-white font-semibold">{{ t('wiki.nutrition') }}</h3>
    </div>
    <table class="w-full text-sm">
      <thead>
        <tr class="text-left text-gray-500 dark:text-gray-400 border-b border-gray-100 dark:border-dark-elevated">
          <th class="px-5 py-2 font-medium"></th>
          <th class="px-3 py-2 font-medium text-right">{{ t('wiki.perServing') }}</th>
          <th class="px-5 py-2 font-medium text-right">{{ t('wiki.total') }}</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="row in rows"
          :key="row.key"
          class="border-b border-gray-50 dark:border-dark-elevated/50 last:border-0"
        >
          <td class="px-5 py-2 font-medium">{{ row.label }}</td>
          <td class="px-3 py-2 text-right tabular-nums">{{ row.perServing }} {{ row.unit }}</td>
          <td class="px-5 py-2 text-right tabular-nums text-gray-500 dark:text-gray-400">
            {{ row.total }} {{ row.unit }}
          </td>
        </tr>
      </tbody>
    </table>
    <p class="px-5 py-2 text-xs text-gray-400">
      {{ t('wiki.perServingHint', { count: servings }) }}
    </p>
  </div>
</template>
