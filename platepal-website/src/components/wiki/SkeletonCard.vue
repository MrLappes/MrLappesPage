<script setup>
defineProps({
  count: { type: Number, default: 6 },
});
</script>

<template>
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
    <div
      v-for="n in count"
      :key="n"
      class="bg-white dark:bg-dark-surface rounded-2xl shadow-md overflow-hidden"
    >
      <div class="wiki-skeleton h-44 w-full rounded-none"></div>
      <div class="p-4 space-y-3">
        <div class="wiki-skeleton h-5 w-3/4"></div>
        <div class="wiki-skeleton h-4 w-full"></div>
        <div class="wiki-skeleton h-4 w-5/6"></div>
        <div class="flex gap-2 pt-2">
          <div class="wiki-skeleton h-6 w-16 rounded-full"></div>
          <div class="wiki-skeleton h-6 w-20 rounded-full"></div>
        </div>
      </div>
    </div>
  </div>
</template>
