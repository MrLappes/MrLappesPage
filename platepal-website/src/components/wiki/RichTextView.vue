<script setup>
import { computed } from 'vue';
import DOMPurify from 'dompurify';

const props = defineProps({
  html: { type: String, default: '' },
});

// The backend already sanitizes, but we sanitize again on render as
// defense-in-depth before using v-html.
const clean = computed(() =>
  DOMPurify.sanitize(props.html || '', {
    USE_PROFILES: { html: true },
    ADD_ATTR: ['target', 'rel'],
  })
);
</script>

<template>
  <div class="wiki-prose" v-html="clean"></div>
</template>
